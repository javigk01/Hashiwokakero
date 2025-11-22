"""
Solucionador alternativo para Hashiwokakero usando BACKTRACKING PURO
Técnica: Recursividad + Backtracking (fuerza bruta optimizada)
No usa propagación de restricciones avanzada, solo prueba y retrocede
"""

import copy

class BacktrackingSolver:
    """Resuelve el puzzle usando backtracking puro con recursividad"""
    
    def __init__(self, game):
        """
        Inicializa el solucionador
        
        Args:
            game: instancia de HashiGame
        """
        self.game = game
        self.solution_bridges = []
        self.iterations = 0
        self.max_iterations = 50000  # Límite más alto para backtracking puro
    
    def solve(self):
        """
        Intenta resolver el puzzle usando backtracking puro
        
        Returns:
            tuple (bool, list) - (éxito, lista de puentes [(a, b), ...])
        """
        # Guardar estado inicial
        initial_state = self._save_state()
        
        # Obtener lista de todas las islas
        islands = list(self.game.islands.keys())
        
        # Ordenar islas por el número requerido (heurística simple: empezar con las más restrictivas)
        islands.sort(key=lambda pos: self.game.islands[pos]['num'], reverse=True)
        
        # Intentar resolver recursivamente
        success = self._backtrack(islands, 0)
        
        if success:
            # Recopilar todos los puentes de la solución
            bridges = []
            for pos, info in self.game.islands.items():
                for neighbor, count in info['bridges'].items():
                    if pos < neighbor:  # Evitar duplicados
                        for _ in range(count):
                            bridges.append((pos, neighbor))
            
            # Restaurar estado inicial
            self._restore_state(initial_state)
            
            return True, bridges
        else:
            # Restaurar estado inicial
            self._restore_state(initial_state)
            return False, []
    
    def _backtrack(self, islands, index):
        """
        Función recursiva de backtracking
        
        Args:
            islands: lista de posiciones de islas
            index: índice de la isla actual
        
        Returns:
            bool - True si se encontró solución
        """
        self.iterations += 1
        
        # Límite de seguridad
        if self.iterations > self.max_iterations:
            return False
        
        # Caso base: verificar si todas las islas están completas
        if self._all_islands_complete():
            # Verificar que el grafo esté conectado
            if self._is_connected():
                return True
            return False
        
        # Si hemos procesado todas las islas pero no están completas, fallo
        if index >= len(islands):
            return False
        
        current_island = islands[index]
        island_info = self.game.islands[current_island]
        used = sum(island_info['bridges'].values())
        
        # Si esta isla ya está completa, pasar a la siguiente
        if used == island_info['num']:
            return self._backtrack(islands, index + 1)
        
        # Si esta isla tiene más puentes de los necesarios, fallo
        if used > island_info['num']:
            return False
        
        # Obtener vecinos válidos (en línea recta sin cruces)
        neighbors = self._get_valid_neighbors(current_island)
        
        # Probar agregar puentes a cada vecino (0, 1 o 2 puentes)
        for neighbor in neighbors:
            # Intentar agregar 1 o 2 puentes
            for bridge_count in [1, 2]:
                # Verificar si podemos agregar estos puentes
                can_add = self._can_add_bridges(current_island, neighbor, bridge_count)
                
                if can_add:
                    # Agregar puente(s)
                    bridges_added = []
                    for _ in range(bridge_count):
                        success, msg, bridge_info = self.game.create_bridge(current_island, neighbor)
                        if success:
                            bridges_added.append((current_island, neighbor))
                        else:
                            # Deshacer puentes agregados en este intento
                            for _ in bridges_added:
                                self.game.delete_bridge(current_island, neighbor)
                            break
                    
                    # Si se agregaron todos los puentes exitosamente
                    if len(bridges_added) == bridge_count:
                        # Recursión: intentar resolver el resto
                        if self._backtrack(islands, index):
                            return True
                        
                        # Backtrack: eliminar los puentes agregados
                        for _ in range(bridge_count):
                            self.game.delete_bridge(current_island, neighbor)
        
        # También probar no agregar más puentes a esta isla (si es válido)
        # Continuar con la siguiente isla
        return self._backtrack(islands, index + 1)
    
    def _all_islands_complete(self):
        """Verifica si todas las islas tienen el número correcto de puentes"""
        for info in self.game.islands.values():
            used = sum(info['bridges'].values())
            if used != info['num']:
                return False
        return True
    
    def _is_connected(self):
        """Verifica si todas las islas están conectadas (DFS/BFS)"""
        if not self.game.islands:
            return True
        
        # DFS desde la primera isla
        start = next(iter(self.game.islands.keys()))
        visited = set()
        stack = [start]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            
            # Agregar vecinos conectados
            for neighbor in self.game.islands[current]['bridges'].keys():
                if neighbor not in visited:
                    stack.append(neighbor)
        
        # Verificar que todas las islas fueron visitadas
        return len(visited) == len(self.game.islands)
    
    def _get_valid_neighbors(self, island_pos):
        """
        Obtiene vecinos válidos para una isla (en línea recta, sin cruces)
        
        Args:
            island_pos: (r, c) posición de la isla
        
        Returns:
            list - lista de posiciones de vecinos válidos
        """
        r, c = island_pos
        neighbors = []
        
        # Buscar en las 4 direcciones
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # arriba, abajo, izq, der
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            # Buscar la primera isla en esta dirección
            while 0 <= nr < self.game.rows and 0 <= nc < self.game.cols:
                if (nr, nc) in self.game.islands:
                    # Verificar que no haya cruce de puentes
                    if self._can_connect(island_pos, (nr, nc)):
                        neighbors.append((nr, nc))
                    break
                nr += dr
                nc += dc
        
        return neighbors
    
    def _can_connect(self, a, b):
        """Verifica si dos islas pueden conectarse sin cruzar otros puentes"""
        # Usar la lógica del juego para verificar
        success, msg, _ = self.game.create_bridge(a, b, dry_run=True)
        return success
    
    def _can_add_bridges(self, a, b, count):
        """
        Verifica si se pueden agregar 'count' puentes entre a y b
        
        Args:
            a: posición de isla a
            b: posición de isla b
            count: número de puentes a agregar (1 o 2)
        
        Returns:
            bool
        """
        info_a = self.game.islands[a]
        info_b = self.game.islands[b]
        
        # Calcular puentes usados
        used_a = sum(info_a['bridges'].values())
        used_b = sum(info_b['bridges'].values())
        
        # Verificar que no excedan el máximo permitido
        remaining_a = info_a['num'] - used_a
        remaining_b = info_b['num'] - used_b
        
        if remaining_a < count or remaining_b < count:
            return False
        
        # Verificar cuántos puentes ya existen
        current_bridges = info_a['bridges'].get(b, 0)
        
        # No se pueden tener más de 2 puentes entre dos islas
        if current_bridges + count > 2:
            return False
        
        return True
    
    def _save_state(self):
        """Guarda el estado actual del juego"""
        return copy.deepcopy(self.game.islands)
    
    def _restore_state(self, state):
        """Restaura un estado guardado del juego"""
        self.game.islands = copy.deepcopy(state)
