import sys
import os
from tkinter import Tk, filedialog
from parser import parse_board
from gui import HashiGUI

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
