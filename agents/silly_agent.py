from random import randint

import torch

from agent import Agent
from game import Piece

device = torch.device("cpu")


class SillyAgent(Agent):
    def __init__(self):
        super().__init__()
        self.data = []  # 用于存储对战数据

    def record_action(self, status, pos, dir_val, reward):
        # 将状态、动作和奖励记录到数据列表中
        self.data.append((status.cpu().numpy(), pos, dir_val, reward))

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
        while True:
            row = randint(0, 2)
            col = randint(0, 2)
            dir_val = randint(0, 7)
            valid, reason = self.game.set_placement(row, col, dir_val)
            if valid:
                self.record_action(self.get_status().to(device).unsqueeze(0), row * 3 + col, dir_val, 0)
                break
