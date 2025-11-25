# Hashiwokakero - Entrega 2

Implementación del juego de puzzle Hashiwokakero (Hashi) con interfaz gráfica y **dos algoritmos de resolución automática**.

## Instrucciones de Uso

### 1. Ejecutar la interfaz (requiere Python 3):

```bash
py main.py example.txt
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

## Estructura del Proyecto

- `main.py` - Punto de entrada del programa
- `gui.py` - Interfaz gráfica con Tkinter
- `game_logic.py` - Lógica del juego (validaciones, estado, operaciones)
- `parser.py` - Parser para archivos de puzzle
- `solver.py` - Solucionador con CSP + Constraint Propagation
- `backtracking_solver.py` - Solucionador con Backtracking Puro
- `example.txt` / `example2.txt` - Puzzles de ejemplo
- `COMPARACION_ALGORITMOS.md` - Comparación detallada de ambos algoritmos
- `SEPARACION_LOGICA_GUI.md` - Documentación de la arquitectura

## Comparación de Algoritmos

| Característica | CSP + Propagation | Backtracking Puro |
|----------------|-------------------|-------------------|
| **Técnica** | Constraint propagation + backtracking | Recursión + backtracking |
| **Iteraciones** | 100-500 | Variable (hasta solución) |
| **Velocidad** | Muy rápida | Moderada |
| **Heurísticas** | Avanzadas (múltiples reglas) | Simples (MRV + poda) |
| **Propósito** | Eficiencia práctica | Enseñanza de algoritmos |

Para más detalles, consulta `COMPARACION_ALGORITMOS.md`.

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
