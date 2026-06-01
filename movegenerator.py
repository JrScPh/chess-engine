from constants import (
    EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    WHITE, BLACK,
    CASTLE_KING, CASTLE_QUEEN,
    EN_PASSANT, DOUBLE_PUSH,
    QUIET, CAPTURE,
    PROMO_Q, PROMO_R, PROMO_B, PROMO_N,
    sq, rank_of, file_of,
)
from board import Board
from move import Move


class MoveGenerator:

    def generate_moves(self, board):
        legal_moves = []
        for move in self.generate_pseudo_legal_moves(board):
            undo = board.make_move(move)
            if not self.is_in_check(board, -board.side):
                legal_moves.append(move)
            board.unmake_move(move, undo)
        return legal_moves

    def generate_pseudo_legal_moves(self, board):
        pseudo_legal_moves = []

        for square in range(64):
            piece = board.piece_at(square)

            if piece == EMPTY:
                continue

            if (piece > 0) != (board.side == WHITE):
                continue

            match abs(piece):
                case PAWN:   pseudo_legal_moves.extend(self.pawn_moves(board, square))
                case KNIGHT: pseudo_legal_moves.extend(self.knight_moves(board, square))
                case BISHOP: pseudo_legal_moves.extend(self.bishop_moves(board, square))
                case ROOK:   pseudo_legal_moves.extend(self.rook_moves(board, square))
                case QUEEN:  pseudo_legal_moves.extend(self.queen_moves(board, square))
                case KING:   pseudo_legal_moves.extend(self.king_moves(board, square))
                case _:      raise ValueError(f"Invalid piece: {piece}")

        return pseudo_legal_moves

    def is_in_check(self, board, side):
        king_sq = board.king_sq[side]
        king_rank = rank_of(king_sq)
        king_file = file_of(king_sq)

        diagonal_deltas  = [[1,1],[1,-1],[-1,1],[-1,-1]]
        rank_file_deltas = [[1,0],[-1,0],[0,1],[0,-1]]
        knight_deltas    = [[2,1],[2,-1],[-2,1],[-2,-1],[1,2],[-1,2],[1,-2],[-1,-2]]
        pawn_deltas      = [[side, 1],[side, -1]]

        diagonal_atk  = [BISHOP * -side, QUEEN * -side]
        rank_file_atk = [ROOK * -side, QUEEN * -side]

        # Diagonal check (bishops and queens)
        for dr, df in diagonal_deltas:
            r, f = king_rank, king_file
            while 0 <= r + dr < 8 and 0 <= f + df < 8:
                r += dr
                f += df
                piece = board.piece_at(sq(f, r))
                if piece != EMPTY:
                    if piece in diagonal_atk:
                        return True
                    break

        # Rank/file check (rooks and queens)
        for dr, df in rank_file_deltas:
            r, f = king_rank, king_file
            while 0 <= r + dr < 8 and 0 <= f + df < 8:
                r += dr
                f += df
                piece = board.piece_at(sq(f, r))
                if piece != EMPTY:
                    if piece in rank_file_atk:
                        return True
                    break

        # Knight check
        for dr, df in knight_deltas:
            r, f = king_rank + dr, king_file + df
            if 0 <= r < 8 and 0 <= f < 8:
                if board.piece_at(sq(f, r)) == KNIGHT * -side:
                    return True

        # Pawn check
        for dr, df in pawn_deltas:
            r, f = king_rank + dr, king_file + df
            if 0 <= r < 8 and 0 <= f < 8:
                if board.piece_at(sq(f, r)) == PAWN * -side:
                    return True

        # King check
        for dr, df in diagonal_deltas + rank_file_deltas:
            r, f = king_rank + dr, king_file + df
            if 0 <= r < 8 and 0 <= f < 8:
                if board.piece_at(sq(f, r)) == KING * -side:
                    return True

        return False