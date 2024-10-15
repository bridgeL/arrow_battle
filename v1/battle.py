from .agent import Agent
from .game import Game


class Battle:
    def __init__(self, agent1: Agent, agent2: Agent, game: Game):
        self.agent1 = agent1
        self.agent1.player_index = 1
        self.agent2 = agent2
        self.agent2.player_index = 2
        self.game = game

    def run(self, rounds=100):
        results = {"win": 0, "tie": 0, "lose": 0}

        for round in range(rounds):
            self.agent1.reset()
            self.agent2.reset()
            self.game.reset()
            step = 0

            while step < 100 and not self.game.is_over:
                if self.game.current_player_index == 1:
                    agent = self.agent1
                else:
                    agent = self.agent2

                action = agent.get_action()
                valid, reason = self.game.step(action)
                step += 1

                assert valid, f"无效动作 {action}， {reason}"

            results[self.game.get_result()] += 1

        print(results)
