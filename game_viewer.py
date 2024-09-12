from game import Game, Dir
from colorama import Fore, Style
from agent import Agent


class GameViewer:
    game: Game

    arrow_map = {
        Dir.LEFT: "←",
        Dir.LEFT_TOP: "↖",
        Dir.TOP: "↑",
        Dir.RIGHT_TOP: "↗",
        Dir.RIGHT: "→",
        Dir.RIGHT_BOTTOM: "↘",
        Dir.BOTTOM: "↓",
        Dir.LEFT_BOTTOM: "↙",
    }

    color_map = {
        0: Fore.RED,  # 玩家0的颜色
        1: Fore.BLUE,  # 玩家1的颜色
        2: Fore.GREEN,  # 玩家2的颜色 (如果有更多玩家，可以继续添加颜色)
        3: Fore.YELLOW,
    }

    def __init__(self) -> None:
        game = Game()
        self.bind_game(game)

    def bind_game(self, game: Game):
        self.game = game
        self.game.on_game_over = self.display_winner
        self.game.on_update_end = self.display_turn
        self.game.on_update = self.display_game

    def set_placement(self, input_str: str):
        try:
            row, col, dir_value = map(int, input_str.split())
        except ValueError:
            print(
                "Invalid input format. Please enter row, column, and direction value."
            )
            return

        valid, reason = self.game.set_placement(row, col, dir_value)
        if not valid:
            print(reason)

    def display_turn(self):
        # print game string for debug
        print(self.game.get_game_str())

        # print next turn
        player = self.game.players[self.game.current_player_index]
        color = self.get_color(player.id)
        print(f"{color}>> Player {player.id}'s turn{Style.RESET_ALL}")

    def get_color(self, player_id):
        return self.color_map.get(player_id, Fore.WHITE)  # 预设一个默认颜色

    def display_winner(self):
        s = ""
        for player in self.game.winner:
            color = self.get_color(player.id)
            s += f"{color}Player {player.id}{Style.RESET_ALL} "
        s = s[:-1]

        if len(self.game.winner) > 1:
            print(f"Tie among {s}")
        else:
            print(f"{s} wins!")

    def display_board(self):
        for i in range(self.game.size):
            row_str = ""
            for j in range(self.game.size):
                tile = self.game.tiles[i * self.game.size + j]
                if tile.piece is None:
                    row_str += "[ ]"
                else:
                    player_id = tile.piece.owner.id
                    direction_arrow = self.arrow_map[tile.piece.dir]
                    color = self.get_color(player_id)
                    row_str += f"[{color}{direction_arrow}{Style.RESET_ALL}]"
            print(row_str)

    def display_score(self):
        for player in self.game.players:
            color = self.get_color(player.id)
            print(
                f"{color}Player {player.id} | score: {player.score} (kill: {player.kill}, remain: {player.remain}, control: {player.control}){Style.RESET_ALL}"
            )

    def display_game(self):
        self.display_board()
        self.display_score()

    def start(self):
        self.display_game()
        self.display_turn()

        while True:
            input_str = input()

            if input_str == "restart":
                print("game restart")
                self.game.restart()
                self.display_game()
                self.display_turn()

            elif input_str == "exit":
                break

            elif input_str.startswith("g"):
                game = Game.from_game_str(input_str)
                self.bind_game(game)
                self.display_game()
                self.display_turn()

            else:
                self.set_placement(input_str)


class PvEGameViewer(GameViewer):
    agent: Agent

    def __init__(self, agent, agent_first) -> None:
        super().__init__()
        self.agent = agent
        self.agent_first = agent_first
        self.agent.bind_game(self.game, 0 if agent_first else 1)

    def start(self):
        """开启Player vs AI 的对弈"""
        self.display_game()
        self.display_turn()

        if self.agent_first:
            while True:
                self.agent.ai_move()
                if self.game.is_game_over:
                    break

                self.set_placement(input())
                if self.game.is_game_over:
                    break

        else:
            while True:
                self.set_placement(input())
                if self.game.is_game_over:
                    break

                self.agent.ai_move()
                if self.game.is_game_over:
                    break


class EvEGameViewer(GameViewer):
    agent_1: Agent
    agent_2: Agent

    def __init__(self, agent_1, agent_2) -> None:
        super().__init__()
        self.agent_1 = agent_1
        self.agent_2 = agent_2
        self.agent_1.bind_game(self.game, 0)
        self.agent_2.bind_game(self.game, 1)

    def start(self):
        """开启AI vs AI 的对弈"""
        self.display_game()
        self.display_turn()

        while True:
            self.agent_1.ai_move()
            if self.game.is_game_over:
                break

            self.agent_2.ai_move()
            if self.game.is_game_over:
                break
