from tkinter import Tk, Canvas, Frame, Label, Button, filedialog, LEFT, RIGHT, BOTH, font
from game_logic import HashiGame

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
        
        # Inicializar la lógica del juego
        self.game = HashiGame(rows, cols, board)
        
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

        # Datos de visualización (solo para GUI)
        self.islands_visual = {}  # (r,c) -> {'id':oval_id, 'text':text_id, 'lines':{(r2,c2): [line_ids]}}
        # Mapeo line_id -> (isla_a, isla_b) para funcionalidad de eliminar con clic
        self.line_to_bridge = {}
        self.selected = None

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
                    self.islands_visual[(r, c)] = {'id': id_oval, 'text': id_text}

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
        if cell in self.islands_visual:
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
        info = self.islands_visual[cell]
        self.canvas.itemconfig(info['id'], outline=COLOR_SELECTED, width=3)

    def unhighlight(self, cell):
        """Quita el resaltado de una isla"""
        info = self.islands_visual[cell]
        self.canvas.itemconfig(info['id'], outline=COLOR_ISLAND_BORDER, width=2)

    def try_create_bridge(self, a, b):
        """Intenta crear un puente entre dos islas"""
        # Usar la lógica del juego para validar y crear el puente
        success, msg, bridge_info = self.game.create_bridge(a, b)
        
        if not success:
            return False, msg
        
        # Dibujar el puente en el canvas
        self.draw_bridge(bridge_info)
        
        self.update_status()
        self.msg_label.config(text="Puente creado")
        
        # Verificar victoria
        if self.game.check_victory():
            self.msg_label.config(text="¡Victoria! Todas las islas están conectadas y completas.")
        
        return True, "OK"
    
    def draw_bridge(self, bridge_info):
        """Dibuja un puente en el canvas basado en la información del puente"""
        a = bridge_info['a']
        b = bridge_info['b']
        count = bridge_info['count']
        is_horizontal = bridge_info['is_horizontal']
        
        r1, c1 = a
        r2, c2 = b
        
        # Calcular coordenadas del canvas
        cx1 = MARGIN + c1 * CELL_SIZE + CELL_SIZE // 2
        cy1 = MARGIN + r1 * CELL_SIZE + CELL_SIZE // 2
        cx2 = MARGIN + c2 * CELL_SIZE + CELL_SIZE // 2
        cy2 = MARGIN + r2 * CELL_SIZE + CELL_SIZE // 2
        
        # Calcular extremos de la línea (desde circunferencia + gap)
        if is_horizontal:
            signx = 1 if cx2 > cx1 else -1
            x1 = cx1 + signx * (ISLAND_RADIUS + BRIDGE_GAP)
            x2 = cx2 - signx * (ISLAND_RADIUS + BRIDGE_GAP)
            y1 = cy1
            y2 = cy2
        else:
            signy = 1 if cy2 > cy1 else -1
            y1 = cy1 + signy * (ISLAND_RADIUS + BRIDGE_GAP)
            y2 = cy2 - signy * (ISLAND_RADIUS + BRIDGE_GAP)
            x1 = cx1
            x2 = cx2
        
        # Obtener o crear almacenamiento de líneas visuales
        av = self.islands_visual[a]
        bv = self.islands_visual[b]
        av.setdefault('lines', {})
        bv.setdefault('lines', {})
        
        lines_ab = av['lines'].get(b, [])
        
        if count == 1:
            # Primer puente: dibujar centrado
            line_id = self.canvas.create_line(x1, y1, x2, y2, width=5, fill=COLOR_BRIDGE)
            lines_ab = [line_id]
            self.line_to_bridge[line_id] = (a, b)
        elif count == 2:
            # Segundo puente: crear dos líneas paralelas
            off = PARALLEL_OFF
            if is_horizontal:
                if len(lines_ab) > 0:
                    # Ajustar la primera línea
                    first = lines_ab[0]
                    self.canvas.coords(first, x1, y1 - off, x2, y2 - off)
                    self.canvas.itemconfig(first, width=3)
                else:
                    first = self.canvas.create_line(x1, y1 - off, x2, y2 - off, width=3, fill=COLOR_BRIDGE)
                second = self.canvas.create_line(x1, y1 + off, x2, y2 + off, width=3, fill=COLOR_BRIDGE)
            else:
                if len(lines_ab) > 0:
                    first = lines_ab[0]
                    self.canvas.coords(first, x1 - off, y1, x2 - off, y2)
                    self.canvas.itemconfig(first, width=3)
                else:
                    first = self.canvas.create_line(x1 - off, y1, x2 - off, y2, width=3, fill=COLOR_BRIDGE)
                second = self.canvas.create_line(x1 + off, y1, x2 + off, y2, width=3, fill=COLOR_BRIDGE)
            lines_ab = [first, second]
            self.line_to_bridge[first] = (a, b)
            self.line_to_bridge[second] = (a, b)
        
        # Guardar las líneas
        av['lines'][b] = lines_ab
        bv['lines'][a] = lines_ab

    def undo(self):
        """Deshace el último puente creado"""
        # Usar la lógica del juego para deshacer
        success, msg, bridge_info = self.game.undo_last_bridge()
        
        if not success:
            self.msg_label.config(text=msg)
            return
        
        # Eliminar el puente visual
        self.remove_bridge_visual(bridge_info['a'], bridge_info['b'])
        
        self.update_status()
        self.msg_label.config(text=msg)

    def delete_bridge_by_line(self, line_id):
        """Elimina un puente cuando el usuario hace clic en su línea"""
        if line_id not in self.line_to_bridge:
            return
        
        a, b = self.line_to_bridge[line_id]
        
        # Usar la lógica del juego para eliminar
        success, msg, bridge_info = self.game.delete_bridge(a, b)
        
        if not success:
            self.msg_label.config(text=msg)
            return
        
        # Eliminar el puente visual
        self.remove_bridge_visual(a, b)
        
        self.update_status()
        self.msg_label.config(text=msg)
    
    def remove_bridge_visual(self, a, b):
        """Elimina las líneas visuales de un puente del canvas y redibuja si quedan puentes"""
        av = self.islands_visual.get(a)
        bv = self.islands_visual.get(b)
        if not av or not bv:
            return
        
        # Eliminar todas las líneas actuales
        lines = av.get('lines', {}).get(b, [])
        for lid in lines:
            try:
                self.canvas.delete(lid)
                if lid in self.line_to_bridge:
                    del self.line_to_bridge[lid]
            except Exception:
                pass
        
        # Eliminar almacenamiento de líneas visuales
        if 'lines' in av and b in av['lines']:
            del av['lines'][b]
        if 'lines' in bv and a in bv['lines']:
            del bv['lines'][a]
        
        # Verificar cuántos puentes quedan en la lógica del juego
        island_info = self.game.get_island_info(a)
        if island_info and b in island_info['bridges']:
            remaining_count = island_info['bridges'][b]
            if remaining_count > 0:
                # Redibujar el/los puente(s) restante(s)
                bridge_info = {
                    'a': a,
                    'b': b,
                    'count': remaining_count,
                    'is_horizontal': a[0] == b[0]
                }
                self.draw_bridge(bridge_info)

    def update_status(self):
        """Actualiza el panel de estado"""
        # Obtener información del estado del juego
        total = self.game.get_total_bridges()
        
        sel = "-"
        if self.selected:
            island_info = self.game.get_island_info(self.selected)
            if island_info:
                sel = f"{island_info['used']}/{island_info['num']}"
        
        self.status_label.config(text=f"Puentes: {total}\nSelección: {sel}")
