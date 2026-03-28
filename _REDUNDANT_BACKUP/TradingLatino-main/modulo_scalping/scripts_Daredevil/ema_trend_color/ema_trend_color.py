# ema_trend_color.py - Detección de tendencia basada en color por pendiente EMA

import pandas as pd

def detectar_color_tendencia(ema: pd.Series) -> str:
    """
    Devuelve 'verde' si la EMA está subiendo, 'rojo' si está bajando.
    """
    if len(ema) < 2:
        return "indefinido"
    if ema.iloc[-1] > ema.iloc[-2]:
        return "verde"
    elif ema.iloc[-1] < ema.iloc[-2]:
        return "rojo"
    else:
        return "plano"
