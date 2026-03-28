# 🔀 Módulo EMA Cross

Este módulo detecta cruces entre dos EMAs, útiles para generar señales de cambio de tendencia:

* Cruce Alcista → "Golden Cross"
* Cruce Bajista → "Death Cross"

Se utiliza comúnmente con combinaciones como EMA 10 vs EMA 55, o EMA 50 vs EMA 200.

---

## ⚙️ Función principal

```python
detectar_cruce_emas(ema_rapida: Series, ema_lenta: Series) -> str | None
```

---

## 📥 Entrada requerida

* `ema_rapida`: Serie más sensible (por ejemplo, EMA 10)
* `ema_lenta`: Serie más lenta (por ejemplo, EMA 55)

---

## 💬 Posibles resultados

* "cruce\_alcista"
* "cruce\_bajista"
* `None` si no hay cruce en la última vela

---

## ✅ Ejemplo de uso

```python
from ema_cross import detectar_cruce_emas

cruce = detectar_cruce_emas(ema10, ema55)
if cruce == "cruce_alcista":
    print("🚀 Golden Cross detectado")
elif cruce == "cruce_bajista":
    print("⚠️ Death Cross detectado")
```

---

## 📦 Parte del sistema

`/Scripts_Daredevil/Scripts/ema_cross/`
