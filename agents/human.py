from agent import Agent


class HumanAgent(Agent):
    def _move(self) -> tuple[bool, str]:
        input_str = input()
        data = input_str.split()
        try:
            # 000
            if len(data) == 1:
                row, col, dir_value = map(int, data[0])

            # 0 0 0
            else:
                row, col, dir_value = map(int, data)
        except ValueError:
            return (
                False,
                "Invalid input format. Please enter row, column, and direction value.",
            )

        valid, reason = self.game.set_placement(row, col, dir_value, self.player_id)
        return valid, reason

    def move(self):
        valid = False
        while not valid:
            valid, reason = self._move()
            if not valid:
                print(reason)
