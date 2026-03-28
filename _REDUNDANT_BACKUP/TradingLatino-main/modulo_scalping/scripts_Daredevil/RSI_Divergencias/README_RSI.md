# 📘 Módulo: RSI + Divergencias

## 🎯 Objetivo

Detectar **divergencias clásicas** entre el RSI y el precio de cierre, útil para anticipar posibles cambios de tendencia.

---

## ⚙️ Indicador aplicado

- **RSI (Relative Strength Index)** con `timeperiod=14`
- **Divergencia Alcista (🔼):** El precio hace un mínimo más bajo, pero el RSI sube.
- **Divergencia Bajista (🔽):** El precio hace un máximo más alto, pero el RSI baja.

---

## 📦 Función principal

```python
rsi, divergencias = detectar_divergencias_rsi(cierre, minimo, maximo)
Parámetros:
cierre: Serie de precios de cierre.

minimo: Serie de mínimos.

maximo: Serie de máximos.

📈 Visualización sugerida
En consola interactiva o gráfico:

RSI en color púrpura

Texto 🔼 o 🔽 sobre el RSI donde se detecta una divergencia

📌 Uso
Este módulo se puede usar como confirmación adicional junto con Koncorde o Whale Signals en tu sistema Daredevil.

🧠 Referencias
Estrategias visuales validadas por Daredevil.

Basado en lógica de lectura RSI divergente simple.