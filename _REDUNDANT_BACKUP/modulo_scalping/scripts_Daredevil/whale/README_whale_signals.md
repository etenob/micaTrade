✅ README_whale_signals
📌 Estructura general:
Sección	Descripción
Config global	Variables de configuración como longitudes de WaveTrend, niveles críticos, etc.
WaveTrend	Calcula wt1, wt2, wt_vwap sin usar marco temporal múltiple (por ahora).
RSIMFI	Métrica custom de presión (RSI + MFI) con offset visual.
Sommi Flag	Detecta los patrones de cambio de dirección para 👽 (bullish) y 👹 (bearish).
Whale Signal	Se generan las señales basadas en los flags detectados, listas para usar.

🧠 Lógica visual reproducida del script original LPWN:
👽 Whale Bullish se activa cuando:

rsimfi alto (presión positiva),

wt2 bajo (zona de sobreventa),

wt1 cruza hacia arriba a wt2,

vwap alcista.

👹 Whale Bearish se activa cuando:

rsimfi bajo (presión negativa),

wt2 alto (zona de sobrecompra),

wt1 cruza hacia abajo a wt2,

vwap bajista.

🧩 Sugerencia para integración modular
Este archivo puede residir en:

bash
Copiar código
/Scripts_Daredevil/Scripts/whale_signals.py
Y luego puede ser importado desde tu consola o módulo principal así:

python
Copiar código
from Scripts.whale_signals import detect_whale_signals
Y usarse con un DataFrame de velas OHLCV:

python
Copiar código
bull, bear = detect_whale_signals(df)
if bull.iloc[-1]:
    print("👽 Señal Whale Alcista detectada")
if bear.iloc[-1]:
    print("👹 Señal Whale Bajista detectada")
🛠️ Próximos pasos opcionales:
Añadir SommiDiamond: Integrar lógica HTF más adelante.

Pasar parámetros desde config.json automáticamente.

Registrar señales detectadas en consola o exportarlas a .csv.

Test unitarios para cada función (wavetrend, rsimfi, detectar_sommi_flag).

🧾 Documentación sugerida en README del módulo:
markdown
Copiar código
# 🐋 Whale Signals 👽👹 - Módulo de señales visuales

Este módulo detecta señales de entrada visual basadas en el script LPWN:
- WaveTrend (WT1/WT2)
- RSI + MFI combinados
- Sommi Flag (Patrón gráfico de cambio de tendencia)

## Funciones principales:

- wavetrend()
- rsimfi()
- detectar_sommi_flag()
- detect_whale_signals()

## Uso:

```python
from Scripts.whale_signals import detect_whale_signals

df = cargar_ohlcv('BTCUSDT_15m.csv')  # DataFrame con columnas: Open, High, Low, Close
bull, bear = detect_whale_signals(df)