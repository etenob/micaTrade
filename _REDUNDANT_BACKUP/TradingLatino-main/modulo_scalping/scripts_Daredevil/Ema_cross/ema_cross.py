# ema_cross.py - Cruces entre EMAs relevantes (Golden/Death Cross)

import pandas as pd

def detectar_cruce_emas(ema_rapida: pd.Series, ema_lenta: pd.Series):
    """
    Detecta cruce alcista o bajista entre dos EMAs.
    Retorna:
    - 'cruce_alcista' si la rápida cruza de abajo hacia arriba
    - 'cruce_bajista' si la rápida cruza de arriba hacia abajo
    - None si no hay cruce
    """
    if len(ema_rapida) < 2 or len(ema_lenta) < 2:
        return None

    cruce_alcista = ema_rapida.iloc[-2] < ema_lenta.iloc[-2] and ema_rapida.iloc[-1] > ema_lenta.iloc[-1]
    cruce_bajista = ema_rapida.iloc[-2] > ema_lenta.iloc[-2] and ema_rapida.iloc[-1] < ema_lenta.iloc[-1]

    if cruce_alcista:
        return "cruce_alcista"
    elif cruce_bajista:
        return "cruce_bajista"
    else:
        return None
