#rsimfi_custom.py

import numpy as np
import pandas as pd

def calculate_rsi(close: pd.Series, length: int = 14) -> pd.Series:
    """Calcula el RSI clásico sobre una serie de precios de cierre."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(length, min_periods=length).mean()
    avg_loss = loss.rolling(length, min_periods=length).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)  # valor neutro en inicio

def calculate_mfi(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, length: int = 14) -> pd.Series:
    """Calcula el Money Flow Index clásico."""
    typical_price = (high + low + close) / 3
    money_flow = typical_price * volume
    positive_flow = []
    negative_flow = []

    for i in range(1, len(typical_price)):
        if typical_price[i] > typical_price[i-1]:
            positive_flow.append(money_flow[i])
            negative_flow.append(0)
        else:
            positive_flow.append(0)
            negative_flow.append(money_flow[i])

    positive_mf = pd.Series(positive_flow).rolling(length).sum()
    negative_mf = pd.Series(negative_flow).rolling(length).sum()

    mfi = 100 * (positive_mf / (positive_mf + negative_mf))
    return mfi.fillna(50)  # valor neutro inicial

def rsi_mfi_custom(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """
    Calcula una versión custom que combina RSI y MFI para la detección Whale de LPWN.
    df debe tener columnas: ['high', 'low', 'close', 'volume'].
    """
    rsi = calculate_rsi(df['close'], length)
    mfi = calculate_mfi(df['high'], df['low'], df['close'], df['volume'], length)

    # Combinación simple ponderada (puede ajustarse según el original LPWN)
    combined = (rsi + mfi) / 2
    return combined
