# ema_combo.py - Cálculo de EMAs (10 / 55 / 100 / 200)

import pandas as pd


def calcular_emas(close: pd.Series):
    """
    Calcula 4 medias exponenciales:
    - EMA 10 (corto plazo)
    - EMA 55 (mediano plazo)
    - EMA 100 (largo plazo)
    - EMA 200 (muy largo plazo)
    """
    ema_10 = close.ewm(span=10).mean()
    ema_55 = close.ewm(span=55).mean()
    ema_100 = close.ewm(span=100).mean()
    ema_200 = close.ewm(span=200).mean()
    return ema_10, ema_55, ema_100, ema_200
