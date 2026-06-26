from constants import (
    EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    WHITE, BLACK,
    CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ,
    CASTLE_KING, CASTLE_QUEEN,
    EN_PASSANT, DOUBLE_PUSH,
    PROMO_Q, PROMO_R, PROMO_B, PROMO_N,
)

PROMO_MAP = {
    PROMO_Q: QUEEN,
    PROMO_R: ROOK,
    PROMO_B: BISHOP,
    PROMO_N: KNIGHT
}

class Board:
    def __init__(self):
        self.squares = [EMPTY] * 64
        self.side = WHITE
        self.castle_rights = CASTLE_WK | CASTLE_WQ | CASTLE_BK | CASTLE_BQ
        self.en_passant = -1
        self.halfmove = 0
        self.fullmove = 1
        self.king_sq = {WHITE: -1, BLACK: -1}

    def piece_at(self, square):
        return self.squares[square]

    def set_piece(self, square, piece):
        current_piece = self.piece_at(square)

        if abs(current_piece) == KING:
            self.king_sq[WHITE if current_piece > 0 else BLACK] = -1
            
        self.squares[square] = piece
        
        if abs(piece) == KING:
            self.king_sq[WHITE if piece > 0 else BLACK] = square

    def make_move(self, move):
        undo = {
            'castle_rights': self.castle_rights,
            'en_passant': self.en_passant,
            'halfmove': self.halfmove
        }

        piece = self.piece_at(move.from_sq)
        piece_type = abs(piece)

        if move.is_en_passant:
            self.set_piece(move.to_sq - 8 * self.side, EMPTY)

        elif move.flag == CASTLE_KING:
            self.set_piece(move.to_sq - 1, self.piece_at(move.to_sq + 1))
            self.set_piece(move.to_sq + 1, EMPTY)

        elif move.flag == CASTLE_QUEEN:
            self.set_piece(move.to_sq + 1, self.piece_at(move.to_sq - 2))
            self.set_piece(move.to_sq - 2, EMPTY)

        if piece_type == KING:
            if self.side == WHITE:
                self.castle_rights &= ~(CASTLE_WK | CASTLE_WQ)
            else:
                self.castle_rights &= ~(CASTLE_BK | CASTLE_BQ)

        if piece_type == ROOK or move.is_capture:
            if move.from_sq == 0  or move.to_sq == 0:  self.castle_rights &= ~CASTLE_WQ
            if move.from_sq == 7  or move.to_sq == 7:  self.castle_rights &= ~CASTLE_WK
            if move.from_sq == 56 or move.to_sq == 56: self.castle_rights &= ~CASTLE_BQ
            if move.from_sq == 63 or move.to_sq == 63: self.castle_rights &= ~CASTLE_BK

        self.en_passant = move.to_sq - 8 * self.side if move.flag == DOUBLE_PUSH else -1

        if move.is_promotion:
            piece = PROMO_MAP[move.flag] * self.side
        self.set_piece(move.from_sq, EMPTY)
        self.set_piece(move.to_sq, piece)
        

        if move.is_capture or piece_type == PAWN:
            self.halfmove = 0
        else:
            self.halfmove += 1

        if self.side == BLACK:
            self.fullmove += 1

        self.side = -self.side

        return undo

    def unmake_move(self, move, undo):
        self.side = -self.side
        self.halfmove = undo['halfmove']
        self.en_passant = undo['en_passant']
        self.castle_rights = undo['castle_rights']

        if self.side == BLACK:
            self.fullmove -= 1

        if move.is_promotion:
            piece = PAWN * self.side
        else:
            piece = self.piece_at(move.to_sq)

        if move.is_en_passant:
            self.set_piece(move.to_sq, EMPTY)
            self.set_piece(move.to_sq - 8 * self.side, PAWN * -self.side)
        elif move.flag == CASTLE_KING:
            self.set_piece(move.to_sq, EMPTY)
            self.set_piece(move.to_sq + 1, ROOK * self.side)
            self.set_piece(move.to_sq - 1, EMPTY)
        elif move.flag == CASTLE_QUEEN:
            self.set_piece(move.to_sq, EMPTY)
            self.set_piece(move.to_sq - 2, ROOK * self.side)
            self.set_piece(move.to_sq + 1, EMPTY)
        elif move.is_capture:
            self.set_piece(move.to_sq, move.captured)
        else:
            self.set_piece(move.to_sq, EMPTY)
            
        self.set_piece(move.from_sq, piece)