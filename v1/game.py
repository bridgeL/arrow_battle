from .model import Action, State


class Game:
    """游戏的纯逻辑部分"""

    def __init__(self, size: int):
        self.size = size
        self.is_over = False
        self.state = State.create(self.size)

    def check_position(self, x: int, y: int) -> tuple[bool, str]:
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False, "该位置超出边界"
        if self.state.map[x][y] != 0:
            return False, "该位置已经有棋子了"
        if self.state.player_index == 1 and self.state.p2_ctrl[x][y] >= 2:
            return False, "该位置被他人控制"
        if self.state.player_index == 2 and self.state.p1_ctrl[x][y] >= 2:
            return False, "该位置被他人控制"
        return True, ""

    def check_end(self):
        size = self.size

        if self.state.player_index == 1:
            for x in range(size):
                for y in range(size):
                    if self.state.map[x][y] == 0 and self.state.p2_ctrl[x][y] < 2:
                        return False

        else:
            for x in range(size):
                for y in range(size):
                    if self.state.map[x][y] == 0 and self.state.p1_ctrl[x][y] < 2:
                        return False

        return True

    def step(self, action: Action) -> tuple[bool, str]:
        valid, reason = self.check_position(action.x, action.y)
        if not valid:
            return False, reason

        self.state = self.state.set_placement(action)
        self.state = self.state.update_ctrl()
        self.state, changed = self.state.fight()
        while changed:
            self.state = self.state.update_ctrl()
            self.state, changed = self.state.fight()

        self.state = self.state.turn_next()
        self.is_over = self.check_end()
        return True, ""

    def reset(self):
        self.is_over = False
        self.state = State.create(self.size)

    def set_state(self, state: State):
        self.is_over = False
        self.state = state

    def get_result(self) -> str:
        scores = self.state.get_scores()
        score1 = sum(scores[0:3])
        score2 = sum(scores[3:6])
        if score1 > score2:
            return "win"
        if score1 == score2:
            return "tie"
        return "lose"
