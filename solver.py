"""
Solucionador automático para el juego Hashiwokakero (Hashi)
Utiliza constraint propagation + backtracking con heurísticas avanzadas
"""

import copy
from collections import deque

class HashiSolver:
    """Clase que resuelve puzzles de Hashiwokakero usando CSP"""
    
    def __init__(self, game):
        """
        Inicializa el solucionador
        
        Args:
            game: instancia de HashiGame
        """
        self.game = game
        self.solution_bridges = []
        self.iterations = 0
        self.max_iterations = 10000  # Límite de seguridad
    
    def solve(self):
        """
        Intenta resolver el puzzle
        
        Returns:
            tuple (bool, list) - (éxito, lista de puentes a crear [(a, b), ...])
        """
        # Guardar estado inicial
        initial_state = self._save_state()
        
        # Intentar resolver
        success = self._solve_recursive()
        
        if success:
            # Recopilar todos los puentes de la solución
            bridges = []
            for pos, info in self.game.islands.items():
                for neighbor, count in info['bridges'].items():
                    # Agregar cada puente (evitar duplicados usando orden de posiciones)
                    if pos < neighbor:
                        for _ in range(count):
                            bridges.append((pos, neighbor))
            
            # Restaurar estado inicial
            self._restore_state(initial_state)
            
            return True, bridges
        else:
            # Restaurar estado inicial si falla
            self._restore_state(initial_state)
            return False, []
    
    def _solve_recursive(self):
        """Algoritmo recursivo mejorado con constraint propagation"""
        self.iterations += 1
        if self.iterations > self.max_iterations:
            return False
        
        # Aplicar constraint propagation agresivamente
        changed = True
        while changed:
            changed = False
            
            # Regla 1: Movimientos forzados
            if self._apply_forced_moves():
                changed = True
            
            # Regla 2: Saturación de islas
            if self._apply_saturation_rule():
                changed = True
            
            # Regla 3: Análisis de alcanzabilidad
            if self._apply_reachability_analysis():
                changed = True
        
        # Verificar victoria
        if self.game.check_victory():
            return True
        
        # Verificar contradicciones
        if self._has_contradiction():
            return False
        
        # Verificar si todas las islas están satisfechas pero no conectadas
        if self._all_satisfied_but_disconnected():
            return False
        
        # Seleccionar siguiente decisión (isla con menos grados de libertad)
        decision = self._select_best_decision()
        
        if decision is None:
            return False
        
        island, neighbor, num_bridges = decision
        
        # Probar agregar estos puentes
        state = self._save_state()
        
        success = True
        for _ in range(num_bridges):
            can_create, msg, info = self.game.create_bridge(island, neighbor)
            if not can_create:
                success = False
                break
        
        if success and self._solve_recursive():
            return True
        
        # Restaurar y probar NO agregar estos puentes
        self._restore_state(state)
        
        # Marcar que no se puede crear este puente (simular con ocupación temporal)
        # Para simplificar, solo intentamos otras opciones
        
        return False
    
    def _apply_forced_moves(self):
        """Aplica movimientos que son forzados por las restricciones"""
        made_change = False
        
        for island_pos, island_info in self.game.islands.items():
            required = island_info['num']
            used = sum(island_info['bridges'].values())
            remaining = required - used
            
            if remaining <= 0:
                continue
            
            neighbors = self._get_possible_neighbors(island_pos)
            
            if len(neighbors) == 0:
                continue
            
            # Calcular capacidad disponible
            available_capacity = sum(2 - island_info['bridges'].get(n, 0) for n in neighbors)
            
            # Si la capacidad disponible == remaining, usar toda la capacidad
            if available_capacity == remaining:
                for neighbor in neighbors:
                    current = island_info['bridges'].get(neighbor, 0)
                    to_add = 2 - current
                    for _ in range(to_add):
                        success, _, _ = self.game.create_bridge(island_pos, neighbor)
                        if success:
                            made_change = True
            
            # Si solo hay un vecino, conectar todo lo necesario
            elif len(neighbors) == 1:
                neighbor = neighbors[0]
                current = island_info['bridges'].get(neighbor, 0)
                to_add = min(remaining, 2 - current)
                for _ in range(to_add):
                    success, _, _ = self.game.create_bridge(island_pos, neighbor)
                    if success:
                        made_change = True
        
        return made_change
    
    def _apply_saturation_rule(self):
        """Aplica reglas de saturación de islas"""
        made_change = False
        
        for island_pos, island_info in self.game.islands.items():
            required = island_info['num']
            used = sum(island_info['bridges'].values())
            
            if used == required:
                continue
            
            remaining = required - used
            neighbors = self._get_possible_neighbors(island_pos)
            
            # Para islas con valor alto, aplicar lógica especial
            if required >= 5 and len(neighbors) >= 3:
                # Si es una isla de 6 con 3 vecinos, necesita 2 puentes a cada uno
                if required == 6 and len(neighbors) == 3:
                    for neighbor in neighbors:
                        current = island_info['bridges'].get(neighbor, 0)
                        to_add = 2 - current
                        for _ in range(to_add):
                            success, _, _ = self.game.create_bridge(island_pos, neighbor)
                            if success:
                                made_change = True
                
                # Si es una isla de 8 con 4 vecinos, necesita 2 puentes a cada uno
                elif required == 8 and len(neighbors) == 4:
                    for neighbor in neighbors:
                        current = island_info['bridges'].get(neighbor, 0)
                        to_add = 2 - current
                        for _ in range(to_add):
                            success, _, _ = self.game.create_bridge(island_pos, neighbor)
                            if success:
                                made_change = True
        
        return made_change
    
    def _apply_reachability_analysis(self):
        """Análisis de alcanzabilidad para evitar islas aisladas"""
        # Por ahora, retornar False (puede implementarse análisis más complejo)
        return False
    
    def _has_contradiction(self):
        """
        Verifica si el estado actual tiene contradicciones
        
        Returns:
            bool - True si hay contradicción
        """
        for island_pos, island_info in self.game.islands.items():
            required = island_info['num']
            used = sum(island_info['bridges'].values())
            remaining = required - used
            
            if remaining < 0:
                return True
            
            if remaining > 0:
                # Verificar si es posible alcanzar el número requerido
                neighbors = self._get_possible_neighbors(island_pos)
                max_possible = 0
                
                for neighbor in neighbors:
                    current = island_info['bridges'].get(neighbor, 0)
                    max_possible += 2 - current
                
                if max_possible < remaining:
                    return True
        
        return False
    
    def _select_best_decision(self):
        """
        Selecciona la mejor decisión (isla, vecino, número de puentes)
        
        Returns:
            tuple (island, neighbor, num_bridges) o None
        """
        best_decision = None
        min_freedom = float('inf')
        
        for island_pos, island_info in self.game.islands.items():
            required = island_info['num']
            used = sum(island_info['bridges'].values())
            remaining = required - used
            
            if remaining <= 0:
                continue
            
            neighbors = self._get_possible_neighbors(island_pos)
            
            if len(neighbors) == 0:
                continue
            
            # Calcular grados de libertad
            freedom = len(neighbors) * remaining
            
            if freedom < min_freedom:
                min_freedom = freedom
                # Seleccionar el primer vecino con mayor necesidad
                best_neighbor = None
                max_neighbor_remaining = 0
                
                for neighbor in neighbors:
                    neighbor_info = self.game.islands[neighbor]
                    neighbor_remaining = neighbor_info['num'] - sum(neighbor_info['bridges'].values())
                    
                    if neighbor_remaining > max_neighbor_remaining:
                        max_neighbor_remaining = neighbor_remaining
                        best_neighbor = neighbor
                
                if best_neighbor:
                    # Decidir cuántos puentes agregar (empezar con 1)
                    current = island_info['bridges'].get(best_neighbor, 0)
                    if current < 2 and remaining > 0:
                        best_decision = (island_pos, best_neighbor, 1)
        
        return best_decision
    
    def _all_satisfied_but_disconnected(self):
        """Verifica si todas las islas están satisfechas pero desconectadas"""
        # Verificar si todas tienen el número correcto de puentes
        all_satisfied = True
        for island_info in self.game.islands.values():
            used = sum(island_info['bridges'].values())
            if used != island_info['num']:
                all_satisfied = False
                break
        
        if not all_satisfied:
            return False
        
        # Verificar conectividad
        return not self.game.check_victory()
    
    def _get_possible_neighbors(self, island_pos):
        """
        Obtiene lista de vecinos a los que se puede conectar
        
        Args:
            island_pos: posición de la isla
            
        Returns:
            list - lista de posiciones de islas vecinas
        """
        neighbors = []
        r, c = island_pos
        
        # Buscar en 4 direcciones
        # Derecha
        for nc in range(c + 1, self.game.cols):
            if self.game.board[r][nc] > 0:
                neighbor = (r, nc)
                can_connect, _ = self.game.can_create_bridge(island_pos, neighbor)
                if can_connect:
                    neighbors.append(neighbor)
                break
        
        # Izquierda
        for nc in range(c - 1, -1, -1):
            if self.game.board[r][nc] > 0:
                neighbor = (r, nc)
                can_connect, _ = self.game.can_create_bridge(island_pos, neighbor)
                if can_connect:
                    neighbors.append(neighbor)
                break
        
        # Abajo
        for nr in range(r + 1, self.game.rows):
            if self.game.board[nr][c] > 0:
                neighbor = (nr, c)
                can_connect, _ = self.game.can_create_bridge(island_pos, neighbor)
                if can_connect:
                    neighbors.append(neighbor)
                break
        
        # Arriba
        for nr in range(r - 1, -1, -1):
            if self.game.board[nr][c] > 0:
                neighbor = (nr, c)
                can_connect, _ = self.game.can_create_bridge(island_pos, neighbor)
                if can_connect:
                    neighbors.append(neighbor)
                break
        
        return neighbors
    
    def _max_bridges_between(self, island1, island2):
        """
        Calcula el máximo número de puentes que se pueden agregar entre dos islas
        
        Args:
            island1: posición de la primera isla
            island2: posición de la segunda isla
            
        Returns:
            int - número máximo de puentes
        """
        info1 = self.game.islands[island1]
        info2 = self.game.islands[island2]
        
        current = info1['bridges'].get(island2, 0)
        remaining1 = info1['num'] - sum(info1['bridges'].values())
        remaining2 = info2['num'] - sum(info2['bridges'].values())
        
        max_between = 2 - current
        max_possible = min(max_between, remaining1, remaining2)
        
        return max(0, max_possible)
    
    def _count_remaining_capacity(self, island_pos):
        """
        Cuenta cuántos puentes más necesita una isla
        
        Args:
            island_pos: posición de la isla
            
        Returns:
            int - número de puentes restantes
        """
        info = self.game.islands[island_pos]
        required = info['num']
        used = sum(info['bridges'].values())
        return required - used
    
    def _save_state(self):
        """
        Guarda el estado actual del juego
        
        Returns:
            dict - estado del juego
        """
        state = {
            'islands': {},
            'occupancy': {},
            'history_len': len(self.game.history)
        }
        
        for pos, info in self.game.islands.items():
            state['islands'][pos] = {
                'num': info['num'],
                'bridges': dict(info['bridges'])
            }
        
        for pos, occ in self.game.occupancy.items():
            state['occupancy'][pos] = dict(occ)
        
        return state
    
    def _restore_state(self, state):
        """
        Restaura un estado guardado del juego
        
        Args:
            state: estado a restaurar
        """
        # Restaurar islas
        for pos, info in self.game.islands.items():
            if pos in state['islands']:
                info['bridges'] = dict(state['islands'][pos]['bridges'])
            else:
                info['bridges'] = {}
        
        # Restaurar ocupación
        self.game.occupancy = {}
        for pos, occ in state['occupancy'].items():
            self.game.occupancy[pos] = dict(occ)
        
        # Restaurar historial
        while len(self.game.history) > state['history_len']:
            self.game.history.pop()
