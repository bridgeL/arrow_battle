import sys
from agents.silly_agent import SillyAgent
from agents.q_learn import QLearningAgent
from game_viewer import GameViewer, EvEGameViewer, PvEGameViewer

if __name__ == "__main__":
    args = sys.argv

    if len(args) > 1:
        choice = int(args[1])
    else:
        choice = int(input("0 PvP\n1 EvE\n2 EvP\n3 PvE\n> "))

    if choice == 0:
        # 玩家对弈
        GameViewer().start()

    elif choice == 1:
        # AI对弈
        agent_1 = SillyAgent()
        agent_1 = QLearningAgent(epsilon=0.0001)
        agent_2 = QLearningAgent(epsilon=0.0001)
        agent_1.load("data/q_table_agent_1.pkl")
        agent_2.load("data/q_table_agent_2.pkl")
        EvEGameViewer(agent_1, agent_2).start()

    elif choice == 2:
        # 玩家AI对弈
        agent = QLearningAgent(epsilon=0.0001)
        agent.load("data/q_table_agent_1.pkl")
        PvEGameViewer(agent, True).start()

    elif choice == 3:
        # 玩家AI对弈
        agent = QLearningAgent(epsilon=0.0001)
        agent.load("data/q_table_agent_2.pkl")
        PvEGameViewer(agent, False).start()
