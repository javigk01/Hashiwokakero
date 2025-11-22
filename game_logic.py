"""
Lógica del juego Hashiwokakero (Hashi)
Maneja el estado del juego, validaciones y operaciones independientemente de la interfaz gráfica
"""

class HashiGame:
    """Clase que contiene toda la lógica del juego Hashiwokakero"""
    
    def __init__(self, rows, cols, board):
        """
        Inicializa el juego con el tablero dado
        
        Args:
            rows: número de filas
            cols: número de columnas
            board: matriz con los valores de las islas (0 = vacío, >0 = isla con ese número)
        """
        self.rows = rows
        self.cols = cols
        self.board = board
        
        # Estructuras de datos para el estado del juego
        # islands: (r,c) -> {'num': n, 'bridges': {(r2,c2): count}}
        self.islands = {}
        
        # occupancy: (r,c) -> {'h': count, 'v': count}
        self.occupancy = {}
        
        # Historial de acciones: lista de dicts con 'a', 'b', 'occ_cells'
        self.history = []
        
        # Inicializar islas
        self._init_islands()
    
    def _init_islands(self):
        """Inicializa el diccionario de islas basado en el tablero"""
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.board[r][c]
                if v > 0:
                    self.islands[(r, c)] = {
                        'num': v,
                        'bridges': {}
                    }
    
    def get_island_info(self, pos):
        """
        Obtiene información de una isla
        
        Args:
            pos: tupla (r, c)
            
        Returns:
            dict con 'num', 'bridges', y 'used' (puentes usados)
        """
        if pos not in self.islands:
            return None
        
        info = self.islands[pos]
        used = sum(info['bridges'].values())
        return {
            'num': info['num'],
            'bridges': dict(info['bridges']),
            'used': used
        }
    
    def get_all_islands(self):
        """Retorna lista de todas las posiciones de islas"""
        return list(self.islands.keys())
    
    def can_create_bridge(self, a, b):
        """
        Verifica si se puede crear un puente entre dos islas
        
        Args:
            a: tupla (r1, c1)
            b: tupla (r2, c2)
            
        Returns:
            tupla (bool, str) - (puede_crear, mensaje_error)
        """
        r1, c1 = a
        r2, c2 = b
        
        # Verificar que ambas sean islas
        if a not in self.islands or b not in self.islands:
            return False, "Una o ambas posiciones no son islas"
        
        # Verificar alineación
        if r1 != r2 and c1 != c2:
            return False, "No alineadas (diagonal)"
        
        # Verificar capacidad de las islas
        ai = self.islands[a]
        bi = self.islands[b]
        used_a = sum(ai['bridges'].values())
        used_b = sum(bi['bridges'].values())
        
        if used_a >= ai['num']:
            return False, f"Isla {ai['num']} ya tiene {used_a} puentes (máximo permitido)"
        if used_b >= bi['num']:
            return False, f"Isla {bi['num']} ya tiene {used_b} puentes (máximo permitido)"
        
        # Verificar cantidad de puentes existentes entre estas dos islas
        existing = ai['bridges'].get(b, 0)
        if existing >= 2:
            return False, "Ya hay 2 puentes entre esas islas"
        
        # Verificar camino libre
        if r1 == r2:
            # horizontal
            step = 1 if c2 > c1 else -1
            for c in range(c1 + step, c2, step):
                if self.board[r1][c] != 0:
                    return False, "Hay isla en el camino"
                occ = self.occupancy.get((r1, c), {'h': 0, 'v': 0})
                if occ['v'] > 0:
                    return False, "Cruza un puente vertical existente"
        else:
            # vertical
            step = 1 if r2 > r1 else -1
            for r in range(r1 + step, r2, step):
                if self.board[r][c1] != 0:
                    return False, "Hay isla en el camino"
                occ = self.occupancy.get((r, c1), {'h': 0, 'v': 0})
                if occ['h'] > 0:
                    return False, "Cruza un puente horizontal existente"
        
        return True, "OK"
    
    def create_bridge(self, a, b, dry_run=False):
        """
        Crea un puente entre dos islas
        
        Args:
            a: tupla (r1, c1)
            b: tupla (r2, c2)
            dry_run: si es True, solo verifica sin crear
            
        Returns:
            tupla (bool, str, dict) - (éxito, mensaje, info_puente)
            info_puente contiene: {'a': a, 'b': b, 'count': nuevo_count, 'cells': celdas_ocupadas}
        """
        can_create, msg = self.can_create_bridge(a, b)
        if not can_create:
            return False, msg, None
        
        # Si es dry_run, retornar sin modificar el estado
        if dry_run:
            return True, "OK", None
        
        r1, c1 = a
        r2, c2 = b
        
        ai = self.islands[a]
        bi = self.islands[b]
        
        # Obtener cantidad existente
        existing = ai['bridges'].get(b, 0)
        
        # Registrar ocupación
        occ_cells = []
        if r1 == r2:
            # horizontal
            for c in range(min(c1, c2) + 1, max(c1, c2)):
                occ = self.occupancy.setdefault((r1, c), {'h': 0, 'v': 0})
                occ['h'] += 1
                occ_cells.append(((r1, c), 'h'))
        else:
            # vertical
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                occ = self.occupancy.setdefault((r, c1), {'h': 0, 'v': 0})
                occ['v'] += 1
                occ_cells.append(((r, c1), 'v'))
        
        # Actualizar contadores
        new_count = existing + 1
        ai['bridges'][b] = new_count
        bi['bridges'][a] = new_count
        
        # Agregar al historial
        self.history.append({
            'a': a,
            'b': b,
            'occ_cells': occ_cells
        })
        
        bridge_info = {
            'a': a,
            'b': b,
            'count': new_count,
            'cells': occ_cells,
            'is_horizontal': r1 == r2
        }
        
        return True, "Puente creado", bridge_info
    
    def undo_last_bridge(self):
        """
        Deshace el último puente creado
        
        Returns:
            tupla (bool, str, dict) - (éxito, mensaje, info_puente_eliminado)
        """
        if not self.history:
            return False, "Nada que deshacer", None
        
        last = self.history.pop()
        a = last['a']
        b = last['b']
        
        # Decrementar ocupación
        for cell, t in last['occ_cells']:
            occ = self.occupancy.get(cell)
            if occ:
                occ[t] = max(0, occ[t] - 1)
        
        # Decrementar contadores
        if b in self.islands[a]['bridges']:
            self.islands[a]['bridges'][b] -= 1
            if self.islands[a]['bridges'][b] <= 0:
                del self.islands[a]['bridges'][b]
        
        if a in self.islands[b]['bridges']:
            self.islands[b]['bridges'][a] -= 1
            if self.islands[b]['bridges'][a] <= 0:
                del self.islands[b]['bridges'][a]
        
        bridge_info = {
            'a': a,
            'b': b,
            'cells': last['occ_cells']
        }
        
        return True, "Se deshizo el último puente", bridge_info
    
    def delete_bridge(self, a, b):
        """
        Elimina UN puente entre dos islas (si hay 2, elimina 1 y deja el otro)
        Args:
            a: tupla (r1, c1)
            b: tupla (r2, c2)
        Returns:
            tupla (bool, str, dict) - (éxito, mensaje, info_puente_eliminado)
        """
        if a not in self.islands or b not in self.islands:
            return False, "Islas no válidas", None
        
        ai = self.islands[a]
        if b not in ai['bridges']:
            return False, "No hay puente entre esas islas", None
        
        count_before = ai['bridges'][b]
        if count_before <= 0:
            return False, "No hay puente entre esas islas", None
        
        # Buscar en el historial el último puente entre a y b (en cualquier orden)
        history_idx = None
        for idx in range(len(self.history) - 1, -1, -1):
            h = self.history[idx]
            if (h['a'] == a and h['b'] == b) or (h['a'] == b and h['b'] == a):
                history_idx = idx
                break
        
        if history_idx is None:
            return False, "Puente no encontrado en historial", None
        
        hist_entry = self.history[history_idx]
        
        # Decrementar ocupación
        for cell, t in hist_entry['occ_cells']:
            occ = self.occupancy.get(cell)
            if occ:
                occ[t] = max(0, occ[t] - 1)
        
        # Decrementar contadores (de uno en uno)
        if b in ai['bridges']:
            ai['bridges'][b] -= 1
            if ai['bridges'][b] <= 0:
                del ai['bridges'][b]
        
        bi = self.islands[b]
        if a in bi['bridges']:
            bi['bridges'][a] -= 1
            if bi['bridges'][a] <= 0:
                del bi['bridges'][a]
        
        # Eliminar del historial
        self.history.pop(history_idx)
        
        bridge_info = {
            'a': a,
            'b': b,
            'cells': hist_entry['occ_cells'],
            'count_after': ai['bridges'].get(b, 0)  # cuántos quedan después de eliminar
        }
        
        return True, "Puente eliminado", bridge_info
    
    def check_victory(self):
        """
        Verifica si se ha ganado el juego
        
        Returns:
            bool - True si todas las islas están completas y conectadas
        """
        # Verificar que todas las islas satisfagan su número
        for pos, info in self.islands.items():
            used = sum(info['bridges'].values())
            if used != info['num']:
                return False
        
        # Verificar conectividad vía DFS
        nodes = list(self.islands.keys())
        if not nodes:
            return False
        
        adj = {n: set() for n in nodes}
        for n, info in self.islands.items():
            for nb in info['bridges'].keys():
                adj[n].add(nb)
        
        # DFS
        start = nodes[0]
        seen = {start}
        stack = [start]
        while stack:
            cur = stack.pop()
            for nb in adj[cur]:
                if nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        
        return len(seen) == len(nodes)
    
    def get_total_bridges(self):
        """
        Retorna el número total de puentes en el tablero
        
        Returns:
            int - cantidad de puentes
        """
        total = 0
        for info in self.islands.values():
            total += sum(info['bridges'].values())
        # Cada puente se cuenta dos veces (ambos extremos)
        return total // 2
    
    def get_game_state(self):
        """
        Retorna el estado completo del juego
        
        Returns:
            dict con información del estado actual
        """
        return {
            'rows': self.rows,
            'cols': self.cols,
            'islands': {pos: {'num': info['num'], 'bridges': dict(info['bridges'])} 
                       for pos, info in self.islands.items()},
            'total_bridges': self.get_total_bridges(),
            'can_undo': len(self.history) > 0,
            'victory': self.check_victory()
        }
