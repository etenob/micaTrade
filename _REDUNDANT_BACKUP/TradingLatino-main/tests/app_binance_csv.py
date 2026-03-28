# app_binance_csv.py
import streamlit as st
import pandas as pd
from binance.client import Client
import datetime

# --- Configuración Binance ---
API_KEY = "TU_API_KEY"
API_SECRET = "TU_API_SECRET"
client = Client(API_KEY, API_SECRET)

# --- UI ---
st.title("📊 Descarga de Velas Históricas - Binance")

# Inputs
symbol = st.text_input("Par de trading (ej: BTCUSDT)", "BTCUSDT")
interval = st.selectbox("Intervalo", ["5m", "15m", "1h", "4h", "1d"])

# Fecha y hora de inicio/fin (UTC)
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Fecha inicio", datetime.date(2025, 9, 28))
    start_hour = st.number_input("Hora inicio (UTC)", 0, 23, 8)
with col2:
    end_date = st.date_input("Fecha fin", datetime.date(2025, 9, 28))
    end_hour = st.number_input("Hora fin (UTC)", 0, 23, 11)

if st.button("📥 Descargar CSV"):
    # Construir datetime
    start_dt = datetime.datetime.combine(start_date, datetime.time(start_hour, 0))
    end_dt = datetime.datetime.combine(end_date, datetime.time(end_hour, 0))

    # Convertir a formato Binance
    start_str = start_dt.strftime("%d %b %Y %H:%M:%S")
    end_str = end_dt.strftime("%d %b %Y %H:%M:%S")

    # Descargar velas
    klines = client.get_historical_klines(symbol, interval, start_str, end_str)

    # Convertir a DataFrame
    df = pd.DataFrame(klines, columns=[
        "timestamp","open","high","low","close","volume",
        "close_time","quote_asset_volume","trades",
        "taker_buy_base","taker_buy_quote","ignore"
    ])

    # Ajustar tipos y timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open","high","low","close","volume"]].astype(float)

    # Guardar CSV
    csv_name = f"{symbol}_{interval}_{start_dt.strftime('%Y%m%d_%H%M')}_{end_dt.strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(csv_name)

    st.success(f"✅ Archivo generado: {csv_name}")
    st.dataframe(df.head(10))
    st.dataframe(df.tail(10))

