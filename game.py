from enum import Enum
from typing import Optional
from event_handler import EventHandler


class Player:
    def __init__(self, id: int) -> None:
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
    def __init__(self, owner: Player, dir: Dir) -> None:
        self.owner = owner
        self.dir = dir

    def __repr__(self) -> str:
        return f"Piece({self.owner}, {self.dir})"


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


class Tile:
    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.piece: Optional[Piece] = None
        self.controllers: list[Player] = []

    def is_attacked(self):
        # 如果格子上有棋子，且控制此格子的玩家不属于这颗棋子的玩家，则该格子被攻击
        if self.piece is not None:
            for player in self.controllers:
                if player is not self.piece.owner:
                    return True
        return False

    def apply_attack(self):
        assert self.piece is not None
        for player in self.controllers:
            if player.id != self.piece.owner.id:
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

    def get_next_tile(self, dir: Dir, game: "Game") -> Optional["Tile"]:
        row_offset, col_offset = offset[dir]

        new_row = self.row + row_offset
        new_col = self.col + col_offset

        if not (0 <= new_row < game.size) or not (0 <= new_col < game.size):
            return None

        return game.tiles[new_row * game.size + new_col]

    def __repr__(self) -> str:
        return f"Tile({self.row}, {self.col}, {self.piece})"


class Game:
    def __init__(self, size=3) -> None:
        self.size = size
        self.num_player = 2
        self.event_handler = EventHandler()
        self.restart()

    def restart(self):
        """重启游戏"""
        # game is over
        self.is_over = False

        #  0 1st player win
        #  1 2nd player win
        # -1 tie
        self.winner_id = -1

        self.tiles = [Tile(i // self.size, i % self.size) for i in range(self.size**2)]
        self.players = [Player(i) for i in range(self.num_player)]
        self.current_player_id = 0

        # 广播事件：game start
        self.event_handler.handle_event("on_game_start")

    def to_game_str(self) -> str:
        state = f"g{self.size}{self.num_player}{self.current_player_id}"
        for tile in self.tiles:
            if tile.piece is None:
                state += "tnn"
            else:
                state += f"t{tile.piece.owner.id}{tile.piece.dir.value}"
        return state

    @classmethod
    def from_game_str(cls, game_str: str):
        size = int(game_str[1])
        current_player_id = int(game_str[2])

        game = cls(size)
        game.current_player_id = current_player_id

        index = 3
        for tile in game.tiles:
            if game_str[index : index + 3] == "tnn":
                tile.piece = None
            else:
                owner_id = int(game_str[index + 1])
                dir_value = int(game_str[index + 2])
                tile.piece = Piece(game.players[owner_id], Dir(dir_value))
            index += 3

        return game

    @property
    def current_player(self):
        return self.players[self.current_player_id]

    def has_valid_moves(self):
        for tile in self.tiles:
            if tile.piece is None:
                if not tile.controllers:
                    return True
                if (
                    len(tile.controllers) == 1
                    and self.current_player is tile.controllers[0]
                ):
                    return True
        return False

    def check_placement_position_valid(self, row: int, col: int) -> tuple[bool, str]:
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False, "Out of bounds"

        tile = self.tiles[row * self.size + col]
        if tile.piece is not None:
            return False, "Tile already occupied"

        if any(player.id != self.current_player_id for player in tile.controllers):
            return False, "Tile controlled by another player"

        return True, ""

    def check_placement_valid(self, row, col, dir_value, player_id) -> tuple[bool, str]:
        if player_id != self.current_player_id:
            return False, "is not your turn"

        if self.is_over:
            return False, "game is over"

        # check dir
        if dir_value < 0 or dir_value >= 8:
            return False, "Invalid direction value"

        # check position
        valid, reason = self.check_placement_position_valid(row, col)
        if not valid:
            return False, f"Invalid move: {reason}"

        return True, ""

    def next_turn(self):
        self.current_player_id = (self.current_player_id + 1) % self.num_player

    def set_placement(
        self, row: int, col: int, dir_value: int, player_id: int
    ) -> tuple[bool, str]:
        valid, reason = self.check_placement_valid(row, col, dir_value, player_id)
        if not valid:
            return valid, reason

        # 落子
        tile = self.tiles[row * self.size + col]
        tile.piece = Piece(self.current_player, Dir(dir_value))

        # 广播事件：placement
        self.event_handler.handle_event("on_placement", tile)

        changed = True
        while changed:
            # 重新计算控制区
            for tile in self.tiles:
                tile.calculate_controllers(self)

            # 更新得分
            for player in self.players:
                player.update_score(self)

            # 广播事件：board update
            self.event_handler.handle_event("on_board_update")

            # 尝试吃子
            changed = False
            for tile in self.tiles:
                if tile.is_attacked():
                    tile.apply_attack()
                    changed = True

        # 切换到下一位
        self.next_turn()

        # 判断游戏是否结束了
        if not self.has_valid_moves():
            self.game_over()
        else:
            # 广播事件：wait next placement
            self.event_handler.handle_event("on_wait_next_placement")

        return valid, reason

    def game_over(self):
        self.is_over = True

        # calculate winner
        max_score = max(p.score for p in self.players)
        winners = [p for p in self.players if p.score == max_score]
        if len(winners) > 1:
            self.winner_id = -1
        else:
            self.winner_id = winners[0].id

        # 广播事件：game over
        self.event_handler.handle_event("on_game_over")
