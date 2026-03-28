# wavetrend.py

import pandas as pd
import numpy as np

def calculate_wavetrend(df: pd.DataFrame, channel_length=9, average_length=12, ma_length=3) -> pd.DataFrame:
    """
    Calcular el indicador WaveTrend como en el script LPWN.

    Retorna:
        DataFrame con columnas 'wt1', 'wt2', 'wtCross', 'wtCrossUp', 'wtCrossDown', 'wtVwap'
    """
    # Cálculo ESA (Exponential Moving Average del precio promedio)
    precio = (df['high'] + df['low'] + df['close']) / 3
    esa = precio.ewm(span=channel_length, adjust=False).mean()
    de = (precio - esa).abs().ewm(span=channel_length, adjust=False).mean()

    ci = (precio - esa) / (0.015 * de)
    wt1 = ci.ewm(span=average_length, adjust=False).mean()
    wt2 = wt1.rolling(window=ma_length).mean()

    wt_cross = (wt1 - wt2).apply(np.sign)
    wt_cross_up = (wt2 - wt1) <= 0
    wt_cross_down = (wt2 - wt1) >= 0
    wt_vwap = wt1 - wt2

    return pd.DataFrame({
        'wt1': wt1,
        'wt2': wt2,
        'wtCross': wt_cross,
        'wtCrossUp': wt_cross_up,
        'wtCrossDown': wt_cross_down,
        'wtVwap': wt_vwap
    })

if __name__ == "__main__":
    # Ejemplo de prueba
    np.random.seed(0)
    n = 100
    df = pd.DataFrame({
        'high': np.random.rand(n) * 100 + 5,
        'low': np.random.rand(n) * 100 - 5,
        'close': np.random.rand(n) * 100
    })

    resultado = calculate_wavetrend(df)
    print(resultado.tail())
