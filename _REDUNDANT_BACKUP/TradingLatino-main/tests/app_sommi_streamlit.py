# app_sommi_streamlit.py
import streamlit as st
import pandas as pd
import numpy as np
import datetime
from binance.client import Client

# --- Configuración Binance ---
API_KEY = "TU_API_KEY"
API_SECRET = "TU_API_SECRET"
client = Client(API_KEY, API_SECRET)

# ==============================
# Funciones auxiliares estrategia
# ==============================
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
    wtCrossUp = (wt1.shift(1) <= wt2.shift(1)) & (wt1 > wt2)
    wtCrossDown = (wt1.shift(1) >= wt2.shift(1)) & (wt1 < wt2)
    return wt1.fillna(0), wt2.fillna(0), wtVwap.fillna(0), wtCrossUp.fillna(False), wtCrossDown.fillna(False)

def f_rsimfi(df, period, multiplier):
    num = (df['close'] - df['open'])
    den = (df['high'] - df['low']).replace(0, np.nan)
    value = (num / den) * multiplier
    return value.rolling(period).mean().reindex(df.index).fillna(0.0)

def f_get_htf_candle(ha_df, tf_minutes):
    rule = f"{tf_minutes}min"
    agg = ha_df.resample(rule).agg({'ha_open':'first', 'ha_close':'last'}).dropna()
    candleBodyDir = agg['ha_close'] > agg['ha_open']
    return candleBodyDir.reindex(ha_df.index, method='ffill').fillna(False)

def detect_sommi_signals(df):
    # --- Heikin Ashi ---
    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4.0
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

    # --- parámetros ---
    wt1, wt2, wtVwap, wtCrossUp, wtCrossDown = f_wavetrend(ha_df['ha_close'], 9, 12, 3)
    rsimfi = f_rsimfi(df, 60, 150)
    candleDir1 = f_get_htf_candle(ha_df, 60)
    candleDir2 = f_get_htf_candle(ha_df, 240)

    bullFlag = (rsimfi > 0) & (wt2 < 0) & wtCrossUp & (wtVwap > 0)
    bearFlag = (rsimfi < 0) & (wt2 > 0) & wtCrossDown & (wtVwap < 0)
    bullDiamond = (wt2 <= 0) & wtCrossUp & candleDir1 & candleDir2
    bearDiamond = (wt2 >= 0) & wtCrossDown & (~candleDir1) & (~candleDir2)

    whale_bull = bullFlag & bullDiamond
    whale_bear = bearFlag & bearDiamond

    bulls = ha_df.index[whale_bull].to_series().dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
    bears = ha_df.index[whale_bear].to_series().dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
    return bulls, bears

# ==============================
# Interfaz Streamlit
# ==============================
st.title("👽 Estrategia Sommi + Binance Downloader")

symbol = st.text_input("Par de trading", "BTCUSDT")
interval = st.selectbox("Intervalo", ["5m", "15m", "1h", "4h"])
start_date = st.date_input("Fecha inicio", datetime.date(2025, 9, 28))
end_date = st.date_input("Fecha fin", datetime.date(2025, 9, 29))

if st.button("📥 Descargar y ejecutar estrategia"):
    start_dt = datetime.datetime.combine(start_date, datetime.time(0, 0))
    end_dt = datetime.datetime.combine(end_date, datetime.time(23, 59))
    start_str = start_dt.strftime("%d %b %Y %H:%M:%S")
    end_str = end_dt.strftime("%d %b %Y %H:%M:%S")

    klines = client.get_historical_klines(symbol, interval, start_str, end_str)
    df = pd.DataFrame(klines, columns=[
        "timestamp","open","high","low","close","volume",
        "close_time","quote_asset_volume","trades",
        "taker_buy_base","taker_buy_quote","ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open","high","low","close","volume"]].astype(float)

    st.dataframe(df.head(10))

    bulls, bears = detect_sommi_signals(df)

    st.subheader("👽 Señales Bullish")
    for ts in bulls:
        st.write("👽", ts)

    st.subheader("👹 Señales Bearish")
    for ts in bears:
        st.write("👹", ts)

