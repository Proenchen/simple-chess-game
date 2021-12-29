import copy
from pieces import Color, Pawn, Piece, King
from board import Board, BOARD_SIZE


class Game:
    def __init__(self):
        self.board = Board()
        self.last_move_from = None
        self.last_move_to = None
        self.isCheckmate = False
        self.current_player = Color.WHITE
        self.genarate_moves()

    def get_position(self):
        current_position = {}
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece((row, col))
                if piece is not None:
                    current_position[(row, col)] = piece
        return current_position

    def move(self, piece, from_pos, to_pos):
        if self.allowed_move(piece, to_pos):
            self.board.move(from_pos, to_pos)
            self.last_move_from = from_pos
            self.last_move_to = to_pos
            self._change_color()
            self.genarate_moves()
            self.is_mate()

    # Checks if a move is allowed
    def allowed_move(self, piece, to_pos):
        # No moves are allowd, if the game has ended
        if self.isCheckmate:
            return False

        # Checks if the player moves his own piece and if the move is possible
        if piece.color != self.current_player or not self._can_move(piece, to_pos):
            return False

        # Checks if the king will be in chech in the resulting position
        self_copy = copy.deepcopy(self)
        self_copy.board.move(piece.pos, to_pos)
        self_copy.genarate_moves()
        if self_copy.is_check():
            return False
        return True

    # Checks the position for checks
    def is_check(self):
        king_pos = self._get_king_pos(self.current_player)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece((row, col))
                if piece is not None and piece.has_legal_move(king_pos):
                    return True
        return False

    def is_mate(self):
        if self.is_check():
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    piece = self.board.get_piece((row, col))
                    if piece is not None and self._exist_legal_move(piece):
                        return False
            self.isCheckmate = True
            return True

    # Returns the position of the king of the current player
    def get_active_king_pos(self):
        return self._get_king_pos(self.current_player)

    # Generate legal moves for every piece
    def genarate_moves(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece((row, col))
                if piece is not None:
                    self._generate_moves_for(piece)

    # private helper methods
    def _get_king_pos(self, color):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece((row, col))
                if piece is not None and piece.color == color and isinstance(piece, King):
                    return (row, col)

    def _change_color(self):
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE

    def _can_move(self, piece, to_pos):
        # extra handling for pawn takes
        # TODO: instanceof vermeiden
        if (isinstance(piece, Pawn) and piece.can_move(to_pos)):
            if (piece.take and self.board.get_piece(to_pos) is None):
                return False
            if (self.board.get_piece(to_pos) is not None and
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

        # checks if piece is in between, if piece moves horizontally
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

        return (piece.can_move(to_pos) and not  # if piece is allowed to move ther in general
                # if a player tries to take his own piece
                (self.board.get_piece(to_pos) is not None and self.board.get_piece(to_pos).color == piece.color))

    # Generates legal moves for a single piece
    def _generate_moves_for(self, piece):
        piece.clear_legal_moves()
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self._can_move(piece, (row, col)):
                    piece.add_legal_move((row, col))

    def _exist_legal_move(self, piece):
        if not piece.legal_moves:
            return False

        if not piece.color == self.current_player:
            return False

        for move in piece.legal_moves:
            self_copy = copy.deepcopy(self)
            self_copy.board.move(piece.pos, move)
            self_copy.genarate_moves()
            if not self_copy.is_check():
                print(move)
                return True
        return False
