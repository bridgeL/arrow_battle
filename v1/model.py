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


class State:
    def __init__(
        self,
        map: list[list[int]],
        p1_ctrl: list[list[int]],
        p2_ctrl: list[list[int]],
        current_player_index: int,
        p1_kill: int,
        p2_kill: int,
    ):
        self.map = map
        self.p1_ctrl = p1_ctrl
        self.p2_ctrl = p2_ctrl
        self.current_player_index = current_player_index
        self.p1_kill = p1_kill
        self.p2_kill = p2_kill

    @classmethod
    def create(cls, size: int):
        map = [[0 for i in range(size)] for j in range(size)]
        p1_ctrl = [[0 for i in range(size)] for j in range(size)]
        p2_ctrl = [[0 for i in range(size)] for j in range(size)]
        current_player_index = 1
        p1_kill = 0
        p2_kill = 0
        return State(map, p1_ctrl, p2_ctrl, current_player_index, p1_kill, p2_kill)
