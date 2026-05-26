from enum import Enum

# Colors
WHITE =  1
BLACK = -1

# Piece types
EMPTY  = 0
PAWN   = 1
KNIGHT = 2
BISHOP = 3
ROOK   = 4
QUEEN  = 5
KING   = 6

# Game status
class GameStatus(Enum):
    ONGOING           = "ongoing"
    CHECK             = "check"
    CHECKMATE         = "checkmate"
    STALEMATE         = "stalemate"
    DRAW_REPETITION   = "draw_repetition"
    DRAW_INSUFFICIENT = "draw_insufficient"
    DRAW_FIFTY_MOVE   = "draw_fifty_move"

# Castling rights
CASTLE_WK = 1
CASTLE_WQ = 2
CASTLE_BK = 4
CASTLE_BQ = 8

# Move flags
QUIET        = 0
DOUBLE_PUSH  = 1
CASTLE_KING  = 2
CASTLE_QUEEN = 3
CAPTURE      = 4
EN_PASSANT   = 5
PROMO_Q      = 6
PROMO_R      = 7
PROMO_B      = 8
PROMO_N      = 9

# Board helpers
def sq(file, rank):
    return rank * 8 + file

def file_of(index):
    return index % 8

def rank_of(index):
    return index // 8