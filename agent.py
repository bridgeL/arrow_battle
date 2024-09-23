from typing import Optional
from game import Game


class Agent:
    game: Optional[Game] = None
    is_training = False

    def bind_game(self, game: Game, player_id: int):
        self.game = game
        self.player_id = player_id
        self.add_event_trigger("on_game_start", self.on_game_start)
        self.add_event_trigger("on_game_over", self.on_game_over)

    def unbind_game(self):
        assert self.game
        self.game.event_handler.remove_all_event_triggers(self)
        self.game = None

    def add_event_trigger(self, event_type: str, callback):
        assert self.game
        self.game.event_handler.add_event_trigger(event_type, self, callback)

    def train(self):
        """切换为训练模式"""
        self.is_training = True

    def test(self):
        """切换为验证模式"""
        self.is_training = False

    def get_action(self) -> tuple[int, int, int]:
        """给出当前状态下的动作"""
        raise NotImplementedError

    def move(self):
        """行动一步"""
        assert self.game
        row, col, dir_val = self.get_action()
        valid, reason = self.game.set_placement(row, col, dir_val, self.player_id)
        assert valid, reason

    def on_game_start(self):
        """当游戏启动时执行一些操作"""

    def on_game_over(self):
        """当游戏结束时执行一些操作"""
