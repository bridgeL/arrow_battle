from random import randint
from agent import Agent


class SillyAgent(Agent):
    def _move(self) -> tuple[bool, str]:
        row = randint(0, 2)
        col = randint(0, 2)
        dir_value = randint(0, 7)
        valid, reason = self.game.set_placement(row, col, dir_value, self.player_id)
        return valid, reason

    def move(self):
        valid = False
        while not valid:
            valid, reason = self._move()
