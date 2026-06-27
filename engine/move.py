from engine.constants import EMPTY, QUIET, PROMO_Q, PROMO_R, PROMO_B, PROMO_N, CASTLE_KING, CASTLE_QUEEN, EN_PASSANT

class Move:
    def __init__(self, from_sq, to_sq, flag=QUIET, captured=EMPTY):
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.flag = flag
        self.captured = captured
        
    def __eq__(self, other):
        return self.from_sq == other.from_sq and self.to_sq == other.to_sq and self.flag == other.flag

    @property
    def is_capture(self):
        return self.captured != EMPTY

    @property
    def is_promotion(self):
        return self.flag in (PROMO_Q, PROMO_R, PROMO_B, PROMO_N)

    @property
    def is_castle(self):
        return self.flag in (CASTLE_KING, CASTLE_QUEEN)

    @property
    def is_en_passant(self):
        return self.flag == EN_PASSANT