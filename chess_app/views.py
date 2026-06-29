from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from engine.game import Game
from engine.move import Move
from engine.constants import EMPTY
import json
import random
from engine.constants import EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, GameStatus

PIECE_VALUES = {PAWN: 1, KNIGHT: 3, BISHOP: 3, ROOK: 5, QUEEN: 9}

def move_from_dict(move):
    return Move(move['from_sq'], move['to_sq'], move['flag'], move['captured'])

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')

def _reconstruct_game(request):
    if 'move_history' not in request.session:
        return None, None
    move_history = request.session['move_history']
    game = Game()
    for move_dict in move_history:
        game.push(move_from_dict(move_dict))
    return game, move_history


def _finalize_and_respond(request, game, move_history, move):
    game.push(move)
    move_history.append({
        'from_sq': move.from_sq, 'to_sq': move.to_sq,
        'flag': move.flag, 'captured': move.captured
    })
    request.session['move_history'] = move_history

    captures = [m['captured'] for m in move_history if m['captured'] != EMPTY]

    return JsonResponse({
        'board': game.board.squares,
        'legal_moves': [{'from_sq': m.from_sq, 'to_sq': m.to_sq, 'flag': m.flag} for m in game.legal_moves],
        'status': game.current_status.value,
        'side': game.board.side,
        'captures': captures,
    })

def start_game(request):
    game = Game()
    request.session['move_history'] = []
    
    data = {
        'board' : game.board.squares,
        'legal_moves' : [{'from_sq': move.from_sq, 'to_sq': move.to_sq, 'flag': move.flag} for move in game.legal_moves],
        'status' : game.current_status.value,
        'side' : game.board.side,
    }
    
    return JsonResponse(data)

def make_move(request):
    game, move_history = _reconstruct_game(request)
    if game is None:
        return JsonResponse({'error': 'No active game'}, status=400)

    incoming_data = json.loads(request.body)
    incoming = Move(incoming_data['from_sq'], incoming_data['to_sq'], incoming_data['flag'])
    matched_move = next((m for m in game.legal_moves if m == incoming), None)

    if matched_move is None:
        return JsonResponse({'error': 'Illegal move'}, status=400)

    return _finalize_and_respond(request, game, move_history, matched_move)

def make_bot_move_easy(request):
    game, move_history = _reconstruct_game(request)
    if game is None:
        return JsonResponse({'error': 'No active game'}, status=400)

    if game.current_status != GameStatus.ONGOING:
        return JsonResponse({'error': 'Game has ended'}, status=400)

    move = choose_easy_bot_move(game)
    return _finalize_and_respond(request, game, move_history, move)

def choose_easy_bot_move(game):
    # 1. Take mate-in-1 if available
    for move in game.legal_moves:
        game.push(move)
        is_mate = game.current_status == GameStatus.CHECKMATE
        game.pop()
        if is_mate:
            return move

    # 2. Shuffle captures, roll each one's odds in turn
    captures = [move for move in game.legal_moves if move.captured != EMPTY]
    random.shuffle(captures)
    for move in captures:
        piece_value = PIECE_VALUES[abs(move.captured)]
        if random.random() < piece_value / 10:
            return move

    # 3. Otherwise, pick uniformly at random
    return random.choice(game.legal_moves)

