from enum import Enum


class Dir(Enum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7


class Action:
    def __init__(self, x: int, y: int, dir: Dir, player_index: int):
        self.x = x
        self.y = y
        self.dir = dir
        self.player_index = player_index

    def __repr__(self):
        return f"Action({self.x}, {self.y}, {self.dir}, p{self.player_index})"
