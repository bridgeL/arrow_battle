from agent import Agent
from game import Game
import torch
import random


def get_state(game: Game):
    state = []

    # 0-8维标注阵营
    for tile in game.tiles:
        if not tile.piece:
            state.append(0)
        else:
            p = tile.piece.owner.id
            p = 1 if p == 0 else p == -1
            state.append(p)

    # 9-17维标注方向
    for tile in game.tiles:
        if not tile.piece:
            state.append(0)
        else:
            v = tile.piece.dir.value
            # 从 [0, 7] 映射到 [-4, 4] \ {0}
            v = v - 4 if v < 4 else v - 3
            state.append(v)

    return state


def get_valid_actions(game: Game):
    actions = []
    for row in range(3):
        for col in range(3):
            valid, reason = game.check_placement_position_valid(row, col)
            if valid:
                for dir_val in range(8):
                    actions.append((row, col, dir_val))
    return actions


def get_action_id(action: tuple):
    row, col, dir_val = action
    return row * 3 * 8 + col * 8 + dir_val


def parse_action_id(action_id: int):
    dir_val = action_id % 8
    action_id //= 8
    col = action_id % 3
    row = action_id // 3
    action = (row, col, dir_val)
    return action


class DQN(torch.nn.Module):
    def __init__(self):
        super().__init__()

        # 18维状态向量
        state_size = 18
        # 72种可能的动作
        action_size = 72

        # 层
        self.fc1 = torch.nn.Linear(state_size, 1024)
        self.fc2 = torch.nn.Linear(1024, 512)
        self.fc3 = torch.nn.Linear(512, action_size)

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


class DQNAgent(Agent):
    def __init__(
        self,
        learn_rate=0.01,
        gamma=0.5,
        epsilon=0.9,
    ) -> None:
        self.model = DQN()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learn_rate)  # type: ignore
        self.criterion = torch.nn.MSELoss()
        self.memory = []
        self.batch_size = 32
        self.gamma = gamma
        self.epsilon = epsilon
        self.game_cnt = 0

    def load(self, filename):
        print(f"加载模型 {filename}")
        self.model.load_state_dict(torch.load(filename, weights_only=True))

    def save(self, filename):
        print(f"保存模型 {filename}")
        torch.save(self.model.state_dict(), filename)

    def on_game_start(self):
        self.last_state = None
        self.last_action_id = -1
        self.reward = 0
        self.last_score = 0

    def get_state(self):
        assert self.game
        state = get_state(self.game)
        state = torch.tensor(state, dtype=torch.float32)
        return state

    def get_valid_actions(self):
        assert self.game
        return get_valid_actions(self.game)

    def on_game_over(self):
        assert self.game
        if self.game.winner_id < 0:
            reward = -10
        elif self.game.winner_id == self.player_id:
            reward = 100
        else:
            reward = -100

        # 游戏结束时，上一个state一定不是None
        assert self.last_state is not None

        # next state 取决于结束时是否轮到当前agent
        if self.game.current_player_id == self.player_id:
            state = self.get_state()
        else:
            state = self.last_state

        # 游戏结束保存经验
        self.store_transition(self.last_state, self.last_action_id, reward, state, True)

        if self.is_training:
            self.train_model()

            # # 每10局结束后训练1次
            # self.game_cnt += 1
            # if self.game_cnt >= 10:
            #     self.game_cnt = 0
            #     self.train_model()

    def get_action(self):
        assert self.game
        # current state
        state = self.get_state()
        valid_actions = self.get_valid_actions()
        score = self.game.current_player.score

        # 处理上一次的state和action id
        if self.last_state is not None:
            # 根据分数变化作为奖励
            d_score = score - self.last_score
            self.reward += d_score * 10

            self.store_transition(
                self.last_state, self.last_action_id, self.reward, state, False
            )

        # save
        self.last_state = state
        self.last_score = score

        if random.random() < self.epsilon:
            # get action by Q network
            q_values = self.model(state)
            action_id = int(torch.argmax(q_values).item())
            action = parse_action_id(action_id)

            # save
            self.last_action_id = action_id

            # check
            if action in valid_actions:
                return action

            # 不存无效数据
            # # give punish for invalid action
            # self.store_transition(state, action_id, -100, state, False)

        # get action randomly
        action = random.choice(valid_actions)
        action_id = get_action_id(action)

        # save
        self.last_action_id = action_id

        return action

    def move(self):
        assert self.game
        action = self.get_action()
        row, col, dir_val = action

        # 清空奖励
        self.reward = 0

        # TODO:
        # 计算落子奖励
        # 选择角落加分：
        if (row == 0 or row == self.game.size - 1) and (
            col == 0 or col == self.game.size - 1
        ):
            self.reward += 10
        # 指向敌方棋子则加分：

        valid, reason = self.game.set_placement(row, col, dir_val, self.player_id)
        assert valid, reason

        # 立刻吃子
        score = self.game.players[self.player_id].score
        d_score = score - self.last_score
        self.reward += d_score * 10

    def store_transition(
        self,
        state: torch.Tensor,
        action_id: int,
        reward,
        next_state: torch.Tensor,
        done: bool,
    ):
        reward = torch.tensor(reward, dtype=torch.float32)

        self.memory.append((state, action_id, reward, next_state, done))
        if len(self.memory) > 10000:
            self.memory.pop(0)

    def train_model(self):
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)

        for state, action_id, reward, next_state, done in minibatch:
            q_values = self.model(state)
            q_value = q_values[action_id]

            if done:
                target = reward  # 终局状态，目标是当前奖励
            else:
                next_q_values = self.model(next_state)
                next_q_value = torch.max(next_q_values)
                target = reward + self.gamma * next_q_value

            loss = self.criterion(q_value, target.clone().detach())
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
