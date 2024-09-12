import random
import sys
import numpy as np
from agent import Agent
from tqdm import tqdm
import pickle

from game import Game


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
        self.restart()
        self.new_state_cnt = 0

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

    def get_score(self):
        """返回总分，remain，kill，control"""
        p = self.game.players[self.player_id]
        score = [
            p.score,
            p.remain,
            p.kill,
            p.control,
        ]
        return tuple(score)

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
        self.state = None
        self.action_index = 0
        self.actions = []
        self.clear_information()

    def choose_action_index(self):
        # 探索: 随机选择一个动作
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, len(self.actions) - 1)
        # 利用: 选择具有最大 Q 值的动作
        return np.argmax(self.q_table[self.state])

    def update_state(self):
        self.last_state = self.state
        self.state = self.get_state()
        self.actions = self.get_valid_actions()

        # 如果查表没有，就新建，并填充为0
        if self.state not in self.q_table:
            # 记录遇到新情况的次数
            self.new_state_cnt += 1

            # 即使actions为空（游戏结束），也要保存一个state，来保存最终的Q值
            n = max(len(self.actions), 1)
            self.q_table[self.state] = np.zeros(n)

    def ai_move(self):
        self.update_state()

        # decision
        action_index = self.choose_action_index()
        action = self.actions[action_index]

        # save decision
        self.action_index = action_index

        # apply
        self.game.set_placement(*action)

    def act(self):
        # decision
        self.action_index = self.choose_action_index()
        action = self.actions[self.action_index]

        # apply
        self.game.set_placement(*action)

    def clear_information(self):
        self.last_score = None
        self.score = None

        self.immediate_state = None
        self.immediate_score = None

        self.reward = 0

    def collect_immediate_information(self):
        self.immediate_state = self.get_state()
        self.immediate_score = self.get_score()

    def collect_information(self):
        self.last_score = self.score
        self.score = self.get_score()

    def get_reward(self):
        """在敌方落子后获得reward"""
        reward = 0
        d_kill = self.score[1] - self.last_score[1]
        reward += d_kill * 5

        # # 训练时要求每个落子的方向尽可能指向更多区域
        # d_pointing = self.immediate_score[4] - self.last_score[4] - 2
        # reward += d_pointing * 10

        # 避免下在自己的控制区
        d_control = self.immediate_score[3] - self.last_score[3]
        if d_control < 0:
            reward += d_control * 5

        self.reward = reward
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

    def update_q_table(self, reward):
        # 获取下一个状态的最大 Q 值
        best_next_action = np.max(self.q_table[self.state])

        # 更新 Q 值
        old_q = self.q_table[self.last_state][self.action_index]
        new_q = reward + self.gamma * best_next_action
        q = (1 - self.alpha) * old_q + self.alpha * new_q
        self.q_table[self.last_state][self.action_index] = q


def train_two_agents(episodes=1000):
    game = Game()

    # 创建两个Agent，分别控制Player 0 和 Player 1
    agent_1 = QLearningAgent()
    agent_2 = QLearningAgent()
    agent_1.bind_game(game, 0)
    agent_2.bind_game(game, 1)
    name_1 = "data/q_table_agent_1.pkl"
    name_2 = "data/q_table_agent_2.pkl"
    # agent_1.load(name_1)
    # agent_2.load(name_2)

    _agent_1 = agent_1
    _agent_2 = agent_2

    miniters = min(episodes // 1000, 50)

    for episode in tqdm(range(episodes), miniters=miniters):
        game.restart()  # 每一局重新开始
        agent_1 = _agent_1
        agent_2 = _agent_2

        agent_1.restart()
        agent_2.restart()

        agent_1.collect_information()
        agent_2.collect_information()

        agent_1.update_state()
        agent_1.act()
        agent_1.collect_immediate_information()

        while not game.is_game_over:
            agent_2.update_state()
            agent_2.act()
            agent_2.collect_immediate_information()
            agent_1.update_state()

            if game.is_game_over:
                agent_1.update_q_table(agent_1.get_final_reward())
                agent_2.update_q_table(agent_2.get_final_reward())
                break

            agent_1.collect_information()
            agent_1.update_q_table(agent_1.get_reward())

            agent_1, agent_2 = agent_2, agent_1

    agent_1 = _agent_1
    agent_2 = _agent_2
    agent_1.save(name_1)
    agent_2.save(name_2)


if __name__ == "__main__":
    args = sys.argv

    episodes = 1000
    if len(args) > 1:
        episodes = int(args[1])

    train_two_agents(episodes)
