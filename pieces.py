from enum import Enum


class Color(Enum):
    WHITE = "White"
    BLACK = "Black"


class Piece:
    def __init__(self, color, pos):
        self.color = color
        self.pos = pos
        self.legal_moves = []

    def __repr__(self):
        return self.name

    def can_move(self, target):
        pass

    def add_legal_move(self, to_pos):
        self.legal_moves.append(to_pos)

    def has_legal_move(self, to_pos):
        return to_pos in self.legal_moves

    def clear_legal_moves(self):
        self.legal_moves.clear()

    def diagonal_move(from_pos, to_pos):
        row_change = from_pos[0] - to_pos[0]
        col_change = from_pos[1] - to_pos[1]
        return abs(row_change) == abs(col_change)

    def horizontal_move(from_pos, to_pos):
        return from_pos[0] == to_pos[0] or from_pos[1] == to_pos[1]


class Knight(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.name = PIECE_REPR[self.color][Knight]

    def can_move(self, target):
        return ((abs(self.pos[0] - target[0]) == 2 and abs(self.pos[1] - target[1]) == 1) or
                (abs(self.pos[1] - target[1]) == 2 and abs(self.pos[0] - target[0]) == 1))


class Queen(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.name = PIECE_REPR[self.color][Queen]

    def can_move(self, target):
        return Piece.horizontal_move(self.pos, target) or Piece.diagonal_move(self.pos, target)


class King(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.moved = False
        self.name = PIECE_REPR[self.color][King]

    def can_move(self, target):
        if abs(self.pos[0] - target[0]) > 1 or abs(self.pos[1] - target[1]) > 1:
            return False
        return Piece.horizontal_move(self.pos, target) or Piece.diagonal_move(self.pos, target)


class Rook(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.name = PIECE_REPR[self.color][Rook]

    def can_move(self, target):
        return Piece.horizontal_move(self.pos, target)


class Bishop(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.name = PIECE_REPR[self.color][Bishop]

    def can_move(self, target):
        return Piece.diagonal_move(self.pos, target)


class Pawn(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.take = False
        self.en_passant = False
        self.promote = False
        self.name = PIECE_REPR[self.color][Pawn]

    def can_move(self, target):
        self.take = False
        self.en_passant = False
        self.promote = False
        if abs(self.pos[1] - target[1]) > 1:
            return False

        if self.color == Color.WHITE:
            if abs(self.pos[1] - target[1]) == 1 and (self.pos[0] - target[0]) == 1:
                self.take = True
                if self.pos[0] == 3:
                    self.en_passant = True
            if target[0] == 0:
                self.promote = True
            if self.pos[0] == 6:
                return ((self.pos[0] - target[0]) == 2 and self.pos[1] == target[1]) or (self.pos[0] - target[0]) == 1
            return (self.pos[0] - target[0]) == 1

        if self.color == Color.BLACK:
            if abs(self.pos[1] - target[1]) == 1 and (target[0] - self.pos[0]) == 1:
                self.take = True
                if self.pos[0] == 4:
                    self.en_passant = True
            if target[0] == 7:
                self.promote = True
            if self.pos[0] == 1:
                return ((target[0] - self.pos[0]) == 2 and self.pos[1] == target[1]) or (target[0] - self.pos[0]) == 1
            return (target[0] - self.pos[0]) == 1


PIECE_REPR = {
    Color.WHITE: {Pawn: "wp", Rook: "wr", Knight: "wn", Bishop: "wb", King: "wk", Queen: "wq"},
    Color.BLACK: {Pawn: "bp", Rook: "br", Knight: "bn", Bishop: "bb", King: "bk", Queen: "bq"}
    }
