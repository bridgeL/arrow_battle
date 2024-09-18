import torch
import torch.nn as nn
import torch.nn.functional as F

from agent import Agent
from game import Piece

device = torch.device("cpu")


class YumiModel(nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 定义三层全连接网络
        self.fc1 = nn.Linear(16 * 16, 1024)  # 第一层
        self.fc2 = nn.Linear(1024, 1024)  # 第二层
        self.fc3 = nn.Linear(1024, 1024)  # 第二层
        self.fc4 = nn.Linear(1024, 16 + 16)  # 第三层

    def forward(self, x, mask_pos=None, mask_dir=None):
        # 展平输入，尺寸为 (batch_size, 9*16)
        x = x.view(x.size(0), -1)

        # 前向传播过程：每一层使用 ReLU 激活函数
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        logits = self.fc4(x)  # 最后一层不加激活函数

        # 分割输出：分别得到 x轴、y轴、方向的 logits
        logits_pos = logits[:, :16]  # 9个值，表示坐标
        logits_dir = logits[:, 16:]  # 剩下 16 个值用于方向 (0~15)

        # 应用掩码：将非法位置的 logits 置为无穷小，避免被选中
        if mask_pos is not None:
            logits_pos = logits_pos + mask_pos
        if mask_dir is not None:
            logits_dir = logits_dir + mask_dir

        # 使用 softmax 获取每个部分的概率分布
        out_pos = F.softmax(logits_pos, dim=1)
        out_dir = F.softmax(logits_dir, dim=1)  # 方向输出概率

        return out_pos, out_dir


class DataLoader:
    def __init__(self, data):
        self.data = data

    def get_batches(self, batch_size):
        for i in range(0, len(self.data), batch_size):
            yield self.data[i:i + batch_size]


def train_model(agent, data_loader, num_epochs=10):
    optimizer = torch.optim.Adam(agent.model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(num_epochs):
        for batch in data_loader.get_batches(64):  # 使用合适的批量大小
            statuses, pos_batches, dir_batches, _ = zip(*batch)
            statuses = torch.tensor(statuses, dtype=torch.float32).to(device)

            optimizer.zero_grad()
            pos_pred, dir_pred = agent.model(statuses)

            loss_pos = criterion(pos_pred, torch.tensor(pos_batches).to(device))
            loss_dir = criterion(dir_pred, torch.tensor(dir_batches).to(device))
            loss = loss_pos + loss_dir

            loss.backward()
            optimizer.step()

        print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {loss.item()}\r', end="")


class YumiAgent(Agent):
    def __init__(self):
        super().__init__()
        self.model = YumiModel().to(device)
        self.data = []  # 用于存储对战数据

    def record_action(self, status, pos, dir_val, reward):
        # 将状态、动作和奖励记录到数据列表中
        self.data.append((status.cpu().numpy(), pos, dir_val, reward))

    def load_model(self, path):
        self.model.load_state_dict(torch.load(path))

    def save_model(self, path):
        torch.save(self.model.state_dict(), path)

    def train(self, epoch=10):
        self.model.train()
        data_loader = DataLoader(self.data)
        train_model(self, data_loader, num_epochs=epoch)
        self.data = []
        self.model.eval()

    def get_reward(self):
        score = self.game.players[self.player_id].score - self.game.players[(self.player_id + 1) % 2].score
        if score > 0:
            score *= 2
        # print(score)
        return score

    def piece_to_vector(self, tile: Piece):
        vec = torch.zeros(16)
        if tile:
            n = 0
            if tile.owner.id == 1:
                n += 8
            n += tile.dir.value
            vec[n] = 1
        return vec

    def get_status(self):
        # 转成9*16的tensor
        status = []
        for tile in self.game.tiles:
            status.append(self.piece_to_vector(tile.piece))
        return torch.stack(status)

    def ai_move(self):
        status = self.get_status().to(device).unsqueeze(0)
        # print(self.game.tiles)
        mask_pos = torch.zeros(16).to(device)
        for row in range(4):
            for col in range(4):
                valid, reason = self.game.check_placement_valid(row, col)
                if not valid:
                    mask_pos[row * 4 + col] = -1e9
        if self.player_id == 0:
            mask_dir = torch.concat([torch.zeros(8), torch.ones(8) * -1e9])
        else:
            mask_dir = torch.concat([torch.ones(8) * -1e9, torch.zeros(8)])
        mask_dir = mask_dir.to(device)
        pos, dir_val = self.model(status, mask_pos, mask_dir)
        # print(mask_pos)
        # print(pos)
        pos = torch.argmax(pos, dim=1)[0].item()
        row = pos // 4
        col = pos % 4
        dir_val = torch.argmax(dir_val, dim=1)[0].item() % 8
        # print("action:", row, col)
        valid, reason = self.game.set_placement(row, col, dir_val)
        if not valid:
            raise Exception("下棋位置不对！" + reason)
        # 记录状态、动作等
        reward = self.get_reward()  # 获取当前步骤的奖励
        self.record_action(status, pos, dir_val, reward)
