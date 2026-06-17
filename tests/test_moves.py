import pytest
from fen import board_from_fen
from move_generator import MoveGenerator
from constants import KNIGHT, QUEEN, WHITE, CAPTURE, QUIET, DOUBLE_PUSH

gen = MoveGenerator()

@pytest.fixture
def empty_board():
    return board_from_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")


@pytest.mark.parametrize("square,expected", [
    (27, 8),   # d4 - fully central
    (26, 8),   # c4 - still central
    (25, 6),   # b4 - one edge cut
    (24, 4),   # a4 - file edge
    (19, 7),   # d3 - fully central
    (11, 6),   # d2 - one edge cut
    (3,  4),   # d1 - rank edge
    (18, 8),   # c3 - fully central
    (9,  4),   # b2 - two edges cut
    (0,  2),   # a1 - corner
    (8,  3),   # a2 - file edge, near corner
    (1,  3),   # b1 - rank edge, near corner
])
def test_knight_moves(empty_board, square, expected):
    empty_board.set_piece(square, KNIGHT * WHITE)
    moves = gen.knight_moves(empty_board, square)
    assert len(moves) == expected
    
def test_knight_captures():
    test_board = board_from_fen("4k3/8/2p1p2/1p3p2/3N4/1p3p2/2p1p2/4K3 w - - 0 1")
    moves = gen.knight_moves(test_board, 27)
    assert len(moves) == 8 and all(move.flag == CAPTURE for move in moves)
    
def test_knight_friendly():
    test_board = board_from_fen("4k3/8/2P1P2/1P3P2/3N4/1P3P2/2P1P2/4K3 w - - 0 1")
    moves = gen.knight_moves(test_board, 27)
    assert len(moves) == 0
    
def test_sliding_moves(empty_board):
    empty_board.set_piece(27, QUEEN * WHITE)
    moves = gen.queen_moves(empty_board, 27)
    assert len(moves) == 27
    
def test_sliding_corner():
    test_board = board_from_fen("4k3/8/8/8/8/8/4K3/Q7 w - - 0 1")
    moves = gen.queen_moves(test_board, 0)
    assert len(moves) == 21
    
def test_sliding_capture():
    test_board = board_from_fen("4k3/8/1p1p1p2/8/p2Q1p2/3pp3/8/p3K3 w - - 0 1")
    moves = gen.queen_moves(test_board, 27)
    captures = [m for m in moves if m.flag == CAPTURE]
    quiets = [m for m in moves if m.flag == QUIET]
    assert len(moves) == 16
    assert len(captures) == 8
    assert len(quiets) == 8

def test_sliding_friendly():
    test_board = board_from_fen("4k3/8/1P1P1P2/8/P2Q1P2/3PP3/8/P3K3 w - - 0 1")
    moves = gen.queen_moves(test_board, 27)
    assert len(moves) == 8
    
def test_pawn_single_push():
    test_board = board_from_fen("4k3/8/8/8/3p2P1/P2P2P1/8/4K3 w - - 0 1")

    a_moves = gen.pawn_moves(test_board, 16)  # a3
    assert len(a_moves) == 1 and a_moves[0].flag == QUIET

    d_moves = gen.pawn_moves(test_board, 19)  # d3
    assert len(d_moves) == 0

    g_moves = gen.pawn_moves(test_board, 22)  # g3
    assert len(g_moves) == 0
    
def test_pawn_double_push():
    test_board = board_from_fen("4k3/8/8/8/3p2P1/8/P2P2P1/4K3 w - - 0 1")

    d_moves = gen.pawn_moves(test_board, 11)  # d2
    assert len(d_moves) == 1
    assert d_moves[0].flag == QUIET

    g_moves = gen.pawn_moves(test_board, 14)  # g2
    assert len(g_moves) == 1
    assert g_moves[0].flag == QUIET

    a_moves = gen.pawn_moves(test_board, 8)  # a2
    assert len(a_moves) == 2
    double_push = next(m for m in a_moves if m.flag == DOUBLE_PUSH)
    assert double_push.to_sq == 24  # a4

    test_board.make_move(double_push)
    assert test_board.en_passant == 16  # a3