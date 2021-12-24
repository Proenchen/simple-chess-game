from pieces import Color, Pawn, Piece
from board import Board, BOARD_SIZE


class Game:
    def __init__(self):
        self.board = Board()
        self.last_move_from = None
        self.last_move_to = None
        self.current_player = Color.WHITE

    def get_position(self):
        current_position = {}
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece((row, col))
                if piece is not None:
                    current_position[(row, col)] = piece
        return current_position

    def move(self, piece, from_pos, to_pos):
        if self.can_move(piece, to_pos):
            self.board.move(from_pos, to_pos)
            self.last_move_from = from_pos
            self.last_move_to = to_pos
            self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE

    def can_move(self, piece, to_pos):
        # extra handling for pawn takes
        # TODO: instanceof vermeiden
        if (isinstance(piece, Pawn) and piece.can_move(to_pos) and self.board.get_piece(to_pos) is not None and
                self.board.get_piece(to_pos).color != piece.color):
            return piece.take

        # checks if piece is in between, if piece moves diagonally
        if Piece.diagonal_move(piece.pos, to_pos):
            step_x = 1 if piece.pos[0] < to_pos[0] else -1
            step_y = 1 if piece.pos[1] < to_pos[1] else -1
            y = piece.pos[1] + step_y
            for x in range(piece.pos[0] + step_x, to_pos[0], step_x):
                if self.board.get_piece((x, y)) is not None:
                    return False
                y += step_y

        # checks if piece is in between, if piece moves diagonally
        if Piece.horizontal_move(piece.pos, to_pos) and piece.pos[0] == to_pos[0]:
            step = 1 if piece.pos[1] < to_pos[1] else -1
            for y in range(piece.pos[1] + step, to_pos[1], step):
                if self.board.get_piece((piece.pos[0], y)) is not None:
                    return False

        if Piece.horizontal_move(piece.pos, to_pos) and piece.pos[1] == to_pos[1]:
            step = 1 if piece.pos[0] < to_pos[0] else -1
            for x in range(piece.pos[0] + step, to_pos[0], step):
                if self.board.get_piece((x, piece.pos[1])) is not None:
                    return False

        return (piece.can_move(to_pos) and  # if piece is allowed to move ther in general
                # if piece is owned by the current player
                piece.color == self.current_player and not
                # if piece is owned by the current player
                (self.board.get_piece(to_pos) is not None and self.board.get_piece(to_pos).color == piece.color))

