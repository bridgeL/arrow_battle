from random import randint
from ..agent import Agent
from ..model import Dir, Action


class SillyAgent(Agent):
    def get_action(self):
        size = self.game.size
        for i in range(1000):
            row = randint(0, size - 1)
            col = randint(0, size - 1)
            dir = Dir(randint(0, 7))
            action = Action(row, col, dir)
            valid, reason = self.game.check_position(row, col)
            if valid:
                return action

        raise Exception("没有可用的行动")
