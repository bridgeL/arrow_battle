import sys
import pickle
import random
from agent import Agent
from tqdm import tqdm
from game import Dir, Game
from .silly_agent import SillyAgent


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
        with open(filename, "rb") as f:
            self.q_table = pickle.load(f)

    def save(self, filename):
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

    def train(self):
        # 设置为训练模式，并重启
        self.is_training = True
        self.last_state = None
        self.mid_state = None
        self.state = None
        self.last_action_index = 0
        self.score = 0
        self.last_score = 0

    def test(self):
        # 设置为测试模式，并重启
        self.is_training = False

    def ai_move(self):
        # 测试模式
        if not self.is_training:
            state = self.get_state()
            actions = self.get_valid_actions()
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

    def update_final_q_table(self, end_by_me):
        final_reward = self.get_final_reward()

        # 由于我无法落子而结束
        if end_by_me:
            self.last_state = self.state
            self.state = self.get_state()

            if self.state not in self.q_table:
                self.q_table[self.state] = [final_reward]

            reward = self.get_reward()
            self.update_q_table(reward)

        # 由于敌方无法落子而结束
        else:
            self.last_state = self.state
            reward = self.get_reward()
            self.update_q_table(reward, final_reward)


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


def train_two_agents(episodes=1000):
    game = Game()

    # 创建两个Agent，分别控制Player 0 和 Player 1
    agent_1 = QLearningAgent(
        alpha=0.1,
        gamma=0.5,
        epsilon=0.099,
    )
    agent_1 = SillyAgent()
    agent_2 = QLearningAgent(
        alpha=0.1,
        gamma=0.5,
        epsilon=0.099,
    )
    # agent_2 = SillyAgent()
    agent_1.bind_game(game, 0)
    agent_2.bind_game(game, 1)
    name_1 = "data/q_table_agent_1.pkl"
    name_2 = "data/q_table_agent_2.pkl"
    # agent_1.load(name_1)
    agent_2.load(name_2)

    agent_1_is_train = True
    agent_1_is_train = False
    both_test = True
    both_test = False

    win_cnt = WinCnt()
    for episode in tqdm(range(episodes)):
        game.restart()  # 每一局重新开始
        if both_test:
            pass

        elif agent_1_is_train:
            agent_1.train()

        else:
            agent_2.train()

        # while True:
        # 30轮内必须结束
        for round in range(30):
            agent_1.ai_move()
            if game.is_game_over:
                if both_test:
                    pass
                elif agent_1_is_train:
                    agent_1.update_final_q_table(False)
                else:
                    agent_2.update_final_q_table(True)
                break

            agent_2.ai_move()
            if game.is_game_over:
                if both_test:
                    pass
                elif agent_1_is_train:
                    agent_1.update_final_q_table(True)
                else:
                    agent_2.update_final_q_table(False)
                break
        else:
            game.game_over()

            # FIXME:
            # 这里有bug，提前结束，那么state对应的action是如何设定的？对应的q值又是多少？
            # 同时state本身不涉及到时间，为什么不同适合一样的state却一个游戏中，一个是游戏结局了？
            # 所以要改
            if both_test:
                pass
            elif agent_1_is_train:
                agent_1.update_final_q_table(True)
            else:
                agent_2.update_final_q_table(False)

        if len(game.winner) > 1:
            win_cnt.tie += 1
        elif game.winner[0].id == 0:
            win_cnt.win += 1
        else:
            win_cnt.lose += 1

    win_cnt.show()
    if both_test:
        pass
    elif agent_1_is_train:
        agent_1.save(name_1)
    else:
        agent_2.save(name_2)


if __name__ == "__main__":
    args = sys.argv

    episodes = 1000
    if len(args) > 1:
        episodes = int(args[1])

    train_two_agents(episodes)
