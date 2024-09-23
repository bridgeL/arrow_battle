from tqdm import tqdm
from agent import Agent
from game import Game
from game_viewer import GameViewer


class Battle:
    def __init__(
        self,
        game: Game,
        game_viewer: GameViewer,
        agent_1: Agent,
        agent_2: Agent,
    ):
        self.game = game
        self.game_viewer = game_viewer
        self.agent_1 = agent_1
        self.agent_2 = agent_2

        self.game_viewer.bind_game(self.game)
        self.agent_1.bind_game(self.game, 0)
        self.agent_2.bind_game(self.game, 1)

    def switch_agent_1(self, agent: Agent):
        self.agent_1.unbind_game()
        self.agent_1 = agent
        self.agent_1.bind_game(self.game, 0)

    def switch_agent_2(self, agent: Agent):
        self.agent_2.unbind_game()
        self.agent_2 = agent
        self.agent_2.bind_game(self.game, 1)

    def single_run(self):
        self.game_viewer.display_on()
        self.game.restart()

        while True:
            self.agent_1.move()
            if self.game.is_over:
                break

            self.agent_2.move()
            if self.game.is_over:
                break

    def run(self, rounds: int):
        self.game_viewer.display_off()

        win = 0
        tie = 0
        lose = 0

        for round in tqdm(range(rounds)):
            self.game.restart()
            while True:
                self.agent_1.move()
                if self.game.is_over:
                    break

                self.agent_2.move()
                if self.game.is_over:
                    break

            if self.game.winner_id == 0:
                win += 1
            elif self.game.winner_id == 1:
                lose += 1
            else:
                tie += 1

        print(f"win: {win}, lose: {lose}, tie: {tie}")
