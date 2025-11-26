# Hashiwokakero - Entrega 2

Implementación del juego de puzzle Hashiwokakero (Hashi) con interfaz gráfica y **dos algoritmos de resolución automática**.

## 📁 Estructura del Proyecto

```
Hashiwokakero/
├── puzzles/              # Tableros de prueba (.txt)
│   ├── example.txt
│   ├── hashitest.txt
│   ├── test_simple1.txt
│   ├── test_simple2.txt
│   ├── test_easy.txt
│   ├── test_moderate1.txt
│   ├── test_moderate2.txt
│   └── test_hard.txt
├── tests/                # Pruebas unitarias
│   ├── test_game_logic.py
│   ├── test_solver.py
│   ├── test_backtracking_solver.py
│   ├── test_parser.py
│   ├── test_integration.py
│   └── run_all_tests.py
├── benchmark/            # Scripts de benchmark
│   ├── benchmark_solvers.py
│   ├── generate_report.py
│   └── visualize_results.py
├── docs/                 # Documentación
│   ├── COMPARACION_ALGORITMOS.md
│   ├── GUIA_USO.md
│   ├── INICIO_RAPIDO.md
│   ├── EXPLICACION_CSP_LIMITACIONES.md
│   └── RESUMEN_IMPLEMENTACION.md
├── main.py              # Punto de entrada
├── gui.py               # Interfaz gráfica
├── game_logic.py        # Lógica del juego
├── solver.py            # Algoritmo CSP
├── backtracking_solver.py  # Algoritmo Backtracking
└── parser.py            # Parser de archivos
```

## Instrucciones de Uso

### 1. Ejecutar la interfaz (requiere Python 3):

```bash
py main.py
# O especificar un tablero:
py main.py puzzles/example.txt
```

### 2. Jugar manualmente:
- Hacer clic en dos islas para crear un puente horizontal o vertical entre ellas
- Hacer clic en un puente existente para eliminarlo
- Las reglas implementadas son:
  - No se permiten conexiones diagonales
  - No se puede pasar por encima de otra isla
  - Máximo 2 puentes entre las mismas islas
  - Los puentes no pueden cruzarse

### 3. Resolución automática:

La interfaz incluye **dos botones de resolución automática**:

#### **Botón 1: Resolver (CSP)**
- Usa **Constraint Propagation + Backtracking**
- Algoritmo inteligente que aplica reglas del dominio
- **Muy rápido** (típicamente < 500 iteraciones)
- Reduce el espacio de búsqueda aplicando restricciones
- Ideal para puzzles complejos

#### **Botón 2: Resolver (Backtracking)**
- Usa **Backtracking Puro Recursivo**
- Fuerza bruta optimizada con heurísticas simples
- Implementa técnicas:
  - **Recursividad**: Llamadas recursivas para explorar el árbol de decisiones
  - **Backtracking**: Retrocede cuando encuentra un estado inválido
  - **Heurística MRV**: Procesa primero las islas más restrictivas
  - **Poda temprana**: Detecta estados inválidos antes de explorarlos
- Más lento pero **didáctico** para estudiar algoritmos
- Sin límite de iteraciones (explora hasta encontrar solución)

Ambos botones alternan entre "Resolver" y "Limpiar". Cuando uno está activo, el otro se deshabilita.

### 2. Ejecutar Pruebas Unitarias

```bash
py tests/run_all_tests.py
```

### 3. Ejecutar Benchmark

```bash
# Benchmark básico
py benchmark/benchmark_solvers.py

# Generar reporte JSON
py benchmark/generate_report.py

# Generar gráficos (requiere matplotlib)
py benchmark/visualize_results.py
```

## Componentes Principales

### Núcleo del Juego
- **`main.py`** - Punto de entrada del programa
- **`gui.py`** - Interfaz gráfica con Tkinter
- **`game_logic.py`** - Lógica del juego (validaciones, estado, operaciones)
- **`parser.py`** - Parser para archivos de puzzle

### Algoritmos de Solución
- **`solver.py`** - Solucionador con CSP + Constraint Propagation
- **`backtracking_solver.py`** - Solucionador con Backtracking Puro

## Comparación de Algoritmos

| Característica | CSP + Propagation | Backtracking Puro |
|----------------|-------------------|-------------------|
| **Técnica** | Constraint propagation + backtracking | Recursión + backtracking |
| **Iteraciones** | 100-500 | Variable (hasta solución) |
| **Velocidad** | Muy rápida | Moderada |
| **Heurísticas** | Avanzadas (múltiples reglas) | Simples (MRV + poda) |
| **Propósito** | Eficiencia práctica | Enseñanza de algoritmos |

Para más detalles, consulta `docs/COMPARACION_ALGORITMOS.md`.

## 📊 Sistema de Benchmark y Pruebas

### Resultados del Benchmark

```
Speedup promedio de CSP: 18.77x más rápido
Mejor caso: 86.95x (Ejemplo Base con 24 islas)
Reducción de iteraciones: 13-561x menos
Tasa de éxito CSP: 75% (6/8 casos)
Tasa de éxito Backtracking: 87.5% (7/8 casos)
```

**Nota importante:** CSP puede no encontrar todas las soluciones debido a que sacrifica completitud por velocidad. Ver `docs/EXPLICACION_CSP_LIMITACIONES.md` para más detalles.

### 📚 Documentación Completa

- **`docs/INICIO_RAPIDO.md`** - Guía de inicio rápido (3 pasos)
- **`docs/GUIA_USO.md`** - Guía completa del sistema de benchmark
- **`docs/COMPARACION_ALGORITMOS.md`** - Análisis detallado de algoritmos
- **`docs/EXPLICACION_CSP_LIMITACIONES.md`** - Por qué CSP puede fallar
- **`docs/TEST_FILES_README.md`** - Documentación de tableros de prueba
- **`docs/RESUMEN_IMPLEMENTACION.md`** - Resumen de la implementación

## Arquitectura

El proyecto utiliza separación de lógica y presentación:
- **game_logic.py**: Toda la lógica del juego (independiente de la GUI)
- **gui.py**: Solo visualización e interacción del usuario
- **Solvers**: Algoritmos de resolución automática

Esta arquitectura facilita:
- Testing independiente de la lógica
- Reutilización del código
- Mantenimiento y escalabilidad
- Implementación de múltiples interfaces (CLI, web, etc.)
