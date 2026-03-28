import yfinance as yf
import pandas as pd
from whale_lpwn import detect_whale_signals

def main():
    # Descargar datos BTC-USD 1 hora últimos 30 días
    ticker = yf.Ticker("BTC-USD")
    df = ticker.history(period="30d", interval="1h")

    # df tiene columnas: Open, High, Low, Close, Volume (notar mayúsculas)
    # Para nuestro módulo necesitamos columnas minúsculas
    df = df.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })

    # Detectar señales Whale 👽 y 👹
    df = detect_whale_signals(df)

    # Mostrar últimas filas con señales
    print(df[['wt1', 'wt2', 'rsi_mfi', 'whale_bull', 'whale_bear']].tail(10))

    # Filtrar y mostrar solo señales de compra
    compras = df[df['whale_bull']]
    print("\nSeñales Whale Compra encontradas:")
    print(compras[['close']])

    # Filtrar y mostrar solo señales de venta
    ventas = df[df['whale_bear']]
    print("\nSeñales Whale Venta encontradas:")
    print(ventas[['close']])

if __name__ == "__main__":
    main()
