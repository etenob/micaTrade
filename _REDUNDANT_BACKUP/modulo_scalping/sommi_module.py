# modulo_scalping/sommi_module.py
import pandas as pd
import numpy as np

# ---------- auxiliares ----------
def ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def sma(series, length):
    return series.rolling(length).mean()

def f_wavetrend(series, chlen, avg, malen):
    esa = ema(series, chlen)
    de = ema((series - esa).abs(), chlen)
    ci = (series - esa) / (0.015 * de.replace(0, np.nan))
    wt1 = ema(ci, avg)
    wt2 = sma(wt1, malen)
    wtVwap = wt1 - wt2
    wt1 = pd.to_numeric(wt1, errors="coerce").fillna(0.0)
    wt2 = pd.to_numeric(wt2, errors="coerce").fillna(0.0)
    wtVwap = pd.to_numeric(wtVwap, errors="coerce").fillna(0.0)
    wtCrossUp = (wt1.shift(1) <= wt2.shift(1)) & (wt1 > wt2)
    wtCrossDown = (wt1.shift(1) >= wt2.shift(1)) & (wt1 < wt2)
    wtCrossUp = wtCrossUp.fillna(False)
    wtCrossDown = wtCrossDown.fillna(False)
    return wt1, wt2, wtVwap, wtCrossUp, wtCrossDown

def f_rsimfi(df, period, multiplier):
    num = (df['close'] - df['open'])
    den = (df['high'] - df['low']).replace(0, np.nan)
    value = (num / den) * multiplier
    return value.rolling(period).mean().reindex(df.index).fillna(0.0)

def f_get_htf_candle(ha_df, tf_minutes):
    rule = f"{tf_minutes}min"
    agg = ha_df.resample(rule).agg({'ha_open':'first', 'ha_close':'last'}).dropna()
    candleBodyDir = agg['ha_close'] > agg['ha_open']
    candleBodyDir = candleBodyDir.reindex(ha_df.index, method='ffill').fillna(False)
    return candleBodyDir

# ---------- API ----------
def generate_signal_from_df(df):
    """
    Input: df: DataFrame con columnas ['time' or index datetime, 'open','high','low','close','volume']
    Returns: dict { "signal": "LONG"/"SHORT"/None, "debug": {...} }
    """
    # --- asegurar índice datetime (espera column 'time' en unix seconds o 'timestamp' string)
    df = df.copy()
    if 'time' in df.columns:
        # convert seconds -> datetime UTC
        df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
    else:
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("df debe contener 'timestamp' o índice datetime")

    df = df.sort_index()
    for c in ['open','high','low','close','volume']:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    # --- Heikin Ashi
    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4.0
    ha_open_arr = np.empty(len(df), dtype=float)
    ha_open_arr[0] = df['open'].iloc[0]
    for i in range(1, len(df)):
        ha_open_arr[i] = (ha_open_arr[i-1] + ha_close.iloc[i-1]) / 2.0
    ha_open = pd.Series(ha_open_arr, index=df.index)
    ha_high = pd.concat([df['high'], ha_open, ha_close], axis=1).max(axis=1)
    ha_low  = pd.concat([df['low'], ha_open, ha_close], axis=1).min(axis=1)
    ha_df = pd.DataFrame({'ha_open': ha_open, 'ha_close': ha_close, 'ha_high': ha_high, 'ha_low': ha_low}, index=df.index)

    # --- parámetros (igual que Pine defaults)
    wtChannelLen = 9
    wtAverageLen = 12
    wtMALen = 3
    rsiMFIperiod = 60
    rsiMFIMultiplier = 150
    sommiHTCRes = 60     # 1H
    sommiHTCRes2 = 240   # 4H

    # --- WaveTrend + RSI/MFI
    wt1, wt2, wtVwap, wtCrossUp, wtCrossDown = f_wavetrend(ha_df['ha_close'], wtChannelLen, wtAverageLen, wtMALen)
    rsimfi = f_rsimfi(df, rsiMFIperiod, rsiMFIMultiplier)

    # --- Flags (usar los umbrales que necesites; aquí defaults = 0)
    bullFlag = (rsimfi > 0) & (wt2 < 0) & wtCrossUp & (wtVwap > 0)
    bearFlag = (rsimfi < 0) & (wt2 > 0) & wtCrossDown & (wtVwap < 0)

    # --- Diamonds (HTF candles)
    candleDir1 = f_get_htf_candle(ha_df, sommiHTCRes)
    candleDir2 = f_get_htf_candle(ha_df, sommiHTCRes2)

    bullDiamond = (wt2 <= 0) & wtCrossUp & candleDir1 & candleDir2
    bearDiamond = (wt2 >= 0) & wtCrossDown & (~candleDir1) & (~candleDir2)

    whale_bull = bullFlag & bullDiamond
    whale_bear = bearFlag & bearDiamond

    # Prepare debug
    debug = {
        "latest_close": float(df['close'].iloc[-1]),
        "wt2_latest": float(wt2.iloc[-1]),
        "wtVwap_latest": float(wtVwap.iloc[-1]),
        "rsimfi_latest": float(rsimfi.iloc[-1]),
        "bullFlag": bool(bullFlag.iloc[-1]) if len(bullFlag)>0 else False,
        "bearFlag": bool(bearFlag.iloc[-1]) if len(bearFlag)>0 else False,
        "has_whale_bull": bool(whale_bull.any()),
        "has_whale_bear": bool(whale_bear.any()),
    }

    # If any bull in last bar -> LONG, if any bear -> SHORT. Prefer latest bar exact match if present
    signal = None
    if whale_bull.iloc[-1]:
        signal = "LONG"
    elif whale_bear.iloc[-1]:
        signal = "SHORT"
    else:
        # fallback: if any True anywhere recently (optional)
        if whale_bull.any():
            signal = "LONG"
        elif whale_bear.any():
            signal = "SHORT"

    return {"signal": signal, "debug": debug, "timestamps_bull": ha_df.index[whale_bull].tolist(), "timestamps_bear": ha_df.index[whale_bear].tolist()}

