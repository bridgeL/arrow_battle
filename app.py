from agents.silly_agent import SillyAgent
from agents.yumi_agent import YumiAgent
from game_viewer import GameViewer, EvEGameViewer, PvEGameViewer

if __name__ == "__main__":
    # # 玩家对弈
    # GameViewer().start()

    # AI对弈
    agent_1 = SillyAgent()
    agent_2 = YumiAgent()
    agent_2.load_model("yumi.pth")
    EvEGameViewer(agent_1, agent_2).start()
