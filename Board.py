import random


def cell_to_index(row, col):
    return row * 9 + col


def index_to_cell(index):
    return divmod(index, 9)


class Sudoku:
    def __init__(self, grid=None):
        self.variables = list(range(81))
        self.domains = {i: list(range(1, 10)) for i in self.variables}
        self.neighbors = {i: set() for i in self.variables}
        self.arcs = set()
        self.grid = [[0 for _ in range(9)] for _ in range(9)]

    def load_initial_grid(self, grid):
        self.grid = [row[:] for row in grid]
        for row in range(9):
            for col in range(9):
                value = grid[row][col]
                if value != 0:
                    idx = cell_to_index(row, col)
                    self.domains[idx] = [value]

    def neighbors_arcs(self):
        for var in self.variables:
            row, col = index_to_cell(var)
            for c in range(9):
                if c != col:
                    neighbor = cell_to_index(row, c)
                    self.neighbors[var].add(neighbor)
                    self.arcs.add((var, neighbor))
            for r in range(9):
                if r != row:
                    neighbor = cell_to_index(r, col)
                    self.neighbors[var].add(neighbor)
                    self.arcs.add((var, neighbor))
            box_row, box_col = (row // 3) * 3, (col // 3) * 3
            for r in range(box_row, box_row + 3):
                for c in range(box_col, box_col + 3):
                    if (r, c) != (row, col):
                        neighbor = cell_to_index(r, c)
                        self.neighbors[var].add(neighbor)
                        self.arcs.add((var, neighbor))

    def is_valid_assignment(self, var, value):
        for neighbor in self.neighbors[var]:
            # If the neighbor has a single value assigned and it matches the value, it's invalid
            if len(self.domains[neighbor]) == 1 and self.domains[neighbor][0] == value:
                return False
        return True

    def is_solved(self):
        return all(len(self.domains[var]) == 1 for var in self.variables)

    def get_assignment(self):
        board = [[0 for _ in range(9)] for _ in range(9)]
        for var in self.variables:
            row, col = index_to_cell(var)
            if len(self.domains[var]) == 1:
                board[row][col] = self.domains[var][0]
        return board

    def print_board(self):
        board = self.get_assignment()
        for i, row in enumerate(board):
            if i % 3 == 0 and i != 0:
                print("-" * 21)
            line = ""
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    line += "| "
                line += (str(val) if val != 0 else ".") + " "
            print(line)
        print()

    def select_unassigned_variable(self):
        # Get a list of variables that are not yet assigned (domains with more than one value)
        unassigned = [v for v in self.variables if len(self.domains[v]) > 1]
        # Return the variable with the smallest domain size (Minimum Remaining Values heuristic)
        # If no unassigned variables exist, return None
        return min(unassigned, key=lambda v: len(self.domains[v]), default=None)  # MRV

    def order_domain_values(self, var):
        # Dictionary to store the count of constraints for each value
        constraint_counts = {}
        # Calculate the number of constraints each value 3ndha on neighbors
        for value in self.domains[var]:
            constraint_counts[value] = sum(
                1 for neighbor in self.neighbors[var] if value in self.domains[neighbor]
            )
        # Sort the values by the number of constraints (ascending order)
        return sorted(self.domains[var], key=lambda val: constraint_counts[val])

    def forward_check(self, var, value):
        """
        Perform forward checking after assigning a value to a variable.
        Removes the assigned value from the domains of neighboring variables.

        Args:
            var: The variable being assigned.
            value: The value being assigned to the variable.

        Returns:
            A dictionary of inferences (removed values) if successful, or None if a failure occurs.
        """
        inferences = {}
        # Iterate through all neighbors of the variable
        for neighbor in self.neighbors[var]:
            # Check if the assigned value exists in the neighbor's domain
            if value in self.domains[neighbor]:
                # If the neighbor's domain becomes empty, return failure
                if len(self.domains[neighbor]) == 1:
                    return None
                # Record the value to be removed from the neighbor's domain
                inferences.setdefault(neighbor, []).append(value) # btw dh lw no neighbor index by3mlo w y5aleelo list value abl ma y append
        # Apply the inferences by removing the values from the neighbors' domains
        for neighbor, values in inferences.items():
            for val in values:
                self.domains[neighbor].remove(val)

        return inferences

    def restore_inferences(self, inferences):
        if inferences:
            for var, values in inferences.items():
                self.domains[var].extend(values)

    def backtrack_solve(self):
        # Check if the puzzle is already solved
        if self.is_solved():
            return True

        # Select the next unassigned variable using the MRV heuristic
        variable = self.select_unassigned_variable()
        if variable is None:
            return False  # No unassigned variables left, but the puzzle is not solved

        # Iterate through the ordered domain values for the selected variable
        for value in self.order_domain_values(variable):
            # Check if assigning the value is valid
            if self.is_valid_assignment(variable, value):
                # Save the current domain state
                original_domain = self.domains[variable][:]
                # Assign the value to the variable
                self.domains[variable] = [value]

                # Perform forward checking to propagate constraints
                inferences = self.forward_check(variable, value)
                if inferences is not None:
                    # Recursively attempt to solve the puzzle
                    if self.backtrack_solve():
                        return True

                # Restore the original domain and undo inferences if the assignment fails
                self.domains[variable] = original_domain
                self.restore_inferences(inferences)

        # Return False if no valid assignment leads to a solution
        return False

    def validate_puzzle(self):
        original_domains = {var: self.domains[var][:] for var in self.variables}
        solvable = self.backtrack_solve()
        self.domains = original_domains
        return solvable

    def generate_puzzle(self, difficulty='medium'):

        # Reset domains and grid
        self.domains = {var: list(range(1, 10)) for var in self.variables}
        self.grid = [[0 for _ in range(9)] for _ in range(9)]

        # Define the number of clues for each difficulty level
        difficulty_levels = {
            'easy': 30,
            'medium': 25,
            'hard': 15
        }
        num_clues = difficulty_levels.get(difficulty, 30)

        # Fill the grid with the specified number of clues
        clues_added = 0
        while clues_added < num_clues:
            # Randomly select a variable (cell)
            variable = random.choice(self.variables)

            # Ensure the variable has more than one possible value
            if len(self.domains[variable]) > 1:
                # Randomly select a value from the variable's domain
                value = random.choice(self.domains[variable])

                # Check if the value is a valid assignment
                if self.is_valid_assignment(variable, value):
                    # Assign the value to the variable
                    self.domains[variable] = [value]
                    row, col = index_to_cell(variable)
                    self.grid[row][col] = value
                    clues_added += 1

        # Validate the generated puzzle; regenerate if invalid
        if not self.validate_puzzle():
            return self.generate_puzzle(difficulty)

        return self.grid

    def enforce_arc_consistency(self):

        # Initialize the queue with all arcs
        arc_queue = list(self.arcs)

        while arc_queue:
            # Dequeue an arc (Xi, Xj)
            Xi, Xj = arc_queue.pop(0)

            # Revise the domain of Xi based on Xj
            if self.revise(Xi, Xj):
                # If the domain of Xi becomes empty, the puzzle is unsolvable
                if len(self.domains[Xi]) == 0:
                    raise ValueError(f"Domain of variable {Xi} is empty. Puzzle is unsolvable.")

                # Add all arcs (Xk, Xi) back to the queue, except the one involving Xj
                for Xk in self.neighbors[Xi]:
                    if Xk != Xj:
                        arc_queue.append((Xk, Xi))

    def revise(self, Xi, Xj):

        revised = False
        current_domain_Xi = self.domains[Xi][:]  # Copy of Xi's domain for logging

        for value in current_domain_Xi:
            # Check if value has no valid counterpart in Xj's domain
            if not any(value != v for v in self.domains[Xj]):
                print(f"Current domain of X{Xi}: {current_domain_Xi}")
                print(f"Domain of X{Xj}: {self.domains[Xj]}")
                print(f"Removed value {value} from X{Xi} because no supporting value exists in X{Xj}")

                # Remove the value from Xi's domain
                self.domains[Xi].remove(value)
                revised = True

                # Log the updated domain of Xi
                print(f"Updated domain of X{Xi}: {self.domains[Xi]}")

        return revised

    def update_grid_from_domains(self):

        for variable in self.variables:
            # If the domain has exactly one value, assign it to the grid
            if len(self.domains[variable]) == 1:
                value = self.domains[variable][0]
                row, col = index_to_cell(variable)
                self.grid[row][col] = value

    def solve_with_arc_consistency(self):

        while True:
            # Enforce arc consistency
            self.enforce_arc_consistency()

            # Save the current state of the grid
            previous_grid = [row[:] for row in self.grid]

            # Update the grid based on the current domains
            self.update_grid_from_domains()

            # If the grid no longer changes, stop the loop
            if self.grid == previous_grid:
                break

        # Check if the puzzle is solved
        if not self.is_solved():
            print("Puzzle could not be solved with arc consistency alone.")