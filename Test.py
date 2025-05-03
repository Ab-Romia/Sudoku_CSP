# import unittest
# from Board import Sudoku
#
# class TestSudoku(unittest.TestCase):
#     def setUp(self):
#         self.sudoku = Sudoku()
#         self.initial_grid = [
#             [5, 3, 0, 0, 7, 0, 0, 0, 0],
#             [6, 0, 0, 1, 9, 5, 0, 0, 0],
#             [0, 9, 8, 0, 0, 0, 0, 6, 0],
#             [8, 0, 0, 0, 6, 0, 0, 0, 3],
#             [4, 0, 0, 8, 0, 3, 0, 0, 1],
#             [7, 0, 0, 0, 2, 0, 0, 0, 6],
#             [0, 6, 0, 0, 0, 0, 2, 8, 0],
#             [0, 0, 0, 4, 1, 9, 0, 0, 5],
#             [0, 0, 0, 0, 8, 0, 0, 7, 9]
#         ]
#
#     def test_load_initial_grid(self):
#         self.sudoku.load_initial_grid(self.initial_grid)
#         self.assertEqual(self.sudoku.grid, self.initial_grid)
#
#     def test_neighbors_arcs(self):
#         self.sudoku.neighbors_arcs()
#         self.assertEqual(len(self.sudoku.neighbors[0]), 20)  # Cell 0 should have 20 neighbors
#         self.assertIn((0, 1), self.sudoku.arcs)  # Arc between cell 0 and cell 1 should exist
#
#
#     def test_is_solved(self):
#         self.sudoku.load_initial_grid(self.initial_grid)
#         self.assertFalse(self.sudoku.is_solved())  # Initial grid is not solved
#         solved_grid = [
#             [5, 3, 4, 6, 7, 8, 9, 1, 2],
#             [6, 7, 2, 1, 9, 5, 3, 4, 8],
#             [1, 9, 8, 3, 4, 2, 5, 6, 7],
#             [8, 5, 9, 7, 6, 1, 4, 2, 3],
#             [4, 2, 6, 8, 5, 3, 7, 9, 1],
#             [7, 1, 3, 9, 2, 4, 8, 5, 6],
#             [9, 6, 1, 5, 3, 7, 2, 8, 4],
#             [2, 8, 7, 4, 1, 9, 6, 3, 5],
#             [3, 4, 5, 2, 8, 6, 1, 7, 9]
#         ]
#         self.sudoku.load_initial_grid(solved_grid)
#         self.assertTrue(self.sudoku.is_solved())  # Solved grid is solved
#
#     def test_backtrack_solve(self):
#         self.sudoku.load_initial_grid(self.initial_grid)
#         self.sudoku.neighbors_arcs()
#         self.assertTrue(self.sudoku.backtrack_solve())  # Puzzle should be solvable
#         self.assertTrue(self.sudoku.is_solved())  # After solving, the puzzle should be solved
#
#     def test_validate_puzzle(self):
#         self.sudoku.load_initial_grid(self.initial_grid)
#         self.sudoku.neighbors_arcs()
#         self.assertTrue(self.sudoku.validate_puzzle())  # Puzzle should be solvable
#
#     def test_generate_puzzle(self):
#         generated_grid = self.sudoku.generate_puzzle(difficulty='easy')
#         self.assertEqual(len([cell for row in generated_grid for cell in row if cell != 0]), 36)  # Easy puzzle should have 36 clues
#         self.assertTrue(self.sudoku.validate_puzzle())  # Generated puzzle should be solvable
#
#     def test_enforce_arc_consistency(self):
#         self.sudoku.load_initial_grid(self.initial_grid)
#         self.sudoku.neighbors_arcs()
#         self.sudoku.enforce_arc_consistency()
#         for var in self.sudoku.variables:
#             self.assertGreater(len(self.sudoku.domains[var]), 0)  # No domain should be empty after enforcing arc consistency
#
#     def test_solve_with_arc_consistency(self):
#         self.sudoku.load_initial_grid(self.initial_grid)
#         self.sudoku.neighbors_arcs()
#         self.sudoku.solve_with_arc_consistency()
#         self.assertTrue(self.sudoku.is_solved())  # Puzzle should be solved after applying arc consistency
#
# if __name__ == "__main__":
#     unittest.main()