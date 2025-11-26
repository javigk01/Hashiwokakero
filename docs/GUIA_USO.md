# Guía de Uso - Sistema de Benchmark para Hashiwokakero

## 📋 Resumen

Este sistema te permite comparar el rendimiento de dos algoritmos de solución para Hashiwokakero:
- **CSP Solver**: Constraint Propagation + Backtracking
- **Backtracking Solver**: Backtracking Puro

## 📁 Archivos Creados

### Archivos de Prueba (7x7)
- `test_simple1.txt` - Tablero simple con 12 islas
- `test_simple2.txt` - Tablero simple con 12 islas
- `test_easy.txt` - Tablero fácil con 10 islas
- `test_moderate1.txt` - Tablero moderado con 14 islas
- `test_moderate2.txt` - Tablero moderado con 12 islas
- `test_hard.txt` - Tablero difícil con 16 islas

### Scripts de Benchmark
1. **`benchmark_solvers.py`** - Benchmark principal con salida en consola
2. **`generate_report.py`** - Genera reporte detallado en JSON
3. **`visualize_results.py`** - Genera gráficos comparativos

### Documentación
- `TEST_FILES_README.md` - Documentación detallada de los archivos de prueba
- `GUIA_USO.md` - Este archivo

## 🚀 Cómo Usar

### 1. Ejecutar Benchmark Básico

```bash
py benchmark_solvers.py
```

**Salida:**
- Resultados individuales por tablero
- Comparación de tiempos e iteraciones
- Resumen final con tabla comparativa

**Ejemplo de salida:**
```
================================================================================
Tablero: Fácil
Archivo: test_easy.txt
================================================================================

Tablero: 7x7
Número de islas: 10

--- CSP Solver (Constraint Propagation) ---
✓ Solución encontrada
  Tiempo: 1.98 ms
  Iteraciones: 6

--- Backtracking Solver (Backtracking Puro) ---
✓ Solución encontrada
  Tiempo: 8.97 ms
  Iteraciones: 133

--- Comparación ---
Speedup CSP: 4.54x más rápido
Ratio de iteraciones: 22.17x
Algoritmo más rápido: CSP (7.00 ms de diferencia)
```

### 2. Generar Reporte JSON

```bash
py generate_report.py
```

**Genera:** `benchmark_report.json` con datos estructurados para análisis

**Contenido del JSON:**
```json
{
  "timestamp": "2025-11-26T17:02:39.569724",
  "description": "Comparación de rendimiento...",
  "test_cases": [...],
  "summary": {
    "total_tests": 8,
    "both_solved": 5,
    "csp_wins": 5,
    "average_speedup": 18.92
  }
}
```

### 3. Visualizar Resultados

```bash
py visualize_results.py
```

**Requisito:** Tener matplotlib instalado
```bash
pip install matplotlib
```

**Genera:** `benchmark_comparison.png` con 6 gráficos:
1. Comparación de tiempos de ejecución
2. Comparación de número de iteraciones
3. Speedup de CSP sobre Backtracking
4. Tiempos en escala logarítmica
5. Ratio de iteraciones
6. Resumen de eficiencia

## 📊 Resultados Esperados

### Métricas Típicas (tableros 7x7)

| Métrica | CSP | Backtracking | Ventaja CSP |
|---------|-----|--------------|-------------|
| Tiempo promedio | ~3-5 ms | ~50-200 ms | **20-80x más rápido** |
| Iteraciones | 4-14 | 100-2000+ | **20-500x menos** |
| Tasa de éxito | Media | Media-Alta | Similar |

### Ejemplo de Resumen

```
RESUMEN COMPARATIVO
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

## 🎯 Casos de Uso

### Para Análisis Rápido
```bash
py benchmark_solvers.py
```

### Para Documentación Completa
```bash
py generate_report.py
py visualize_results.py
```

### Para Análisis Personalizado
1. Ejecuta `generate_report.py`
2. Abre `benchmark_report.json`
3. Procesa los datos con tu herramienta preferida

## 🔧 Personalización

### Agregar Nuevos Tableros de Prueba

1. Crea un archivo `.txt` con formato:
   ```
   7,7
   2020002
   0000000
   2000002
   ...
   ```

2. Agrega a la lista en `benchmark_solvers.py`:
   ```python
   test_files = [
       # ... archivos existentes ...
       ("Mi Tablero", "mi_tablero.txt"),
   ]
   ```

3. Haz lo mismo en `generate_report.py`

### Modificar Métricas

Edita las funciones en los scripts para agregar:
- Uso de memoria
- Profundidad de recursión
- Nodos explorados
- Etc.

## 📈 Interpretación de Resultados

### Speedup
- **< 1x**: Backtracking más rápido (raro)
- **1-5x**: CSP ligeramente más rápido
- **5-20x**: CSP significativamente más rápido
- **> 20x**: CSP extremadamente superior

### Iteraciones
- Menos iteraciones = algoritmo más eficiente
- CSP típicamente requiere 20-500x menos iteraciones

### Casos Sin Solución
- Normal que algunos tableros no tengan solución
- Ambos algoritmos deberían coincidir en estos casos

## ⚠️ Notas Importantes

1. **Variabilidad de Tiempos**: Los tiempos pueden variar entre ejecuciones
2. **Hardware**: Resultados dependen del hardware utilizado
3. **Tableros Válidos**: No todos los tableros tienen solución
4. **Python**: Los scripts requieren Python 3.6+

## 🐛 Solución de Problemas

### Error: "module matplotlib not found"
```bash
pip install matplotlib
```

### Error: "No se encontró el archivo"
Verifica que estés en el directorio correcto:
```bash
cd "ruta/a/Hashiwokakero"
```

### Los tiempos son muy diferentes
Normal. Ejecuta múltiples veces para obtener promedios

### Ningún algoritmo encuentra solución
El tablero puede no tener solución válida

## 📚 Archivos Adicionales

- `solver.py` - Implementación CSP
- `backtracking_solver.py` - Implementación Backtracking
- `game_logic.py` - Lógica del juego
- `parser.py` - Parser de archivos

## 🎓 Para tu Proyecto

### En tu Reporte Incluye:
1. **Tabla de resultados** del benchmark
2. **Gráficos generados** por visualize_results.py
3. **Análisis de complejidad** temporal
4. **Conclusiones** sobre eficiencia

### Ejemplo de Conclusión:
> "El algoritmo CSP mostró un speedup promedio de 20.57x sobre 
> Backtracking puro en tableros 7x7, reduciendo las iteraciones 
> en un 95% gracias a la propagación de restricciones."

## 📞 Comandos Rápidos

```bash
# Benchmark completo
py benchmark_solvers.py

# Generar reporte JSON
py generate_report.py

# Visualizar (requiere matplotlib)
py visualize_results.py

# Ejecutar todo
py generate_report.py ; py visualize_results.py
```

---

¡Listo para medir el rendimiento de tus algoritmos! 🚀
