const boardContainer = document.getElementById('board');
const pieceSymbols = {
    1: '♙', 2: '♘', 3: '♗', 4: '♖', 5: '♕', 6: '♔',
    '-1': '♟', '-2': '♞', '-3': '♝', '-4': '♜', '-5': '♛', '-6': '♚',
};

function fileOf(index) {
    return index % 8;
}

function rankOf(index) {
    return Math.floor(index / 8);
}

async function startGame() {
    const response = await fetch('/api/start-game/');
    const data = await response.json();
    console.log(data);
    for (let i = 0; i < 64; i++) {
        const square = document.querySelector(`[data-square="${i}"]`);
        if (data.board[i] == 0) {
            square.textContent = ' ';
        } else {
            square.textContent = pieceSymbols[data.board[i]];
        }
    }
}

for (let i = 7; i >= 0; i--) {
    for (let j = 0; j < 8; j++) {
        const square = document.createElement('div');
        square.dataset.square = i * 8 + j;
        if ((i + j) % 2 == 0) {
            square.className = 'square dark';
        } else {
            square.className = 'square light';
        }
        boardContainer.appendChild(square);
    }
}

startGame();