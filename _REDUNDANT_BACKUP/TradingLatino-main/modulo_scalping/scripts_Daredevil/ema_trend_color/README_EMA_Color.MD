# 🟢🔴 Módulo EMA Trend Color

Este módulo interpreta la **pendiente de una EMA** para devolver un "color de tendencia" visual:

* 🟢 `verde` → si la EMA está subiendo
* 🔴 `rojo` → si la EMA está bajando
* ⚪️ `plano` → si no hay cambio

Es útil para pintar zonas del gráfico o indicar la dirección de manera simple.

---

## ⚙️ Función principal

```python
detectar_color_tendencia(ema: Series) -> str
```

---

## 📥 Entrada requerida

* `ema`: Serie temporal de una media exponencial

---

## 💬 Posibles resultados

* "verde"
* "rojo"
* "plano"
* "indefinido" (si hay menos de 2 datos)

---

## ✅ Ejemplo de uso

```python
from ema_trend_color import detectar_color_tendencia

color = detectar_color_tendencia(ema_55)
print(f"Color de tendencia EMA55: {color}")
```

---

## 📦 Parte del sistema

`/Scripts_Daredevil/Scripts/ema_trend_color/`
