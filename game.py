from enum import Enum
from typing import Optional


class Player:
    id: int

    kill: int
    remain: int
    control: int

    def __init__(self, id) -> None:
        self.id = id

        self.kill = 0
        self.remain = 0
        self.control = 0

    @property
    def score(self):
        return self.kill + self.remain + self.control

    def update_score(self, game: "Game"):
        self.remain = 0
        self.control = 0

        for tile in game.tiles:
            # 空格子检查是否是控制区
            if tile.piece == None:
                if self in tile.controllers:
                    self.control += 1

            # 有棋子检查是否是自己
            else:
                if tile.piece.owner is self:
                    self.remain += 1

    def __repr__(self) -> str:
        return f"Player({self.id})"


class Dir(Enum):
    LEFT = 0
    LEFT_TOP = 1
    TOP = 2
    RIGHT_TOP = 3
    RIGHT = 4
    RIGHT_BOTTOM = 5
    BOTTOM = 6
    LEFT_BOTTOM = 7

    def is_opposite(self, dir: "Dir"):
        return (8 + self.value - dir.value) % 8 == 4

    def __repr__(self) -> str:
        return self.name


class Piece:
    owner: Player
    dir: Dir

    def __repr__(self) -> str:
        return f"Piece({self.owner}, {self.dir})"


class Tile:
    piece: Piece | None
    row: int
    col: int
    controllers: list[Player]
    offset = {
        Dir.LEFT: (0, -1),
        Dir.LEFT_TOP: (-1, -1),
        Dir.TOP: (-1, 0),
        Dir.RIGHT_TOP: (-1, 1),
        Dir.RIGHT: (0, 1),
        Dir.RIGHT_BOTTOM: (1, 1),
        Dir.BOTTOM: (1, 0),
        Dir.LEFT_BOTTOM: (1, -1),
    }

    def __init__(self, row, col) -> None:
        self.row = row
        self.col = col
        self.piece = None
        self.controllers: list[Player] = []

    def is_attacked(self):
        # 如果格子上有棋子，且控制此格子的玩家不属于这颗棋子的玩家，则该格子被攻击
        if self.piece is not None:
            for player in self.controllers:
                if player is not self.piece.owner:
                    return True
        return False

    def apply_attack(self):
        for player in self.controllers:
            if player is not self.piece.owner:
                player.kill += 1
        self.piece = None

    def calculate_controllers(self, game: "Game"):
        new_controllers = []
        for dir in Dir:
            next_tile = self.get_next_tile(dir, game)
            while next_tile and next_tile.piece is None:
                next_tile = next_tile.get_next_tile(dir, game)

            if next_tile and next_tile.piece and next_tile.piece.dir.is_opposite(dir):
                new_controllers.append(next_tile.piece.owner)

        self.controllers = [
            player for player in game.players if new_controllers.count(player) > 1
        ]

    def __repr__(self) -> str:
        return f"Tile({self.row},{self.col},{self.piece})"

    def get_next_tile(self, dir: Dir, game: "Game") -> Optional["Tile"]:
        row_offset, col_offset = self.offset[dir]

        new_row = self.row + row_offset
        new_col = self.col + col_offset

        if game.infinite_border:
            new_row %= game.size
            new_col %= game.size
        else:
            if not (0 <= new_row < game.size) or not (0 <= new_col < game.size):
                return None

        return game.tiles[new_row * game.size + new_col]


class Game:
    size: int
    tiles: list[Tile]
    infinite_border: bool
    num_player: int
    players: list[Player]
    winner: list[Player]
    is_game_over: bool
    current_player_index: int
    on_update = lambda x: x
    on_game_over = lambda x: x
    on_update_end = lambda x: x

    def __init__(self, size=3, num_player=2, infinite_border=False) -> None:
        self.size = size
        self.num_player = num_player
        self.infinite_border = infinite_border
        self.restart()

    def restart(self):
        self.tiles = [Tile(i // self.size, i % self.size) for i in range(self.size**2)]
        self.players = [Player(i) for i in range(self.num_player)]
        self.current_player_index = 0
        self.is_game_over = False
        self.winner = []

    def get_game_str(self) -> str:
        state = f"g{self.size}{self.num_player}{self.current_player_index}"
        for tile in self.tiles:
            if tile.piece is None:
                state += "tnn"
            else:
                state += f"t{tile.piece.owner.id}{tile.piece.dir.value}"
        return state

    @classmethod
    def from_game_str(cls, game_str: str):
        size = int(game_str[1])
        num_player = int(game_str[2])
        current_player_index = int(game_str[3])

        game = cls(size, num_player, False)
        game.current_player_index = current_player_index

        index = 4
        for tile in game.tiles:
            if game_str[index : index + 3] == "tnn":
                tile.piece = None
            else:
                owner_id = int(game_str[index + 1])
                dir_value = int(game_str[index + 2])
                tile.piece = Piece()
                tile.piece.owner = game.players[owner_id]
                tile.piece.dir = Dir(dir_value)
            index += 3

        game.update_score()
        return game

    def has_valid_moves(self):
        current_player = self.players[self.current_player_index]
        for tile in self.tiles:
            if tile.piece is None:
                if not tile.controllers:
                    return True
                if len(tile.controllers) == 1 and current_player is tile.controllers[0]:
                    return True
        return False

    def check_placement_valid(self, row: int, col: int) -> tuple[bool, str]:
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False, "Out of bounds"

        tile = self.tiles[row * self.size + col]
        if tile.piece is not None:
            return False, "Tile already occupied"

        if any(
            player != self.players[self.current_player_index]
            for player in tile.controllers
        ):
            return False, "Tile controlled by another player"

        return True, ""

    def set_placement(self, row: int, col: int, dir_value: int) -> tuple[bool, str]:
        if self.is_game_over:
            return False, "game is over"

        # check dir
        if dir_value < 0 or dir_value >= 8:
            return False, "Invalid direction value"

        dir = Dir(dir_value)

        # check position
        valid, reason = self.check_placement_valid(row, col)
        if not valid:
            return False, f"Invalid move: {reason}"

        # set placement
        tile = self.tiles[row * self.size + col]
        tile.piece = Piece()
        tile.piece.owner = self.players[self.current_player_index]
        tile.piece.dir = dir

        # 切换到下一位
        self.current_player_index = (self.current_player_index + 1) % self.num_player
        changed = True

        # 持续更新直到没有变化
        while changed:
            changed = self.update_board()
            self.update_score()

            # 告知外界
            self.on_update()

        # 判断游戏是否结束了
        if not self.has_valid_moves():
            self.game_over()
        else:
            self.on_update_end()

        return True, ""

    def game_over(self):
        self.is_game_over = True
        max_score = max(p.score for p in self.players)
        self.winner = [p for p in self.players if p.score == max_score]
        self.on_game_over()

    def update_score(self):
        for player in self.players:
            player.update_score(self)

    def update_board(self):
        for tile in self.tiles:
            tile.calculate_controllers(self)

        # remove tiles
        changed = False
        for tile in self.tiles:
            if tile.is_attacked():
                tile.apply_attack()
                changed = True

        return changed
