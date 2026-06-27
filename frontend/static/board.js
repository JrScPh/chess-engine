const boardContainer = document.getElementById('board');
const promotionDialog = document.getElementById('promotion-dialog');
const pieceSymbols = {
    1: '♙', 2: '♘', 3: '♗', 4: '♖', 5: '♕', 6: '♔',
    '-1': '♟', '-2': '♞', '-3': '♝', '-4': '♜', '-5': '♛', '-6': '♚',
};
let currentMoves = []
let data = null;
let pendingFromSq = null;
let pendingToSq = null;

function fileOf(index) {
    return index % 8;
}
function rankOf(index) {
    return Math.floor(index / 8);
}
function setBoard() {
    for (let i = 0; i < 64; i++) {
        const square = document.querySelector(`[data-square="${i}"]`);
        if (data.board[i] == 0) {
            square.textContent = ' ';
        } else {
            square.textContent = pieceSymbols[data.board[i]];
        }
    }
}
function clearHighlights() {
    for (let i = 0; i < 64; i++) {
        const square = document.querySelector(`[data-square="${i}"]`);
        square.classList.remove('highlighted');
    }
}
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
}
function updateStatusMessage() {
    const title = document.getElementById('status-title');
    const subtitle = document.getElementById('status-subtitle');
    const winner = data.side === 1 ? 'Black' : 'White';
    const currentSide = data.side === 1 ? 'White' : 'Black';
    console.log(data.side, data.status)
    if (data.status === 'ongoing') {
        title.textContent = 'Ongoing';
        subtitle.textContent = `${currentSide} to play`;
    }
    if (data.status === 'checkmate') {
        title.textContent = 'Checkmate';
        subtitle.textContent = `${winner} wins!`;
    }
    if (data.status === 'stalemate') {
        title.textContent = 'Stalemate';
        subtitle.textContent = 'No legal moves left';
    }
    if (data.status === 'draw_repetition') {
        title.textContent = 'Draw';
        subtitle.textContent = 'By threefold repetition';
    }
    if (data.status === 'draw_insufficient') {
        title.textContent = 'Draw';
        subtitle.textContent = 'By insufficient material';
    }
    if (data.status === 'draw_fifty_move') {
        title.textContent = 'Draw';
        subtitle.textContent = 'By fifty-move rule';
    }
}
async function startGame() {
    const response = await fetch('/api/start-game/');
    data = await response.json();
    console.log(data);
    setBoard();
    updateStatusMessage();
}
function onSquareClick(squareIndex) {
    if (currentMoves.some(move => move.to_sq === squareIndex)) {
        const matchedMove = currentMoves.find(move => move.to_sq === squareIndex);
        if ([6, 7, 8, 9].includes(matchedMove.flag)) {
            pendingFromSq = matchedMove.from_sq;
            pendingToSq = matchedMove.to_sq;
            promotionDialog.classList.remove('hidden');
        } else {
            makeMove(matchedMove);
        }
        currentMoves = [];
        return;
    }
    clearHighlights();
    currentMoves = data.legal_moves.filter(move => move.from_sq === squareIndex);
    for (const move of currentMoves) {
        const square = document.querySelector(`[data-square="${move.to_sq}"]`);
        square.classList.add('highlighted');
    }
}
function handlePromotion(flag) {
    makeMove({ from_sq: pendingFromSq, to_sq: pendingToSq, flag: flag });
    promotionDialog.classList.add('hidden');
}
async function makeMove(move) {
    const response = await fetch('/api/make-move/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            from_sq: move.from_sq,
            to_sq: move.to_sq,
            flag: move.flag,
        }),
    });
    data = await response.json();
    clearHighlights();
    setBoard();
    updateStatusMessage();
}

for (let i = 7; i >= 0; i--) {
    for (let j = 0; j < 8; j++) {
        const square = document.createElement('div');
        const id = i * 8 + j
        square.dataset.square = id;
        square.addEventListener('click', () => onSquareClick(id));
        if ((i + j) % 2 == 0) {
            square.className = 'square dark';
        } else {
            square.className = 'square light';
        }
        boardContainer.appendChild(square);
    }
}
document.getElementById('promo-queen').addEventListener('click', () => handlePromotion(6));
document.getElementById('promo-rook').addEventListener('click', () => handlePromotion(7));
document.getElementById('promo-bishop').addEventListener('click', () => handlePromotion(8));
document.getElementById('promo-knight').addEventListener('click', () => handlePromotion(9));

startGame();