from ..game import Game
from ..model import Dir, State
from colorama import Fore, Style

arrow_map = {
    Dir.N_: "↑",
    Dir.NE: "↗",
    Dir.E_: "→",
    Dir.SE: "↘",
    Dir.S_: "↓",
    Dir.SW: "↙",
    Dir.W_: "←",
    Dir.NW: "↖",
}


class VisualGame(Game):
    """对接命令行界面的可视化游戏"""

    def reset(self):
        super().reset()
        self.display_state(self.state)

    def display_state(self, state: State):
        size = len(state.map)
        print(
            "board"
            + " " * (size * 3 - 2)
            + "p1 control"
            + " " * (size * 3 - 7)
            + "p2 control"
        )
        for x in range(size):
            row_str = ""

            # board
            for y in range(size):
                if state.map[x][y] == 0:
                    row_str += "[ ]"
                else:
                    dir = Dir(abs(state.map[x][y]) - 1)
                    arrow = arrow_map[dir]
                    if state.map[x][y] > 0:
                        color = Fore.RED
                    else:
                        color = Fore.BLUE
                    row_str += f"[{color}{arrow}{Style.RESET_ALL}]"

            # p1 control
            row_str += "   "
            for y in range(size):
                row_str += f"[{state.p1_ctrl[x][y]}]"

            # p2 control
            row_str += "   "
            for y in range(size):
                row_str += f"[{state.p2_ctrl[x][y]}]"

            print(row_str)

        scores = state.get_scores()
        print(f"p1: k{scores[0]} c{scores[1]} r{scores[2]} sum{sum(scores[0:3])}")
        print(f"p2: k{scores[3]} c{scores[4]} r{scores[5]} sum{sum(scores[3:6])}")
        print("-" * 70)

    def step(self, action) -> tuple[bool, str]:
        if self.state.player_index == 1:
            color = Fore.RED
        else:
            color = Fore.BLUE
        print(f"{color}{action}{Style.RESET_ALL}")

        valid, reason = self.check_position(action.x, action.y)
        if not valid:
            return False, reason

        self.state = self.state.set_placement(action)
        self.state = self.state.update_ctrl()
        self.display_state(self.state)
        self.state, changed = self.state.fight()
        while changed:
            self.state = self.state.update_ctrl()
            self.display_state(self.state)
            self.state, changed = self.state.fight()

        self.state = self.state.turn_next()
        self.is_over = self.check_end()
        return True, ""
