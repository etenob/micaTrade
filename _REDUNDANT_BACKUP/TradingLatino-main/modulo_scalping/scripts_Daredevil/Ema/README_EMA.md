# 📊 Módulo EMA Combo

Este módulo calcula cuatro medias móviles exponenciales clave para análisis técnico:

* EMA 10 → corto plazo
* EMA 55 → mediano plazo
* EMA 100 → largo plazo
* EMA 200 → muy largo plazo

Estas EMAs son comúnmente usadas para detectar:

* Tendencias dominantes
* Cruces de medias (estrategias Golden/Death Cross)
* Zonas de soporte/resistencia dinámica

---

## ⚙️ Función principal

```python
calcular_emas(close: Series) -> (ema_10, ema_55, ema_100, ema_200)
```

---

## 📥 Entrada requerida

* `close`: Serie de precios de cierre (`pandas.Series`)

---

## ✅ Ejemplo de uso

```python
from ema_combo import calcular_emas

ema10, ema55, ema100, ema200 = calcular_emas(df['Close'])
```

---

## 📦 Parte del sistema

`/Scripts_Daredevil/Scripts/ema_combo/`
