from .game import Game
from .model import Action


class Agent:
    def __init__(self, game: Game, player_index: int):
        self.game = game
        self.player_index = player_index

    def reset(self):
        pass

    def get_action(self) -> Action:
        raise NotImplementedError
