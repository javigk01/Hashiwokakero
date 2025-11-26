# Comparación de Algoritmos de Solución - Hashiwokakero

## Resumen

Se implementaron dos solucionadores para el juego Hashiwokakero, cada uno usando técnicas algorítmicas diferentes:

1. **Solver CSP (solver.py)**: Usa Constraint Propagation + Backtracking
2. **Backtracking Puro (backtracking_solver.py)**: Usa Recursividad + Backtracking sin optimizaciones

---

## 1. Solver CSP (Constraint Propagation + Backtracking)

### Técnicas utilizadas:
- **Propagación de restricciones**: Aplica reglas determinísticas para reducir el espacio de búsqueda
- **Backtracking guiado por heurísticas**: Solo retrocede cuando las reglas no pueden avanzar más
- **Reglas greedy locales**: Aplica movimientos forzados cuando una isla solo tiene una opción válida

### Características:
```python
# Ejemplo de regla aplicada:
- Si una isla tiene valor 4 y solo 2 vecinos, conectar con 2 puentes a cada uno
- Si una isla necesita exactamente N puentes y tiene N vecinos, conectar 1 puente a cada uno
- Saturación: si una isla está completa, no agregar más puentes
```

### Complejidad:
- **Mejor caso**: O(n) cuando las reglas resuelven todo el puzzle sin backtracking
- **Peor caso**: O(b^d) donde b es el factor de ramificación y d la profundidad
- **Espacio**: O(d) para la pila de recursión

### Ventajas:
- Muy rápido en puzzles con muchas restricciones
- Reduce drásticamente el espacio de búsqueda
- Pocas iteraciones necesarias

### Desventajas:
- Más complejo de implementar
- Requiere diseñar reglas específicas del dominio

---

## 2. Backtracking Puro (Recursivo)

### Técnicas utilizadas:
- **Backtracking recursivo**: Prueba todas las combinaciones posibles de puentes
- **Fuerza bruta optimizada**: Solo explora estados válidos (sin violar restricciones básicas)
- **Heurística simple**: Ordena islas por número requerido (más restrictivas primero)

### Características:
```python
# Algoritmo básico:
1. Para cada isla:
   2. Para cada vecino válido:
      3. Probar agregar 1 puente
      4. Probar agregar 2 puentes
      5. Si funciona, continuar recursivamente
      6. Si no, retroceder (backtrack)
```

### Complejidad:
- **Mejor caso**: O(n·m) donde n es número de islas y m vecinos promedio
- **Peor caso**: O(3^(n·m)) probando 0, 1 o 2 puentes para cada par
- **Espacio**: O(d) para la pila de recursión

### Ventajas:
- Simple de implementar
- No requiere reglas específicas del dominio
- Garantiza encontrar solución si existe

### Desventajas:
- Mucho más lento que CSP con propagación
- Más iteraciones necesarias
- Puede explorar muchos estados inválidos

---

## Comparación Práctica

| Característica | CSP + Propagation | Backtracking Puro |
|----------------|-------------------|-------------------|
| **Técnica principal** | Constraint propagation | Recursión + backtracking |
| **Iteraciones típicas** | 100-500 | 5,000-50,000 |
| **Velocidad** | Muy rápida | Lenta a moderada |
| **Complejidad código** | Alta | Baja |
| **Uso de memoria** | Moderado | Bajo |
| **Optimización** | Heurísticas avanzadas | Heurística simple |

---

## Clasificación de Técnicas

### Backtracking Puro incluye:
✅ **Backtracking**: Retrocede cuando encuentra estado inválido  
✅ **Recursividad**: Usa llamadas recursivas para explorar el árbol de decisiones  
✅ **Fuerza bruta (optimizada)**: Prueba todas las combinaciones válidas  
✅ **Heurística greedy local**: Ordena islas por restricción (más restrictivas primero)  
❌ **NO usa memoización**: Cada estado se explora independientemente  
❌ **NO usa programación dinámica**: No hay subproblemas superpuestos  
❌ **NO usa A***: No hay función de costo ni búsqueda informada

### Solver CSP incluye:
✅ **Propagación de restricciones**: Reduce espacio de búsqueda aplicando reglas  
✅ **Backtracking**: Solo cuando las reglas no pueden avanzar  
✅ **Greedy (parcial)**: Aplica movimientos forzados inmediatamente  
✅ **Heurísticas avanzadas**: Selecciona mejores decisiones primero  
❌ **NO es puramente greedy**: Puede retroceder si una decisión falla  
❌ **NO usa memoización**: Cada exploración es única  

---

## Recomendaciones de Uso

- **Usar CSP Solver** cuando:
  - El puzzle es grande o complejo
  - Se necesita velocidad
  - El puzzle tiene muchas restricciones naturales

- **Usar Backtracking Puro** cuando:
  - Se quiere demostrar el algoritmo básico
  - Se estudia recursividad y backtracking
  - El puzzle es pequeño (< 7x7)
  - Se prefiere simplicidad sobre velocidad

---

## Conclusión

Ambos algoritmos resuelven el mismo problema pero con enfoques diferentes:
- El **Backtracking Puro** es un enfoque de **fuerza bruta optimizada** con recursividad
- El **Solver CSP** es un enfoque **inteligente** que combina reglas del dominio con búsqueda

El Backtracking Puro es ideal para aprender los conceptos fundamentales de recursividad y backtracking, mientras que el Solver CSP es más eficiente para uso práctico en puzzles complejos.
