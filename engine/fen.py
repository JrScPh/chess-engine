from engine.constants import (
    EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    WHITE, BLACK,
    CASTLE_WK, CASTLE_WQ, CASTLE_BK, CASTLE_BQ,
    sq, file_of, rank_of,
)
from engine.board import Board

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def board_from_fen(fen=STARTING_FEN):
    fields = fen.split(" ")
    board = Board()

    # Piece placement
    rank = 7
    for row in fields[0].split('/'):
        file = 0
        for char in row:
            if char.isnumeric():
                file += int(char)
            else:
                if char.isupper():
                    side = WHITE
                else:
                    side = BLACK
                square = sq(file, rank)
                match char.lower():
                    case 'r': board.set_piece(square, ROOK * side)
                    case 'n': board.set_piece(square, KNIGHT * side)
                    case 'b': board.set_piece(square, BISHOP * side)
                    case 'q': board.set_piece(square, QUEEN * side)
                    case 'k': board.set_piece(square, KING * side)
                    case 'p': board.set_piece(square, PAWN * side)
                    case _: raise ValueError(f"Invalid FEN character: {char}")
                file += 1
        rank -= 1

    # Side to move
    board.side = WHITE if fields[1] == 'w' else BLACK

    # Castling rights
    board.castle_rights = 0
    if 'K' in fields[2]: board.castle_rights |= CASTLE_WK
    if 'Q' in fields[2]: board.castle_rights |= CASTLE_WQ
    if 'k' in fields[2]: board.castle_rights |= CASTLE_BK
    if 'q' in fields[2]: board.castle_rights |= CASTLE_BQ

    # En passant
    board.en_passant = -1 if fields[3] == '-' else sq(ord(fields[3][0]) - ord('a'), int(fields[3][1]) - 1)

    # Clocks
    board.halfmove = int(fields[4])
    board.fullmove = int(fields[5])

    return board


def board_to_fen(board):
    PIECE_TO_FEN = {
        PAWN * WHITE: 'P', KNIGHT * WHITE: 'N', BISHOP * WHITE: 'B',
        ROOK * WHITE: 'R', QUEEN * WHITE: 'Q', KING * WHITE: 'K',
        PAWN * BLACK: 'p', KNIGHT * BLACK: 'n', BISHOP * BLACK: 'b',
        ROOK * BLACK: 'r', QUEEN * BLACK: 'q', KING * BLACK: 'k',
    }

    fen = ""

    for rank in range(7, -1, -1):
        empty_squares = 0

        for file in range(0, 8):
            piece = board.piece_at(sq(file, rank))

            if piece == EMPTY:
                empty_squares += 1
            else:
                if empty_squares:
                    fen += str(empty_squares)
                    empty_squares = 0
                fen += PIECE_TO_FEN[piece]

        if empty_squares:
            fen += str(empty_squares)

        fen += ' ' if rank == 0 else '/'

    # Side to move
    fen += 'w ' if board.side == WHITE else 'b '

    # Castling rights
    castling = ''
    if board.castle_rights & CASTLE_WK: castling += 'K'
    if board.castle_rights & CASTLE_WQ: castling += 'Q'
    if board.castle_rights & CASTLE_BK: castling += 'k'
    if board.castle_rights & CASTLE_BQ: castling += 'q'
    fen += (castling if castling else '-') + ' '

    # En passant
    if board.en_passant == -1:
        fen += '- '
    else:
        fen += 'abcdefgh'[file_of(board.en_passant)] + str(rank_of(board.en_passant) + 1) + ' '

    # Clocks
    fen += str(board.halfmove) + ' ' + str(board.fullmove)

    return fen