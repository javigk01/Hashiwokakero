"""
Hashiwokakero - Entrega 1
Interfaz básica usando Tkinter: lectura de archivo, visualización y conectar islas manualmente.
"""
import sys
import os
from tkinter import Tk, Canvas, Frame, Label, Button, filedialog, LEFT, RIGHT, BOTH, TOP, BOTTOM

CELL_SIZE = 60
MARGIN = 20


def parse_board(path):
    """Lee el archivo y retorna (rows, cols, board) donde board es lista de listas de int."""
    with open(path, "r", encoding="utf-8") as f:
        first = f.readline().strip()
        if not first:
            raise ValueError("Archivo vacío o formato inválido")
        parts = first.split(",")
        if len(parts) != 2:
            raise ValueError("Primera línea debe ser 'rows,cols'")
        rows = int(parts[0])
        cols = int(parts[1])
        board = []
        for _ in range(rows):
            line = f.readline().strip()
            if len(line) < cols:
                raise ValueError("Línea demasiado corta en el tablero")
            row = [int(ch) for ch in line[:cols]]
            board.append(row)
    return rows, cols, board


class HashiGUI:
    def __init__(self, master, rows, cols, board):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.board = board
        self.width = MARGIN * 2 + cols * CELL_SIZE
        self.height = MARGIN * 2 + rows * CELL_SIZE
        # layout: left canvas, right status
        container = Frame(master)
        container.pack(fill=BOTH, expand=True)
        self.canvas = Canvas(container, width=self.width, height=self.height, bg="white")
        self.canvas.pack(side=LEFT)

        self.status_frame = Frame(container)
        self.status_frame.pack(side=RIGHT, fill=BOTH)
        self.status_label = Label(self.status_frame, text="Puentes: 0\nSeleccion: -")
        self.status_label.pack(padx=10, pady=10)

        # islands: store neighbor bridge counts and line ids
        self.islands = {}  # (r,c) -> {'num':n, 'id':oval_id, 'text':text_id, 'bridges':{(r2,c2):count}, 'lines':{(r2,c2): [line_ids]}}
        self.bridges = []  # list of canvas line ids (for bookkeeping)
        # occupancy per cell between islands: (r,c) -> {'h':count,'v':count}
        self.occupancy = {}
        self.selected = None

        self.draw_grid()
        self.draw_islands()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_grid(self):
        for r in range(self.rows + 1):
            y = MARGIN + r * CELL_SIZE
            self.canvas.create_line(MARGIN, y, self.width - MARGIN, y, fill="#eee")
        for c in range(self.cols + 1):
            x = MARGIN + c * CELL_SIZE
            self.canvas.create_line(x, MARGIN, x, self.height - MARGIN, fill="#eee")

    def draw_islands(self):
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.board[r][c]
                if v > 0:
                    x = MARGIN + c * CELL_SIZE + CELL_SIZE // 2
                    y = MARGIN + r * CELL_SIZE + CELL_SIZE // 2
                    radius = 18
                    id_oval = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#ffe", outline="#000")
                    id_text = self.canvas.create_text(x, y, text=str(v), font=("Arial", 12, "bold"))
                    self.islands[(r, c)] = {'num': v, 'id': id_oval, 'text': id_text, 'bridges': {}}

    def on_click(self, event):
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
                else:
                    print("Puente creado")
                self.unhighlight(self.selected)
                self.selected = None

    def pixel_to_cell(self, x, y):
        if x < MARGIN or y < MARGIN or x > self.width - MARGIN or y > self.height - MARGIN:
            return None
        c = (x - MARGIN) // CELL_SIZE
        r = (y - MARGIN) // CELL_SIZE
        return int(r), int(c)

    def highlight(self, cell):
        info = self.islands[cell]
        self.canvas.itemconfig(info['id'], outline="red", width=2)

    def unhighlight(self, cell):
        info = self.islands[cell]
        self.canvas.itemconfig(info['id'], outline="black", width=1)

    def try_create_bridge(self, a, b):
        # Check alignment
        (r1, c1) = a
        (r2, c2) = b
        if r1 != r2 and c1 != c2:
            return False, "No alineadas (diagonal)"
        # determine direction and path
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
        # check existing bridges count between these two
        ai = self.islands[a]
        bi = self.islands[b]
        key = b
        existing = ai['bridges'].get(key, 0)
        if existing >= 2:
            return False, "Ya hay 2 puentes entre esas islas"
        # create bridge visually (as line). Use offset for double bridge
        x1 = MARGIN + c1 * CELL_SIZE + CELL_SIZE // 2
        y1 = MARGIN + r1 * CELL_SIZE + CELL_SIZE // 2
        x2 = MARGIN + c2 * CELL_SIZE + CELL_SIZE // 2
        y2 = MARGIN + r2 * CELL_SIZE + CELL_SIZE // 2
        # manage lines per pair
        ai.setdefault('lines', {})
        bi.setdefault('lines', {})
        lines_ab = ai['lines'].get(key, [])

        if existing == 0:
            # first bridge: draw centered
            if r1 == r2:
                line_id = self.canvas.create_line(x1, y1, x2, y2, width=6, fill="#000")
            else:
                line_id = self.canvas.create_line(x1, y1, x2, y2, width=6, fill="#000")
            lines_ab = [line_id]
        else:
            # second bridge: create two parallel lines and adjust first
            # offsets
            off = 6
            if r1 == r2:
                # horizontal: adjust first to y-off, second to y+off
                first = lines_ab[0]
                self.canvas.coords(first, x1, y1 - off, x2, y2 - off)
                self.canvas.itemconfig(first, width=4)
                second = self.canvas.create_line(x1, y1 + off, x2, y2 + off, width=4, fill="#000")
            else:
                first = lines_ab[0]
                self.canvas.coords(first, x1 - off, y1, x2 - off, y2)
                self.canvas.itemconfig(first, width=4)
                second = self.canvas.create_line(x1 + off, y1, x2 + off, y2, width=4, fill="#000")
            lines_ab = [first, second]

        # store back
        ai['lines'][key] = lines_ab
        bi['lines'][a] = lines_ab
        # register in occupancy the cells between islands
        if r1 == r2:
            for c in range(min(c1, c2) + 1, max(c1, c2)):
                occ = self.occupancy.setdefault((r1, c), {'h': 0, 'v': 0})
                occ['h'] += 1
        else:
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                occ = self.occupancy.setdefault((r, c1), {'h': 0, 'v': 0})
                occ['v'] += 1

        self.bridges.extend(lines_ab)
        # update data
        ai['bridges'][b] = existing + 1
        bi['bridges'][a] = existing + 1
        self.update_status()
        return True, "OK"

    def update_status(self):
        total = 0
        for v in self.islands.values():
            total += sum(v['bridges'].values())
        # each bridge counted twice (both endpoints)
        total = total // 2
        sel = "-"
        if self.selected:
            info = self.islands[self.selected]
            used = sum(info['bridges'].values())
            sel = f"{used}/{info['num']}"
        self.status_label.config(text=f"Puentes: {total}\nSeleccion: {sel}")


if __name__ == "__main__":
    root = Tk()
    root.title("Hashiwokakero - Entrega 1")

    # buscar archivo ejemplo en el directorio
    default_path = os.path.join(os.path.dirname(__file__), "example.txt")
    if len(sys.argv) > 1:
        path = sys.argv[1]
    elif os.path.exists(default_path):
        path = default_path
    else:
        path = filedialog.askopenfilename(title="Abrir tablero", filetypes=[("Text files","*.txt"), ("All files","*")])
        if not path:
            print("No se seleccionó archivo. Saliendo.")
            sys.exit(0)

    rows, cols, board = parse_board(path)
    app = HashiGUI(root, rows, cols, board)
    root.mainloop()
