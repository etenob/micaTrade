# whale_signals.py - Señal Whale 👽👹 derivada del script LPWN

import numpy as np
import pandas as pd

# --- Configuraciones default (adaptables desde config.json)
WT_CHANNEL_LEN = 9
WT_AVG_LEN = 12
WT_MA_LEN = 3
RSIMFI_PERIOD = 60
RSIMFI_MULT = 150
RSIMFI_POS_Y = 2.5

VWAP_BULL = 0
VWAP_BEAR = 0
WT_BULL_LEVEL = 0
WT_BEAR_LEVEL = 0
RSIMFI_BULL_LEVEL = 0
RSIMFI_BEAR_LEVEL = 0

# --- WaveTrend simplificado (sin timeframe múltiple aún)
def wavetrend(close, high, low, channel_len, avg_len, ma_len):
    hlc3 = (high + low + close) / 3
    esa = hlc3.ewm(span=channel_len).mean()
    de = abs(hlc3 - esa).ewm(span=channel_len).mean()
    ci = (hlc3 - esa) / (0.015 * de)
    wt1 = ci.ewm(span=avg_len).mean()
    wt2 = wt1.rolling(ma_len).mean()
    wt_vwap = wt1 - wt2
    return wt1, wt2, wt_vwap

# --- RSI + MFI combinado
def rsimfi(close, open_, high, low, period, multiplier, offset):
    with np.errstate(divide='ignore', invalid='ignore'):
        value = ((close - open_) / (high - low)) * multiplier
        value = pd.Series(value).rolling(period).mean() - offset
        return value

# --- Sommi Flag Detector
def detectar_sommi_flag(df):
    wt1, wt2, wt_vwap = wavetrend(df['close'], df['high'], df['low'], WT_CHANNEL_LEN, WT_AVG_LEN, WT_MA_LEN)
    rsimfi_val = rsimfi(df['close'], df['open'], df['high'], df['low'], RSIMFI_PERIOD, RSIMFI_MULT, RSIMFI_POS_Y)

    # Cruces WT
    wt_cross = (wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1)) | (wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1))
    wt_cross_up = wt2 - wt1 <= 0
    wt_cross_down = wt2 - wt1 >= 0

    bull_flag = (rsimfi_val > RSIMFI_BULL_LEVEL) & (wt2 < WT_BULL_LEVEL) & wt_cross & wt_cross_up & (wt_vwap > VWAP_BULL)
    bear_flag = (rsimfi_val < RSIMFI_BEAR_LEVEL) & (wt2 > WT_BEAR_LEVEL) & wt_cross & wt_cross_down & (wt_vwap < VWAP_BEAR)

    return bull_flag.fillna(False), bear_flag.fillna(False)

# --- Señal final: Whale 👽 / 👹
def detect_whale_signals(df):
    bull_flag, bear_flag = detectar_sommi_flag(df)
    senal_whale_bull = bull_flag
    senal_whale_bear = bear_flag
    return senal_whale_bull, senal_whale_bear
