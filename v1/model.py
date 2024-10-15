from enum import Enum


class Dir(Enum):
    N_ = 0
    NE = 1
    E_ = 2
    SE = 3
    S_ = 4
    SW = 5
    W_ = 6
    NW = 7


dxdy_map = {
    Dir.N_: (-1, 0),
    Dir.NE: (-1, 1),
    Dir.E_: (0, 1),
    Dir.SE: (1, 1),
    Dir.S_: (1, 0),
    Dir.SW: (1, -1),
    Dir.W_: (0, -1),
    Dir.NW: (-1, -1),
}


class Action:
    def __init__(self, x: int, y: int, dir: Dir):
        self.x = x
        self.y = y
        self.dir = dir

    def __repr__(self):
        return f"Action(x={self.x}, y={self.y}, {self.dir})"


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
        self.player_index = current_player_index
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

    def clone(self):
        size = len(self.map)
        map = [[self.map[j][i] for i in range(size)] for j in range(size)]
        p1_ctrl = [[self.p1_ctrl[j][i] for i in range(size)] for j in range(size)]
        p2_ctrl = [[self.p2_ctrl[j][i] for i in range(size)] for j in range(size)]
        return State(
            map, p1_ctrl, p2_ctrl, self.player_index, self.p1_kill, self.p2_kill
        )

    def __repr__(self):
        return f"State(map={self.map}, p{self.player_index}, k1={self.p1_kill}, k2={self.p2_kill})"

    def update_ctrl(self):
        next_state = self.clone()
        size = len(next_state.map)

        for x in range(size):
            for y in range(size):
                next_state.p1_ctrl[x][y] = 0
                next_state.p2_ctrl[x][y] = 0

        for x in range(size):
            for y in range(size):
                if next_state.map[x][y] == 0:
                    continue

                dir = Dir(abs(next_state.map[x][y]) - 1)
                dx, dy = dxdy_map[dir]

                if next_state.map[x][y] > 0:
                    xx = x + dx
                    yy = y + dy
                    while xx >= 0 and xx < size and yy >= 0 and yy < size:
                        next_state.p1_ctrl[xx][yy] += 1
                        xx += dx
                        yy += dy

                else:
                    xx = x + dx
                    yy = y + dy
                    while xx >= 0 and xx < size and yy >= 0 and yy < size:
                        next_state.p2_ctrl[xx][yy] += 1
                        xx += dx
                        yy += dy
        return next_state

    def turn_next(self):
        next_state = self.clone()
        if next_state.player_index == 1:
            next_state.player_index = 2
        else:
            next_state.player_index = 1
        return next_state

    def fight(self):
        next_state = self.clone()
        size = len(next_state.map)

        is_anyone_dead = False
        for x in range(size):
            for y in range(size):
                if next_state.map[x][y] == 0:
                    continue
                if next_state.map[x][y] < 0:
                    if next_state.p1_ctrl[x][y] >= 2:
                        next_state.map[x][y] = 0
                        next_state.p1_kill += 1
                        is_anyone_dead = True
                else:
                    if next_state.p2_ctrl[x][y] >= 2:
                        next_state.map[x][y] = 0
                        next_state.p2_kill += 1
                        is_anyone_dead = True

        return next_state, is_anyone_dead

    def set_placement(self, action: Action):
        next_state = self.clone()
        if self.player_index == 1:
            next_state.map[action.x][action.y] = action.dir.value + 1
        else:
            next_state.map[action.x][action.y] = -(action.dir.value + 1)
        return next_state

    def get_scores(self):
        size = len(self.map)
        ctrl1 = 0
        ctrl2 = 0
        remain1 = 0
        remain2 = 0
        for x in range(size):
            for y in range(size):
                if self.map[x][y] == 0:
                    if self.p1_ctrl[x][y] >= 2:
                        ctrl1 += 1
                    if self.p2_ctrl[x][y] >= 2:
                        ctrl2 += 1
                elif self.map[x][y] > 0:
                    remain1 += 1
                else:
                    remain2 += 1
        return [self.p1_kill, ctrl1, remain1, self.p2_kill, ctrl2, remain2]
