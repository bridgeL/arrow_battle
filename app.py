from agents.silly_agent import SillyAgent
from agents.q_learn import QLearningAgent
from game_viewer import GameViewer, AgentGameViewer

if __name__ == "__main__":
    # # 玩家对弈
    # GameViewer().start()

    # AI对弈
    agent_1 = SillyAgent()
    agent_1 = QLearningAgent()
    agent_2 = QLearningAgent()
    agent_1.load("data/q_table_agent_1.pkl")
    agent_2.load("data/q_table_agent_2.pkl")
    AgentGameViewer(agent_1, agent_2).start()
