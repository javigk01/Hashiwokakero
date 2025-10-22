from tkinter import Tk, Canvas, Frame, Label, Button, filedialog, LEFT, RIGHT, BOTH, font

# Constantes de visualización
CELL_SIZE = 60
MARGIN = 20
ISLAND_RADIUS = 18
BRIDGE_GAP = 6  # distancia desde la circunferencia de la isla donde inicia el puente
PARALLEL_OFF = 6  # desplazamiento para puentes dobles

# Paleta de colores mejorada
COLOR_BG = "#F5F5F5"  # fondo general (gris claro)
COLOR_CANVAS_BG = "#FFFFFF"  # fondo del canvas (blanco)
COLOR_GRID = "#E0E0E0"  # líneas de la grilla (gris suave)
COLOR_ISLAND = "#FFE5B4"  # fondo de las islas (durazno claro)
COLOR_ISLAND_BORDER = "#8B4513"  # borde de las islas (marrón)
COLOR_ISLAND_TEXT = "#2C3E50"  # texto de las islas (azul oscuro)
COLOR_BRIDGE = "#34495E"  # color de los puentes (gris azulado)
COLOR_SELECTED = "#E74C3C"  # color de selección (rojo)
COLOR_BUTTON_BG = "#3498DB"  # fondo de botones (azul)
COLOR_BUTTON_FG = "#FFFFFF"  # texto de botones (blanco)

class HashiGUI:
    def __init__(self, master, rows, cols, board):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.board = board
        self.width = MARGIN * 2 + cols * CELL_SIZE
        self.height = MARGIN * 2 + rows * CELL_SIZE
        
        # Configurar fuentes personalizadas
        self.font_title = font.Font(family="Segoe UI", size=10, weight="bold")
        self.font_label = font.Font(family="Segoe UI", size=9)
        self.font_island = font.Font(family="Arial", size=14, weight="bold")
        
        # Diseño: canvas a la izquierda, panel de estado a la derecha
        container = Frame(master, bg=COLOR_BG)
        container.pack(fill=BOTH, expand=True)
        self.canvas = Canvas(container, width=self.width, height=self.height, bg=COLOR_CANVAS_BG)
        self.canvas.pack(side=LEFT, padx=10, pady=10)

        self.status_frame = Frame(container, bg=COLOR_BG)
        self.status_frame.pack(side=RIGHT, fill=BOTH, padx=10, pady=10)
        self.status_label = Label(self.status_frame, text="Puentes: 0\nSelección: -", 
                                  bg=COLOR_BG, fg=COLOR_ISLAND_TEXT, font=self.font_label, justify=LEFT)
        self.status_label.pack(padx=10, pady=10)
        self.msg_label = Label(self.status_frame, text="", bg=COLOR_BG, fg=COLOR_ISLAND_TEXT, 
                               font=self.font_label, wraplength=150)
        self.msg_label.pack(padx=10, pady=6)

        # Islas: almacena contadores de puentes vecinos e IDs de líneas
        self.islands = {}  # (r,c) -> {'num':n, 'id':oval_id, 'text':text_id, 'bridges':{(r2,c2):count}, 'lines':{(r2,c2): [line_ids]}}
        self.bridges = []  # lista de IDs de líneas del canvas (para contabilidad)
        # Ocupación por celda entre islas: (r,c) -> {'h':count,'v':count}
        self.occupancy = {}
        # Historial de acciones para deshacer: lista de dicts con claves: a,b,lines,occupancy_cells
        self.history = []
        self.selected = None
        # Mapeo line_id -> (isla_a, isla_b) para funcionalidad de eliminar con clic
        self.line_to_bridge = {}

        self.draw_grid()
        self.draw_islands()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_grid(self):
        """Dibuja la grilla del tablero"""
        for r in range(self.rows + 1):
            y = MARGIN + r * CELL_SIZE
            self.canvas.create_line(MARGIN, y, self.width - MARGIN, y, fill=COLOR_GRID, width=1)
        for c in range(self.cols + 1):
            x = MARGIN + c * CELL_SIZE
            self.canvas.create_line(x, MARGIN, x, self.height - MARGIN, fill=COLOR_GRID, width=1)

    def draw_islands(self):
        """Dibuja las islas en el tablero"""
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.board[r][c]
                if v > 0:
                    x = MARGIN + c * CELL_SIZE + CELL_SIZE // 2
                    y = MARGIN + r * CELL_SIZE + CELL_SIZE // 2
                    radius = ISLAND_RADIUS
                    id_oval = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, 
                                                      fill=COLOR_ISLAND, outline=COLOR_ISLAND_BORDER, width=2)
                    id_text = self.canvas.create_text(x, y, text=str(v), font=self.font_island, fill=COLOR_ISLAND_TEXT)
                    self.islands[(r, c)] = {'num': v, 'id': id_oval, 'text': id_text, 'bridges': {}}

    def on_click(self, event):
        """Maneja los clics del usuario en el canvas"""
        # Verificar si se hizo clic en una línea de puente primero
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        if clicked_item in self.line_to_bridge:
            # El usuario hizo clic en una línea de puente - eliminarla
            self.delete_bridge_by_line(clicked_item)
            return
        
        cell = self.pixel_to_cell(event.x, event.y)
        if not cell:
            return
        if cell in self.islands:
            if self.selected is None:
                self.selected = cell
                self.highlight(cell)
            else:
                if cell == self.selected:
                    self.unhighlight(cell)
                    self.selected = None
                    return
                # intentar crear puente
                ok, msg = self.try_create_bridge(self.selected, cell)
                if not ok:
                    print("No se puede crear puente:", msg)
                    self.msg_label.config(text=msg)
                else:
                    print("Puente creado")
                self.unhighlight(self.selected)
                self.selected = None

    def pixel_to_cell(self, x, y):
        """Convierte coordenadas de píxel a coordenadas de celda"""
        if x < MARGIN or y < MARGIN or x > self.width - MARGIN or y > self.height - MARGIN:
            return None
        c = (x - MARGIN) // CELL_SIZE
        r = (y - MARGIN) // CELL_SIZE
        return int(r), int(c)

    def highlight(self, cell):
        """Resalta una isla seleccionada"""
        info = self.islands[cell]
        self.canvas.itemconfig(info['id'], outline=COLOR_SELECTED, width=3)

    def unhighlight(self, cell):
        """Quita el resaltado de una isla"""
        info = self.islands[cell]
        self.canvas.itemconfig(info['id'], outline=COLOR_ISLAND_BORDER, width=2)

    def try_create_bridge(self, a, b):
        """Intenta crear un puente entre dos islas"""
        # Verificar alineación
        (r1, c1) = a
        (r2, c2) = b
        if r1 != r2 and c1 != c2:
            return False, "No alineadas (diagonal)"
        
        # Verificar si alguna isla excedería su capacidad
        ai = self.islands[a]
        bi = self.islands[b]
        used_a = sum(ai['bridges'].values())
        used_b = sum(bi['bridges'].values())
        
        if used_a >= ai['num']:
            return False, f"Isla {ai['num']} ya tiene {used_a} puentes (máximo permitido)"
        if used_b >= bi['num']:
            return False, f"Isla {bi['num']} ya tiene {used_b} puentes (máximo permitido)"
        
        # Determinar dirección y camino
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
        # Verificar cantidad de puentes existentes entre estas dos islas
        key = b
        existing = ai['bridges'].get(key, 0)
        if existing >= 2:
            return False, "Ya hay 2 puentes entre esas islas"
        # Crear puente visualmente (como línea). Calcular extremos para que se detengan en la circunferencia + gap
        cx1 = MARGIN + c1 * CELL_SIZE + CELL_SIZE // 2
        cy1 = MARGIN + r1 * CELL_SIZE + CELL_SIZE // 2
        cx2 = MARGIN + c2 * CELL_SIZE + CELL_SIZE // 2
        cy2 = MARGIN + r2 * CELL_SIZE + CELL_SIZE // 2
        # Vector de dirección
        dx = cx2 - cx1
        dy = cy2 - cy1
        # Normalizar solo para alineados con ejes
        if dx != 0:
            signx = 1 if dx > 0 else -1
            x1 = cx1 + signx * (ISLAND_RADIUS + BRIDGE_GAP)
            x2 = cx2 - signx * (ISLAND_RADIUS + BRIDGE_GAP)
            y1 = cy1
            y2 = cy2
        else:
            signy = 1 if dy > 0 else -1
            y1 = cy1 + signy * (ISLAND_RADIUS + BRIDGE_GAP)
            y2 = cy2 - signy * (ISLAND_RADIUS + BRIDGE_GAP)
            x1 = cx1
            x2 = cx2
        # Manejar líneas por par
        ai.setdefault('lines', {})
        bi.setdefault('lines', {})
        lines_ab = ai['lines'].get(key, [])

        # Corregir: si el conteo existente no coincide con las líneas reales, reiniciar
        if existing != len(lines_ab):
            existing = len(lines_ab)
            if existing == 0:
                ai['bridges'][key] = 0
                bi['bridges'][a] = 0

        if existing == 0:
            # Primer puente: dibujar centrado
            if r1 == r2:
                line_id = self.canvas.create_line(x1, y1, x2, y2, width=5, fill=COLOR_BRIDGE)
            else:
                line_id = self.canvas.create_line(x1, y1, x2, y2, width=5, fill=COLOR_BRIDGE)
            lines_ab = [line_id]
            # Registrar línea para eliminar con clic
            self.line_to_bridge[line_id] = (a, b)
        else:
            # Segundo puente: crear dos líneas paralelas y ajustar la primera
            # Desplazamientos
            off = PARALLEL_OFF
            if r1 == r2:
                # horizontal: ajustar primera a y-off, segunda a y+off
                first = lines_ab[0]
                self.canvas.coords(first, x1, y1 - off, x2, y2 - off)
                self.canvas.itemconfig(first, width=3)
                second = self.canvas.create_line(x1, y1 + off, x2, y2 + off, width=3, fill=COLOR_BRIDGE)
            else:
                first = lines_ab[0]
                self.canvas.coords(first, x1 - off, y1, x2 - off, y2)
                self.canvas.itemconfig(first, width=3)
                second = self.canvas.create_line(x1 + off, y1, x2 + off, y2, width=3, fill=COLOR_BRIDGE)
            lines_ab = [first, second]
            # Registrar ambas líneas para eliminar con clic
            self.line_to_bridge[first] = (a, b)
            self.line_to_bridge[second] = (a, b)

        # Guardar de vuelta
        ai['lines'][key] = lines_ab
        bi['lines'][a] = lines_ab
        # Registrar en ocupación las celdas entre islas y guardarlas para deshacer
        occ_cells = []
        if r1 == r2:
            for c in range(min(c1, c2) + 1, max(c1, c2)):
                occ = self.occupancy.setdefault((r1, c), {'h': 0, 'v': 0})
                occ['h'] += 1
                occ_cells.append(((r1, c), 'h'))
        else:
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                occ = self.occupancy.setdefault((r, c1), {'h': 0, 'v': 0})
                occ['v'] += 1
                occ_cells.append(((r, c1), 'v'))

        self.bridges.extend(lines_ab)
        # Actualizar datos
        ai['bridges'][b] = existing + 1
        bi['bridges'][a] = existing + 1
        # Agregar al historial para deshacer
        self.history.append({'a': a, 'b': b, 'lines': list(lines_ab), 'occ_cells': occ_cells})
        self.update_status()
        self.msg_label.config(text="Puente creado")
        # Verificar victoria
        if self.check_victory():
            self.msg_label.config(text="¡Victoria! Todas las islas están conectadas y completas.")
        return True, "OK"

    def undo(self):
        """Deshace el último puente creado"""
        if not self.history:
            self.msg_label.config(text="Nada que deshacer")
            return
        last = self.history.pop()
        a = last['a']
        b = last['b']
        lines = last['lines']
        # Eliminar líneas del canvas
        for lid in lines:
            try:
                self.canvas.delete(lid)
            except Exception:
                pass
        # Decrementar ocupación
        for cell, t in last['occ_cells']:
            occ = self.occupancy.get(cell)
            if occ:
                occ[t] = max(0, occ[t] - 1)
        # Decrementar contadores de puentes y eliminar entradas de líneas
        if b in self.islands[a]['bridges']:
            self.islands[a]['bridges'][b] -= 1
            if self.islands[a]['bridges'][b] <= 0:
                del self.islands[a]['bridges'][b]
        if a in self.islands[b]['bridges']:
            self.islands[b]['bridges'][a] -= 1
            if self.islands[b]['bridges'][a] <= 0:
                del self.islands[b]['bridges'][a]
        # Ajustar almacenamiento de líneas
        if 'lines' in self.islands[a] and b in self.islands[a]['lines']:
            del self.islands[a]['lines'][b]
        if 'lines' in self.islands[b] and a in self.islands[b]['lines']:
            del self.islands[b]['lines'][a]
        self.update_status()
        self.msg_label.config(text="Se deshizo el último puente")

    def delete_bridge_by_line(self, line_id):
        """Elimina un puente cuando el usuario hace clic en su línea"""
        if line_id not in self.line_to_bridge:
            return
        
        a, b = self.line_to_bridge[line_id]
        ai = self.islands[a]
        bi = self.islands[b]
        
        # Obtener todas las líneas para este puente
        lines = ai.get('lines', {}).get(b, [])
        if not lines:
            return
        
        # Encontrar la entrada del historial para este puente (buscar hacia atrás)
        history_idx = None
        for idx in range(len(self.history) - 1, -1, -1):
            h = self.history[idx]
            if h['a'] == a and h['b'] == b:
                history_idx = idx
                break
        
        if history_idx is None:
            return
        
        # Obtener la entrada del historial
        hist_entry = self.history[history_idx]
        
        # Eliminar líneas del canvas
        for lid in hist_entry['lines']:
            try:
                self.canvas.delete(lid)
                if lid in self.line_to_bridge:
                    del self.line_to_bridge[lid]
            except Exception:
                pass
        
        # Decrementar ocupación
        for cell, t in hist_entry['occ_cells']:
            occ = self.occupancy.get(cell)
            if occ:
                occ[t] = max(0, occ[t] - 1)
        
        # Decrementar contadores de puentes
        if b in ai['bridges']:
            ai['bridges'][b] -= 1
            if ai['bridges'][b] <= 0:
                del ai['bridges'][b]
        if a in bi['bridges']:
            bi['bridges'][a] -= 1
            if bi['bridges'][a] <= 0:
                del bi['bridges'][a]
        
        # Eliminar almacenamiento de líneas
        if 'lines' in ai and b in ai['lines']:
            del ai['lines'][b]
        if 'lines' in bi and a in bi['lines']:
            del bi['lines'][a]
        
        # Eliminar del historial
        self.history.pop(history_idx)
        
        self.update_status()
        self.msg_label.config(text="Puente eliminado")

    def check_victory(self):
        """Verifica si se ha ganado el juego"""
        # Verificar que todas las islas satisfagan su número
        for pos, info in self.islands.items():
            used = sum(info['bridges'].values())
            if used != info['num']:
                return False
        # Verificar conectividad vía DFS
        # Construir adyacencia
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

    def update_status(self):
        """Actualiza el panel de estado"""
        total = 0
        for v in self.islands.values():
            total += sum(v['bridges'].values())
        # Cada puente se cuenta dos veces (ambos extremos)
        total = total // 2
        sel = "-"
        if self.selected:
            info = self.islands[self.selected]
            used = sum(info['bridges'].values())
            sel = f"{used}/{info['num']}"
        self.status_label.config(text=f"Puentes: {total}\nSelección: {sel}")
