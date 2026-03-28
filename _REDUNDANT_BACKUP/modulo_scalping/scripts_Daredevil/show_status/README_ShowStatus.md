# 🧾 Módulo Show Status

Este módulo representa el **panel interpretativo principal** del script LPWN. Combina la evaluación del ADX y del Momentum para generar un estado textual general del mercado.

---

## 🔍 ¿Qué hace?

* Usa `interpretar_adx()` para analizar fuerza direccional (nivel 23)
* Usa `interpretar_momentum()` para entender hacia dónde se mueve el precio
* Combina ambos para emitir un diagnóstico como:

  * "Fuerte movimiento alcista"
  * "Movimiento bajista queriendo ganar fuerza"
  * "Movimiento débil o sin fuerza"

---

## ⚙️ Función principal

```python
estado_general(adx_value, adx_prev, sc1, sc2, sc3, sc4, nivel_critico=23) -> str
```

---

## 📥 Requiere como entrada:

* `adx_value`: Valor actual del ADX
* `adx_prev`: Valor anterior del ADX
* `sc1` a `sc4`: Estados booleanos de momentum (ver módulo `estado_momentum`)

---

## ✅ Ejemplo de uso

```python
from show_status import estado_general

texto = estado_general(adx_value=25, adx_prev=22, sc1=True, sc2=False, sc3=True, sc4=False)
print(texto)
```

---

## 📦 Parte del sistema

`/Scripts_Daredevil/Scripts/show_status/`
