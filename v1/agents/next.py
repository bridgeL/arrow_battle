from ..agent import Agent
from ..model import Action, Dir, State
from ..game import Game


class NextAgent(Agent):
    def __init__(self, game, player_index):
        super().__init__(game, player_index)
        self.test_game = Game(game.size)
        actions: list[Action] = []

        for x in range(self.game.size):
            for y in range(self.game.size):
                for d in Dir.__members__.values():
                    actions.append(Action(x, y, d, player_index))
        self.my_actions = actions

    def get_scores(self, state: State):
        size = self.game.size
        watch1 = 0
        watch2 = 0

        for x in range(size):
            for y in range(size):
                w1 = state.p1_ctrl[x][y]
                w2 = state.p2_ctrl[x][y]
                watch1 += min(w1, 2)
                watch2 += min(w2, 2)

        return [watch1, watch2]

    def get_reward(self, state: State, action: Action):
        self.test_game.set_state(state)
        old_scores = self.get_scores(state)
        valid, reason = self.test_game.step(action)
        if not valid:
            return -100.0
        next_state = self.test_game.state
        new_scores = self.get_scores(next_state)

        reward = 0.0
        if self.player_index == 1:
            reward += (new_scores[0] - old_scores[0]) * 1.0
        else:
            reward += (new_scores[1] - old_scores[1]) * 1.0

        return reward

    def get_action(self):
        return self.find_best_action(self.game.state)

    def find_best_action(self, state: State):
        best_r = float("-inf")
        best_action = None

        for action in self.my_actions:
            r = self.get_reward(state, action)
            if r > best_r:
                best_r = r
                best_action = action

        return best_action
