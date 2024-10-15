from ..agent import Agent
from ..model import Dir, Action


class HumanAgent(Agent):
    def get_action(self):
        while True:
            while True:
                input_str = input(f"{self.player_index}> ")
                try:
                    row = int(input_str[0])
                    col = int(input_str[1])
                    dir = Dir(int(input_str[2]))
                except:
                    print("Invalid input format.")
                else:
                    break

            action = Action(row, col, dir)
            valid, reason = self.game.check_position(row, col)
            if not valid:
                print(reason)
            else:
                return action
