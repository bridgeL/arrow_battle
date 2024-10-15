from random import choice
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
                    actions.append(Action(x, y, d))
        self.actions = actions

    def get_scores(self, state: State):
        size = self.game.size
        score1 = 0
        score2 = 0

        for x in range(size):
            for y in range(size):
                w1 = state.p1_ctrl[x][y]
                w2 = state.p2_ctrl[x][y]
                score1 += min(w1, 2)
                score2 += min(w2, 2)

        return [score1, score2]

    def get_reward(self, state: State, action: Action):
        self.test_game.state = state
        old_scores = self.get_scores(state)
        valid, reason = self.test_game.check_position(action.x, action.y)
        if not valid:
            return -100.0, state

        self.test_game.step(action)
        mid_state = self.test_game.state
        new_scores = self.get_scores(mid_state)

        reward = 0.0
        if self.player_index == 1:
            reward += (new_scores[0] - old_scores[0]) * 1.0
        else:
            reward += (new_scores[1] - old_scores[1]) * 1.0

        return reward, mid_state

    def get_action(self):
        return self.find_best_action(self.game.state)

    def find_best_action(self, state: State):
        best_v = float("-inf")
        best_action = None

        for action in self.actions:
            r, mid_state = self.get_reward(state, action)

            worst_rr = 0
            # worst_rr = float("inf")
            # for action2 in self.actions:
            #     self.test_game.state = mid_state
            #     valid, reason = self.test_game.check_position(action2.x, action2.y)
            #     if not valid:
            #         continue
            #     self.test_game.step(action2)
            #     next_state = self.test_game.state

            #     best_rr = float("-inf")
            #     for action3 in self.actions:
            #         rr, _ = self.get_reward(next_state, action3)
            #         if rr > best_rr:
            #             best_rr = rr

            #     if best_rr < worst_rr:
            #         worst_rr = best_rr

            v = r + worst_rr
            if v > best_v:
                best_v = v
                best_action = action

        return best_action
