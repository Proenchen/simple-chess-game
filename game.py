import copy
import pieces as p
from board import Board, BOARD_SIZE

PROMOTION_PIECES = [p.Queen, p.Rook, p.Knight, p.Bishop]


class Game:
    def __init__(self):
        self.board = Board()
        self.last_move_from = None
        self.last_move_to = None
        self.is_checkmate = False
        self.stalemate = False
        self.en_passant = False
        self.promotion = False
        self.current_player = p.Color.WHITE
        self.genarate_moves()
        self.occured_positions = {frozenset(self.get_position()): 1}
        self.threefold_rep = False
        self.fifty_moves = False
        self.move_count_for_fifty = 0

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
            if self.board.get_piece(to_pos) is not None or isinstance(piece, p.Pawn):
                self.occured_positions.clear()

            if self.en_passant and self.occured_positions.get(frozenset(self.get_position())) is not None:
                self.occured_positions[frozenset(self.get_position())] -= 1

            if isinstance(piece, p.Pawn) or (self.board.get_piece(to_pos) is not None):
                self.move_count_for_fifty = 0
            else:
                self.move_count_for_fifty += 0.5

            self.board.move(from_pos, to_pos)

            pos = frozenset(self.get_position())
            if self.occured_positions.get(pos) is not None:
                self.occured_positions[pos] += 1
                if self.occured_positions[pos] == 3:
                    self.threefold_rep = True
            else:
                self.occured_positions[pos] = 1

            self.last_move_from = from_pos
            self.last_move_to = to_pos

            if isinstance(piece, p.King):
                piece.moved = True
                if to_pos[1] - from_pos[1] == 2:
                    self.board.move((to_pos[0], to_pos[1] + 1), (from_pos[0], from_pos[1] + 1))
                    self.occured_positions.clear()

                elif to_pos[1] - from_pos[1] == -2:
                    self.board.move((to_pos[0], to_pos[1] - 2), (from_pos[0], from_pos[1] - 1))
                    self.occured_positions.clear()

            if isinstance(piece, p.Pawn) and piece.promote:
                self.promotion = True

            if self.en_passant:
                self.en_passant = False
                if isinstance(piece, p.Pawn):
                    self.board.remove_piece((self.last_move_from[0], self.last_move_to[1]))

            self._change_color()
            self.genarate_moves()
            if not self.is_mate():
                self.is_stalemate()

            if self.move_count_for_fifty == 50:
                self.fifty_moves = True

    # Checks if a move is allowed
    def allowed_move(self, piece, to_pos):
        # No moves are allowd, if the game has ended
        if self.is_checkmate:
            return False

        # Checks if the player moves his own piece and if the move is possible
        if piece.color != self.current_player or not self._can_move(piece, to_pos):
            return False

        # Checks if the king will be in check in the resulting position
        return self._check_for_resulting_checks(piece, to_pos)

    # Checks the position for checks
    def is_check(self):
        king_pos = self._get_king_pos(self.current_player)
        return self._check_on(king_pos)

    def is_mate(self):
        if self.is_check() and not self._moves_left():
            self.is_checkmate = True
            return True
        return False

    def is_stalemate(self):
        if not self._moves_left():
            self.stalemate = True
            return True
        return False

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

    def promote(self, name, pos, color):
        cls = getattr(p, name)
        self.board.place_piece(cls(color, pos), pos)
        self._change_color()
        self.genarate_moves()
        if not self.is_mate():
            self.is_stalemate()
        self._change_color()
        self.promotion = False

    # private helper methods
    # -----------------------------------------------------------------------------------------------
    def _get_king_pos(self, color):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece((row, col))
                if piece is not None and piece.color == color and isinstance(piece, p.King):
                    return (row, col)

    def _change_color(self):
        self.current_player = p.Color.BLACK if self.current_player == p.Color.WHITE else p.Color.WHITE

    def _can_move(self, piece, to_pos):
        # extra handling for pawn takes
        if isinstance(piece, p.Pawn) and piece.can_move(to_pos):
            if (piece.en_passant and
                    isinstance(self.board.get_piece((piece.pos[0], to_pos[1])), p.Pawn) and
                    self.board.get_piece((piece.pos[0], to_pos[1])).color != piece.color and
                    self.last_move_to == (piece.pos[0], to_pos[1]) and
                    abs(self.last_move_from[0] - piece.pos[0]) == 2 and
                    self.last_move_from[1] == to_pos[1]):
                self.en_passant = True
                return True

            if piece.take and self.board.get_piece(to_pos) is None:
                return False
            if (self.board.get_piece(to_pos) is not None and
                    self.board.get_piece(to_pos).color != piece.color):
                return piece.take

        # castling handling
        if isinstance(piece, p.King) and not piece.moved:
            # short castle
            if to_pos[0] == piece.pos[0] and (to_pos[1] - piece.pos[1] == 2):
                if self.is_check():
                    return False

                for i in range(piece.pos[1] + 1, piece.pos[1] + 3):
                    if self.board.get_piece((piece.pos[0], i)) is not None or self._check_on((piece.pos[0], i)):
                        return False

                rook = self.board.get_piece((piece.pos[0], piece.pos[1] + 3))
                return rook is not None and isinstance(rook, p.Rook) and rook.color == piece.color

            # long castle
            if to_pos[0] == piece.pos[0] and (to_pos[1] - piece.pos[1] == -2):
                if self.is_check():
                    return False

                for i in range(piece.pos[1] - 3, piece.pos[1]):
                    if self.board.get_piece((piece.pos[0], i)) is not None or self._check_on((piece.pos[0], i)):
                        return False

                rook = self.board.get_piece((piece.pos[0], piece.pos[1] - 4))
                return rook is not None and isinstance(rook, p.Rook) and rook.color == piece.color

        # checks if piece is in between, if piece moves diagonally
        if p.Piece.diagonal_move(piece.pos, to_pos):
            step_x = 1 if piece.pos[0] < to_pos[0] else -1
            step_y = 1 if piece.pos[1] < to_pos[1] else -1
            y = piece.pos[1] + step_y
            for x in range(piece.pos[0] + step_x, to_pos[0], step_x):
                if self.board.get_piece((x, y)) is not None:
                    return False
                y += step_y

        # checks if piece is in between, if piece moves horizontally
        if p.Piece.horizontal_move(piece.pos, to_pos) and piece.pos[0] == to_pos[0]:
            step = 1 if piece.pos[1] < to_pos[1] else -1
            for y in range(piece.pos[1] + step, to_pos[1], step):
                if self.board.get_piece((piece.pos[0], y)) is not None:
                    return False

        if p.Piece.horizontal_move(piece.pos, to_pos) and piece.pos[1] == to_pos[1]:
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
            if self._check_for_resulting_checks(piece, move):
                return True
        return False

    def _moves_left(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece((row, col))
                if piece is not None and self._exist_legal_move(piece):
                    return True
        return False

    def _check_on(self, pos):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece((row, col))
                if piece is not None and piece.has_legal_move(pos) and piece.color != self.current_player:
                    return True
        return False

    def _check_for_resulting_checks(self, piece, to_pos):
        self_copy = copy.deepcopy(self)
        self_copy.board.move(piece.pos, to_pos)
        self_copy.genarate_moves()
        if not self_copy.is_check():
            return True
        return False
