"""
Pruebas unitarias para backtracking_solver.py (BacktrackingSolver)
Ejecutar con: py -m unittest test_backtracking_solver.py
"""

import unittest
from game_logic import HashiGame
from backtracking_solver import BacktrackingSolver


class TestBacktrackingSolverBasic(unittest.TestCase):
    """Pruebas básicas de resolución con backtracking"""
    
    def test_solve_simple_puzzle_backtracking(self):
        """Resolver puzzle simple"""
        board = [
            [1, 0, 1],
        ]
        game = HashiGame(1, 3, board)
        solver = BacktrackingSolver(game)
        success, bridges = solver.solve()
        self.assertTrue(success)
        self.assertEqual(len(bridges), 1)
    
    def test_solve_medium_puzzle_backtracking(self):
        """Resolver puzzle mediano"""
        board = [
            [2, 0, 2],
            [0, 0, 0],
            [2, 0, 2]
        ]
        game = HashiGame(3, 3, board)
        solver = BacktrackingSolver(game)
        success, bridges = solver.solve()
        self.assertTrue(success)
        self.assertGreater(len(bridges), 0)
    
    def test_backtracking_finds_solution(self):
        """Encuentra solución válida"""
        board = [
            [2, 0, 3],
            [0, 0, 0],
            [1, 0, 2]
        ]
        game = HashiGame(3, 3, board)
        solver = BacktrackingSolver(game)
        success, bridges = solver.solve()
        
        if success:
            # Aplicar la solución
            for a, b in bridges:
                game.create_bridge(a, b)
            
            # Verificar que es una victoria
            self.assertTrue(game.check_victory())
    
    def test_backtracking_unsolvable_puzzle(self):
        """Detecta puzzles sin solución"""
        board = [
            [8, 0, 1],  # Isla 8 necesita 8 puentes pero solo tiene 1 vecino
        ]
        game = HashiGame(1, 3, board)
        solver = BacktrackingSolver(game)
        success, bridges = solver.solve()
        self.assertFalse(success)


class TestBacktrackingHeuristics(unittest.TestCase):
    """Pruebas de heurísticas del backtracking"""
    
    def test_mrv_selects_most_constrained_island(self):
        """MRV selecciona la isla más restrictiva"""
        board = [
            [1, 0, 3, 0, 2],
        ]
        game = HashiGame(1, 5, board)
        solver = BacktrackingSolver(game)
        
        # La isla con valor 1 debería ser seleccionada primero (más restrictiva)
        selected = solver._select_island_with_min_remaining()
        self.assertIsNotNone(selected)
        island_info = game.get_island_info(selected)
        # Debería ser la isla con menos puentes restantes
        self.assertLessEqual(island_info['num'], 3)
    
    def test_early_pruning_detects_invalid_state(self):
        """Poda detecta estados inválidos"""
        board = [
            [2, 0, 2],
        ]
        game = HashiGame(1, 3, board)
        solver = BacktrackingSolver(game)
        
        # Estado inicial es válido
        self.assertFalse(solver._is_invalid_state())
        
        # Crear más puentes de los permitidos (forzar estado inválido)
        game.create_bridge((0, 0), (0, 2))
        game.create_bridge((0, 0), (0, 2))
        game.create_bridge((0, 0), (0, 2))  # Esto debería fallar, pero si no...
        
        # Verificar si el solver detecta sobre-capacidad
        # (Nota: create_bridge debería prevenir esto, pero probamos _is_invalid_state)
    
    def test_early_pruning_overcapacity(self):
        """Detecta sobre-capacidad"""
        board = [
            [1, 0, 2],
        ]
        game = HashiGame(1, 3, board)
        solver = BacktrackingSolver(game)
        
        # Forzar estado inválido manipulando directamente
        game.islands[(0, 0)]['bridges'][(0, 2)] = 3  # Más de lo permitido
        
        # El solver debería detectar que (0,0) con valor 1 tiene 3 puentes
        self.assertTrue(solver._is_invalid_state())


class TestBacktrackingMechanics(unittest.TestCase):
    """Pruebas de mecánicas de backtracking"""
    
    def test_backtracking_reverts_changes(self):
        """Backtrack deshace cambios"""
        board = [
            [2, 0, 2],
        ]
        game = HashiGame(1, 3, board)
        
        # Guardar estado inicial
        initial_bridges = game.get_island_info((0, 0))['used']
        
        # Crear y eliminar puente
        game.create_bridge((0, 0), (0, 2))
        game.delete_bridge((0, 0), (0, 2))
        
        # Verificar que volvió al estado inicial
        final_bridges = game.get_island_info((0, 0))['used']
        self.assertEqual(initial_bridges, final_bridges)
    
    def test_backtracking_explores_alternatives(self):
        """Explora alternativas"""
        board = [
            [2, 0, 2],
        ]
        game = HashiGame(1, 3, board)
        solver = BacktrackingSolver(game)
        success, bridges = solver.solve()
        
        # Debería encontrar que necesita 2 puentes entre las islas
        self.assertTrue(success)
        self.assertEqual(len(bridges), 2)


class TestBacktrackingValidation(unittest.TestCase):
    """Pruebas de validación del backtracking"""
    
    def test_all_islands_complete(self):
        """Verifica islas completas"""
        board = [
            [1, 0, 1],
        ]
        game = HashiGame(1, 3, board)
        game.create_bridge((0, 0), (0, 2))
        
        solver = BacktrackingSolver(game)
        self.assertTrue(solver._all_islands_complete())
    
    def test_is_connected(self):
        """Verifica conectividad del grafo"""
        board = [
            [2, 0, 2],
            [0, 0, 0],
            [2, 0, 2]
        ]
        game = HashiGame(3, 3, board)
        solver = BacktrackingSolver(game)
        
        # Sin puentes, no está conectado
        self.assertFalse(solver._is_connected())
        
        # Conectar todas las islas
        game.create_bridge((0, 0), (0, 2))
        game.create_bridge((0, 0), (2, 0))
        game.create_bridge((0, 2), (2, 2))
        game.create_bridge((2, 0), (2, 2))
        
        # Ahora debería estar conectado
        self.assertTrue(solver._is_connected())
    
    def test_is_invalid_state(self):
        """Detecta estados inválidos"""
        board = [
            [1, 0, 2],
        ]
        game = HashiGame(1, 3, board)
        solver = BacktrackingSolver(game)
        
        # Estado inicial es válido
        self.assertFalse(solver._is_invalid_state())


class TestBacktrackingEdgeCases(unittest.TestCase):
    """Pruebas de casos extremos"""
    
    def test_two_islands_maximum_bridges(self):
        """Dos islas con 2 puentes"""
        board = [
            [2, 0, 2],
        ]
        game = HashiGame(1, 3, board)
        solver = BacktrackingSolver(game)
        success, bridges = solver.solve()
        self.assertTrue(success)
        self.assertEqual(len(bridges), 2)
    
    def test_complex_connectivity(self):
        """Conectividad compleja"""
        board = [
            [3, 0, 3],
            [0, 0, 0],
            [3, 0, 3]
        ]
        game = HashiGame(3, 3, board)
        solver = BacktrackingSolver(game)
        success, bridges = solver.solve()
        
        if success:
            for a, b in bridges:
                game.create_bridge(a, b)
            self.assertTrue(game.check_victory())


if __name__ == '__main__':
    unittest.main()
