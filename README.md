# Sudoku AI Solver & Generator 🧠

A modern, feature-rich web-based Sudoku solver and generator powered by advanced Constraint Satisfaction Problem (CSP) algorithms.

![Sudoku AI](https://img.shields.io/badge/AI-Powered-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

### 🎮 Gameplay Features
- **Smart Puzzle Generation**: Generate unique Sudoku puzzles with 4 difficulty levels (Easy, Medium, Hard, Expert)
- **AI Solver**: Watch the AI solve puzzles using advanced CSP algorithms
- **Interactive Gameplay**: Click cells or use keyboard input (1-9, arrow keys)
- **Hint System**: Get intelligent hints when stuck (limited to 3 per game)
- **Auto-Check Errors**: Instantly validate your moves
- **Undo/Redo**: Full history tracking with unlimited undo/redo
- **Timer**: Track your solving time
- **Mistake Counter**: Keep track of errors

### 🎨 Design Features
- **Modern UI/UX**: Beautiful gradient-based design with smooth animations
- **Dark/Light Theme**: Toggle between dark and light themes
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Animations**: Smooth transitions, hover effects, and solving animations
- **Number Highlighting**: Automatically highlights same numbers
- **Visual Feedback**: Color-coded cells for fixed, selected, error, and hint states

### 🧠 Algorithm Features
- **Backtracking Search**: Efficient depth-first search algorithm
- **Arc Consistency (AC-3)**: Domain reduction through constraint propagation
- **Forward Checking**: Prune domains before making assignments
- **Minimum Remaining Values (MRV)**: Smart variable ordering heuristic
- **Least Constraining Value (LCV)**: Intelligent value ordering heuristic

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Ab-Romia/Sudoku_CSP.git
cd Sudoku_CSP
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open your browser**
Navigate to: `http://localhost:5000`

## 🎯 How to Use

### Playing the Game
1. Click **"New Puzzle"** to generate a puzzle
2. Select a difficulty level (Easy, Medium, Hard, Expert)
3. Click on any empty cell to select it
4. Enter numbers using:
   - Number pad on screen
   - Keyboard numbers (1-9)
   - Delete/Backspace to erase
5. Use arrow keys to navigate between cells

### Using the AI Solver
1. Load or generate a puzzle
2. Click **"AI Solve"** to watch the algorithm solve it
3. The solver will animate the solution process

### Getting Hints
- Click **"Get Hint"** to reveal one correct number
- You have 3 hints per game

### Other Features
- **Check Progress**: Validate your current solution
- **Undo/Redo**: Navigate through your move history
- **Clear**: Reset the puzzle to initial state
- **Theme Toggle**: Switch between dark and light themes

## 🏗️ Project Structure

```
Sudoku_CSP/
├── app.py                 # Flask backend server
├── Board.py              # CSP solver implementation
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css   # Styles and animations
│   └── js/
│       └── app.js      # Frontend logic
├── GUI.py               # Desktop Tkinter GUI (legacy)
└── README.md
```

## 🔧 API Endpoints

### Generate Puzzle
```http
POST /api/generate
Content-Type: application/json

{
  "difficulty": "medium"
}
```

### Solve Puzzle
```http
POST /api/solve
Content-Type: application/json

{
  "puzzle": [[...], ...]
}
```

### Validate Board
```http
POST /api/validate
Content-Type: application/json

{
  "board": [[...], ...]
}
```

### Get Hint
```http
POST /api/hint
Content-Type: application/json

{
  "puzzle": [[...], ...],
  "current": [[...], ...]
}
```

## 🧮 Algorithm Details

### Backtracking with CSP
The solver uses a sophisticated backtracking algorithm enhanced with CSP techniques:

1. **Variable Selection (MRV)**: Selects the cell with the fewest remaining possible values
2. **Value Ordering (LCV)**: Tries values that constrain other cells the least
3. **Arc Consistency**: Reduces domains by propagating constraints
4. **Forward Checking**: Eliminates values that would lead to empty domains

This combination ensures efficient solving even for difficult puzzles.

## 🎨 Customization

### Themes
The application supports custom themes. Toggle between dark and light modes using the theme button in the top-right corner.

### Preferences
Customize your experience with:
- Auto-check errors on/off
- Highlight same numbers on/off
- Show/hide timer

## 🐛 Troubleshooting

### Server won't start
- Ensure Python 3.8+ is installed
- Check if port 5000 is available
- Verify all dependencies are installed

### Puzzle won't generate
- Check your internet connection
- Ensure the backend server is running
- Check browser console for errors

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👨‍💻 Author

Created with ❤️ by the Sudoku CSP Team

## 🙏 Acknowledgments

- CSP algorithms based on Russell & Norvig's "Artificial Intelligence: A Modern Approach"
- UI inspired by modern puzzle game designs
- Icons by Font Awesome

---

**Enjoy solving Sudoku with AI! 🎉**
