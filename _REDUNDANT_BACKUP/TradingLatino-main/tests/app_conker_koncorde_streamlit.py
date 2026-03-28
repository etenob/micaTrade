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
# 📌 Backtest Conker + Koncorde
# ==============================
def backtest_signals(df, kon):
    trades = []
    position = None
    entry_price = None
    entry_time = None

    for i in range(1, len(df)):
        conker_sig = generate_conker_signal(df.iloc[:i+1])
        k_buy = kon['buy_ck'].iloc[i]
        k_sell = kon['sell_ck'].iloc[i]

        # 🚀 Entrada
        if position is None:
            if conker_sig == "buy" and k_buy:
                position = "long"
                entry_price = df['close'].iloc[i]
                entry_time = df.index[i]
                trades.append({"time": entry_time, "signal": "BUY", "price": entry_price})
            elif conker_sig == "sell" and k_sell:
                position = "short"
                entry_price = df['close'].iloc[i]
                entry_time = df.index[i]
                trades.append({"time": entry_time, "signal": "SELL", "price": entry_price})

        # ❌ Salida
        else:
            if position == "long" and conker_sig == "sell" and k_sell:
                exit_price = df['close'].iloc[i]
                profit = (exit_price - entry_price) / entry_price * 100
                trades.append({
                    "time": df.index[i], "signal": "CLOSE_LONG",
                    "price": exit_price, "profit%": round(profit, 2)
                })
                position = None

            elif position == "short" and conker_sig == "buy" and k_buy:
                exit_price = df['close'].iloc[i]
                profit = (entry_price - exit_price) / entry_price * 100
                trades.append({
                    "time": df.index[i], "signal": "CLOSE_SHORT",
                    "price": exit_price, "profit%": round(profit, 2)
                })
                position = None

    return pd.DataFrame(trades)

# ==============================
# 📌 Métricas
# ==============================
def calculate_metrics(trade_log: pd.DataFrame):
    closed_trades = trade_log[trade_log['signal'].str.contains("CLOSE")]
    total_trades = len(closed_trades)
    if total_trades == 0:
        return {"total": 0, "wins": 0, "losses": 0, "winrate": 0, "avg_profit": 0}

    wins = (closed_trades["profit%"] > 0).sum()
    losses = (closed_trades["profit%"] <= 0).sum()
    winrate = round((wins / total_trades) * 100, 2)
    avg_profit = round(closed_trades["profit%"].mean(), 2)

    return {"total": total_trades, "wins": wins, "losses": losses, "winrate": winrate, "avg_profit": avg_profit}

# ==============================
# 📌 Interfaz Streamlit
# ==============================
st.title("💎 Estrategia Conker + Koncorde (Backtest)")

symbol = st.text_input("Par de trading", "BTCUSDT")
interval = st.selectbox("Intervalo", ["5m", "15m", "1h", "4h", "1d"])
start_date = st.date_input("Fecha inicio", datetime.date(2025, 9, 20))
end_date = st.date_input("Fecha fin", datetime.date(2025, 10, 4))

if st.button("📥 Descargar y ejecutar backtest"):
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

    st.subheader(f"📊 Velas descargadas (Total: {len(df)})")
    st.dataframe(df.head(10))

    # Señales
    kon = calc_koncorde(df)
    trade_log = backtest_signals(df, kon)

    # Historial
    st.subheader("📒 Historial de operaciones")
    st.dataframe(trade_log)

    # Métricas
    metrics = calculate_metrics(trade_log)
    st.subheader("📌 Tablero de Resultados")
    st.markdown(f"""
    - Total operaciones: **{metrics['total']}**
    - Ganadoras: **{metrics['wins']}**
    - Perdedoras: **{metrics['losses']}**
    - Winrate: **{metrics['winrate']}%**
    - Profit promedio: **{metrics['avg_profit']}%**
    """)

