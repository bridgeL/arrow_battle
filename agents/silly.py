from random import choice, randint
from agent import Agent


class SillyAgent(Agent):
    def get_action(self) -> tuple[int, int, int]:
        assert self.game
        items = []
        for i in range(3):
            for j in range(3):
                valid, reason = self.game.check_placement_position_valid(i, j)
                if valid:
                    items.append((i, j))

        row, col = choice(items)
        dir_value = randint(0, 7)
        return (row, col, dir_value)
