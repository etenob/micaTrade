# test_sommi.py  (VERSIÓN CORREGIDA)
import pandas as pd
import numpy as np

# ---------- auxiliares ----------
def ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def sma(series, length):
    return series.rolling(length).mean()

def f_wavetrend(series, chlen, avg, malen):
    # series: pd.Series (ha_close) con índice datetime
    esa = ema(series, chlen)
    de = ema((series - esa).abs(), chlen)
    ci = (series - esa) / (0.015 * de.replace(0, np.nan))
    wt1 = ema(ci, avg)
    wt2 = sma(wt1, malen)
    wtVwap = wt1 - wt2
    # forzar numeric y llenar NaN
    wt1 = pd.to_numeric(wt1, errors="coerce").fillna(0.0)
    wt2 = pd.to_numeric(wt2, errors="coerce").fillna(0.0)
    wtVwap = pd.to_numeric(wtVwap, errors="coerce").fillna(0.0)
    # cruce tipo "cross up / cross down" (mejor que usar solo >/<)
    wtCrossUp = (wt1.shift(1) <= wt2.shift(1)) & (wt1 > wt2)
    wtCrossDown = (wt1.shift(1) >= wt2.shift(1)) & (wt1 < wt2)
    wtCrossUp = wtCrossUp.fillna(False)
    wtCrossDown = wtCrossDown.fillna(False)
    return wt1, wt2, wtVwap, wtCrossUp, wtCrossDown

def f_rsimfi(df, period, multiplier):
    # df: OHLC indexed by timestamp
    num = (df['close'] - df['open'])
    den = (df['high'] - df['low']).replace(0, np.nan)
    value = (num / den) * multiplier
    return value.rolling(period).mean().reindex(df.index).fillna(0.0)

def f_get_htf_candle(ha_df, tf_minutes):
    # ha_df: DataFrame con índice datetime y columnas ha_open, ha_close
    rule = f"{tf_minutes}min"
    agg = ha_df.resample(rule).agg({'ha_open':'first', 'ha_close':'last'}).dropna()
    candleBodyDir = agg['ha_close'] > agg['ha_open']
    # reindex al índice base (ha_df.index) y forward-fill
    candleBodyDir = candleBodyDir.reindex(ha_df.index, method='ffill').fillna(False)
    return candleBodyDir

# ---------- detector ----------
def detect_sommi_signals(csv_file):
    df = pd.read_csv(csv_file)
    # timestamp -> índice datetime (crucial)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp').sort_index()

    # asegurar columnas numéricas
    for c in ['open','high','low','close','volume']:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    # --- Heikin Ashi (mantener índice datetime) ---
    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4.0

    # construir ha_open eficientemente con numpy
    ha_open_arr = np.empty(len(df), dtype=float)
    ha_open_arr[0] = df['open'].iloc[0]
    for i in range(1, len(df)):
        ha_open_arr[i] = (ha_open_arr[i-1] + ha_close.iloc[i-1]) / 2.0
    ha_open = pd.Series(ha_open_arr, index=df.index)

    ha_high = pd.concat([df['high'], ha_open, ha_close], axis=1).max(axis=1)
    ha_low  = pd.concat([df['low'], ha_open, ha_close], axis=1).min(axis=1)

    ha_df = pd.DataFrame({
        'ha_open': ha_open,
        'ha_close': ha_close,
        'ha_high': ha_high,
        'ha_low': ha_low
    }, index=df.index)

    # --- parámetros (default del Pine mostrado) ---
    wtChannelLen = 9
    wtAverageLen = 12
    wtMALen = 3
    rsiMFIperiod = 60
    rsiMFIMultiplier = 150
    sommiHTCRes = 60   # 1H
    sommiHTCRes2 = 240 # 4H

    # --- WaveTrend y RSI+MFI (todas series con mismo índice datetime) ---
    wt1, wt2, wtVwap, wtCrossUp, wtCrossDown = f_wavetrend(ha_df['ha_close'], wtChannelLen, wtAverageLen, wtMALen)
    rsimfi = f_rsimfi(df, rsiMFIperiod, rsiMFIMultiplier)

    # debug rápido (siempre imprimir al testear)
    print("DEBUG: wt2 dtype:", wt2.dtype, " index type:", type(wt2.index[0]))
    print("DEBUG: candle counts:", len(df), "na in wt2:", wt2.isna().sum(), "na in rsimfi:", rsimfi.isna().sum())

    # --- Flags (usar los umbrales que tengas; acá defaults = 0 como el Pine)
    bullFlag = (rsimfi > 0) & (wt2 < 0) & wtCrossUp & (wtVwap > 0)
    bearFlag = (rsimfi < 0) & (wt2 > 0) & wtCrossDown & (wtVwap < 0)

    # --- HTF diamonds
    candleDir1 = f_get_htf_candle(ha_df, sommiHTCRes)   # 1H bollean
    candleDir2 = f_get_htf_candle(ha_df, sommiHTCRes2)  # 4H boolean

    # asegurar que todos tengan mismo índice (deberían)
    assert wt2.index.equals(ha_df.index)
    assert candleDir1.index.equals(ha_df.index)

    # --- Diamond conditions
    bullDiamond = (wt2 <= 0) & wtCrossUp & candleDir1 & candleDir2
    bearDiamond = (wt2 >= 0) & wtCrossDown & (~candleDir1) & (~candleDir2)

    # --- final
    whale_bull = bullFlag & bullDiamond
    whale_bear = bearFlag & bearDiamond

    # debug counts
    print("DEBUG: bullFlag.sum(), bullDiamond.sum(), whale_bull.sum():",
          int(bullFlag.sum()), int(bullDiamond.sum()), int(whale_bull.sum()))
    print("DEBUG: bearFlag.sum(), bearDiamond.sum(), whale_bear.sum():",
          int(bearFlag.sum()), int(bearDiamond.sum()), int(whale_bear.sum()))

    bull_timestamps = ha_df.index[whale_bull].to_series().dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
    bear_timestamps = ha_df.index[whale_bear].to_series().dt.strftime("%Y-%m-%d %H:%M:%S").tolist()

    return bull_timestamps, bear_timestamps

# ---------- main ----------
if __name__ == "__main__":
    archivo = "2025-09-30T03-01_export.csv"  # ruta relativa o absoluta a tu CSV de 5m
    bulls, bears = detect_sommi_signals(archivo)

    print("\n👽 Señales bullish encontradas:")
    for ts in bulls:
        print("  👽", ts)

    print("\n👹 Señales bearish encontradas:")
    for ts in bears:
        print("  👹", ts)

