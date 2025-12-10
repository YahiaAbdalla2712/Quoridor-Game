class Board:
    def __init__(self, size=9):
        self.size = size
        self.pawns = {}
        self.walls = []
        self.reset_board()

    def reset_board(self):
        self.pawns['Player1'] = (self.size // 2, 0)
        self.pawns['Player2'] = (self.size // 2, self.size - 1)
        self.walls = []

    def is_valid_move(self, player, move):

        return True

    def is_valid_wall(self, wall_pos):

        return True

    def move_pawn(self, player, move):
        if self.is_valid_move(player, move):
            self.pawns[player] = move

    def place_wall(self, wall_pos):
        if self.is_valid_wall(wall_pos):
            self.walls.append(wall_pos)
