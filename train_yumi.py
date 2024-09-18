import os

from agents.silly_agent import SillyAgent
from agents.yumi_agent import YumiAgent
from game import Game

if __name__ == "__main__":
    is_train = False
    # AI对弈
    # agent_1 = SillyAgent()
    agent_1 = YumiAgent()
    if os.path.exists("yumi_test.pth"):
        agent_1.load_model("yumi_test.pth")
    # agent_2 = YumiAgent()
    agent_2 = SillyAgent()
    # if os.path.exists("yumi_test.pth"):
    #     agent_2.load_model("yumi_test.pth")
    game = Game(size=4)
    agent_1.bind_game(game, 0)
    agent_2.bind_game(game, 1)
    win = 0
    tie = 0
    lose = 0
    for _ in range(1000):
        game.restart()
        while not game.is_game_over:
            agent_1.ai_move()
            if game.is_game_over:
                break
            agent_2.ai_move()
        if len(game.winner) == 2:  # 平局
            tie += 1
            # print("tie")
            # if is_train:
            # agent_1.train(5)
            # agent_2.train(5)
        elif game.winner[0].id == 0:  # 2输了
            lose += 1
            # print("lose")
            if is_train:
                agent_2.data = agent_1.data
                agent_1.data = []
                # agent_1.train(10)
                agent_2.train(10)
        else:  # 2赢了
            win += 1
            # print("win")
            if is_train:
                # agent_1.data = agent_2.data
                # agent_1.train(10)
                agent_2.train(10)
        print(win, tie, lose, round(win / max(win + lose, 1), 2))
    if is_train:
        # agent_1.save_model("yumi_test.pth")
        agent_2.save_model("yumi_test.pth")
