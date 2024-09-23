from agents.human import HumanAgent
from agents.silly import SillyAgent
from agents.xinyang.dqn import DQNAgent
from battle import Battle
from game import Game
from game_viewer import GameViewer

game = Game()
game_viewer = GameViewer()

agent_1 = SillyAgent()
agent_2 = DQNAgent()
# agent_2.train()
agent_2.load("data/dqn_agent_1.pth")


battle = Battle(game, game_viewer, agent_1, agent_2)
battle.run(100)
# agent_2.save("data/dqn_agent_1.pth")

agent_3 = SillyAgent()
battle.switch_agent_2(agent_3)
battle.run(100)

agent_4 = HumanAgent()
battle.switch_agent_1(agent_4)
battle.single_run()
