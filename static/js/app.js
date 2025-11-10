// Game State
const GameState = {
    puzzle: null,
    solution: null,
    current: null,
    initialGrid: null,
    selectedCell: null,
    difficulty: 'medium',
    timer: 0,
    timerInterval: null,
    hints: 3,
    mistakes: 0,
    history: [],
    historyIndex: -1,
    isAutoCheck: true,
    isHighlightSame: true,
    isShowTimer: true
};

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    initializeGrid();
    attachEventListeners();
    loadPreferences();
});

// Create the Sudoku grid
function initializeGrid() {
    const grid = document.getElementById('sudokuGrid');
    grid.innerHTML = '';

    for (let i = 0; i < 81; i++) {
        const cell = document.createElement('div');
        cell.classList.add('cell');
        cell.dataset.index = i;
        cell.addEventListener('click', () => selectCell(i));
        grid.appendChild(cell);
    }
}

// Attach event listeners
function attachEventListeners() {
    // Difficulty buttons
    document.querySelectorAll('.diff-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            GameState.difficulty = e.target.dataset.difficulty;
            document.getElementById('currentDifficulty').textContent =
                GameState.difficulty.charAt(0).toUpperCase() + GameState.difficulty.slice(1);
        });
    });

    // Action buttons
    document.getElementById('generateBtn').addEventListener('click', generatePuzzle);
    document.getElementById('solveBtn').addEventListener('click', solvePuzzle);
    document.getElementById('hintBtn').addEventListener('click', getHint);
    document.getElementById('checkBtn').addEventListener('click', checkProgress);
    document.getElementById('undoBtn').addEventListener('click', undo);
    document.getElementById('redoBtn').addEventListener('click', redo);
    document.getElementById('clearBtn').addEventListener('click', clearUserInputs);

    // Number pad
    document.querySelectorAll('.num-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (GameState.selectedCell !== null) {
                const num = parseInt(btn.dataset.num);
                placeNumber(num);
            }
        });
    });

    // Keyboard input
    document.addEventListener('keydown', handleKeyPress);

    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Preferences
    document.getElementById('autoCheckErrors').addEventListener('change', (e) => {
        GameState.isAutoCheck = e.target.checked;
        savePreferences();
    });

    document.getElementById('highlightSame').addEventListener('change', (e) => {
        GameState.isHighlightSame = e.target.checked;
        savePreferences();
        updateGridDisplay();
    });

    document.getElementById('showTimer').addEventListener('change', (e) => {
        GameState.isShowTimer = e.target.checked;
        savePreferences();
        document.querySelector('.stat-item:first-child').style.display =
            e.target.checked ? 'flex' : 'none';
    });

    // Modal buttons
    document.getElementById('newGameBtn').addEventListener('click', () => {
        closeModal();
        generatePuzzle();
    });

    document.getElementById('closeModalBtn').addEventListener('click', closeModal);
}

// Generate a new puzzle
async function generatePuzzle() {
    showLoading(true);
    resetGame();

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ difficulty: GameState.difficulty })
        });

        const data = await response.json();

        if (data.success) {
            GameState.puzzle = data.puzzle;
            GameState.solution = data.solution;
            GameState.current = JSON.parse(JSON.stringify(data.puzzle));
            GameState.initialGrid = JSON.parse(JSON.stringify(data.puzzle));
            updateGridDisplay();
            startTimer();
            addToHistory();
        } else {
            showError('Failed to generate puzzle: ' + data.error);
        }
    } catch (error) {
        showError('Error generating puzzle: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Solve the current puzzle
async function solvePuzzle() {
    if (!GameState.current) {
        showError('No puzzle to solve!');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ puzzle: GameState.puzzle })
        });

        const data = await response.json();

        if (data.success) {
            // Animate the solution
            animateSolution(data.solution);
        } else {
            showError('Failed to solve: ' + data.error);
            showLoading(false);
        }
    } catch (error) {
        showError('Error solving puzzle: ' + error.message);
        showLoading(false);
    }
}

// Animate the solution cell by cell
async function animateSolution(solution) {
    const cells = document.querySelectorAll('.cell');

    for (let i = 0; i < 81; i++) {
        const row = Math.floor(i / 9);
        const col = i % 9;

        if (GameState.initialGrid[row][col] === 0) {
            await new Promise(resolve => setTimeout(resolve, 30));
            GameState.current[row][col] = solution[row][col];
            cells[i].textContent = solution[row][col];
            cells[i].classList.add('solved');
        }
    }

    showLoading(false);
    setTimeout(() => {
        checkWin();
    }, 500);
}

// Get a hint
async function getHint() {
    if (!GameState.puzzle || !GameState.solution) {
        showError('No puzzle loaded!');
        return;
    }

    if (GameState.hints <= 0) {
        showError('No hints left!');
        return;
    }

    try {
        const response = await fetch('/api/hint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                puzzle: GameState.solution,
                current: GameState.current
            })
        });

        const data = await response.json();

        if (data.success) {
            const index = data.row * 9 + data.col;
            GameState.current[data.row][data.col] = data.value;
            GameState.hints--;

            updateHintsDisplay();
            selectCell(index);

            const cells = document.querySelectorAll('.cell');
            cells[index].textContent = data.value;
            cells[index].classList.add('hint');

            setTimeout(() => {
                cells[index].classList.remove('hint');
            }, 1000);

            addToHistory();
            checkWin();
        } else {
            showError(data.error || 'No hints available');
        }
    } catch (error) {
        showError('Error getting hint: ' + error.message);
    }
}

// Check progress and highlight errors
async function checkProgress() {
    if (!GameState.current) {
        showError('No puzzle to check!');
        return;
    }

    try {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: GameState.current })
        });

        const data = await response.json();

        if (data.success) {
            const cells = document.querySelectorAll('.cell');
            cells.forEach(cell => cell.classList.remove('error'));

            if (data.valid) {
                showSuccess('No errors found!');
            } else {
                data.errors.forEach(error => {
                    const index = error.row * 9 + error.col;
                    cells[index].classList.add('error');
                });
                showError(`Found ${data.errors.length} error(s)!`);
            }
        }
    } catch (error) {
        showError('Error checking progress: ' + error.message);
    }
}

// Place a number in the selected cell
function placeNumber(num) {
    if (GameState.selectedCell === null || !GameState.current) return;

    const row = Math.floor(GameState.selectedCell / 9);
    const col = GameState.selectedCell % 9;

    // Don't allow changing initial cells
    if (GameState.initialGrid && GameState.initialGrid[row][col] !== 0) return;

    GameState.current[row][col] = num;
    updateGridDisplay();
    addToHistory();

    if (GameState.isAutoCheck && num !== 0) {
        checkCell(row, col);
    }

    if (num !== 0) {
        checkWin();
    }
}

// Check if a specific cell has an error
function checkCell(row, col) {
    const value = GameState.current[row][col];
    if (value === 0) return;

    const cells = document.querySelectorAll('.cell');
    const index = row * 9 + col;

    // Check if the value matches the solution
    if (GameState.solution && GameState.solution[row][col] !== value) {
        cells[index].classList.add('error');
        GameState.mistakes++;
        updateMistakesDisplay();
    } else {
        cells[index].classList.remove('error');
    }
}

// Select a cell
function selectCell(index) {
    GameState.selectedCell = index;
    updateGridDisplay();
}

// Update the grid display
function updateGridDisplay() {
    if (!GameState.current) return;

    const cells = document.querySelectorAll('.cell');
    cells.forEach((cell, index) => {
        const row = Math.floor(index / 9);
        const col = index % 9;
        const value = GameState.current[row][col];

        cell.textContent = value !== 0 ? value : '';
        cell.classList.remove('fixed', 'selected', 'highlighted');

        // Mark fixed cells
        if (GameState.initialGrid && GameState.initialGrid[row][col] !== 0) {
            cell.classList.add('fixed');
        }

        // Highlight selected cell
        if (index === GameState.selectedCell) {
            cell.classList.add('selected');
        }

        // Highlight same numbers
        if (GameState.isHighlightSame && value !== 0 &&
            GameState.selectedCell !== null) {
            const selectedValue = GameState.current[
                Math.floor(GameState.selectedCell / 9)
            ][GameState.selectedCell % 9];

            if (value === selectedValue) {
                cell.classList.add('highlighted');
            }
        }
    });
}

// History management
function addToHistory() {
    if (!GameState.current) return;

    // Remove future history if we're not at the end
    GameState.history = GameState.history.slice(0, GameState.historyIndex + 1);

    // Add current state
    GameState.history.push(JSON.parse(JSON.stringify(GameState.current)));
    GameState.historyIndex++;

    // Limit history size
    if (GameState.history.length > 50) {
        GameState.history.shift();
        GameState.historyIndex--;
    }

    updateUndoRedoButtons();
}

function undo() {
    if (GameState.historyIndex > 0) {
        GameState.historyIndex--;
        GameState.current = JSON.parse(JSON.stringify(GameState.history[GameState.historyIndex]));
        updateGridDisplay();
        updateUndoRedoButtons();
    }
}

function redo() {
    if (GameState.historyIndex < GameState.history.length - 1) {
        GameState.historyIndex++;
        GameState.current = JSON.parse(JSON.stringify(GameState.history[GameState.historyIndex]));
        updateGridDisplay();
        updateUndoRedoButtons();
    }
}

function updateUndoRedoButtons() {
    document.getElementById('undoBtn').disabled = GameState.historyIndex <= 0;
    document.getElementById('redoBtn').disabled =
        GameState.historyIndex >= GameState.history.length - 1;
}

// Clear user inputs (keep initial puzzle)
function clearUserInputs() {
    if (!GameState.initialGrid) return;

    if (confirm('Clear all your inputs?')) {
        GameState.current = JSON.parse(JSON.stringify(GameState.initialGrid));
        GameState.mistakes = 0;
        updateGridDisplay();
        updateMistakesDisplay();
        addToHistory();
    }
}

// Timer functions
function startTimer() {
    stopTimer();
    GameState.timer = 0;
    GameState.timerInterval = setInterval(() => {
        GameState.timer++;
        updateTimerDisplay();
    }, 1000);
}

function stopTimer() {
    if (GameState.timerInterval) {
        clearInterval(GameState.timerInterval);
        GameState.timerInterval = null;
    }
}

function updateTimerDisplay() {
    const minutes = Math.floor(GameState.timer / 60);
    const seconds = GameState.timer % 60;
    document.getElementById('timer').textContent =
        `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateHintsDisplay() {
    document.getElementById('hintsLeft').textContent = GameState.hints;
}

function updateMistakesDisplay() {
    document.getElementById('mistakes').textContent = GameState.mistakes;
}

// Check if puzzle is solved
function checkWin() {
    if (!GameState.current || !GameState.solution) return;

    // Check if all cells are filled
    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            if (GameState.current[r][c] === 0) return;
            if (GameState.current[r][c] !== GameState.solution[r][c]) return;
        }
    }

    // Puzzle solved!
    stopTimer();
    showWinModal();
}

// Show win modal
function showWinModal() {
    const modal = document.getElementById('winModal');
    const minutes = Math.floor(GameState.timer / 60);
    const seconds = GameState.timer % 60;

    document.getElementById('winTime').textContent =
        `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('winMistakes').textContent = GameState.mistakes;
    document.getElementById('winHints').textContent = 3 - GameState.hints;

    modal.classList.add('active');
}

function closeModal() {
    document.getElementById('winModal').classList.remove('active');
}

// Reset game state
function resetGame() {
    stopTimer();
    GameState.puzzle = null;
    GameState.solution = null;
    GameState.current = null;
    GameState.initialGrid = null;
    GameState.selectedCell = null;
    GameState.timer = 0;
    GameState.hints = 3;
    GameState.mistakes = 0;
    GameState.history = [];
    GameState.historyIndex = -1;

    updateTimerDisplay();
    updateHintsDisplay();
    updateMistakesDisplay();
    updateUndoRedoButtons();

    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.textContent = '';
        cell.className = 'cell';
    });
}

// Keyboard handler
function handleKeyPress(e) {
    if (GameState.selectedCell === null) return;

    if (e.key >= '1' && e.key <= '9') {
        placeNumber(parseInt(e.key));
    } else if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') {
        placeNumber(0);
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown' ||
               e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        e.preventDefault();
        navigateCell(e.key);
    }
}

// Navigate between cells with arrow keys
function navigateCell(key) {
    let row = Math.floor(GameState.selectedCell / 9);
    let col = GameState.selectedCell % 9;

    switch (key) {
        case 'ArrowUp': row = Math.max(0, row - 1); break;
        case 'ArrowDown': row = Math.min(8, row + 1); break;
        case 'ArrowLeft': col = Math.max(0, col - 1); break;
        case 'ArrowRight': col = Math.min(8, col + 1); break;
    }

    selectCell(row * 9 + col);
}

// Theme toggle
function toggleTheme() {
    document.body.classList.toggle('light-theme');
    const icon = document.querySelector('#themeToggle i');

    if (document.body.classList.contains('light-theme')) {
        icon.className = 'fas fa-sun';
        localStorage.setItem('theme', 'light');
    } else {
        icon.className = 'fas fa-moon';
        localStorage.setItem('theme', 'dark');
    }
}

// Save and load preferences
function savePreferences() {
    localStorage.setItem('autoCheck', GameState.isAutoCheck);
    localStorage.setItem('highlightSame', GameState.isHighlightSame);
    localStorage.setItem('showTimer', GameState.isShowTimer);
}

function loadPreferences() {
    // Load theme
    const theme = localStorage.getItem('theme');
    if (theme === 'light') {
        document.body.classList.add('light-theme');
        document.querySelector('#themeToggle i').className = 'fas fa-sun';
    }

    // Load preferences
    const autoCheck = localStorage.getItem('autoCheck');
    const highlightSame = localStorage.getItem('highlightSame');
    const showTimer = localStorage.getItem('showTimer');

    if (autoCheck !== null) {
        GameState.isAutoCheck = autoCheck === 'true';
        document.getElementById('autoCheckErrors').checked = GameState.isAutoCheck;
    }

    if (highlightSame !== null) {
        GameState.isHighlightSame = highlightSame === 'true';
        document.getElementById('highlightSame').checked = GameState.isHighlightSame;
    }

    if (showTimer !== null) {
        GameState.isShowTimer = showTimer === 'true';
        document.getElementById('showTimer').checked = GameState.isShowTimer;
        document.querySelector('.stat-item:first-child').style.display =
            GameState.isShowTimer ? 'flex' : 'none';
    }
}

// UI helpers
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert(message);
}
