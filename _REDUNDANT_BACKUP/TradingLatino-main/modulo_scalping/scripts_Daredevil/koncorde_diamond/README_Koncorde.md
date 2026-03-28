# 💎 Módulo Koncorde Diamond

Detecta cruces de la línea marrón del Koncorde respecto a su media móvil. Esta lógica corresponde a la señal visual del **"Koncorde Diamond"** en el script LPWN.

---

## 🔍 ¿Qué hace?

Evalúa los últimos dos valores de las líneas:

* Si la línea marrón cruza **por arriba** de su media → ✅ Señal Bull (punto verde)
* Si cruza **por debajo** → ❌ Señal Bear (punto rojo)

---

## ⚙️ Función

```python
detectar_koncorde_diamond(marron: Series, media: Series, show_kd: bool = True)
```

Devuelve una cadena de texto indicando si hay señal:

* "✅ Punto verde - Señal Koncorde Bull"
* "❌ Punto rojo - Señal Koncorde Bear"
* `None` si no hay cruce

---

## 🧪 Requisitos de entrada

* `marron`: Serie de valores de la línea marrón (calculada previamente)
* `media`: Media móvil de la línea marrón

---

## ✅ Ejemplo de uso

```python
from koncorde import detectar_koncorde_diamond

mensaje = detectar_koncorde_diamond(marron, media)
if mensaje:
    print(f"🚨 Koncorde Diamond: {mensaje}")
```

---

## 📦 Parte del sistema

`/Scripts_Daredevil/Scripts/koncorde_diamond/`
