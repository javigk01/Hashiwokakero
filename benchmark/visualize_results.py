"""
Script para visualizar los resultados del benchmark
Genera gráficos comparativos de los dos algoritmos
"""

import json
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def load_report(filename="benchmark_report.json"):
    """Carga el reporte JSON generado"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_comparison_charts(report):
    """Genera gráficos comparativos a partir del reporte"""
    
    # Filtrar solo los casos donde ambos algoritmos encontraron solución
    solved_cases = [tc for tc in report["test_cases"] 
                   if tc.get("csp", {}).get("success") and tc.get("backtracking", {}).get("success")]
    
    if not solved_cases:
        print("No hay casos resueltos por ambos algoritmos para graficar.")
        return
    
    # Extraer datos
    names = [tc["name"] for tc in solved_cases]
    csp_times = [tc["csp"]["time_ms"] for tc in solved_cases]
    bt_times = [tc["backtracking"]["time_ms"] for tc in solved_cases]
    csp_iters = [tc["csp"]["iterations"] for tc in solved_cases]
    bt_iters = [tc["backtracking"]["iterations"] for tc in solved_cases]
    speedups = [tc["comparison"]["speedup"] for tc in solved_cases]
    
    # Configurar el estilo
    plt.style.use('default')
    
    # Gráfico 1: Comparación de tiempos
    fig1 = plt.figure(figsize=(10, 6))
    ax1 = fig1.add_subplot(111)
    x = np.arange(len(names))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, csp_times, width, label='CSP', color='#2ecc71', alpha=0.8)
    bars2 = ax1.bar(x + width/2, bt_times, width, label='Backtracking', color='#e74c3c', alpha=0.8)
    
    ax1.set_xlabel('Tablero', fontweight='bold')
    ax1.set_ylabel('Tiempo (ms)', fontweight='bold')
    ax1.set_title('Comparación de Tiempos de Ejecución', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Gráfico 2: Comparación de iteraciones
    fig2 = plt.figure(figsize=(10, 6))
    ax2 = fig2.add_subplot(111)
    bars3 = ax2.bar(x - width/2, csp_iters, width, label='CSP', color='#3498db', alpha=0.8)
    bars4 = ax2.bar(x + width/2, bt_iters, width, label='Backtracking', color='#9b59b6', alpha=0.8)
    
    ax2.set_xlabel('Tablero', fontweight='bold')
    ax2.set_ylabel('Iteraciones', fontweight='bold')
    ax2.set_title('Comparación de Número de Iteraciones', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Gráfico 3: Speedup
    fig3 = plt.figure(figsize=(10, 6))
    ax3 = fig3.add_subplot(111)
    bars5 = ax3.bar(x, speedups, color='#f39c12', alpha=0.8)
    ax3.axhline(y=1, color='r', linestyle='--', linewidth=1, alpha=0.5, label='Sin diferencia')
    
    ax3.set_xlabel('Tablero', fontweight='bold')
    ax3.set_ylabel('Speedup (x veces más rápido)', fontweight='bold')
    ax3.set_title('Speedup de CSP sobre Backtracking', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(names, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # Agregar valores sobre las barras del speedup
    for i, v in enumerate(speedups):
        ax3.text(i, v + max(speedups)*0.02, f'{v:.1f}x', ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    # Gráfico 4: Tiempos en escala logarítmica
    fig4 = plt.figure(figsize=(10, 6))
    ax4 = fig4.add_subplot(111)
    ax4.plot(names, csp_times, marker='o', linewidth=2, markersize=8, label='CSP', color='#2ecc71')
    ax4.plot(names, bt_times, marker='s', linewidth=2, markersize=8, label='Backtracking', color='#e74c3c')
    
    ax4.set_xlabel('Tablero', fontweight='bold')
    ax4.set_ylabel('Tiempo (ms) - Escala Log', fontweight='bold')
    ax4.set_title('Tiempos de Ejecución (Escala Logarítmica)', fontsize=12, fontweight='bold')
    ax4.set_yscale('log')
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax4.legend()
    ax4.grid(True, alpha=0.3, which="both")
    plt.tight_layout()
    plt.show()
    
    # Gráfico 5: Ratio de iteraciones
    fig5 = plt.figure(figsize=(10, 6))
    ax5 = fig5.add_subplot(111)
    iter_ratios = [tc["comparison"]["iteration_ratio"] for tc in solved_cases]
    bars6 = ax5.bar(x, iter_ratios, color='#1abc9c', alpha=0.8)
    
    ax5.set_xlabel('Tablero', fontweight='bold')
    ax5.set_ylabel('Ratio de Iteraciones', fontweight='bold')
    ax5.set_title('Ratio de Iteraciones (BT/CSP)', fontsize=12, fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels(names, rotation=45, ha='right')
    ax5.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Gráfico 6: Resumen de eficiencia
    fig6 = plt.figure(figsize=(10, 6))
    ax6 = fig6.add_subplot(111)
    summary = report["summary"]
    
    categories = ['Tiempo\nTotal\n(ms)', 'Iteraciones\nPromedio', 'Velocidad\nPromedio\n(x)']
    csp_summary = [
        summary["total_csp_time_ms"],
        np.mean(csp_iters),
        1.0  # Base de referencia
    ]
    bt_summary = [
        summary["total_bt_time_ms"],
        np.mean(bt_iters),
        summary["average_speedup"]
    ]
    
    x_pos = np.arange(len(categories))
    width = 0.35
    
    # Normalizar para mejor visualización
    max_time = max(summary["total_csp_time_ms"], summary["total_bt_time_ms"])
    max_iter = max(np.mean(csp_iters), np.mean(bt_iters))
    
    normalized_csp = [
        csp_summary[0] / max_time * 100,
        csp_summary[1] / max_iter * 100,
        csp_summary[2]
    ]
    normalized_bt = [
        bt_summary[0] / max_time * 100,
        bt_summary[1] / max_iter * 100,
        bt_summary[2]
    ]
    
    bars7 = ax6.bar(x_pos - width/2, normalized_csp, width, label='CSP', color='#2ecc71', alpha=0.8)
    bars8 = ax6.bar(x_pos + width/2, [normalized_bt[0], normalized_bt[1], bt_summary[2]], 
                    width, label='Backtracking', color='#e74c3c', alpha=0.8)
    
    ax6.set_ylabel('Valor Normalizado / Speedup', fontweight='bold')
    ax6.set_title('Resumen de Eficiencia', fontsize=12, fontweight='bold')
    ax6.set_xticks(x_pos)
    ax6.set_xticklabels(categories)
    ax6.legend()
    ax6.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    print("✓ Todas las gráficas se han mostrado")


def print_summary(report):
    """Imprime un resumen del reporte"""
    print("\n" + "=" * 80)
    print("RESUMEN DEL BENCHMARK")
    print("=" * 80)
    
    summary = report["summary"]
    print(f"\nTotal de pruebas: {summary['total_tests']}")
    print(f"Casos resueltos por ambos: {summary['both_solved']}")
    print(f"Casos sin solución: {summary['both_failed']}")
    print(f"\nVictorias:")
    print(f"  - CSP: {summary['csp_wins']}")
    print(f"  - Backtracking: {summary['backtracking_wins']}")
    print(f"\nTiempo total:")
    print(f"  - CSP: {summary['total_csp_time_ms']:.2f} ms")
    print(f"  - Backtracking: {summary['total_bt_time_ms']:.2f} ms")
    print(f"\nSpeedup promedio de CSP: {summary['average_speedup']:.2f}x")
    print("=" * 80)


def main():
    """Función principal"""
    try:
        # Cargar reporte
        print("Cargando reporte...")
        report = load_report()
        
        # Imprimir resumen
        print_summary(report)
        
        # Generar gráficos
        print("\nGenerando gráficos...")
        plot_comparison_charts(report)
        
    except FileNotFoundError:
        print("Error: No se encontró el archivo benchmark_report.json")
        print("Ejecuta primero: py generate_report.py")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
