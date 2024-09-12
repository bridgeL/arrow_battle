from random import randint
from agent import Agent


class SillyAgent(Agent):
    def ai_move(self):
        for i in range(1000):
            row = randint(0, 2)
            col = randint(0, 2)
            dir_val = randint(0, 7)
            valid, reason = self.game.set_placement(row, col, dir_val)
            if valid:
                break
