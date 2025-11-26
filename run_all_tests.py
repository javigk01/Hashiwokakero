"""
Script para ejecutar todas las pruebas unitarias
Ejecutar con: py run_all_tests.py
"""

import unittest
import sys

# Importar todos los módulos de pruebas
import test_game_logic
import test_solver
import test_backtracking_solver
import test_parser
import test_integration


def run_all_tests():
    """Ejecuta todas las suites de pruebas"""
    
    # Crear el test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las pruebas
    print("=" * 70)
    print("EJECUTANDO TODAS LAS PRUEBAS UNITARIAS - HASHIWOKAKERO")
    print("=" * 70)
    
    print("\n[1/5] Cargando pruebas de game_logic...")
    suite.addTests(loader.loadTestsFromModule(test_game_logic))
    
    print("[2/5] Cargando pruebas de solver (CSP)...")
    suite.addTests(loader.loadTestsFromModule(test_solver))
    
    print("[3/5] Cargando pruebas de backtracking_solver...")
    suite.addTests(loader.loadTestsFromModule(test_backtracking_solver))
    
    print("[4/5] Cargando pruebas de parser...")
    suite.addTests(loader.loadTestsFromModule(test_parser))
    
    print("[5/5] Cargando pruebas de integración...")
    suite.addTests(loader.loadTestsFromModule(test_integration))
    
    print("\n" + "=" * 70)
    print("EJECUTANDO PRUEBAS...")
    print("=" * 70 + "\n")
    
    # Ejecutar las pruebas con verbosidad
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE RESULTADOS")
    print("=" * 70)
    print(f"Pruebas ejecutadas: {result.testsRun}")
    print(f"Exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallidas: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print(f"Omitidas: {len(result.skipped)}")
    print("=" * 70)
    
    # Retornar código de salida apropiado
    if result.wasSuccessful():
        print("\n✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        return 0
    else:
        print("\n✗ ALGUNAS PRUEBAS FALLARON")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
