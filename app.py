from agents.silly_agent import SillyAgent
from game_viewer import GameViewer, EvEGameViewer, PvEGameViewer

if __name__ == "__main__":
    # # 玩家对弈
    # GameViewer().start()

    # AI对弈
    agent_1 = SillyAgent()
    agent_2 = SillyAgent()
    EvEGameViewer(agent_1, agent_2).start()
