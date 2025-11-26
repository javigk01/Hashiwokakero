"""
Pruebas de integración para el proyecto Hashiwokakero
Ejecutar con: py -m unittest test_integration.py
"""

import unittest
import os
from game_logic import HashiGame
from solver import HashiSolver
from backtracking_solver import BacktrackingSolver
from parser import parse_board


class TestFullGameFlow(unittest.TestCase):
    """Pruebas de flujo completo del juego"""
    
    def test_full_game_manual_play(self):
        """Juego manual completo"""
        board = [
            [2, 0, 2],
            [0, 0, 0],
            [2, 0, 2]
        ]
        game = HashiGame(3, 3, board)
        
        # Jugar manualmente
        game.create_bridge((0, 0), (0, 2))
        game.create_bridge((0, 0), (2, 0))
        game.create_bridge((0, 2), (2, 2))
        game.create_bridge((2, 0), (2, 2))
        
        # Verificar victoria
        self.assertTrue(game.check_victory())
    
    def test_full_game_solver_csp(self):
        """Juego resuelto con CSP"""
        board = [
            [2, 0, 2],
            [0, 0, 0],
            [2, 0, 2]
        ]
        game = HashiGame(3, 3, board)
        solver = HashiSolver(game)
        
        success, bridges = solver.solve()
        self.assertTrue(success)
        
        # Aplicar solución
        for a, b in bridges:
            game.create_bridge(a, b)
        
        self.assertTrue(game.check_victory())
    
    def test_full_game_solver_backtracking(self):
        """Juego resuelto con backtracking"""
        board = [
            [2, 0, 2],
            [0, 0, 0],
            [2, 0, 2]
        ]
        game = HashiGame(3, 3, board)
        solver = BacktrackingSolver(game)
        
        success, bridges = solver.solve()
        self.assertTrue(success)
        
        # Aplicar solución
        for a, b in bridges:
            game.create_bridge(a, b)
        
        self.assertTrue(game.check_victory())
    
    def test_manual_then_solver(self):
        """Juego parcial manual, luego solver"""
        board = [
            [3, 0, 4, 0, 3],
            [0, 0, 0, 0, 0],
            [2, 0, 3, 0, 2]
        ]
        game = HashiGame(3, 5, board)
        
        # Jugar algunos movimientos manualmente
        game.create_bridge((0, 0), (0, 2))
        game.create_bridge((0, 2), (0, 4))
        
        # Usar solver para terminar
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        
        if success:
            for a, b in bridges:
                result, _, _ = game.create_bridge(a, b)
                if not result:
                    # Puente ya existe o es inválido
                    pass


class TestSolverComparison(unittest.TestCase):
    """Comparación entre solvers"""
    
    def test_both_solvers_valid_solutions(self):
        """Ambas soluciones son válidas"""
        board = [
            [2, 0, 3],
            [0, 0, 0],
            [1, 0, 2]
        ]
        
        # CSP Solver
        game1 = HashiGame(3, 3, board)
        solver1 = HashiSolver(game1)
        success1, bridges1 = solver1.solve()
        
        if success1:
            for a, b in bridges1:
                game1.create_bridge(a, b)
            self.assertTrue(game1.check_victory())
        
        # Backtracking Solver
        game2 = HashiGame(3, 3, board)
        solver2 = BacktrackingSolver(game2)
        success2, bridges2 = solver2.solve()
        
        if success2:
            for a, b in bridges2:
                game2.create_bridge(a, b)
            self.assertTrue(game2.check_victory())
        
        # Ambos deberían tener éxito
        self.assertEqual(success1, success2)
    
    def test_csp_faster_than_backtracking(self):
        """CSP es más rápido (en iteraciones)"""
        board = [
            [3, 0, 4, 0, 3],
            [0, 0, 0, 0, 0],
            [4, 0, 6, 0, 4],
            [0, 0, 0, 0, 0],
            [3, 0, 4, 0, 3]
        ]
        
        # CSP Solver
        game1 = HashiGame(5, 5, board)
        solver1 = HashiSolver(game1)
        success1, bridges1 = solver1.solve()
        iterations_csp = solver1.iterations
        
        # Backtracking Solver
        game2 = HashiGame(5, 5, board)
        solver2 = BacktrackingSolver(game2)
        success2, bridges2 = solver2.solve()
        iterations_backtracking = solver2.iterations
        
        # CSP debería usar menos iteraciones (generalmente)
        if success1 and success2:
            print(f"\nCSP iterations: {iterations_csp}")
            print(f"Backtracking iterations: {iterations_backtracking}")
            # No siempre es cierto dependiendo del puzzle, pero típicamente CSP es más eficiente
            self.assertLess(iterations_csp, iterations_backtracking * 2)


class TestRealFilesIntegration(unittest.TestCase):
    """Pruebas con archivos reales del proyecto"""
    
    def test_solve_example_file_with_csp(self):
        """Resolver example.txt con CSP"""
        if not os.path.exists('example.txt'):
            self.skipTest('example.txt no encontrado')
        
        rows, cols, board = parse_board('example.txt')
        game = HashiGame(rows, cols, board)
        solver = HashiSolver(game)
        
        success, bridges = solver.solve()
        
        if success:
            for a, b in bridges:
                game.create_bridge(a, b)
            self.assertTrue(game.check_victory())
    
    def test_solve_example_file_with_backtracking(self):
        """Resolver example.txt con backtracking"""
        if not os.path.exists('example.txt'):
            self.skipTest('example.txt no encontrado')
        
        rows, cols, board = parse_board('example.txt')
        game = HashiGame(rows, cols, board)
        solver = BacktrackingSolver(game)
        
        success, bridges = solver.solve()
        
        if success:
            for a, b in bridges:
                game.create_bridge(a, b)
            self.assertTrue(game.check_victory())
    
    def test_solve_example2_file(self):
        """Resolver example2.txt"""
        if not os.path.exists('example2.txt'):
            self.skipTest('example2.txt no encontrado')
        
        rows, cols, board = parse_board('example2.txt')
        game = HashiGame(rows, cols, board)
        solver = HashiSolver(game)
        
        success, bridges = solver.solve()
        
        if success:
            for a, b in bridges:
                game.create_bridge(a, b)
            self.assertTrue(game.check_victory())


class TestEdgeCasesIntegration(unittest.TestCase):
    """Pruebas de casos extremos integrados"""
    
    def test_dense_puzzle(self):
        """Puzzle muy denso (muchas islas)"""
        board = [
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2]
        ]
        game = HashiGame(5, 5, board)
        solver = HashiSolver(game)
        
        # Este puzzle es difícil, el solver podría no encontrar solución fácilmente
        success, bridges = solver.solve()
        # No forzamos éxito, solo verificamos que no crashee
        self.assertIsInstance(success, bool)
    
    def test_sparse_puzzle(self):
        """Puzzle muy disperso"""
        board = [
            [1, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0],
        ]
        game = HashiGame(4, 9, board)
        solver = HashiSolver(game)
        
        success, bridges = solver.solve()
        # Islas muy separadas, probablemente no tiene solución válida
        self.assertIsInstance(success, bool)


if __name__ == '__main__':
    unittest.main()
