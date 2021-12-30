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

    def remove_piece(self, pos):
        self.board[pos[0], pos[1]] = None

    def place_piece(self, piece, pos):
        self.board[pos[0]][pos[1]] = piece

    def move(self, from_pos, to_pos):
        if from_pos == to_pos:
            return

        piece = self.get_piece(from_pos)
        if piece is None:
            return

        self.place_piece(piece, to_pos)
        piece.pos = to_pos
        self.remove_piece(from_pos)
