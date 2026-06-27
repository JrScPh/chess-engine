from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from engine.game import Game
from engine.move import Move
import json

def move_from_dict(move):
    return Move(move['from_sq'], move['to_sq'], move['flag'], move['captured'])

def index(request):
    return render(request, 'index.html')

def start_game(request):
    game = Game()
    request.session['move_history'] = []
    
    data = {
        'board' : game.board.squares,
        'legal_moves' : [{'from_sq': move.from_sq, 'to_sq': move.to_sq, 'flag': move.flag} for move in game.legal_moves],
        'status' : game.current_status.value,
    }
    
    return JsonResponse(data)

def make_move(request):
    if 'move_history' not in request.session:
        return JsonResponse({'error': 'No active game'}, status=400)
    
    game = Game()
    for move in request.session['move_history']:
        game.push(move_from_dict(move))
        
    incoming_data = json.loads(request.body)
    
    incoming = Move(incoming_data['from_sq'], incoming_data['to_sq'], incoming_data['flag'])
    matched_move = next((m for m in game.legal_moves if m == incoming), None)
    
    if matched_move is None:
        return JsonResponse({'error':'Illegal move'}, status=400)
    
    game.push(matched_move)
    
    move_history = request.session.get('move_history', [])
    move_history.append({'from_sq': matched_move.from_sq, 'to_sq': matched_move.to_sq, 'flag': matched_move.flag, 'captured': matched_move.captured})
    request.session['move_history'] = move_history
    
    outgoing_data = {
        'board' : game.board.squares,
        'legal_moves' : [{'from_sq': move.from_sq, 'to_sq': move.to_sq, 'flag': move.flag} for move in game.legal_moves],
        'status' : game.current_status.value,
    }
    
    return JsonResponse(outgoing_data)