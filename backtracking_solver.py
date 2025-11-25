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
        self.max_iterations = 1000000  # Sin límite práctico
    
    def solve(self):
        """
        Intenta resolver el puzzle usando backtracking puro
        
        Returns:
            tuple (bool, list) - (éxito, lista de puentes [(a, b), ...])
        """
        # Guardar estado inicial
        initial_state = self._save_state()
        
        # Generar todos los pares posibles de islas que pueden conectarse
        self.possible_connections = self._generate_possible_connections()
        
        # Intentar resolver recursivamente
        success = self._backtrack()
        
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
    
    def _generate_possible_connections(self):
        """
        Genera una lista de todas las posibles conexiones entre islas
        Ordena por heurística: islas más restrictivas primero
        
        Returns:
            list de tuplas (isla_a, isla_b, max_puentes_posibles)
        """
        connections = []
        islands = list(self.game.islands.keys())
        
        for i, island_a in enumerate(islands):
            for island_b in islands[i+1:]:
                # Verificar si están alineadas
                r1, c1 = island_a
                r2, c2 = island_b
                
                if r1 == r2 or c1 == c2:  # Misma fila o columna
                    # Verificar que no haya otra isla en el camino
                    if self._path_is_clear(island_a, island_b):
                        connections.append((island_a, island_b))
        
        # Ordenar conexiones por la suma de números requeridos (más restrictivas primero)
        connections.sort(key=lambda conn: (
            self.game.islands[conn[0]]['num'] + self.game.islands[conn[1]]['num']
        ), reverse=True)
        
        return connections
    
    def _backtrack(self):
        """
        Función recursiva de backtracking
        Prueba todas las combinaciones posibles de puentes
        
        Returns:
            bool - True si se encontró solución
        """
        self.iterations += 1
        
        # Verificar si ya se encontró la solución
        if self._is_solution():
            return True
        
        # Verificar si el estado actual es inválido (poda temprana)
        if self._is_invalid_state():
            return False
        
        # Encontrar la isla con menos opciones restantes (heurística MRV - Minimum Remaining Values)
        island = self._select_island_with_min_remaining()
        
        if island is None:
            # No hay más islas incompletas, pero no es solución
            return False
        
        # Obtener vecinos válidos para esta isla
        neighbors = self._get_valid_neighbors(island)
        
        # Probar agregar puentes a cada vecino
        for neighbor in neighbors:
            # Probar con 0, 1 o 2 puentes (en orden)
            for num_bridges in [1, 2]:
                # Verificar si podemos agregar estos puentes
                if self._can_add_bridges(island, neighbor, num_bridges):
                    # Agregar puente(s)
                    added_successfully = True
                    for _ in range(num_bridges):
                        success, msg, bridge_info = self.game.create_bridge(island, neighbor)
                        if not success:
                            added_successfully = False
                            break
                    
                    if added_successfully:
                        # Recursión: intentar resolver con este estado
                        if self._backtrack():
                            return True
                        
                        # Backtrack: eliminar los puentes agregados
                        for _ in range(num_bridges):
                            self.game.delete_bridge(island, neighbor)
        
        # Si ninguna opción funcionó, retornar False
        return False
    
    def _path_is_clear(self, island_a, island_b):
        """
        Verifica si el camino entre dos islas está libre de otras islas
        
        Args:
            island_a: (r, c)
            island_b: (r, c)
        
        Returns:
            bool
        """
        r1, c1 = island_a
        r2, c2 = island_b
        
        if r1 == r2:  # Horizontal
            c_min, c_max = min(c1, c2), max(c1, c2)
            for c in range(c_min + 1, c_max):
                if self.game.board[r1][c] != 0:
                    return False
        elif c1 == c2:  # Vertical
            r_min, r_max = min(r1, r2), max(r1, r2)
            for r in range(r_min + 1, r_max):
                if self.game.board[r][c1] != 0:
                    return False
        else:
            return False
        
        return True
    
    def _select_island_with_min_remaining(self):
        """
        Selecciona la isla con menos puentes restantes por colocar (heurística MRV)
        Esto reduce el factor de ramificación y hace el backtracking más eficiente
        
        Returns:
            (r, c) o None si todas las islas están completas
        """
        min_remaining = float('inf')
        selected_island = None
        
        for pos, info in self.game.islands.items():
            used = sum(info['bridges'].values())
            remaining = info['num'] - used
            
            if remaining > 0 and remaining < min_remaining:
                min_remaining = remaining
                selected_island = pos
        
        return selected_island
    
    def _is_solution(self):
        """
        Verifica si el estado actual es una solución válida
        
        Returns:
            bool
        """
        # Todas las islas deben estar completas
        if not self._all_islands_complete():
            return False
        
        # El grafo debe estar conectado
        if not self._is_connected():
            return False
        
        return True
    
    def _is_invalid_state(self):
        """
        Verifica si el estado actual es inválido (poda temprana)
        Esto permite cortar ramas del árbol de búsqueda temprano
        
        Returns:
            bool - True si el estado es inválido
        """
        for pos, info in self.game.islands.items():
            used = sum(info['bridges'].values())
            
            # Si una isla tiene más puentes de los necesarios, estado inválido
            if used > info['num']:
                return True
            
            # Si una isla no puede completarse (no tiene suficientes vecinos disponibles)
            remaining = info['num'] - used
            if remaining > 0:
                # Contar cuántos puentes más se pueden agregar desde esta isla
                max_addable = 0
                neighbors = self._get_valid_neighbors(pos)
                for neighbor in neighbors:
                    current_bridges = info['bridges'].get(neighbor, 0)
                    max_addable += (2 - current_bridges)  # Máximo 2 puentes por conexión
                
                if max_addable < remaining:
                    return True
        
        return False
    
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
