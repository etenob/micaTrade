# 🐳 Módulo Whale LPWN

Este módulo detecta señales Whale 👽 (alcista) y 👹 (bajista) basadas en el indicador WaveTrend + RSI+MFI, como se implementa en el script “Multiple Strategies \[LPWN]”.

---

## 🔍 ¿Qué hace?

Calcula si se cumple la **combinación Sommi Flag**, que representa un posible cambio fuerte de dirección del mercado, usando:

* WaveTrend (`wt1`, `wt2`, `vwap`)
* RSI+MFI adaptado (basado en movimiento relativo)
* Cruces de tendencia (`wt_cross`, up/down)

⚠️ Por ahora **no incluye Sommi Diamond**, ya que requiere candles Heikin Ashi HTF.

---

## ⚙️ Funciones incluidas

```python
detectar_senales_whale(df) → (bool_series_bull, bool_series_bear)
```

Usar esta función pasando un DataFrame con columnas:
`['Open', 'High', 'Low', 'Close']`

---

## 🛠️ Parámetros usados (ajustables en config o hardcode)

* WaveTrend:

  * `WT_CHANNEL_LEN = 9`
  * `WT_AVG_LEN = 12`
  * `WT_MA_LEN = 3`
* RSI+MFI:

  * `RSIMFI_PERIOD = 60`
  * `RSIMFI_MULT = 150`
  * `RSIMFI_POS_Y = 2.5`

---

## ✅ Ejemplo de uso

```python
from whale import detectar_senales_whale

bull, bear = detectar_senales_whale(df)
if bull.iloc[-1]:
    print("🚨 Señal Whale 👽 detectada")
elif bear.iloc[-1]:
    print("🚨 Señal Whale 👹 detectada")
```

---

## 📦 Parte del sistema:

`/Scripts_Daredevil/Scripts/whale_lpwn/`
