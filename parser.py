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
