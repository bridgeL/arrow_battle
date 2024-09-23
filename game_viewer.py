from game import Game, Dir, Player, Tile
from colorama import Fore, Style

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

first_player_color = Fore.RED
second_player_color = Fore.BLUE
reset_color = Style.RESET_ALL


class GameViewer:
    def __init__(self) -> None:
        self.displaying = True

    def bind_game(self, game: Game):
        self.game = game
        self.add_event_trigger("on_game_over", self.on_game_over)
        self.add_event_trigger("on_wait_next_placement", self.on_wait_next_placement)
        self.add_event_trigger("on_board_update", self.display_board)
        self.add_event_trigger("on_game_start", self.on_game_start)
        self.add_event_trigger("on_placement", self.display_placement)

    def display_on(self):
        self.displaying = True

    def display_off(self):
        self.displaying = False

    def add_event_trigger(self, event_type: str, callback):
        def _func(*args):
            if not self.displaying:
                return
            callback(*args)

        self.game.event_handler.add_event_trigger(event_type, self, _func)

    def on_game_start(self):
        self.display_board()
        self.display_score()
        print("-" * 70)
        self.display_turn()

    def on_game_over(self):
        self.display_score()
        print("-" * 70)
        self.display_winner()

    def on_wait_next_placement(self):
        self.display_score()
        print("-" * 70)
        self.display_turn()

    def display_placement(self, tile: Tile):
        player_id = self.game.current_player_id
        color = first_player_color if player_id == 0 else second_player_color
        print(f"Set placement: {color}{tile}{reset_color} ")

    def display_turn(self):
        player_id = self.game.current_player_id
        color = first_player_color if player_id == 0 else second_player_color
        print(f"Waiting for {color}Player {player_id}{reset_color} to move")

    def display_winner(self):
        if self.game.winner_id == -1:
            print("Tie!")
        elif self.game.winner_id == 0:
            print(f"{first_player_color}Player 0{reset_color} wins!")
        else:
            print(f"{second_player_color}Player 1{reset_color} wins!")

    def display_board(self):
        for i in range(self.game.size):
            row_str = ""
            for j in range(self.game.size):
                tile = self.game.tiles[i * self.game.size + j]
                if tile.piece is None:
                    row_str += "[ ]"
                else:
                    player_id = tile.piece.owner.id
                    direction_arrow = arrow_map[tile.piece.dir]
                    color = (
                        first_player_color if player_id == 0 else second_player_color
                    )
                    row_str += f"[{color}{direction_arrow}{reset_color}]"
            print(row_str)

        # print game string for debug
        print(self.game.to_game_str())

    def display_player_score(self, player: Player, color):
        s = (
            f"{color}"
            f"Player {player.id} | "
            f"score: {player.score} ("
            f"kill: {player.kill}, "
            f"remain: {player.remain}, "
            f"control: {player.control})"
            f"{reset_color}"
        )
        print(s)

    def display_score(self):
        self.display_player_score(self.game.players[0], first_player_color)
        self.display_player_score(self.game.players[1], second_player_color)
