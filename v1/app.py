from .battle import Battle
from .game import Game
from .games.visual_game import VisualGame
from .agents.human import HumanAgent
from .agents.silly import SillyAgent
from .agents.next import NextAgent

SS = 3

if SS == 1:
    game = VisualGame(size=3)
    agent1 = HumanAgent(game, player_index=1)
    agent2 = HumanAgent(game, player_index=2)
    battle = Battle(agent1, agent2, game)
    battle.run(rounds=1)

if SS == 2:
    game = VisualGame(size=4)
    agent1 = SillyAgent(game, player_index=1)
    agent2 = SillyAgent(game, player_index=2)
    battle = Battle(agent1, agent2, game)
    battle.run(rounds=1)

if SS == 3:
    game = Game(size=3)
    agent1 = SillyAgent(game, player_index=1)
    agent2 = NextAgent(game, player_index=2)
    battle = Battle(agent1, agent2, game)
    battle.run(rounds=100)
