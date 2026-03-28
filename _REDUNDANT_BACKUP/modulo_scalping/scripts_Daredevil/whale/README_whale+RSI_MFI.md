# Módulo Whale LPWN

Este módulo integra el cálculo de WaveTrend y el RSI+MFI custom para detectar señales Whale 👽 y 👹 basadas en el indicador original "Multiple Strategies [LPWN]" de Lupown.

## Archivos

- `whale_lpwn.py`  
  Función principal `detect_whale_signals` que recibe DataFrame con OHLCV y devuelve señales Whale.

- `wavetrend.py`  
  Función `calculate_wavetrend` para calcular WaveTrend wt1 y wt2.

- `rsimfi_custom.py`  
  Función `rsi_mfi_custom` que combina RSI y MFI para mejorar la detección.

## Uso básico

```python
import pandas as pd
from whale_lpwn import detect_whale_signals

# df con columnas ['open', 'high', 'low', 'close', 'volume']
df_signals = detect_whale_signals(df)
print(df_signals[['wt1', 'wt2', 'rsi_mfi', 'whale_bull', 'whale_bear']])
Notas
Las condiciones para las señales Whale pueden ajustarse según tu análisis detallado del script LPWN original.

Este módulo es la base para detección de señales Whale en tu sistema Kernel_Daredevil_TradingBot.

