from agent import Agent
from agents.silly import SillyAgent
from game import Game


def get_state(game: Game):
    state = []

    # 0-8维标注阵营
    for tile in game.tiles:
        if not tile.piece:
            state.append(0)
        else:
            p = tile.piece.owner.id
            state.append(p)

    # 9-17维标注方向
    for tile in game.tiles:
        if not tile.piece:
            state.append(0)
        else:
            v = tile.piece.dir.value
            state.append(v)

    return state


def get_valid_actions(game: Game):
    actions = []
    for row in range(3):
        for col in range(3):
            valid, reason = game.check_placement_position_valid(row, col)
            if valid:
                for dir_val in range(8):
                    actions.append((row, col, dir_val))
    return actions


def get_action_id(action: tuple):
    row, col, dir_val = action
    return row * 3 * 8 + col * 8 + dir_val


def parse_action_id(action_id: int):
    dir_val = action_id % 8
    action_id //= 8
    col = action_id % 3
    row = action_id // 3
    action = (row, col, dir_val)
    return action


class SLearnAgent(Agent):
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
        

    def on_game_over(self):
        assert self.game
        if self.is_training:
            if self.game.winner_id == self.player_id:
                