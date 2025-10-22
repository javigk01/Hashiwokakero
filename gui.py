from tkinter import Tk, Canvas, Frame, Label, Button, filedialog, LEFT, RIGHT, BOTH
CELL_SIZE = 60
MARGIN = 20
# visual tuning
ISLAND_RADIUS = 18
BRIDGE_GAP = 6  # distance from island circumference where bridge starts
PARALLEL_OFF = 6  # offset for double bridges

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
        self.undo_button = Button(self.status_frame, text="Deshacer último puente", command=self.undo)
        self.undo_button.pack(padx=10, pady=6)
        self.msg_label = Label(self.status_frame, text="")
        self.msg_label.pack(padx=10, pady=6)

        # islands: store neighbor bridge counts and line ids
        self.islands = {}  # (r,c) -> {'num':n, 'id':oval_id, 'text':text_id, 'bridges':{(r2,c2):count}, 'lines':{(r2,c2): [line_ids]}}
        self.bridges = []  # list of canvas line ids (for bookkeeping)
        # occupancy per cell between islands: (r,c) -> {'h':count,'v':count}
        self.occupancy = {}
        # action history for undo: list of dicts with keys: a,b,lines,occupancy_cells
        self.history = []
        self.selected = None
        # map line_id -> (island_a, island_b) for click-to-delete functionality
        self.line_to_bridge = {}

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
                    radius = ISLAND_RADIUS
                    id_oval = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#ffe", outline="#000")
                    id_text = self.canvas.create_text(x, y, text=str(v), font=("Arial", 12, "bold"))
                    self.islands[(r, c)] = {'num': v, 'id': id_oval, 'text': id_text, 'bridges': {}}

    def on_click(self, event):
        # Check if clicked on a bridge line first
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        if clicked_item in self.line_to_bridge:
            # User clicked on a bridge line - delete it
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
        
        # Check if either island would exceed its capacity
        ai = self.islands[a]
        bi = self.islands[b]
        used_a = sum(ai['bridges'].values())
        used_b = sum(bi['bridges'].values())
        
        if used_a >= ai['num']:
            return False, f"Isla {ai['num']} ya tiene {used_a} puentes (máximo permitido)"
        if used_b >= bi['num']:
            return False, f"Isla {bi['num']} ya tiene {used_b} puentes (máximo permitido)"
        
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
        key = b
        existing = ai['bridges'].get(key, 0)
        if existing >= 2:
            return False, "Ya hay 2 puentes entre esas islas"
        # create bridge visually (as line). Compute endpoints so they stop at island circumference + gap
        cx1 = MARGIN + c1 * CELL_SIZE + CELL_SIZE // 2
        cy1 = MARGIN + r1 * CELL_SIZE + CELL_SIZE // 2
        cx2 = MARGIN + c2 * CELL_SIZE + CELL_SIZE // 2
        cy2 = MARGIN + r2 * CELL_SIZE + CELL_SIZE // 2
        # direction vector
        dx = cx2 - cx1
        dy = cy2 - cy1
        # normalize for axis-aligned only
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
        # manage lines per pair
        ai.setdefault('lines', {})
        bi.setdefault('lines', {})
        lines_ab = ai['lines'].get(key, [])

        # Fix: if existing count doesn't match actual lines, reset
        if existing != len(lines_ab):
            existing = len(lines_ab)
            if existing == 0:
                ai['bridges'][key] = 0
                bi['bridges'][a] = 0

        if existing == 0:
            # first bridge: draw centered
            if r1 == r2:
                line_id = self.canvas.create_line(x1, y1, x2, y2, width=6, fill="#000")
            else:
                line_id = self.canvas.create_line(x1, y1, x2, y2, width=6, fill="#000")
            lines_ab = [line_id]
            # Register line for click-to-delete
            self.line_to_bridge[line_id] = (a, b)
        else:
            # second bridge: create two parallel lines and adjust first
            # offsets
            off = PARALLEL_OFF
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
            # Register both lines for click-to-delete
            self.line_to_bridge[first] = (a, b)
            self.line_to_bridge[second] = (a, b)

        # store back
        ai['lines'][key] = lines_ab
        bi['lines'][a] = lines_ab
        # register in occupancy the cells between islands and record them for undo
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
        # update data
        ai['bridges'][b] = existing + 1
        bi['bridges'][a] = existing + 1
        # push to history for undo
        self.history.append({'a': a, 'b': b, 'lines': list(lines_ab), 'occ_cells': occ_cells})
        self.update_status()
        self.msg_label.config(text="Puente creado")
        # check victory
        if self.check_victory():
            self.msg_label.config(text="¡Victoria! Todas las islas están conectadas y completas.")
        return True, "OK"

    def undo(self):
        if not self.history:
            self.msg_label.config(text="Nada que deshacer")
            return
        last = self.history.pop()
        a = last['a']
        b = last['b']
        lines = last['lines']
        # remove lines from canvas
        for lid in lines:
            try:
                self.canvas.delete(lid)
            except Exception:
                pass
        # decrement occupancy
        for cell, t in last['occ_cells']:
            occ = self.occupancy.get(cell)
            if occ:
                occ[t] = max(0, occ[t] - 1)
        # decrement bridge counts and remove lines entries
        if b in self.islands[a]['bridges']:
            self.islands[a]['bridges'][b] -= 1
            if self.islands[a]['bridges'][b] <= 0:
                del self.islands[a]['bridges'][b]
        if a in self.islands[b]['bridges']:
            self.islands[b]['bridges'][a] -= 1
            if self.islands[b]['bridges'][a] <= 0:
                del self.islands[b]['bridges'][a]
        # adjust lines storage
        if 'lines' in self.islands[a] and b in self.islands[a]['lines']:
            del self.islands[a]['lines'][b]
        if 'lines' in self.islands[b] and a in self.islands[b]['lines']:
            del self.islands[b]['lines'][a]
        self.update_status()
        self.msg_label.config(text="Se deshizo el último puente")

    def delete_bridge_by_line(self, line_id):
        """Delete a bridge when user clicks on its line"""
        if line_id not in self.line_to_bridge:
            return
        
        a, b = self.line_to_bridge[line_id]
        ai = self.islands[a]
        bi = self.islands[b]
        
        # Get all lines for this bridge
        lines = ai.get('lines', {}).get(b, [])
        if not lines:
            return
        
        # Find the history entry for this bridge (search backwards)
        history_idx = None
        for idx in range(len(self.history) - 1, -1, -1):
            h = self.history[idx]
            if h['a'] == a and h['b'] == b:
                history_idx = idx
                break
        
        if history_idx is None:
            return
        
        # Get the history entry
        hist_entry = self.history[history_idx]
        
        # Remove lines from canvas
        for lid in hist_entry['lines']:
            try:
                self.canvas.delete(lid)
                if lid in self.line_to_bridge:
                    del self.line_to_bridge[lid]
            except Exception:
                pass
        
        # Decrement occupancy
        for cell, t in hist_entry['occ_cells']:
            occ = self.occupancy.get(cell)
            if occ:
                occ[t] = max(0, occ[t] - 1)
        
        # Decrement bridge counts
        if b in ai['bridges']:
            ai['bridges'][b] -= 1
            if ai['bridges'][b] <= 0:
                del ai['bridges'][b]
        if a in bi['bridges']:
            bi['bridges'][a] -= 1
            if bi['bridges'][a] <= 0:
                del bi['bridges'][a]
        
        # Remove lines storage
        if 'lines' in ai and b in ai['lines']:
            del ai['lines'][b]
        if 'lines' in bi and a in bi['lines']:
            del bi['lines'][a]
        
        # Remove from history
        self.history.pop(history_idx)
        
        self.update_status()
        self.msg_label.config(text="Puente eliminado")

    def check_victory(self):
        # check all islands satisfied their number
        for pos, info in self.islands.items():
            used = sum(info['bridges'].values())
            if used != info['num']:
                return False
        # check connectivity via BFS
        # build adjacency
        nodes = list(self.islands.keys())
        if not nodes:
            return False
        adj = {n: set() for n in nodes}
        for n, info in self.islands.items():
            for nb in info['bridges'].keys():
                adj[n].add(nb)
        # BFS
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
