import numpy as np
import pieces as p

BOARD_SIZE = 8


# Represents the chess board
class Board:
    SQUARES = {(col, row): col % 2 == row % 2 for col in range(BOARD_SIZE) for row in range(BOARD_SIZE)}

    def __init__(self):
        self.board = np.empty([BOARD_SIZE, BOARD_SIZE], dtype=object)
        self._set_up()

    def __repr__(self):
        return str(self.board)

    # Sets up the starting position
    def _set_up(self):
        for col in range(BOARD_SIZE):
            self.board[6][col] = p.Pawn(p.Color.WHITE, (6, col))
            self.board[1][col] = p.Pawn(p.Color.BLACK, (1, col))

        placers = [p.Rook, p.Knight, p.Bishop, p.Queen, p.King, p.Bishop, p.Knight, p.Rook]

        for i in range(BOARD_SIZE):
            self.board[7][i] = placers[i](p.Color.WHITE, (7, i))
            self.board[0][i] = placers[i](p.Color.BLACK, (0, i))

    def get_piece(self, pos):
        return self.board[pos[0]][pos[1]]

    def move(self, from_pos, to_pos):
        if from_pos == to_pos:
            return
        if self.board[from_pos[0]][from_pos[1]] is not None:
            self.board[to_pos[0]][to_pos[1]] = self.board[from_pos[0]][from_pos[1]]
            self.board[to_pos[0]][to_pos[1]].pos = (to_pos[0], to_pos[1])
            self.board[from_pos[0]][from_pos[1]] = None

    def diagonal_move(from_pos, to_pos):
        row_change = from_pos[0] - to_pos[0]
        col_change = from_pos[1] - to_pos[1]
        return abs(row_change) == abs(col_change)
