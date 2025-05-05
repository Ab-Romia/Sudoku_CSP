# GUI.py (Modified)

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import random
from Board import Sudoku, cell_to_index, index_to_cell # Import your Sudoku logic
import sys # Import sys to check stdout

# --- Constants ---
GRID_SIZE = 9
CELL_SIZE = 40
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
LOG_HEIGHT = 10 # Initial number of lines for the log area
MIN_WINDOW_WIDTH = GRID_WIDTH + 50
MIN_WINDOW_HEIGHT = GRID_HEIGHT + 150 + LOG_HEIGHT * 10 # Adjust minimum height as needed

# Colors for visualization
COLOR_BG = "#F0F0F0"
COLOR_GRID = "#ABB2B9"
COLOR_CELL_FIXED = "#E8E8E8" # Clues or user input
COLOR_CELL_EMPTY = "white"
COLOR_CELL_SOLVED = "#D5F5E3" # Solved cells by agent
COLOR_CELL_TRYING = "#FDEDEC" # Cell currently being tested by backtracking
COLOR_CELL_CONFLICT = "#FADBD8" # Used for input validation conflicts

# --- GUI Class ---
class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver CSP")
        # Initial size, but now resizable
        self.root.geometry(f"{MIN_WINDOW_WIDTH}x{MIN_WINDOW_HEIGHT}")
        # Make window resizable
        self.root.resizable(True, True)
        # Set minimum size
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)


        # --- Sudoku Board Instance ---
        self.sudoku_board = Sudoku()
        self.sudoku_board.neighbors_arcs() # Initialize neighbors and arcs once

        # --- State Variables ---
        self.solving_in_progress = False
        self.current_mode = tk.StringVar(value="generate") # 'generate' or 'input'
        self.difficulty = tk.StringVar(value="medium")
        self.revision_count = 0
        self.prune_count = 0

        # --- GUI Elements ---
        self.entries = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        # Main frame to hold controls and grid (pack vertically)
        top_frame = ttk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.control_frame = ttk.Frame(top_frame, padding="10")
        self.grid_frame = tk.Frame(top_frame, bd=2, relief=tk.SUNKEN)

        # Frame for the log area (will expand)
        self.log_frame = ttk.Frame(root, padding=(10, 0, 10, 10)) # Add padding
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True) # Fill and expand

        self.log_area = None # Will be created later

        # --- Styling ---
        style = ttk.Style()
        style.configure("TButton", padding=5, font=('Helvetica', 10))
        style.configure("TRadiobutton", padding=5, font=('Helvetica', 10))
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TFrame", background=COLOR_BG)
        self.root.configure(bg=COLOR_BG)

        # --- Setup Layout ---
        self.setup_controls()
        self.setup_grid()
        self.setup_log_area() # Log area setup adjusted for expansion

        # Pack controls and grid into the top frame
        self.control_frame.pack(pady=5)
        self.grid_frame.pack(pady=5)


        # --- Initial State ---
        self.update_mode() # Set initial mode controls

    def setup_controls(self):
        # Controls setup remains the same, using grid within control_frame
        ttk.Label(self.control_frame, text="Mode:").grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Radiobutton(self.control_frame, text="Generate Puzzle", variable=self.current_mode, value="generate", command=self.update_mode).grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Radiobutton(self.control_frame, text="User Input", variable=self.current_mode, value="input", command=self.update_mode).grid(row=0, column=2, padx=5, sticky=tk.W)

        self.difficulty_label = ttk.Label(self.control_frame, text="Difficulty:")
        self.difficulty_menu = ttk.OptionMenu(self.control_frame, self.difficulty, "medium", "easy", "medium", "hard")
        self.difficulty_label.grid(row=1, column=0, padx=5, sticky=tk.W)
        self.difficulty_menu.grid(row=1, column=1, padx=5, sticky=tk.W)

        self.generate_button = ttk.Button(self.control_frame, text="Generate", command=self.generate_puzzle_gui)
        self.load_button = ttk.Button(self.control_frame, text="Load User Grid", command=self.load_user_input_gui)
        self.solve_button = ttk.Button(self.control_frame, text="Solve", command=self.solve_puzzle_gui, state=tk.DISABLED)
        self.clear_button = ttk.Button(self.control_frame, text="Clear", command=self.clear_grid_gui)

        self.generate_button.grid(row=1, column=2, padx=5, sticky=tk.W+tk.E)
        self.load_button.grid(row=1, column=2, padx=5, sticky=tk.W+tk.E)
        self.solve_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        self.clear_button.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W+tk.E)

    def setup_grid(self):
        # Grid setup remains the same, using grid within grid_frame
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                entry = tk.Entry(self.grid_frame, width=2, font=('Helvetica', 18, 'bold'),
                                 justify='center', bd=1, relief=tk.SOLID,
                                 disabledbackground=COLOR_CELL_FIXED,
                                 bg=COLOR_CELL_EMPTY)

                padx = (5, 0) if c % 3 == 0 and c != 0 else (1, 0)
                pady = (5, 0) if r % 3 == 0 and r != 0 else (1, 0)

                entry.grid(row=r, column=c, sticky="nsew", padx=padx, pady=pady)
                self.entries[r][c] = entry

        for i in range(GRID_SIZE):
            self.grid_frame.grid_rowconfigure(i, weight=1, minsize=CELL_SIZE)
            self.grid_frame.grid_columnconfigure(i, weight=1, minsize=CELL_SIZE)

    def setup_log_area(self):
        # Log area setup adjusted to fill and expand within its frame
        ttk.Label(self.log_frame, text="Solver Log:").pack(anchor=tk.W)
        self.log_area = scrolledtext.ScrolledText(self.log_frame, height=LOG_HEIGHT, wrap=tk.WORD, state=tk.DISABLED,
                                                  font=('Courier New', 9))
        # Make the ScrolledText widget expand within the log_frame
        self.log_area.pack(fill=tk.BOTH, expand=True)

    # --- GUI Update and Interaction ---

    def update_mode(self):
        """Configures GUI elements based on the selected mode."""
        mode = self.current_mode.get()
        # Avoid clearing if just switching modes without action
        # self.clear_grid_gui() # Maybe don't clear automatically here

        if mode == "generate":
            self.difficulty_label.grid()
            self.difficulty_menu.grid()
            self.generate_button.grid()
            self.load_button.grid_remove()
            # Check if grid has content before disabling solve
            grid_empty = all(not self.entries[r][c].get() for r in range(GRID_SIZE) for c in range(GRID_SIZE))
            self.solve_button.config(state=tk.DISABLED if grid_empty else tk.NORMAL)
            # Decide editability based on whether a puzzle is *loaded*
            self.set_grid_editable(grid_empty) # Editable only if empty

        else: # mode == "input"
            self.difficulty_label.grid()
            self.difficulty_menu.grid()
            self.generate_button.grid()
            self.generate_button.config(state=tk.NORMAL)

            self.load_button.grid()
            self.load_button.config(state=tk.NORMAL)
            self.set_grid_editable(True) # Allow input
            self.solve_button.config(state=tk.DISABLED) # Disable solve until loaded


    def set_grid_editable(self, editable):
        """Enable or disable all grid entries."""
        state = tk.NORMAL if editable else tk.DISABLED
        # Don't change background based on editability alone, use value/fixed status
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.entries[r][c]:
                   # Only change state, background managed by update_gui_cell
                   self.entries[r][c].config(state=state)


    def log(self, message):
        """Appends a message to the GUI log area AND prints to console."""
        # 1. Print to console
        # Check if stdout is valid (e.g., when running with pythonw.exe it might not be)
        if sys.stdout:
            try:
                 print(message, flush=True) # flush ensures it appears immediately
            except Exception:
                pass # Ignore print errors if console is unavailable

        # 2. Update GUI log area
        if self.log_area and self.log_area.winfo_exists(): # Check if widget exists
            try:
                self.log_area.config(state=tk.NORMAL)
                self.log_area.insert(tk.END, message + "\n")
                self.log_area.see(tk.END) # Scroll to the end
                self.log_area.config(state=tk.DISABLED)
                # Use update_idletasks for responsiveness without forced redraw
                if self.root.winfo_exists():
                    self.root.update_idletasks()
            except tk.TclError:
                 # Handle case where the widget might be destroyed during shutdown
                 pass


    def update_gui_cell(self, row, col, value, color=None, is_fixed=False, delay=0.01):
        """Updates a single cell in the GUI grid."""
        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE): return
        entry = self.entries[row][col]
        if not entry or not entry.winfo_exists(): return # Check if entry exists

        original_state = entry.cget('state')
        entry.config(state=tk.NORMAL)
        entry.delete(0, tk.END)
        bg_color = color if color else (COLOR_CELL_FIXED if is_fixed else (COLOR_CELL_SOLVED if value != 0 else COLOR_CELL_EMPTY))
        fg_color = 'black' # Default text color

        if value != 0:
            entry.insert(0, str(value))

        # Set background and potentially foreground (if needed)
        entry.config(bg=bg_color, fg=fg_color)

        # Determine final state
        final_state = tk.DISABLED if is_fixed or (value != 0 and not color == COLOR_CELL_TRYING) else tk.NORMAL
        # If it was trying, keep it normal temporarily, backtrack will reset state
        if color == COLOR_CELL_TRYING:
             final_state = tk.NORMAL

        # Apply final state and ensure disabledbackground matches bg
        entry.config(state=final_state, disabledbackground=bg_color)


        if delay > 0 and self.solving_in_progress: # Only delay during active solving
             if self.root.winfo_exists():
                self.root.update() # Force redraw only if delaying
                time.sleep(delay)


    def update_gui_board_from_logic(self, board_grid, fixed_mask=None, solved_color=COLOR_CELL_SOLVED):
        """Updates the entire GUI grid based on a 2D list."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if not self.entries[r][c].winfo_exists(): continue # Skip if destroyed
                value = board_grid[r][c]
                # Determine if fixed: use mask if provided, else assume initial non-zero are fixed
                is_fixed = bool(fixed_mask and fixed_mask[r][c]) if fixed_mask is not None else (value != 0)
                # Determine color based on fixed status or solved status
                color = COLOR_CELL_FIXED if is_fixed else (solved_color if value != 0 else COLOR_CELL_EMPTY)
                self.update_gui_cell(r, c, value, color=color, is_fixed=is_fixed, delay=0) # No delay for full update


    def clear_grid_gui(self):
        """Clears the GUI grid and resets the solver."""
        self.log("Clearing grid...")
        self.sudoku_board = Sudoku() # Re-initialize the board logic
        self.sudoku_board.neighbors_arcs()

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.entries[r][c] and self.entries[r][c].winfo_exists():
                    entry = self.entries[r][c]
                    entry.config(state=tk.NORMAL, bg=COLOR_CELL_EMPTY)
                    entry.delete(0, tk.END)

        if self.log_area and self.log_area.winfo_exists():
            self.log_area.config(state=tk.NORMAL)
            self.log_area.delete('1.0', tk.END)
            self.log_area.config(state=tk.DISABLED)

        self.solve_button.config(state=tk.DISABLED)
        self.solving_in_progress = False
        self.prune_count = 0
        self.revision_count = 0

        # Reset grid editability based on current mode
        mode = self.current_mode.get()
        self.set_grid_editable(mode == "input")
        self.log("Grid cleared.")


    def generate_puzzle_gui(self):
        """Generates a puzzle and displays it."""
        if self.solving_in_progress: return
        self.clear_grid_gui() # Clear first
        diff = self.difficulty.get()
        self.log(f"Generating '{diff}' puzzle... (This may take a while due to validation)")

        # Disable buttons during generation
        self.generate_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.root.update() # Show disabled state

        try:
            start_gen_time = time.time()
            # Use a temporary board for generation to keep main board clean until loaded
            temp_board = Sudoku()
            temp_board.neighbors_arcs()
            generated_grid = temp_board.generate_puzzle(difficulty=diff) # This is the slow part
            gen_duration = time.time() - start_gen_time
            self.log(f"Generation logic finished in {gen_duration:.2f} seconds.")

            # Load the generated grid into our main board instance
            self.sudoku_board.load_initial_grid(generated_grid)

            # Create a mask of fixed cells (the clues)
            fixed_mask = [[(cell != 0) for cell in row] for row in generated_grid]

            self.update_gui_board_from_logic(generated_grid, fixed_mask=fixed_mask)
            self.log("Puzzle generated and loaded. Ready to solve.")
            self.solve_button.config(state=tk.NORMAL)
            self.set_grid_editable(False) # Make grid read-only after generation

        except Exception as e:
            messagebox.showerror("Generation Error", f"Failed to generate puzzle: {e}")
            self.log(f"Error during generation: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.clear_grid_gui() # Clear if generation failed
        finally:
             # Re-enable buttons
             self.generate_button.config(state=tk.NORMAL)
             # Load button state depends on mode, update_mode handles it
             self.clear_button.config(state=tk.NORMAL)
             self.update_mode() # Refresh button states based on mode


    def load_user_input_gui(self):
        """Loads the puzzle entered by the user."""
        if self.solving_in_progress: return
        self.log("Loading user input...")
        user_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        fixed_mask = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        input_valid = True

        try:
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if not self.entries[r][c].winfo_exists(): continue
                    val_str = self.entries[r][c].get().strip()
                    if val_str:
                        if not val_str.isdigit() or not 1 <= int(val_str) <= 9:
                            self.update_gui_cell(r, c, val_str, color=COLOR_CELL_CONFLICT) # Show invalid input visually
                            messagebox.showerror("Input Error", f"Invalid input at ({r+1},{c+1}): '{val_str}'. Use numbers 1-9 or leave blank.")
                            self.log(f"Input Error: Invalid character '{val_str}' at ({r+1},{c+1}).")
                            input_valid = False
                            # Keep loop going to find all errors, but don't load if any exist
                            continue # Skip processing this cell further

                        value = int(val_str)
                        user_grid[r][c] = value
                        fixed_mask[r][c] = True # Mark user input as fixed
                    else:
                        user_grid[r][c] = 0

            if not input_valid:
                 self.solve_button.config(state=tk.DISABLED)
                 return # Stop if any input was invalid


            # --- Input seems syntactically valid, now load and check consistency ---
            self.log("Input syntax valid. Checking initial consistency...")
            # Reset and load the board logic
            self.sudoku_board = Sudoku()
            self.sudoku_board.neighbors_arcs()
            self.sudoku_board.load_initial_grid(user_grid)

            # Validate the initial user grid for obvious conflicts before solving
            initial_conflicts = False
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                     if user_grid[r][c] != 0:
                         idx = cell_to_index(r,c)
                         # Check against other *initial* values
                         temp_val = user_grid[r][c]
                         user_grid[r][c] = 0 # Temporarily remove to check against others
                         if not self.sudoku_board.is_valid_assignment(idx, temp_val):
                             user_grid[r][c] = temp_val # Put it back
                             self.update_gui_cell(r, c, temp_val, color=COLOR_CELL_CONFLICT, is_fixed=True)
                             self.log(f"Error: Initial conflict detected for value {temp_val} at ({r+1},{c+1}).")
                             initial_conflicts = True
                         else:
                             user_grid[r][c] = temp_val # Put it back
                             # Update cell to fixed color if no conflict
                             self.update_gui_cell(r, c, temp_val, color=COLOR_CELL_FIXED, is_fixed=True)


            if initial_conflicts:
                 messagebox.showerror("Invalid Input", f"Conflicts detected in the initial grid (marked red). Please correct.")
                 self.solve_button.config(state=tk.DISABLED)
                 self.set_grid_editable(True) # Allow user to fix errors
                 return


            # --- Grid loaded and seems consistent ---
            # Update GUI board with fixed colors (already done partially above)
            # self.update_gui_board_from_logic(user_grid, fixed_mask=fixed_mask)
            self.set_grid_editable(False) # Lock grid after successful load
            self.solve_button.config(state=tk.NORMAL)
            self.log("User grid loaded successfully and seems consistent. Ready to solve.")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during loading: {e}")
            self.log(f"Error: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.solve_button.config(state=tk.DISABLED)


    # --- Solving Logic with Visualization Callbacks ---

    def solve_puzzle_gui(self):
        """Initiates the solving process with visualization."""
        if self.solving_in_progress: return
        if not self.sudoku_board or self.sudoku_board.is_solved(): # Check if already solved or no board
            if self.sudoku_board and self.sudoku_board.is_solved():
                 self.log("Puzzle is already solved.")
            else:
                 messagebox.showerror("Error", "No puzzle loaded or generated, or puzzle already solved.")
                 self.log("Solver not started: No loaded puzzle or already solved.")
            return

        self.solving_in_progress = True
        # Disable relevant controls
        self.solve_button.config(state=tk.DISABLED)
        self.generate_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        if self.difficulty_menu: self.difficulty_menu.config(state=tk.DISABLED)
        # Disable mode switches more robustly
        for widget in self.control_frame.winfo_children():
             if isinstance(widget, (ttk.Radiobutton, ttk.OptionMenu)):
                  widget.config(state=tk.DISABLED)
        self.root.update() # Ensure UI reflects disabled state

        self.log("\n--- Starting Solver ---")
        self.revision_count = 0
        self.prune_count = 0 # Reset counters

        # --- Define Callbacks for Visualization/Logging ---
        def gui_update_callback(action, variable, value=None, color=None):
            """Callback to update the GUI during solving."""
            if variable is None: return
            row, col = index_to_cell(variable)
            if action == "assign":
                # Use a distinct color for trying, keep cell editable temporarily
                self.update_gui_cell(row, col, value, color=COLOR_CELL_TRYING, is_fixed=False, delay=0.02)
            elif action == "backtrack":
                # Revert cell appearance, make it editable again
                 self.update_gui_cell(row, col, 0, color=COLOR_CELL_EMPTY, is_fixed=False, delay=0.01)
            elif action == "singleton":
                 # Final assignment by AC or backtracking success, make it look solved/fixed
                 self.update_gui_cell(row, col, value, color=COLOR_CELL_SOLVED, is_fixed=True, delay=0.01)
                 self.log(f"* Singleton Assigned: Cell ({row+1},{col+1}) = {value}")


        def log_callback(message_type, **kwargs):
            """Callback for logging solver actions."""
            if message_type == "revise":
                self.revision_count += 1
                Xi, Xj, old_domain_Xi, removed_value, new_domain_Xi = kwargs['Xi'], kwargs['Xj'], kwargs['old_domain_Xi'], kwargs['removed_value'], kwargs['new_domain_Xi']
                self.prune_count += 1
                r1,c1 = index_to_cell(Xi)
                r2,c2 = index_to_cell(Xj)
                log_msg = (f"Arc Revised: (X{Xi}[{r1+1},{c1+1}], X{Xj}[{r2+1},{c2+1}])\n"
                           f"  Domain X{Xi} Before: {old_domain_Xi}\n"
                           f"  Removed '{removed_value}' from X{Xi} due to X{Xj}\n"
                           f"  Domain X{Xi} After:  {new_domain_Xi}")
                self.log(log_msg)
            elif message_type == "start_revise":
                 Xi, Xj = kwargs['Xi'], kwargs['Xj']
                 r1,c1 = index_to_cell(Xi)
                 r2,c2 = index_to_cell(Xj)
                 # Only log if domains are not singletons already (reduces noise)
                 if len(kwargs['domain_Xi']) > 1:
                     self.log(f"Revising Arc: (X{Xi}[{r1+1},{c1+1}], X{Xj}[{r2+1},{c2+1}]) | Domain X{Xi}: {kwargs['domain_Xi']} | Domain X{Xj}: {kwargs['domain_Xj']}")


        # --- Run Solver Steps ---
        try:
            # 1. Initial Arc Consistency (AC-3)
            self.log("\n--- Running Arc Consistency (AC-3) ---")
            start_time_ac = time.time()
            self.enforce_arc_consistency_visual(log_callback, gui_update_callback)
            ac_duration = time.time() - start_time_ac
            self.log(f"--- Arc Consistency Finished ({ac_duration:.3f}s) ---")

            # Update grid with any singletons found by AC-3
            self.log("Updating grid visually after AC-3...")
            self.update_grid_from_domains_visual(gui_update_callback) # Pass callback to log singletons

            # 2. Check if solved after AC-3
            if self.sudoku_board.is_solved():
                self.log("\n--- Puzzle Solved using Arc Consistency alone! ---")
                self.finalize_solve(success=True)
                return # Stop here

            # 3. Backtracking Search with Forward Checking
            self.log("\n--- Starting Backtracking Search with Forward Checking ---")
            start_time_bt = time.time()
            solved = self.backtrack_solve_visual(gui_update_callback, log_callback)
            bt_duration = time.time() - start_time_bt
            self.log(f"--- Backtracking Finished ({bt_duration:.3f}s) ---")

            self.finalize_solve(success=solved)

        except ValueError as e: # Catch unsolvable puzzles from revise
             messagebox.showerror("Unsolvable", f"The puzzle became inconsistent during solving: {e}")
             self.log(f"Error: Unsolvable - {e}")
             self.finalize_solve(success=False)
        except Exception as e:
            messagebox.showerror("Solver Error", f"An unexpected error occurred during solving: {e}")
            self.log(f"Runtime Error: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.finalize_solve(success=False)


    def finalize_solve(self, success):
         """Cleans up after the solver finishes."""
         # Ensure final grid state reflects the outcome accurately
         final_grid = self.sudoku_board.get_assignment()
         # Determine which cells were originally fixed (clues/user input)
         # Re-read initial fixed state if necessary, or assume loaded board state
         fixed_mask = [[(self.sudoku_board.grid[r][c] != 0 and len(self.sudoku_board.domains[cell_to_index(r,c)])==1 and self.entries[r][c].cget('state') == tk.DISABLED) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
         # A better way might be to store the initial fixed mask when loading/generating

         self.update_gui_board_from_logic(final_grid, fixed_mask=None) # Use default fixed detection for final display


         if success:
             messagebox.showinfo("Success", "Sudoku Solved Successfully!")
             self.log("\n--- Solution Found ---")
         else:
             messagebox.showwarning("Failed", "Could not find a solution for the puzzle.")
             self.log("\n--- Failed to Find Solution ---")

         # Log Summary
         self.log("\n--- Solver Summary ---")
         self.log(f"Total Arc Revisions Attempted: {self.revision_count}")
         self.log(f"Total Domain Values Pruned (in revise/FC): {self.prune_count}")
         self.log("----------------------")


         # Re-enable controls
         self.solving_in_progress = False
         # Re-enable buttons carefully based on mode and state
         self.clear_button.config(state=tk.NORMAL)
         # Solve button should only be enabled if a valid puzzle is loaded/generated but not solved
         is_loaded_or_generated = not all(not self.entries[r][c].get() for r in range(GRID_SIZE) for c in range(GRID_SIZE))
         self.solve_button.config(state=tk.NORMAL if is_loaded_or_generated and not self.sudoku_board.is_solved() else tk.DISABLED)

         # Re-enable mode-specific controls
         mode = self.current_mode.get()
         if mode == 'generate':
              self.generate_button.config(state=tk.NORMAL)
              if self.difficulty_menu: self.difficulty_menu.config(state=tk.NORMAL)
         else: # input mode
              self.load_button.config(state=tk.NORMAL)

         # Re-enable radio buttons
         for widget in self.control_frame.winfo_children():
             if isinstance(widget, (ttk.Radiobutton, ttk.OptionMenu)):
                  widget.config(state=tk.NORMAL)

         # Refresh grid editability based on current mode and if puzzle is solved
         self.set_grid_editable(mode == 'input' and not is_loaded_or_generated) # Editable only in input mode if grid is clear


    # --- Solver Methods Adapted for Visualization/Logging ---
    # (These methods remain largely the same as before, ensure they use the passed callbacks)

    def revise_visual(self, Xi, Xj, log_callback):
        """Adapted revise method to include logging callbacks."""
        revised = False
        domain_Xi = self.sudoku_board.domains[Xi]
        domain_Xj = self.sudoku_board.domains[Xj]

        # Reduce noise: Only log start_revise if Xi has multiple possibilities
        if len(domain_Xi) > 1:
            log_callback("start_revise", Xi=Xi, Xj=Xj, domain_Xi=domain_Xi[:], domain_Xj=domain_Xj[:])

        original_domain_Xi = domain_Xi[:] # Copy for iteration

        values_removed_this_call = []
        for value in original_domain_Xi:
            # For Sudoku's all-different constraint:
            # We need to remove value from Xi's domain if it equals Xj's value
            # and Xj can only be that value (domain size 1)
            if len(domain_Xj) == 1 and value == domain_Xj[0]:
                if value in domain_Xi:  # Check if it wasn't already removed
                    domain_Xi.remove(value)
                    values_removed_this_call.append(value)
                    revised = True

        # Log revision results if any value was actually removed
        if revised:
            log_callback("revise", Xi=Xi, Xj=Xj, old_domain_Xi=original_domain_Xi, 
                        removed_value=values_removed_this_call, new_domain_Xi=domain_Xi)

        return revised

    def enforce_arc_consistency_visual(self, log_callback, gui_callback):
        """
        AC-3: returns True if no domain is wiped out, False otherwise.
        Uses revise_visual for logging.
        """
        from collections import deque
        # build initial queue of all arcs
        queue = deque((Xi, Xj)
                      for Xi in self.sudoku_board.variables
                      for Xj in self.sudoku_board.neighbors[Xi])
        while queue:
            Xi, Xj = queue.popleft()
            # revise_visual returns True if it removed something
            if self.revise_visual(Xi, Xj, log_callback):
                # if Xi’s domain is now empty, failure
                if not self.sudoku_board.domains[Xi]:
                    return False
                # re-enqueue all arcs (Xk -> Xi), except Xj->Xi
                for Xk in self.sudoku_board.neighbors[Xi]:
                    if Xk != Xj:
                        queue.append((Xk, Xi))
        return True

    def update_grid_from_domains_visual(self, gui_callback):
         """Update grid after AC, calling GUI callback for new singletons."""
         self.log("Updating GUI with new singletons found...")
         newly_assigned_count = 0
         for variable in self.sudoku_board.variables:
             if len(self.sudoku_board.domains[variable]) == 1:
                 value = self.sudoku_board.domains[variable][0]
                 row, col = index_to_cell(variable)
                 # Check if it wasn't already set on the GUI grid or internal grid
                 current_gui_val_str = self.entries[row][col].get()
                 is_newly_assigned = True
                 if self.sudoku_board.grid[row][col] == value: # Check internal grid first
                     is_newly_assigned = False
                 elif current_gui_val_str.isdigit() and int(current_gui_val_str) == value:
                      # Also check GUI in case internal grid wasn't updated yet
                      is_newly_assigned = False


                 if is_newly_assigned:
                     gui_callback("singleton", variable, value) # Calls update_gui_cell
                     self.sudoku_board.grid[row][col] = value # Update internal grid state
                     newly_assigned_count += 1

         if newly_assigned_count > 0:
             self.log(f"Applied {newly_assigned_count} new singleton value(s) to the grid.")
         else:
             self.log("No new singletons found to apply from current domains.")


    def forward_check_visual(self, var, value):
        """ Perform forward checking, return inferences for restoration"""
        inferences = {} # Store removals: {neighbor_var: [removed_values]}
        # Iterate through neighbors
        for neighbor in self.sudoku_board.neighbors[var]:
            neighbor_domain = self.sudoku_board.domains[neighbor]
            if value in neighbor_domain:
                # Correct check: Only fail if removing this value would leave domain empty
                if len(neighbor_domain) == 1 and neighbor_domain[0] == value:
                    # This assignment would empty a neighbor's domain - failure
                    return None

                # Record the inference (value to be removed)
                inferences.setdefault(neighbor, []).append(value)

        # Apply the recorded inferences
        for neighbor, values_to_remove in inferences.items():
            neighbor_domain = self.sudoku_board.domains[neighbor]
            for val in values_to_remove:
                if val in neighbor_domain: # Check if still present
                    neighbor_domain.remove(val)
                    self.prune_count += 1 # Count FC prunes

        return inferences # Return the actual removals for restoration

    def backtrack_solve_visual(self, gui_callback, log_callback):
        """Backtracking + full AC-3 propagation at each step."""
        # 1) Check for completion: every domain is size 1
        if all(len(self.sudoku_board.domains[v]) == 1
               for v in self.sudoku_board.variables):
            # fill the grid from domains
            for v in self.sudoku_board.variables:
                r, c = index_to_cell(v)
                self.sudoku_board.grid[r][c] = self.sudoku_board.domains[v][0]
            return True

        # 2) Select next var (MRV)
        var = self.sudoku_board.select_unassigned_variable()
        row, col = index_to_cell(var)

        # snapshot all domains to restore later
        saved_domains = {v: self.sudoku_board.domains[v][:] 
                         for v in self.sudoku_board.variables}

        # 3) Try each value in LCV order (or raw domain)
        for value in self.sudoku_board.order_domain_values(var) or saved_domains[var]:
            if not self.sudoku_board.is_valid_assignment(var, value):
                continue

            # visualize the tentative assign
            gui_callback("assign", var, value)
            # commit to grid & domain
            self.sudoku_board.grid[row][col] = value
            self.sudoku_board.domains[var] = [value]

            # 4) Propagate with AC-3
            if self.enforce_arc_consistency_visual(log_callback, gui_callback):
                # reflect any new singletons in the GUI
                self.update_grid_from_domains_visual(gui_callback)
                # recurse
                if self.backtrack_solve_visual(gui_callback, log_callback):
                    return True

            # 5) Backtrack: restore grid + all domains
            self.sudoku_board.grid[row][col] = 0
            for v in self.sudoku_board.variables:
                self.sudoku_board.domains[v] = saved_domains[v]
            gui_callback("backtrack", var)

        # no value worked
        return False


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()