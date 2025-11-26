"""
Pruebas unitarias para parser.py
Ejecutar con: py -m unittest test_parser.py
"""

import unittest
import os
import tempfile
from parser import parse_board


class TestParser(unittest.TestCase):
    """Pruebas de parsing de archivos"""
    
    def setUp(self):
        """Crear archivos temporales para testing"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Limpiar archivos temporales"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_parse_valid_file(self):
        """Parser lee archivo válido"""
        # Crear archivo temporal con puzzle válido
        file_path = os.path.join(self.temp_dir, 'test_puzzle.txt')
        with open(file_path, 'w') as f:
            f.write('3,3\n')
            f.write('203\n')
            f.write('000\n')
            f.write('102\n')
        
        rows, cols, board = parse_board(file_path)
        self.assertEqual(rows, 3)
        self.assertEqual(cols, 3)
        self.assertEqual(len(board), 3)
        self.assertEqual(len(board[0]), 3)
    
    def test_parse_returns_correct_dimensions(self):
        """Dimensiones correctas"""
        file_path = os.path.join(self.temp_dir, 'test_puzzle.txt')
        with open(file_path, 'w') as f:
            f.write('5,7\n')
            for _ in range(5):
                f.write('0000000\n')
        
        rows, cols, board = parse_board(file_path)
        self.assertEqual(rows, 5)
        self.assertEqual(cols, 7)
    
    def test_parse_returns_correct_board(self):
        """Tablero correcto"""
        file_path = os.path.join(self.temp_dir, 'test_puzzle.txt')
        with open(file_path, 'w') as f:
            f.write('2,2\n')
            f.write('12\n')
            f.write('34\n')
        
        rows, cols, board = parse_board(file_path)
        self.assertEqual(board[0][0], 1)
        self.assertEqual(board[0][1], 2)
        self.assertEqual(board[1][0], 3)
        self.assertEqual(board[1][1], 4)
    
    def test_parse_with_empty_cells(self):
        """Maneja celdas vacías"""
        file_path = os.path.join(self.temp_dir, 'test_puzzle.txt')
        with open(file_path, 'w') as f:
            f.write('3,3\n')
            f.write('102\n')
            f.write('000\n')
            f.write('304\n')
        
        rows, cols, board = parse_board(file_path)
        self.assertEqual(board[0][1], 0)
        self.assertEqual(board[1][0], 0)
        self.assertEqual(board[1][1], 0)
        self.assertEqual(board[1][2], 0)
    
    def test_parse_nonexistent_file(self):
        """Error con archivo inexistente"""
        with self.assertRaises(FileNotFoundError):
            parse_board('nonexistent_file.txt')


class TestParserRealFiles(unittest.TestCase):
    """Pruebas con archivos reales del proyecto"""
    
    def test_parse_example_txt(self):
        """Parser lee example.txt si existe"""
        if os.path.exists('example.txt'):
            rows, cols, board = parse_board('example.txt')
            self.assertGreater(rows, 0)
            self.assertGreater(cols, 0)
            self.assertEqual(len(board), rows)
            self.assertEqual(len(board[0]), cols)
    
    def test_parse_example2_txt(self):
        """Parser lee example2.txt si existe"""
        if os.path.exists('example2.txt'):
            rows, cols, board = parse_board('example2.txt')
            self.assertGreater(rows, 0)
            self.assertGreater(cols, 0)
            self.assertEqual(len(board), rows)
            self.assertEqual(len(board[0]), cols)


if __name__ == '__main__':
    unittest.main()
