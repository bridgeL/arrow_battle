import sys
import pickle
import random
from agent import Agent
from tqdm import tqdm
from game import Dir, Game
from game_viewer import GameViewer
from .silly_agent import SillyAgent


class SafeAgent:
    def load(self, filename):
        pass

    def restart(self):
        pass

    def game_over(self, end_by_my_action, overtime):
        pass


class SafeSillyAgent(SafeAgent, SillyAgent):
    pass


class SafeHumanAgent(SafeAgent, Agent):
    game_viewer: GameViewer

    def __init__(self) -> None:
        super().__init__()
        self.game_viewer = GameViewer()

    def bind_game(self, game, player_id):
        super().bind_game(game, player_id)
        self.game_viewer.bind_game(game)

    def restart(self):
        self.first = True

    def set_placement(self, input_str: str):
        try:
            row, col, dir_value = map(int, input_str.split())
        except ValueError:
            print(
                "Invalid input format. Please enter row, column, and direction value."
            )
            return False

        valid, reason = self.game.set_placement(row, col, dir_value)
        if not valid:
            print(reason)
        return valid

    def ai_move(self):
        if self.first:
            self.first = False
            self.game_viewer.display_board()
        while not self.set_placement(input()):
            pass


class QLearningAgent(Agent):
    def __init__(
        self,
        alpha=0.1,
        gamma=0.9,
        epsilon=0.1,
    ) -> None:
        self.q_table = {}  # 状态-动作值表
        self.alpha = alpha  # 学习率
        self.gamma = gamma  # 折扣因子
        self.epsilon = epsilon  # 探索概率
        self.test()

    def load(self, filename):
        print("AI载入中...", filename)
        with open(filename, "rb") as f:
            self.q_table = pickle.load(f)

    def save(self, filename):
        print("AI保存中...", filename)
        # 保存训练后的 Q 表
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)

    def get_state(self):
        state = []

        # 前9维标注阵营
        for tile in self.game.tiles:
            if not tile.piece:
                state.append(0)
            elif tile.piece.owner.id == 0:
                state.append(1)
            else:
                state.append(-1)

        # 后9维标注方向
        for tile in self.game.tiles:
            if not tile.piece:
                state.append(0)
            else:
                state.append(tile.piece.dir.value)

        return tuple(state)

    def get_valid_actions(self):
        """获取当前合法的所有动作"""
        actions = []
        for row in range(self.game.size):
            for col in range(self.game.size):
                if self.game.check_placement_valid(row, col)[0]:
                    for dir_value in range(8):  # 8个方向
                        action = (row, col, dir_value)
                        actions.append(action)
        return tuple(actions)

    def restart(self):
        self.last_state = None
        self.mid_state = None
        self.state = None
        self.last_action_index = 0
        self.score = 0
        self.last_score = 0
        # self.new_state = 0

    def train(self):
        # 设置为训练模式，并重启
        self.is_training = True
        self.restart()

    def test(self):
        # 设置为测试模式，并重启
        self.is_training = False
        self.restart()

    def ai_move(self):
        # 测试模式
        if not self.is_training:
            state = self.get_state()
            actions = self.get_valid_actions()

            # if state not in self.q_table:
            #     self.new_state += 1

            action_index = self.choose_action_index(state, actions)
            action = actions[action_index]
            self.game.set_placement(*action)

        # 训练模式
        else:
            self.last_state = self.state
            self.last_score = self.score
            state = self.get_state()
            actions = self.get_valid_actions()
            self.score = self.game.players[self.player_id].score
            self.state = state

            # 如果查表没有，就新建，并填充为0
            if state not in self.q_table:
                # self.new_state += 1
                self.q_table[state] = [0] * len(actions)

            # 并非首次行动，则更新上次行动的Q表
            if self.last_state is not None:
                reward = self.get_reward()
                self.update_q_table(reward)

            # 决策
            action_index = self.choose_action_index(state, actions)
            action = actions[action_index]
            self.game.set_placement(*action)
            self.mid_state = self.get_state()

            self.last_action = action
            self.last_action_index = action_index

    def choose_action_index(self, state, actions):
        # 探索: 随机选择一个动作
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, len(actions) - 1)

        # 探索：未见过的新情况
        if state not in self.q_table:
            return random.randint(0, len(actions) - 1)

        # 利用: 选择具有最大 Q 值的动作
        arr = self.q_table[state]
        return max(range(len(arr)), key=lambda i: arr[i])

    def get_reward(self):
        """在敌方落子后获得reward"""
        base_reward = (self.score - self.last_score) * 10
        direction_reward = self.get_direction_reward()
        target_reward = self.get_target_reward()

        return base_reward + direction_reward + target_reward

    def get_direction_reward(self):
        reward = 0
        row, col, dir_value = self.last_action

        # 惩罚指向外部的方向
        if row == 0 and dir_value in [1, 2, 3]:
            reward -= 15
        if row == self.game.size - 1 and dir_value in [5, 6, 7]:
            reward -= 15
        if col == 0 and dir_value in [7, 0, 1]:
            reward -= 15
        if col == self.game.size - 1 and dir_value in [3, 4, 5]:
            reward -= 15

        # 奖励指向中心的方向
        center = self.game.size // 2
        if (row < center and dir_value in [5, 6, 7]) or (
            row > center and dir_value in [1, 2, 3]
        ):
            reward += 5
        if (col < center and dir_value in [3, 4, 5]) or (
            col > center and dir_value in [7, 0, 1]
        ):
            reward += 5

        return reward

    def get_target_reward(self):
        reward = 0
        row, col, dir_value = self.last_action
        n: int = row * self.game.size + col
        next_tile = self.game.tiles[n].get_next_tile(Dir(dir_value), self.game)

        while next_tile:
            if next_tile.piece:
                if next_tile.piece.owner.id != self.player_id:
                    # 奖励指向对方棋子
                    reward += 20
                else:
                    # 轻微惩罚指向自己的棋子
                    reward -= 5
                break
            next_tile = next_tile.get_next_tile(Dir(dir_value), self.game)

        return reward

    def get_final_reward(self):
        # 平局
        if len(self.game.winner) > 1:
            return -10

        # 赢了
        if self.game.winner[0].id == self.player_id:
            return 100

        # 输了
        return -100

    def update_q_table(self, reward, best_action_q=None):
        if best_action_q is None:
            # 获取下一个状态的最大 Q 值
            best_action_q = max(self.q_table[self.state])

        # 更新 Q 值
        old_q = self.q_table[self.last_state][self.last_action_index]
        new_q = reward + self.gamma * best_action_q
        q = (1 - self.alpha) * old_q + self.alpha * new_q
        self.q_table[self.last_state][self.last_action_index] = q

    def game_over(self, end_by_my_action, overtime):
        if not self.is_training:
            return

        final_reward = self.get_final_reward()

        # 由于游戏超时而结束
        if overtime:
            return

        # 在我的上一步行动后，由于敌方无法落子而结束
        if end_by_my_action:
            self.last_state = self.state
            reward = self.get_reward()
            self.update_q_table(reward, final_reward)

        # 在敌方的上一步行动后，由于我无法落子而结束
        else:
            self.last_state = self.state
            self.state = self.get_state()

            if self.state not in self.q_table:
                self.q_table[self.state] = [final_reward]

            reward = self.get_reward()
            self.update_q_table(reward)


class WinCnt:
    def __init__(self) -> None:
        self.clear()

    def clear(self):
        self.tie = 0
        self.win = 0
        self.lose = 0

    @property
    def cnt(self):
        return self.tie + self.win + self.lose

    def show(self):
        print(f"tie: {self.tie/self.cnt*100:.2f}%")
        print(f"win: {self.win/self.cnt*100:.2f}%")
        print(f"lose: {self.lose/self.cnt*100:.2f}%")


def train_two_agents(mode=1):
    game = Game()
    if mode == 1:
        print("agent 1 探索阶段")
        episodes = 100000

    elif mode == 2:
        print("agent 1 学习阶段")
        episodes = 10000

    elif mode == 3:
        print("agent 2 探索阶段")
        episodes = 100000

    elif mode == 4:
        print("agent 2 学习阶段")
        episodes = 10000

    elif mode == 5:
        print("agent 1 vs agent 2 测试")
        episodes = 1000

    # 创建两个Agent，分别控制Player 0 和 Player 1
    agent_1 = QLearningAgent(
        alpha=0.1,
        gamma=0.9,
        epsilon=0.5 if mode == 1 else 0.0005,
    )
    if mode in [1, 2]:
        agent_1.train()
    # agent_1 = SafeSillyAgent()
    # agent_1 = SafeHumanAgent()

    agent_2 = QLearningAgent(
        alpha=0.1,
        gamma=0.9,
        epsilon=0.5 if mode == 3 else 0.0005,
    )
    if mode in [3, 4]:
        agent_2.train()
    # agent_2 = SafeSillyAgent()

    agent_1.bind_game(game, 0)
    agent_2.bind_game(game, 1)
    name_1 = "data/q_table_agent_1.pkl"
    name_2 = "data/q_table_agent_2.pkl"
    agent_1.load(name_1)
    agent_2.load(name_2)

    win_cnt = WinCnt()
    for episode in tqdm(range(episodes)):
        game.restart()  # 每一局重新开始
        agent_1.restart()
        agent_2.restart()

        # while True:
        # 30轮内必须结束
        for round in range(30):
            agent_1.ai_move()
            if game.is_game_over:
                agent_1.game_over(True, False)
                agent_2.game_over(False, False)
                break

            agent_2.ai_move()
            if game.is_game_over:
                agent_1.game_over(False, False)
                agent_2.game_over(True, False)
                break
        else:
            game.game_over()
            agent_1.game_over(False, True)
            agent_2.game_over(True, True)

        if len(game.winner) > 1:
            win_cnt.tie += 1
        elif game.winner[0].id == 0:
            win_cnt.win += 1
        else:
            win_cnt.lose += 1

    win_cnt.show()
    safe_save(agent_1, name_1)
    safe_save(agent_2, name_2)


def safe_save(agent, name):
    if type(agent) is QLearningAgent and agent.is_training:
        agent.save(name)


if __name__ == "__main__":
    args = sys.argv

    if len(args) == 1:
        train_two_agents(1)
        train_two_agents(2)
        train_two_agents(3)
        train_two_agents(4)
    else:
        train_two_agents(int(args[1]))
