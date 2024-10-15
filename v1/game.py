from .model import Action, Dir

dxdy_map = {
    Dir.N: (-1, 0),
    Dir.NE: (-1, 1),
    Dir.E: (0, 1),
    Dir.SE: (1, 1),
    Dir.S: (1, 0),
    Dir.SW: (1, -1),
    Dir.W: (0, -1),
    Dir.NW: (-1, -1),
}


class Game:
    """游戏的纯逻辑部分"""

    def __init__(self, size: int):
        self.size = size
        self.reset()

    def check_position(self, x: int, y: int, player_index: int) -> tuple[bool, str]:
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False, "该位置超出边界"
        if self.map[x][y] != 0:
            return False, "该位置已经有棋子了"
        if player_index == 1 and self.p2_ctrl[x][y] >= 2:
            return False, "该位置被他人控制"
        if player_index == 2 and self.p1_ctrl[x][y] >= 2:
            return False, "该位置被他人控制"
        return True, ""

    def update(self):
        self.update_ctrl()
        while self.fight():
            self.update_ctrl()

    def fight(self):
        is_anyone_dead = False
        for x in range(self.size):
            for y in range(self.size):
                if self.map[x][y] == 0:
                    continue
                if self.map[x][y] < 0:
                    if self.p1_ctrl[x][y] >= 2:
                        self.map[x][y] = 0
                        self.p1_kill += 1
                        is_anyone_dead = True
                else:
                    if self.p2_ctrl[x][y] >= 2:
                        self.map[x][y] = 0
                        self.p2_kill += 1
                        is_anyone_dead = True
        return is_anyone_dead

    def update_ctrl(self):
        for x in range(self.size):
            for y in range(self.size):
                self.p1_ctrl[x][y] = 0
                self.p2_ctrl[x][y] = 0

        for x in range(self.size):
            for y in range(self.size):
                if self.map[x][y] == 0:
                    continue

                dir = Dir(abs(self.map[x][y]) - 1)
                dx, dy = dxdy_map[dir]

                if self.map[x][y] > 0:
                    xx = x + dx
                    yy = y + dy
                    while xx >= 0 and xx < self.size and yy >= 0 and yy < self.size:
                        self.p1_ctrl[xx][yy] += 1
                        xx += dx
                        yy += dy

                else:
                    xx = x + dx
                    yy = y + dy
                    while xx >= 0 and xx < self.size and yy >= 0 and yy < self.size:
                        self.p2_ctrl[xx][yy] += 1
                        xx += dx
                        yy += dy

    def check_end(self):
        if self.current_player_index == 1:
            for x in range(self.size):
                for y in range(self.size):
                    if self.map[x][y] == 0 and self.p2_ctrl[x][y] < 2:
                        return False
        else:
            for x in range(self.size):
                for y in range(self.size):
                    if self.map[x][y] == 0 and self.p1_ctrl[x][y] < 2:
                        return False

        return True

    def check_action(self, action: Action) -> tuple[bool, str]:
        if self.is_over:
            return False, "游戏已经结束"

        if self.current_player_index != action.player_index:
            return False, "没轮到你行动"

        return self.check_position(action.x, action.y, action.player_index)

    def set_placement(self, action: Action):
        if action.player_index == 1:
            self.map[action.x][action.y] = action.dir.value + 1
        else:
            self.map[action.x][action.y] = -(action.dir.value + 1)

    def turn_next(self):
        if self.current_player_index == 1:
            self.current_player_index = 2
        else:
            self.current_player_index = 1

    def step(self, action: Action) -> tuple[bool, str]:
        valid, reason = self.check_action(action)
        if not valid:
            return False, reason

        self.set_placement(action)
        self.update()
        self.turn_next()

        self.is_over = self.check_end()
        return True, ""

    def reset(self):
        size = self.size
        self.is_over = False
        self.map = [[0 for i in range(size)] for j in range(size)]
        self.p1_ctrl = [[0 for i in range(size)] for j in range(size)]
        self.p2_ctrl = [[0 for i in range(size)] for j in range(size)]
        self.current_player_index = 1
        self.p1_kill = 0
        self.p2_kill = 0

    def get_scores(self):
        ctrl1 = 0
        ctrl2 = 0
        remain1 = 0
        remain2 = 0
        for x in range(self.size):
            for y in range(self.size):
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

    def get_result(self) -> str:
        scores = self.get_scores()
        score1 = sum(scores[0:3])
        score2 = sum(scores[3:6])
        if score1 > score2:
            return "win"
        if score1 == score2:
            return "tie"
        return "lose"
