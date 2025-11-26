"""
Script para generar un reporte detallado en formato JSON
de los resultados del benchmark
"""

import json
import time
import sys
import os
from datetime import datetime

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from benchmark_solvers import test_solver
from parser import parse_board
from game_logic import HashiGame
from solver import HashiSolver
from backtracking_solver import BacktrackingSolver


def generate_detailed_report(test_files, output_file="benchmark_report.json"):
    """
    Genera un reporte detallado en JSON con los resultados del benchmark
    
    Args:
        test_files: lista de tuplas (nombre, archivo)
        output_file: nombre del archivo JSON de salida
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "description": "Comparación de rendimiento entre CSP y Backtracking en Hashiwokakero",
        "board_size": "7x7",
        "test_cases": [],
        "summary": {}
    }
    
    total_csp_time = 0
    total_bt_time = 0
    csp_wins = 0
    bt_wins = 0
    both_solved = 0
    both_failed = 0
    
    print("Generando reporte detallado...")
    print("=" * 80)
    
    for test_name, test_file in test_files:
        print(f"Procesando: {test_name}...")
        
        try:
            # Parsear el tablero
            rows, cols, board = parse_board(test_file)
            num_islands = sum(1 for r in range(rows) for c in range(cols) if board[r][c] > 0)
            
            # Crear instancias del juego
            game_csp = HashiGame(rows, cols, board)
            board_copy = [row[:] for row in board]
            game_bt = HashiGame(rows, cols, board_copy)
            
            # Probar CSP
            success_csp, time_csp, iter_csp = test_solver(game_csp, HashiSolver, "CSP")
            
            # Probar Backtracking
            success_bt, time_bt, iter_bt = test_solver(game_bt, BacktrackingSolver, "Backtracking")
            
            # Calcular métricas
            speedup = None
            iter_ratio = None
            faster = None
            
            if success_csp and success_bt:
                both_solved += 1
                speedup = time_bt / time_csp if time_csp > 0 else float('inf')
                iter_ratio = iter_bt / iter_csp if iter_csp > 0 else float('inf')
                faster = "CSP" if time_csp < time_bt else "Backtracking"
                
                if faster == "CSP":
                    csp_wins += 1
                else:
                    bt_wins += 1
                
                total_csp_time += time_csp
                total_bt_time += time_bt
            elif not success_csp and not success_bt:
                both_failed += 1
            
            # Agregar al reporte
            test_case = {
                "name": test_name,
                "file": test_file,
                "board_dimensions": f"{cols}x{rows}",
                "num_islands": num_islands,
                "csp": {
                    "success": success_csp,
                    "time_ms": round(time_csp, 2),
                    "iterations": iter_csp
                },
                "backtracking": {
                    "success": success_bt,
                    "time_ms": round(time_bt, 2),
                    "iterations": iter_bt
                },
                "comparison": {
                    "speedup": round(speedup, 2) if speedup else None,
                    "iteration_ratio": round(iter_ratio, 2) if iter_ratio else None,
                    "faster": faster
                }
            }
            
            report["test_cases"].append(test_case)
            
        except Exception as e:
            print(f"Error procesando {test_file}: {e}")
            test_case = {
                "name": test_name,
                "file": test_file,
                "error": str(e)
            }
            report["test_cases"].append(test_case)
    
    # Agregar resumen
    report["summary"] = {
        "total_tests": len(test_files),
        "both_solved": both_solved,
        "both_failed": both_failed,
        "csp_wins": csp_wins,
        "backtracking_wins": bt_wins,
        "total_csp_time_ms": round(total_csp_time, 2),
        "total_bt_time_ms": round(total_bt_time, 2),
        "average_speedup": round(total_bt_time / total_csp_time, 2) if total_csp_time > 0 else None
    }
    
    # Guardar en archivo JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("=" * 80)
    print(f"\n✓ Reporte generado exitosamente: {output_file}")
    print(f"  - {both_solved} casos resueltos por ambos algoritmos")
    print(f"  - CSP ganó en {csp_wins} casos")
    print(f"  - Speedup promedio: {report['summary']['average_speedup']}x")


def main():
    """Función principal"""
    # Obtener ruta base del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    puzzles_dir = os.path.join(project_root, "puzzles")
    
    test_files = [
        ("Simple 1", os.path.join(puzzles_dir, "test_simple1.txt")),
        ("Simple 2", os.path.join(puzzles_dir, "test_simple2.txt")),
        ("Fácil", os.path.join(puzzles_dir, "test_easy.txt")),
        ("Moderado 1", os.path.join(puzzles_dir, "test_moderate1.txt")),
        ("Moderado 2", os.path.join(puzzles_dir, "test_moderate2.txt")),
        ("Difícil", os.path.join(puzzles_dir, "test_hard.txt")),
        ("Ejemplo Base", os.path.join(puzzles_dir, "example.txt")),
        ("Hash Test", os.path.join(puzzles_dir, "hashitest.txt")),
    ]
    
    generate_detailed_report(test_files)


if __name__ == '__main__':
    main()
