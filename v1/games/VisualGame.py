from ..game import Game
from ..model import Dir
from colorama import Fore, Style

arrow_map = {
    Dir.N: "↑",
    Dir.NE: "↗",
    Dir.E: "→",
    Dir.SE: "↘",
    Dir.S: "↓",
    Dir.SW: "↙",
    Dir.W: "←",
    Dir.NW: "↖",
}


class VisualGame(Game):
    """对接命令行界面的可视化游戏"""

    def reset(self):
        super().reset()
        self.display_game()

    def display_game(self):
        print(
            "board"
            + " " * (self.size * 3 - 2)
            + "p1 control"
            + " " * (self.size * 3 - 7)
            + "p2 control"
        )
        for x in range(self.size):
            row_str = ""

            # board
            for y in range(self.size):
                if self.map[x][y] == 0:
                    row_str += "[ ]"
                else:
                    dir = Dir(abs(self.map[x][y]) - 1)
                    arrow = arrow_map[dir]
                    if self.map[x][y] > 0:
                        color = Fore.RED
                    else:
                        color = Fore.BLUE
                    row_str += f"[{color}{arrow}{Style.RESET_ALL}]"

            # p1 control
            row_str += "   "
            for y in range(self.size):
                row_str += f"[{self.p1_ctrl[x][y]}]"

            # p2 control
            row_str += "   "
            for y in range(self.size):
                row_str += f"[{self.p2_ctrl[x][y]}]"

            print(row_str)

        scores = self.get_scores()
        print(f"p1: k{scores[0]} c{scores[1]} r{scores[2]} sum{sum(scores[0:3])}")
        print(f"p2: k{scores[3]} c{scores[4]} r{scores[5]} sum{sum(scores[3:6])}")
        print("-" * 70)

    def step(self, action):
        if action.player_index == 1:
            color = Fore.RED
        else:
            color = Fore.BLUE
        print(f"{color}{action}{Style.RESET_ALL}")
        return super().step(action)

    def update(self):
        self.update_ctrl()
        self.display_game()
        while self.fight():
            self.update_ctrl()
            self.display_game()
