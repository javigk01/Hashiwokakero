# Archivos de Prueba y Benchmark - Hashiwokakero

## Descripción

Este conjunto de archivos de prueba está diseñado para comparar el rendimiento de dos algoritmos de solución para el juego Hashiwokakero:

1. **CSP Solver** (solver.py): Utiliza Constraint Propagation + Backtracking
2. **Backtracking Solver** (backtracking_solver.py): Utiliza Backtracking Puro

Todos los tableros de prueba son de tamaño **7x7** para mantener la consistencia en las comparaciones.

## Archivos de Prueba Disponibles

### Tableros de Prueba Nuevos (7x7)

- **test_simple1.txt**: Tablero simple con 12 islas
- **test_simple2.txt**: Tablero simple con 12 islas
- **test_easy.txt**: Tablero fácil con 10 islas
- **test_moderate1.txt**: Tablero moderado con 14 islas
- **test_moderate2.txt**: Tablero moderado con 12 islas
- **test_hard.txt**: Tablero difícil con 16 islas

### Tableros Existentes (7x7)

- **example.txt**: Tablero ejemplo con 24 islas (más complejo)
- **hashitest.txt**: Tablero de prueba con 14 islas

## Uso del Benchmark

### Ejecutar el Benchmark Completo

```bash
py benchmark_solvers.py
```

Este comando ejecutará ambos algoritmos en todos los archivos de prueba y mostrará:
- Tiempo de ejecución en milisegundos
- Número de iteraciones
- Comparación de velocidad (speedup)
- Resumen final con estadísticas

### Salida del Benchmark

El script produce:
1. **Resultados individuales** por cada tablero
2. **Comparación directa** cuando ambos algoritmos encuentran solución
3. **Resumen comparativo** con tabla de resultados y totales

## Resultados Típicos

En pruebas con tableros 7x7, el **algoritmo CSP** típicamente:
- Es **4x a 80x más rápido** que Backtracking puro
- Requiere **20x a 500x menos iteraciones**
- Gana en todos los casos donde ambos encuentran solución

### Ejemplo de Salida

```
Tablero              CSP (ms)        BT (ms)         Speedup    Mejor
-------------------- --------------- --------------- ---------- ----------
Simple 1                     2.93          36.90     12.60x   CSP
Fácil                        1.98           8.97      4.54x   CSP
Difícil                      6.36          55.82      8.78x   CSP
Ejemplo Base                 2.97         220.19     74.08x   CSP
-------------------- --------------- --------------- ---------- ----------
TOTAL                       16.12         331.58

Victorias: CSP = 5, Backtracking = 0
Speedup promedio de CSP: 20.57x
```

## Estructura de los Archivos de Prueba

Formato de un archivo .txt:

```
7,7
2020002
0000000
2000002
0000000
2000002
0000000
2020002
```

- **Primera línea**: `filas,columnas`
- **Líneas siguientes**: Matriz del tablero donde:
  - `0` = celda vacía
  - `1-8` = isla con ese número de puentes requeridos

## Creación de Nuevos Tableros de Prueba

Para crear un nuevo tablero de prueba:

1. Crea un archivo .txt con el formato especificado
2. Asegúrate de que el tablero sea 7x7
3. Coloca islas con valores del 1 al 8
4. Agrega el archivo a la lista en `benchmark_solvers.py`

### Ejemplo de Código para Agregar

```python
test_files = [
    # ... archivos existentes ...
    ("Mi Tablero", "mi_tablero.txt"),
]
```

## Consideraciones

- **Tableros con solución**: Algunos tableros pueden no tener solución válida, lo cual es normal
- **Tiempo de ejecución**: Varía según la complejidad del tablero y el número de islas
- **Iteraciones**: El algoritmo CSP requiere significativamente menos iteraciones gracias a la propagación de restricciones

## Archivos Relacionados

- `benchmark_solvers.py`: Script principal de benchmark
- `solver.py`: Implementación del algoritmo CSP
- `backtracking_solver.py`: Implementación del algoritmo de Backtracking
- `parser.py`: Parser de archivos de tablero
- `game_logic.py`: Lógica del juego

## Notas

- Los tiempos pueden variar según el hardware
- Se recomienda ejecutar múltiples veces para obtener promedios consistentes
- El algoritmo CSP es significativamente más eficiente en la mayoría de casos
