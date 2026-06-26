import pytest  # type: ignore[import]
from engine.fen import board_from_fen
from engine.move_generator import MoveGenerator
from engine.constants import *
from engine.game import Game
from engine.move import Move

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
    
def test_pawn_captures():
    test_board = board_from_fen("4k3/8/8/8/2p1p2/3P4/8/4K3 w - - 0 1")
    moves = gen.pawn_moves(test_board, 19)  # d3
    captures = [m for m in moves if m.flag == CAPTURE]
    assert len(captures) == 2
    
def test_pawn_friendly():
    test_board = board_from_fen("4k3/8/8/8/2P1P2/3P4/8/4K3 w - - 0 1")
    moves = gen.pawn_moves(test_board, 19)  # d3
    assert len(moves) == 1
    
def test_pawn_en_passant():
    test_board = board_from_fen("4k3/8/8/3Pp3/8/8/8/4K3 w - e6 0 1")
    moves = gen.pawn_moves(test_board, 35)  # d5
    assert any(move.flag == EN_PASSANT for move in moves)
    
def test_pawn_promo():
    test_board = board_from_fen("1n2k3/2P5/8/8/8/8/8/4K3 w - - 0 1")
    moves = gen.pawn_moves(test_board, 50)  # c7

    quiet_promos = [m for m in moves if m.flag in (PROMO_Q, PROMO_R, PROMO_B, PROMO_N) and m.captured == EMPTY]
    capture_promos = [m for m in moves if m.flag in (PROMO_Q, PROMO_R, PROMO_B, PROMO_N) and m.captured != EMPTY]

    assert len(quiet_promos) == 4
    assert len(capture_promos) == 4
    assert all(m.captured == KNIGHT * BLACK for m in capture_promos)
    assert {m.flag for m in quiet_promos} == {PROMO_Q, PROMO_R, PROMO_B, PROMO_N}
    assert {m.flag for m in capture_promos} == {PROMO_Q, PROMO_R, PROMO_B, PROMO_N}
    
def test_king_quiet():
    test_board = board_from_fen("7k/8/8/8/4K3/8/8/8 w - - 0 1")
    moves = gen.king_moves(test_board, 28)
    assert len(moves) == 8
    assert all(m.flag == QUIET for m in moves)


def test_king_capture():
    test_board = board_from_fen("7k/8/8/3nnn3/3nKn3/3nnn3/8/8 w - - 0 1")
    moves = gen.king_moves(test_board, 28)
    assert len(moves) == 8
    assert all(m.flag == CAPTURE for m in moves)


def test_king_friendly():
    test_board = board_from_fen("7k/8/8/3NNN3/3NKN3/3NNN3/8/8 w - - 0 1")
    moves = gen.king_moves(test_board, 28)
    assert len(moves) == 0

def test_king_avoid_check():
    test_board = board_from_fen("7k/8/3r4/2r5/4K3/6r1/5r2/8 w - - 0 1")
    moves = gen.generate_moves(test_board)
    assert not any(m.from_sq == 28 for m in moves)
    
@pytest.mark.parametrize("fen,king_sq", [
    ("4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1", 4),    # white
    ("r3k2r/8/8/8/8/8/8/4K3 b kq - 0 1", 60),   # black
])
def test_castle_legal(fen, king_sq):
    test_board = board_from_fen(fen)
    moves = gen.king_moves(test_board, king_sq)
    castle_moves = [m for m in moves if m.flag in (CASTLE_KING, CASTLE_QUEEN)]
    assert len(castle_moves) == 2
    
@pytest.mark.parametrize("fen,king_sq", [
    ("4k3/8/8/8/8/8/8/R2NKN1R w KQ - 0 1", 4),    # white, knights on c1/f1
    ("r1n1kn1r/8/8/8/8/8/8/4K3 b kq - 0 1", 60),   # black, knights on c8/f8
])
def test_castle_blocked(fen, king_sq):
    test_board = board_from_fen(fen)
    moves = gen.king_moves(test_board, king_sq)
    castle_moves = [m for m in moves if m.flag in (CASTLE_KING, CASTLE_QUEEN)]
    assert len(castle_moves) == 0
    
@pytest.mark.parametrize("fen,king_sq", [
    ("4k3/8/8/8/8/8/8/R3K2R w - - 0 1", 4),
    ("r3k2r/8/8/8/8/8/8/4K3 b - - 0 1", 60),
])
def test_castle_no_rights(fen, king_sq):
    test_board = board_from_fen(fen)
    moves = gen.king_moves(test_board, king_sq)
    castle_moves = [m for m in moves if m.flag in (CASTLE_KING, CASTLE_QUEEN)]
    assert len(castle_moves) == 0
    
@pytest.mark.parametrize("fen,king_sq", [
    ("4k3/4q3/8/8/8/8/8/R3K2R w KQ - 0 1", 4),    # white king in check from queen e7
    ("r3k2r/8/8/8/8/8/4Q3/4K3 b kq - 0 1", 60),   # black king in check from queen e2
])
def test_castle_in_check(fen, king_sq):
    test_board = board_from_fen(fen)
    moves = gen.king_moves(test_board, king_sq)
    castle_moves = [m for m in moves if m.flag in (CASTLE_KING, CASTLE_QUEEN)]
    assert len(castle_moves) == 0
    
@pytest.mark.parametrize("fen,king_sq", [
    ("4k3/8/8/8/2q5/8/8/R3K2R w KQ - 0 1", 4),    # white, queen on c4
    ("r3k2r/8/8/2Q5/8/8/8/4K3 b kq - 0 1", 60),   # black, queen on c5
])
def test_castle_attacked(fen, king_sq):
    test_board = board_from_fen(fen)
    moves = gen.king_moves(test_board, king_sq)
    castle_moves = [m for m in moves if m.flag in (CASTLE_KING, CASTLE_QUEEN)]
    assert len(castle_moves) == 0
    
def test_pinned_rook_file():
    test_board = board_from_fen("4r3/8/8/8/8/8/4R3/4K3 w - - 0 1")
    moves = gen.generate_moves(test_board)
    rook_moves = [m for m in moves if m.from_sq == 12]
    assert sorted(m.to_sq for m in rook_moves) == [20, 28, 36, 44, 52, 60]
    
def test_pinned_bishop_diagonal():
    test_board = board_from_fen("7k/8/8/8/7b/8/5B2/4K3 w - - 0 1")
    moves = gen.generate_moves(test_board)
    bishop_moves = [m for m in moves if m.from_sq == 13]
    assert sorted(m.to_sq for m in bishop_moves) == [22, 31]
    
def test_en_passant_discovered_check():
    test_board = board_from_fen("7k/8/8/K2Pp2r/8/8/8/8 w - e6 0 1")
    moves = gen.generate_moves(test_board)
    ep_moves = [m for m in moves if m.from_sq == 35 and m.flag == EN_PASSANT]
    assert len(ep_moves) == 0
    
def test_game_push():
    test_game = Game()
    test_move = Move(12,28,DOUBLE_PUSH)
    test_undo = {
            'castle_rights': test_game.board.castle_rights,
            'en_passant': test_game.board.en_passant,
            'halfmove': test_game.board.halfmove
        }
    test_game.push(test_move)
    assert len(test_game.history) == 1
    assert test_game.history[0] == (test_move, test_undo)
    assert len(test_game.position_counts) == 2
    assert test_game.position_counts["rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3"] == 1
    
def test_game_pop():
    test_game = Game()
    test_game.push(Move(12,28,DOUBLE_PUSH))
    test_game.pop()
    assert len(test_game.history) == 0
    assert len(test_game.position_counts) == 1
    assert test_game.position_counts["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"] == 1
    
def test_scholars_mate():
    test_game = Game()
    test_game.push(Move(12, 28, DOUBLE_PUSH))             # e4
    test_game.push(Move(52, 36, DOUBLE_PUSH))             # e5
    test_game.push(Move(5, 26, QUIET))                    # Bc4
    test_game.push(Move(57, 42, QUIET))                   # Nc6
    test_game.push(Move(3, 39, QUIET))                    # Qh5
    test_game.push(Move(62, 45, QUIET))                   # Nf6
    test_game.push(Move(39, 53, CAPTURE, PAWN * BLACK))   # Qxf7#

    assert test_game.current_status == GameStatus.CHECKMATE
    
def test_stalemate():
    game = Game("k7/8/2Q5/K7/8/8/8/8 w - - 0 1")
    game.push(Move(42, 41, QUIET))  # Qc6-b6
    assert game.current_status == GameStatus.STALEMATE
    
def test_draw_fifty_move():
    game = Game("4k3/8/8/8/8/8/8/R3K3 w - - 99 50")
    game.push(Move(4, 12, QUIET))  # Ke1-e2
    assert game.current_status == GameStatus.DRAW_FIFTY_MOVE
    
def test_insufficient_king_vs_king():
    game = Game("k7/8/8/3p4/4K3/8/8/8 w - - 0 1")
    game.push(Move(36, 35, CAPTURE, PAWN * BLACK))  # Kxd5
    assert game.current_status == GameStatus.DRAW_INSUFFICIENT


def test_insufficient_knight_vs_king():
    game = Game("k7/8/8/1p6/8/2N5/8/4K3 w - - 0 1")
    game.push(Move(18, 33, CAPTURE, PAWN * BLACK))  # Nxb5
    assert game.current_status == GameStatus.DRAW_INSUFFICIENT


def test_insufficient_same_color_bishops():
    game = Game("4kb2/8/8/8/8/8/3p4/2B1K3 w - - 0 1")
    game.push(Move(2, 11, CAPTURE, PAWN * BLACK))  # Bxd2
    assert game.current_status == GameStatus.DRAW_INSUFFICIENT
    
def test_sufficient_opposite_color_bishops():
    game = Game("3kb3/8/8/8/8/8/3p4/2B1K3 w - - 0 1")
    game.push(Move(2, 11, CAPTURE, PAWN * BLACK))  # Bxd2
    assert game.current_status == GameStatus.ONGOING
    
def test_draw_repetition():
    game = Game()
    sequence = [
        (1, 18),   # Nb1-c3
        (57, 42),  # Nb8-c6
        (18, 1),   # Nc3-b1
        (42, 57),  # Nc6-b8
        (1, 18),   # Nb1-c3
        (57, 42),  # Nb8-c6
        (18, 1),   # Nc3-b1
        (42, 57),  # Nc6-b8
    ]

    for from_sq, to_sq in sequence:
        game.push(Move(from_sq, to_sq, QUIET))

    assert game.current_status == GameStatus.DRAW_REPETITION