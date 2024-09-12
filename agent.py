from game import Game


class Agent:
    game: Game
    player_id: int

    def bind_game(self, game, player_id):
        self.game = game
        self.player_id = player_id

    # 请重写该方法
    def ai_move(self):
        raise NotImplementedError
