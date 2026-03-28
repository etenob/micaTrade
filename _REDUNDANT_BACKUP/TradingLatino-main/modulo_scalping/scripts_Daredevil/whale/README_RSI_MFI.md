# Módulo RSI_MFI_Custom

Este módulo contiene la función `rsi_mfi_custom` que calcula un indicador híbrido entre RSI y MFI, basado en la lógica del script original "Multiple Strategies [LPWN]" de Lupown.

## Objetivo

Generar una señal combinada que refleje la fuerza relativa (RSI) y el flujo de dinero (MFI) para identificar condiciones de sobrecompra o sobreventa, usada para detectar patrones Whale (👽/👹).

## Funciones

- `calculate_rsi(close: pd.Series, length: int = 14) -> pd.Series`  
  Calcula el RSI clásico sobre la serie de precios de cierre.

- `calculate_mfi(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, length: int = 14) -> pd.Series`  
  Calcula el Money Flow Index clásico.

- `rsi_mfi_custom(df: pd.DataFrame, length: int = 14) -> pd.Series`  
  Combina ambos indicadores para obtener un valor único, que se usa para la lógica de detección Whale.

## Uso

El input esperado es un DataFrame con columnas mínimas:  
`'high'`, `'low'`, `'close'`, `'volume'`.

Ejemplo básico:

```python
import pandas as pd
from rsimfi_custom import rsi_mfi_custom

# Supongamos df con las columnas necesarias
result = rsi_mfi_custom(df)
El resultado es una serie con valores que oscilan entre 0 y 100, similar al RSI o MFI tradicional.

Nota
La combinación aquí es simple (promedio), pero puede ajustarse o mejorarse para replicar con mayor precisión el comportamiento del script original de Lupown.