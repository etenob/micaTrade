# 📈 Módulo ADX Status

Evalúa la pendiente del indicador ADX y su relación con un nivel crítico (por defecto 23). Este módulo representa el bloque de interpretación textual del ADX dentro del script LPWN.

---

## 🔍 ¿Qué hace?

Analiza las dos últimas velas del ADX y determina:

* Si la pendiente es positiva o negativa
* Si está por encima o por debajo del nivel 23

Devuelve una **interpretación textual** útil para análisis o alertas.

---

## ⚙️ Función principal

```python
interpretar_adx(adx_series: Series, nivel_critico: float = 23) -> str
```

---

## 💬 Posibles resultados

* "ADX con pendiente positiva por encima del punto 23"
* "ADX con pendiente positiva por debajo del punto 23"
* "ADX con pendiente negativa por debajo del punto 23"
* "ADX con pendiente negativa por encima del punto 23"
* "ADX sin cambio relevante"

---

## ✅ Ejemplo de uso

```python
from adx import interpretar_adx

mensaje = interpretar_adx(adx_series)
print(f"📊 Estado del ADX: {mensaje}")
```

---

## 📦 Parte del sistema

`/Scripts_Daredevil/Scripts/adx_status/`
