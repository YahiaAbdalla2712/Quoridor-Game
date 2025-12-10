class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.walls_remaining = 10

    def make_move(self, board):
        if self.is_ai:
            return self.ai_move(board)
        else:

            pass

    def ai_move(self, board):

        pass
