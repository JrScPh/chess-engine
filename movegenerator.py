from constants import (
    EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    WHITE, BLACK,
    CASTLE_KING, CASTLE_QUEEN,
    EN_PASSANT, DOUBLE_PUSH,
    QUIET, CAPTURE,
    PROMO_Q, PROMO_R, PROMO_B, PROMO_N,
    CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ,
    sq, rank_of, file_of,
)
from board import Board
from move import Move

DIAGONAL_DELTAS  = [[1,1],[1,-1],[-1,1],[-1,-1]]
RANK_FILE_DELTAS = [[1,0],[-1,0],[0,1],[0,-1]]
KNIGHT_DELTAS    = [[2,1],[2,-1],[-2,1],[-2,-1],[1,2],[-1,2],[1,-2],[-1,-2]]
ALL_DELTAS = DIAGONAL_DELTAS + RANK_FILE_DELTAS

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

            pt = abs(piece)
            if   pt == PAWN:   pseudo_legal_moves.extend(self.pawn_moves(board, square))
            elif pt == KNIGHT: pseudo_legal_moves.extend(self.knight_moves(board, square))
            elif pt == BISHOP: pseudo_legal_moves.extend(self.bishop_moves(board, square))
            elif pt == ROOK:   pseudo_legal_moves.extend(self.rook_moves(board, square))
            elif pt == QUEEN:  pseudo_legal_moves.extend(self.queen_moves(board, square))
            elif pt == KING:   pseudo_legal_moves.extend(self.king_moves(board, square))
            else: raise ValueError(f"Invalid piece: {piece}")

        return pseudo_legal_moves

    def is_square_attacked(self, board, square, side):
        sq_rank = rank_of(square)
        sq_file = file_of(square)

        diagonal_atk  = [BISHOP * -side, QUEEN * -side]
        rank_file_atk = [ROOK * -side, QUEEN * -side]

        for dr, df in DIAGONAL_DELTAS:
            r, f = sq_rank, sq_file
            while 0 <= r + dr < 8 and 0 <= f + df < 8:
                r += dr
                f += df
                piece = board.piece_at(sq(f, r))
                if piece != EMPTY:
                    if piece in diagonal_atk:
                        return True
                    break

        for dr, df in RANK_FILE_DELTAS:
            r, f = sq_rank, sq_file
            while 0 <= r + dr < 8 and 0 <= f + df < 8:
                r += dr
                f += df
                piece = board.piece_at(sq(f, r))
                if piece != EMPTY:
                    if piece in rank_file_atk:
                        return True
                    break

        for dr, df in KNIGHT_DELTAS:
            r, f = sq_rank + dr, sq_file + df
            if 0 <= r < 8 and 0 <= f < 8:
                if board.piece_at(sq(f, r)) == KNIGHT * -side:
                    return True

        pawn_deltas = [[side, 1], [side, -1]]
        for dr, df in pawn_deltas:
            r, f = sq_rank + dr, sq_file + df
            if 0 <= r < 8 and 0 <= f < 8:
                if board.piece_at(sq(f, r)) == PAWN * -side:
                    return True

        for dr, df in ALL_DELTAS:
            r, f = sq_rank + dr, sq_file + df
            if 0 <= r < 8 and 0 <= f < 8:
                if board.piece_at(sq(f, r)) == KING * -side:
                    return True

        return False

    def is_in_check(self, board, side):
        return self.is_square_attacked(board, board.king_sq[side], side)
    
    def king_moves(self, board, square):
        moves = []
        r, f = rank_of(square), file_of(square)

        for dr, df in ALL_DELTAS:
            cur_r, cur_f = r + dr, f + df

            if 0 <= cur_r < 8 and 0 <= cur_f < 8:
                to_sq = sq(cur_f, cur_r)
                target = board.piece_at(to_sq)

                if target == EMPTY:
                    moves.append(Move(square, to_sq))
                elif (target > 0) != (board.side == WHITE):
                    moves.append(Move(square, to_sq, CAPTURE, target))
                else:
                    continue

        if not self.is_in_check(board, board.side):
            if board.side == WHITE:
                if board.castle_rights & CASTLE_WK:
                    if all(board.piece_at(s) == EMPTY and not self.is_square_attacked(board, s, board.side) for s in [5, 6]):
                        moves.append(Move(square, 6, CASTLE_KING))
                if board.castle_rights & CASTLE_WQ:
                    if board.piece_at(1) == EMPTY:
                        if all(board.piece_at(s) == EMPTY and not self.is_square_attacked(board, s, board.side) for s in [2, 3]):
                            moves.append(Move(square, 2, CASTLE_QUEEN))
            else:
                if board.castle_rights & CASTLE_BK:
                    if all(board.piece_at(s) == EMPTY and not self.is_square_attacked(board, s, board.side) for s in [61, 62]):
                        moves.append(Move(square, 62, CASTLE_KING))
                if board.castle_rights & CASTLE_BQ:
                    if board.piece_at(57) == EMPTY:
                        if all(board.piece_at(s) == EMPTY and not self.is_square_attacked(board, s, board.side) for s in [58, 59]):
                            moves.append(Move(square, 58, CASTLE_QUEEN))

        return moves