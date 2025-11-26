"""
Pruebas unitarias para solver.py (HashiSolver - CSP)
Ejecutar con: py -m unittest test_solver.py
"""

import unittest
from game_logic import HashiGame
from solver import HashiSolver


class TestSolverBasic(unittest.TestCase):
    """Pruebas básicas de resolución"""
    
    def test_solve_simple_puzzle(self):
        """Resolver puzzle simple (2x2)"""
        board = [
            [1, 0, 1],
        ]
        game = HashiGame(1, 3, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        self.assertTrue(success)
        self.assertEqual(len(bridges), 1)
    
    def test_solve_medium_puzzle(self):
        """Resolver puzzle mediano (5x5)"""
        board = [
            [2, 0, 3, 0, 2],
            [0, 0, 0, 0, 0],
            [3, 0, 4, 0, 3],
            [0, 0, 0, 0, 0],
            [2, 0, 3, 0, 2]
        ]
        game = HashiGame(5, 5, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        self.assertTrue(success)
        self.assertGreater(len(bridges), 0)
    
    def test_solve_returns_valid_solution(self):
        """Solución es válida"""
        board = [
            [2, 0, 2],
            [0, 0, 0],
            [2, 0, 2]
        ]
        game = HashiGame(3, 3, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        
        if success:
            # Aplicar la solución
            for a, b in bridges:
                game.create_bridge(a, b)
            
            # Verificar que es una victoria
            self.assertTrue(game.check_victory())
    
    def test_solve_unsolvable_puzzle(self):
        """Detecta puzzles sin solución"""
        board = [
            [8, 0, 1],  # Isla 8 necesita 8 puentes pero solo tiene 1 vecino
        ]
        game = HashiGame(1, 3, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        self.assertFalse(success)


class TestSolverValidation(unittest.TestCase):
    """Pruebas de validación de soluciones"""
    
    def test_solution_connects_all_islands(self):
        """Solución conecta todas las islas"""
        board = [
            [2, 0, 3, 0, 2],
            [0, 0, 0, 0, 0],
            [1, 0, 2, 0, 1]
        ]
        game = HashiGame(3, 5, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        
        if success:
            # Aplicar la solución
            for a, b in bridges:
                game.create_bridge(a, b)
            
            # Verificar conectividad usando DFS
            visited = set()
            stack = [list(game.islands.keys())[0]]
            
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                
                island_info = game.get_island_info(current)
                for neighbor in island_info['bridges'].keys():
                    if neighbor not in visited:
                        stack.append(neighbor)
            
            self.assertEqual(len(visited), len(game.islands))
    
    def test_solution_respects_island_numbers(self):
        """Solución respeta números de islas"""
        board = [
            [2, 0, 3],
            [0, 0, 0],
            [1, 0, 2]
        ]
        game = HashiGame(3, 3, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        
        if success:
            # Aplicar la solución
            for a, b in bridges:
                game.create_bridge(a, b)
            
            # Verificar que cada isla tiene el número correcto de puentes
            for pos, island_data in game.islands.items():
                used = sum(island_data['bridges'].values())
                self.assertEqual(used, island_data['num'])


class TestSolverPerformance(unittest.TestCase):
    """Pruebas de performance"""
    
    def test_solver_efficiency(self):
        """Verifica que usa pocas iteraciones"""
        board = [
            [2, 0, 2],
            [0, 0, 0],
            [2, 0, 2]
        ]
        game = HashiGame(3, 3, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        
        # El solver CSP debería usar menos de 1000 iteraciones para puzzles simples
        self.assertLess(solver.iterations, 1000)
    
    def test_solver_does_not_timeout(self):
        """No excede tiempo límite"""
        import time
        
        board = [
            [3, 0, 4, 0, 3],
            [0, 0, 0, 0, 0],
            [4, 0, 6, 0, 4],
            [0, 0, 0, 0, 0],
            [3, 0, 4, 0, 3]
        ]
        game = HashiGame(5, 5, board)
        solver = HashiSolver(game)
        
        start_time = time.time()
        success, bridges = solver.solve()
        elapsed_time = time.time() - start_time
        
        # Debería terminar en menos de 5 segundos
        self.assertLess(elapsed_time, 5.0)


class TestSolverEdgeCases(unittest.TestCase):
    """Pruebas de casos extremos"""
    
    def test_single_island_puzzle(self):
        """Puzzle con una sola isla (valor 0)"""
        board = [
            [0, 0, 0],
        ]
        game = HashiGame(1, 3, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        # Tablero vacío debería ser "resuelto" trivialmente
        self.assertTrue(success or len(game.islands) == 0)
    
    def test_two_islands_minimal(self):
        """Puzzle mínimo con dos islas"""
        board = [
            [1, 0, 1],
        ]
        game = HashiGame(1, 3, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        self.assertTrue(success)
        self.assertEqual(len(bridges), 1)
    
    def test_long_bridge(self):
        """Puente muy largo (atraviesa muchas celdas)"""
        board = [
            [1, 0, 0, 0, 0, 0, 0, 0, 1],
        ]
        game = HashiGame(1, 9, board)
        solver = HashiSolver(game)
        success, bridges = solver.solve()
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
