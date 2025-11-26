"""
Script para comparar el rendimiento de los dos algoritmos de solución
Mide el tiempo de ejecución en diferentes tableros de prueba 7x7
"""

import time
import sys
import os

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from parser import parse_board
from game_logic import HashiGame
from solver import HashiSolver
from backtracking_solver import BacktrackingSolver


def test_solver(game, solver_class, solver_name):
    """
    Prueba un solucionador y mide su tiempo de ejecución
    
    Args:
        game: instancia de HashiGame
        solver_class: clase del solucionador (HashiSolver o BacktrackingSolver)
        solver_name: nombre del solucionador para mostrar
    
    Returns:
        tuple: (éxito, tiempo_ms, iteraciones)
    """
    solver = solver_class(game)
    
    start_time = time.perf_counter()
    success, bridges = solver.solve()
    end_time = time.perf_counter()
    
    elapsed_ms = (end_time - start_time) * 1000
    iterations = solver.iterations
    
    return success, elapsed_ms, iterations


def run_benchmark(test_files):
    """
    Ejecuta el benchmark en todos los archivos de prueba
    
    Args:
        test_files: lista de tuplas (nombre, archivo)
    """
    print("=" * 80)
    print("BENCHMARK DE ALGORITMOS - HASHIWOKAKERO")
    print("Comparación: CSP (Constraint Propagation) vs Backtracking Puro")
    print("=" * 80)
    
    results = []
    
    for test_name, test_file in test_files:
        print(f"\n{'=' * 80}")
        print(f"Tablero: {test_name}")
        print(f"Archivo: {test_file}")
        print(f"{'=' * 80}")
        
        try:
            # Parsear el tablero
            rows, cols, board = parse_board(test_file)
            
            # Contar número de islas
            num_islands = sum(1 for r in range(rows) for c in range(cols) if board[r][c] > 0)
            
            # Crear una instancia del juego para CSP
            game_csp = HashiGame(rows, cols, board)
            
            # Crear una instancia del juego para Backtracking
            board_copy = [row[:] for row in board]  # Copia profunda
            game_bt = HashiGame(rows, cols, board_copy)
            
            print(f"\nTablero: {cols}x{rows}")
            print(f"Número de islas: {num_islands}")
            
            # Probar CSP Solver
            print("\n--- CSP Solver (Constraint Propagation) ---")
            success_csp, time_csp, iter_csp = test_solver(game_csp, HashiSolver, "CSP")
            
            if success_csp:
                print(f"✓ Solución encontrada")
                print(f"  Tiempo: {time_csp:.2f} ms")
                print(f"  Iteraciones: {iter_csp}")
            else:
                print(f"✗ No se encontró solución")
                print(f"  Tiempo: {time_csp:.2f} ms")
                print(f"  Iteraciones: {iter_csp}")
            
            # Probar Backtracking Solver
            print("\n--- Backtracking Solver (Backtracking Puro) ---")
            success_bt, time_bt, iter_bt = test_solver(game_bt, BacktrackingSolver, "Backtracking")
            
            if success_bt:
                print(f"✓ Solución encontrada")
                print(f"  Tiempo: {time_bt:.2f} ms")
                print(f"  Iteraciones: {iter_bt}")
            else:
                print(f"✗ No se encontró solución")
                print(f"  Tiempo: {time_bt:.2f} ms")
                print(f"  Iteraciones: {iter_bt}")
            
            # Comparación
            if success_csp and success_bt:
                print(f"\n--- Comparación ---")
                speedup = time_bt / time_csp if time_csp > 0 else float('inf')
                iter_ratio = iter_bt / iter_csp if iter_csp > 0 else float('inf')
                
                print(f"Speedup CSP: {speedup:.2f}x más rápido")
                print(f"Ratio de iteraciones: {iter_ratio:.2f}x")
                
                faster = "CSP" if time_csp < time_bt else "Backtracking"
                diff = abs(time_csp - time_bt)
                print(f"Algoritmo más rápido: {faster} ({diff:.2f} ms de diferencia)")
            
            # Guardar resultados
            results.append({
                'name': test_name,
                'file': test_file,
                'islands': num_islands,
                'csp_success': success_csp,
                'csp_time': time_csp,
                'csp_iter': iter_csp,
                'bt_success': success_bt,
                'bt_time': time_bt,
                'bt_iter': iter_bt
            })
            
        except Exception as e:
            print(f"\n✗ Error al procesar {test_file}: {e}")
            import traceback
            traceback.print_exc()
    
    # Resumen final
    print(f"\n\n{'=' * 80}")
    print("RESUMEN COMPARATIVO")
    print(f"{'=' * 80}")
    print(f"\n{'Tablero':<20} {'CSP (ms)':<15} {'BT (ms)':<15} {'Speedup':<10} {'Mejor':<10}")
    print(f"{'-'*20} {'-'*15} {'-'*15} {'-'*10} {'-'*10}")
    
    total_csp_time = 0
    total_bt_time = 0
    csp_wins = 0
    bt_wins = 0
    
    for result in results:
        if result['csp_success'] and result['bt_success']:
            speedup = result['bt_time'] / result['csp_time'] if result['csp_time'] > 0 else float('inf')
            faster = "CSP" if result['csp_time'] < result['bt_time'] else "BT"
            
            if faster == "CSP":
                csp_wins += 1
            else:
                bt_wins += 1
            
            total_csp_time += result['csp_time']
            total_bt_time += result['bt_time']
            
            print(f"{result['name']:<20} {result['csp_time']:>12.2f}   {result['bt_time']:>12.2f}   {speedup:>7.2f}x   {faster:<10}")
    
    print(f"{'-'*20} {'-'*15} {'-'*15} {'-'*10} {'-'*10}")
    print(f"{'TOTAL':<20} {total_csp_time:>12.2f}   {total_bt_time:>12.2f}")
    print(f"\nVictorias: CSP = {csp_wins}, Backtracking = {bt_wins}")
    
    if total_csp_time > 0:
        overall_speedup = total_bt_time / total_csp_time
        print(f"Speedup promedio de CSP: {overall_speedup:.2f}x")
    
    print("=" * 80)


def main():
    """Función principal"""
    # Obtener ruta base del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    puzzles_dir = os.path.join(project_root, "puzzles")
    
    # Lista de archivos de prueba (nombre, archivo)
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
    
    run_benchmark(test_files)


if __name__ == '__main__':
    main()
