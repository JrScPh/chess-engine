import sys
import time
import argparse
from fen import board_from_fen, STARTING_FEN
from move_generator import MoveGenerator, perft

KIWIPETE_FEN = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"

if len(sys.argv) < 2:
    print("Error: missing depth input")
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument("depth", type=int)
parser.add_argument("-k","--kiwipete", action="store_true")
args = parser.parse_args()

if args.kiwipete:
    fen_name = "Kiwipete"
    board = board_from_fen(KIWIPETE_FEN)
else:
    fen_name = "Standard"
    board = board_from_fen()
gen = MoveGenerator()

start = time.perf_counter()
nodes = perft(board, gen, args.depth)
elapsed = time.perf_counter() - start

print(f"FEN: {fen_name}")
print(f"Nodes: {nodes}")
print(f"Time: {elapsed:.2f}s")