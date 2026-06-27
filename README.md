# Chess Engine (Python)

A chess engine built from scratch in Python, with a Django backend and a vanilla JS/HTML/CSS frontend. Move generation, rules enforcement, and game state are handled entirely server-side; the frontend is a thin rendering layer with no game logic of its own.

This is the Python implementation in a planned multi-language chess project (Java, C, C++ versions to follow as separate repos).

## Features

- Full move generation from scratch (no chess libraries) — all piece types, castling, en passant, promotion (including underpromotion)
- Check, checkmate, and stalemate detection
- Draw detection: threefold repetition, fifty-move rule, insufficient material
- FEN parsing and serialization
- Perft-validated move generator (starting position to depth 5, Kiwipete to depth 4)
- Session-based game state — no database required
- Click-to-move web UI with legal move highlighting and captured-piece tracking

## Tech Stack

- **Engine:** Python
- **Backend:** Django
- **Frontend:** Vanilla JavaScript, HTML, CSS
- **Testing:** pytest

## Project Structure

```
chess-engine/
├── engine/          # Core chess engine (board, moves, rules, FEN)
├── chess_app/       # Django app (views, urls)
├── webapp/          # Django project settings
├── frontend/
│   ├── templates/   # HTML
│   └── static/      # CSS, JS
├── tests/           # pytest test suite + perft.py
└── manage.py
```

## Setup

```bash
git clone https://github.com/<your-username>/chess-engine.git
cd chess-engine
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to play.

## Running Tests

```bash
pytest
```

For perft verification:

```bash
python tests/perft.py <depth>
python tests/perft.py <depth> -k   # Kiwipete position
```

## Status

Core engine and playable web UI are complete. A bot opponent (rule-based and ML-based difficulty tiers) is planned next.
