# 🧭 Módulo Estado Momentum

Este módulo evalúa la direccionalidad del movimiento del precio en base a cuatro condiciones booleanas (`sc1` a `sc4`). Forma parte del sistema de diagnóstico visual del script LPWN.

---

## 🔍 ¿Qué hace?

Evalúa la estructura del movimiento:

* `sc1`: tendencia alcista de corto plazo
* `sc2`: tendencia bajista de corto plazo
* `sc3`: confirmación alcista de largo plazo
* `sc4`: confirmación bajista de largo plazo

Según la combinación de estos factores, devuelve una interpretación textual de la dirección del momentum.

---

## ⚙️ Función principal

```python
interpretar_momentum(sc1: bool, sc2: bool, sc3: bool, sc4: bool) -> str
```

---

## 💬 Posibles resultados

* "Direccionalidad alcista"
* "Direccionalidad bajista"
* "Direccionalidad indefinida"

---

## ✅ Ejemplo de uso

```python
from estado_momentum import interpretar_momentum

mensaje = interpretar_momentum(sc1=True, sc2=False, sc3=True, sc4=False)
print(f"📊 Estado del Momentum: {mensaje}")
```

---

## 📦 Parte del sistema

`/Scripts_Daredevil/Scripts/estado_momentum/`
