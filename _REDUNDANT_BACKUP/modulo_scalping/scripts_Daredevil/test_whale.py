import pandas as pd
import yfinance as yf
from whale.whale_signals import detect_whale_signals

def main():
    # Descargar datos de ejemplo
    df = yf.download("BTC-USD", period="3mo", interval="1h")

    # Mostrar columnas originales
    print("📥 Columnas originales:", df.columns)

    # Normalizar columnas
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0].lower() for col in df.columns]
    else:
        df.rename(columns=lambda x: x.lower(), inplace=True)

    print("📊 Columnas normalizadas:", df.columns)

    # Detectar señales
    df_signals, whale_signals = detect_whale_signals(df)

    # Mostrar señales detectadas (el objeto whale_signals)
    print("\n🔍 Señales detectadas (whale_signals):")
    print(whale_signals.tail(10))

    # Si la función devuelve df con columnas agregadas, mostramos solo las nuevas
    if isinstance(df_signals, pd.DataFrame):
        extra_cols = [col for col in df_signals.columns if col not in df.columns]
        print("\n🧠 Últimas señales Whale en df_signals:")
        print(df_signals[extra_cols].tail(10))

if __name__ == "__main__":
    main()
