# app_conker_streamlit.py
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
# 📌 Koncorde en Pandas
# ==============================
def calc_koncorde(df: pd.DataFrame,
                  m=15,
                  longitudPVI=90,
                  longitudNVI=90,
                  longitudMFI=14,
                  boLength=25):
    """
    Replica el cálculo del indicador Koncorde (Lupown).
    Devuelve señales de Buy/Sell basadas en marrón vs media.
    """
    tprice = (df['open'] + df['high'] + df['low'] + df['close']) / 4.0  # ohlc4

    # === PVI y NVI ===
    vol = df['volume']
    ret = df['close'].pct_change().fillna(0)

    pvi = pd.Series(1000.0, index=df.index)
    nvi = pd.Series(1000.0, index=df.index)
    for i in range(1, len(df)):
        if vol.iloc[i] > vol.iloc[i - 1]:
            pvi.iloc[i] = pvi.iloc[i - 1] + ret.iloc[i] * pvi.iloc[i - 1]
            nvi.iloc[i] = nvi.iloc[i - 1]
        else:
            nvi.iloc[i] = nvi.iloc[i - 1] + ret.iloc[i] * nvi.iloc[i - 1]
            pvi.iloc[i] = pvi.iloc[i - 1]

    # suavizados
    pvim = pvi.ewm(span=m, adjust=False).mean()
    nvim = nvi.ewm(span=m, adjust=False).mean()

    pvimax = pvim.rolling(longitudPVI).max()
    pvimin = pvim.rolling(longitudPVI).min()
    oscp = (pvi - pvim) * 100 / (pvimax - pvimin)

    nvimax = nvim.rolling(longitudNVI).max()
    nvimin = nvim.rolling(longitudNVI).min()
    azul = (nvi - nvim) * 100 / (nvimax - nvimin)

    # === MFI ===
    tp = (df['high'] + df['low'] + df['close']) / 3.0
    rmf = tp * df['volume']
    pos_mf = rmf.where(tp > tp.shift(1), 0)
    neg_mf = rmf.where(tp < tp.shift(1), 0)
    pos_sum = pos_mf.rolling(longitudMFI).sum()
    neg_sum = neg_mf.rolling(longitudMFI).sum().replace(0, np.nan)
    mfi = 100 * (pos_sum / (pos_sum + neg_sum))

    # === Bollinger Oscillator ===
    basisK = tprice.rolling(boLength).mean()
    devK = tprice.rolling(boLength).std() * 2
    upperK = basisK + devK
    lowerK = basisK - devK
    OB1 = (upperK + lowerK) / 2.0
    OB2 = upperK - lowerK
    BollOsc = (tprice - OB1) / OB2 * 100

    # === RSI ===
    delta = tprice.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # === Stochastic ===
    low_min = df['low'].rolling(21).min()
    high_max = df['high'].rolling(21).max()
    stoc = 100 * (tprice - low_min) / (high_max - low_min)
    stoc = stoc.rolling(3).mean()

    marron = (rsi + mfi + BollOsc + stoc / 3) / 2
    verde = marron + oscp
    media = marron.ewm(span=m, adjust=False).mean()

    # === Señales ===
    buy_ck = (marron.shift(1) <= media.shift(1)) & (marron > media)
    sell_ck = (marron.shift(1) >= media.shift(1)) & (marron < media)

    return pd.DataFrame({
        'marron': marron,
        'media': media,
        'verde': verde,
        'azul': azul,
        'buy_ck': buy_ck,
        'sell_ck': sell_ck
    }, index=df.index)

# ==============================
# 📌 Conker Diamond (simplificado)
# ==============================
def generate_conker_signal(df: pd.DataFrame):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if last["close"] > last["open"] and last["close"] > prev["close"]:
        return "buy"
    elif last["close"] < last["open"] and last["close"] < prev["close"]:
        return "sell"
    return None

# ==============================
# Interfaz Streamlit
# ==============================
st.title("💎 Estrategia Conker + Koncorde")

symbol = st.text_input("Par de trading", "BTCUSDT")
interval = st.selectbox("Intervalo", ["5m", "15m", "1h", "4h"])
start_date = st.date_input("Fecha inicio", datetime.date(2025, 9, 20))
end_date = st.date_input("Fecha fin", datetime.date(2025, 9, 29))

if st.button("📥 Descargar y ejecutar"):
    start_dt = datetime.datetime.combine(start_date, datetime.time(0, 0))
    end_dt = datetime.datetime.combine(end_date, datetime.time(23, 59))
    start_str = start_dt.strftime("%d %b %Y %H:%M:%S")
    end_str = end_dt.strftime("%d %b %Y %H:%M:%S")

    # Descargar velas
    klines = client.get_historical_klines(symbol, interval, start_str, end_str)
    df = pd.DataFrame(klines, columns=[
        "timestamp","open","high","low","close","volume",
        "close_time","quote_asset_volume","trades",
        "taker_buy_base","taker_buy_quote","ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open","high","low","close","volume"]].astype(float)

    st.subheader("📊 Velas descargadas")
    st.dataframe(df.tail(10))

    # Calcular señales Koncorde
    kon = calc_koncorde(df)

    # Señal Conker
    conker_signal = generate_conker_signal(df)

    st.subheader("✅ Señales Detectadas")
    if conker_signal == "buy" and kon['buy_ck'].iloc[-1]:
        st.write("🚀 **BUY confirmado (Conker + Koncorde)**")
    elif conker_signal == "sell" and kon['sell_ck'].iloc[-1]:
        st.write("🔻 **SELL confirmado (Conker + Koncorde)**")
    else:
        st.write("⏳ No hay confirmación")

    st.subheader("📈 Últimos cálculos Koncorde")
    st.dataframe(kon.tail(10))

