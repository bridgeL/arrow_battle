from .game import Game
from .model import Action


class Agent:
    def __init__(self, game: Game, player_index: int):
        self.game = game
        self.player_index = player_index
        self.is_training = False

    def train(self):
        self.is_training = True

    def test(self):
        self.is_training = False

    def reset(self):
        pass

    def get_action(self) -> Action:
        raise NotImplementedError
