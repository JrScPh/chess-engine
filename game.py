from constants import (
    EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    WHITE, BLACK,
    GameStatus,
    file_of, rank_of,
)
from board import Board
from fen import board_from_fen, board_to_fen, STARTING_FEN
from move_generator import MoveGenerator
from move import Move


class Game:

    def __init__(self, fen=STARTING_FEN):
        self.board = board_from_fen(fen)
        self.move_gen = MoveGenerator()
        self.history = []
        self.position_counts = {' '.join(fen.split()[:4]): 1}
        self.current_status = self.status()

    def _position_key(self):
        return ' '.join(board_to_fen(self.board).split()[:4])

    def push(self, move):
        undo = self.board.make_move(move)
        self.history.append((move, undo))
        pos = self._position_key()
        self.position_counts[pos] = self.position_counts.get(pos, 0) + 1
        self.current_status = self.status()

    def pop(self):
        pos = self._position_key()
        self.position_counts[pos] = self.position_counts.get(pos, 0) - 1
        if self.position_counts[pos] < 1:
            del self.position_counts[pos]
        move, undo = self.history.pop()
        self.board.unmake_move(move, undo)
        self.current_status = self.status()

    def status(self):
        self.legal_moves = self.move_gen.generate_moves(self.board)

        if not self.legal_moves:
            if self.move_gen.is_in_check(self.board, self.board.side):
                return GameStatus.CHECKMATE
            return GameStatus.STALEMATE

        if self.board.halfmove >= 100:
            return GameStatus.DRAW_FIFTY_MOVE

        if self._is_insufficient_material():
            return GameStatus.DRAW_INSUFFICIENT

        if self._is_repetition():
            return GameStatus.DRAW_REPETITION

        return GameStatus.ONGOING

    def _is_repetition(self):
        return self.position_counts.get(self._position_key(), 0) >= 3

    def _is_insufficient_material(self):
        pieces = [(square, piece) for square, piece in enumerate(self.board.squares) if piece != EMPTY]
        length = len(pieces)

        if length > 4:
            return False

        if length == 2:
            return True

        elif length == 3:
            if any(abs(piece) in (KNIGHT, BISHOP) for square, piece in pieces):
                return True

        elif length == 4:
            bishops = [(square, piece) for square, piece in pieces if abs(piece) == BISHOP]
            if len(bishops) == 2:
                sq1, sq2 = bishops[0][0], bishops[1][0]
                if (rank_of(sq1) + file_of(sq1)) % 2 == (rank_of(sq2) + file_of(sq2)) % 2:
                    return True

        return False