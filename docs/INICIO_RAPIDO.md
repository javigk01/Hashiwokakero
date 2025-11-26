# 🚀 Inicio Rápido - Sistema de Benchmark

## Ejecución en 3 Pasos

### 1️⃣ Benchmark Básico
```bash
py benchmark_solvers.py
```
**Resultado:** Comparación de tiempos en consola

### 2️⃣ Reporte JSON
```bash
py generate_report.py
```
**Resultado:** Archivo `benchmark_report.json` con datos estructurados

### 3️⃣ Visualización (Opcional)
```bash
pip install matplotlib
py visualize_results.py
```
**Resultado:** Archivo `benchmark_comparison.png` con 6 gráficos

---

## 📊 Resultado Esperado

```
Tablero              CSP (ms)        BT (ms)         Speedup    Mejor
-------------------- --------------- --------------- ---------- ----------
Simple 1                     2.86          36.15     12.65x   CSP
Fácil                        2.32           8.86      3.82x   CSP
Difícil                      6.16          57.26      9.30x   CSP
Ejemplo Base                 2.71         239.54     88.49x   CSP
Hash Test                    1.84           8.17      4.44x   CSP

Speedup promedio de CSP: 22.04x
```

---

## 📁 Archivos de Prueba

Todos los tableros son **7x7**:
- `test_simple1.txt`
- `test_easy.txt`
- `test_hard.txt`
- `example.txt`
- `hashitest.txt`
- Y más...

---

## 📚 Más Información

- **Guía completa:** `GUIA_USO.md`
- **Resumen:** `RESUMEN_IMPLEMENTACION.md`
- **Archivos de prueba:** `TEST_FILES_README.md`

---

¡Listo para comparar algoritmos! 🎯
