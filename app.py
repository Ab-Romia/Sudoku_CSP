from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from Board import Sudoku, cell_to_index, index_to_cell
import random
import copy

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_puzzle():
    """Generate a new Sudoku puzzle"""
    try:
        data = request.get_json()
        difficulty = data.get('difficulty', 'medium')

        sudoku = Sudoku()
        sudoku.neighbors_arcs()

        # Generate a complete solution first
        solution_grid = generate_complete_solution()

        # Remove numbers based on difficulty
        puzzle_grid = create_puzzle_from_solution(solution_grid, difficulty)

        return jsonify({
            'success': True,
            'puzzle': puzzle_grid,
            'solution': solution_grid
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/solve', methods=['POST'])
def solve_puzzle():
    """Solve a given Sudoku puzzle"""
    try:
        data = request.get_json()
        puzzle = data.get('puzzle')

        if not puzzle:
            return jsonify({
                'success': False,
                'error': 'No puzzle provided'
            }), 400

        sudoku = Sudoku()
        sudoku.neighbors_arcs()
        sudoku.load_initial_grid(puzzle)

        # Try to solve
        if sudoku.backtrack_solve():
            solution = sudoku.get_assignment()
            return jsonify({
                'success': True,
                'solution': solution
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No solution found'
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate_puzzle():
    """Validate a Sudoku board"""
    try:
        data = request.get_json()
        board = data.get('board')

        if not board:
            return jsonify({
                'success': False,
                'error': 'No board provided'
            }), 400

        is_valid, errors = validate_board(board)

        return jsonify({
            'success': True,
            'valid': is_valid,
            'errors': errors
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hint', methods=['POST'])
def get_hint():
    """Get a hint for the current puzzle"""
    try:
        data = request.get_json()
        puzzle = data.get('puzzle')
        current = data.get('current')

        if not puzzle or not current:
            return jsonify({
                'success': False,
                'error': 'Missing data'
            }), 400

        # Find an empty cell and provide the correct value
        for r in range(9):
            for c in range(9):
                if current[r][c] == 0:
                    return jsonify({
                        'success': True,
                        'row': r,
                        'col': c,
                        'value': puzzle[r][c]
                    })

        return jsonify({
            'success': False,
            'error': 'No empty cells'
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_complete_solution():
    """Generate a complete valid Sudoku solution"""
    sudoku = Sudoku()
    sudoku.neighbors_arcs()

    # Fill diagonal 3x3 boxes first (they don't affect each other)
    for box in range(3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        idx = 0
        for r in range(box * 3, box * 3 + 3):
            for c in range(box * 3, box * 3 + 3):
                sudoku.grid[r][c] = nums[idx]
                var = cell_to_index(r, c)
                sudoku.domains[var] = [nums[idx]]
                idx += 1

    # Solve the rest using backtracking
    sudoku.backtrack_solve()
    return sudoku.get_assignment()

def create_puzzle_from_solution(solution, difficulty):
    """Create a puzzle by removing numbers from a solution"""
    puzzle = [row[:] for row in solution]

    # Difficulty settings: number of cells to keep filled
    cells_to_keep = {
        'easy': 45,
        'medium': 35,
        'hard': 25,
        'expert': 20
    }

    keep_count = cells_to_keep.get(difficulty, 35)

    # Get all cell positions
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    # Remove numbers while ensuring unique solution
    cells_filled = 81
    for r, c in positions:
        if cells_filled <= keep_count:
            break

        temp = puzzle[r][c]
        puzzle[r][c] = 0

        # Verify puzzle still has unique solution
        sudoku = Sudoku()
        sudoku.neighbors_arcs()
        sudoku.load_initial_grid(puzzle)

        if sudoku.backtrack_solve():
            cells_filled -= 1
        else:
            puzzle[r][c] = temp

    return puzzle

def validate_board(board):
    """Validate a Sudoku board and return errors"""
    errors = []

    # Check rows
    for r in range(9):
        seen = {}
        for c in range(9):
            val = board[r][c]
            if val != 0:
                if val in seen:
                    errors.append({
                        'type': 'row',
                        'row': r,
                        'col': c,
                        'value': val,
                        'conflict': seen[val]
                    })
                seen[val] = {'row': r, 'col': c}

    # Check columns
    for c in range(9):
        seen = {}
        for r in range(9):
            val = board[r][c]
            if val != 0:
                if val in seen:
                    errors.append({
                        'type': 'col',
                        'row': r,
                        'col': c,
                        'value': val,
                        'conflict': seen[val]
                    })
                seen[val] = {'row': r, 'col': c}

    # Check 3x3 boxes
    for box_r in range(3):
        for box_c in range(3):
            seen = {}
            for r in range(box_r * 3, box_r * 3 + 3):
                for c in range(box_c * 3, box_c * 3 + 3):
                    val = board[r][c]
                    if val != 0:
                        if val in seen:
                            errors.append({
                                'type': 'box',
                                'row': r,
                                'col': c,
                                'value': val,
                                'conflict': seen[val]
                            })
                        seen[val] = {'row': r, 'col': c}

    return (len(errors) == 0, errors)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
