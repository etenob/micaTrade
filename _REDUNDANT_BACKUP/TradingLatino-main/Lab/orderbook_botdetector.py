# ============================================================
# /Lab - Detector de Bots de Mercado
# ------------------------------------------------------------
# Objetivo:
#   Monitorear en tiempo real el orderbook y flujo de trades
#   para detectar huellas típicas de bots:
#       - Imbalance (desequilibrio entre bids y asks)
#       - Spread manipulado (top_bid vs top_ask)
#       - Taker imbalance (flujo de compras vs ventas)
#
# Uso:
#   - Requiere: pip install ccxt pandas numpy
#   - Ejecutar directamente para guardar un CSV con features
#   - Más adelante: acoplar a Next.js para monitoreo visual
#
# Filosofía Daredevil:
#   No se trata de pelear contra los bots,
#   sino de "cabalgar" sus huellas para usarlas a favor 😎
# ============================================================

import ccxt
import time
import numpy as np
import pandas as pd
from datetime import datetime

# --- Configuración ---
EXCHANGE = ccxt.binance()         # Podés cambiar por Bybit, BingX, etc.
SYMBOL = 'BTC/USDT'               # Par a monitorear
DEPTH_LEVELS = 10                 # Profundidad de orderbook
WINDOW_SEC = 30                   # Intervalo entre capturas (segundos)


def get_orderbook():
    """Descarga el orderbook en vivo"""
    ob = EXCHANGE.fetch_order_book(SYMBOL, depth=DEPTH_LEVELS)
    bids = np.array(ob['bids'])[:DEPTH_LEVELS]  # [[price, qty], ...]
    asks = np.array(ob['asks'])[:DEPTH_LEVELS]
    return bids, asks


def orderbook_features(bids, asks):
    """Extrae métricas clave para detectar actividad de bots"""
    bid_vol = bids[:, 1].astype(float).sum()
    ask_vol = asks[:, 1].astype(float).sum()
    imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol + 1e-9)

    top_bid = float(bids[0, 0])
    top_ask = float(asks[0, 0])
    spread = (top_ask - top_bid) / top_bid

    return {
        'imbalance': imbalance,   # >0 → más compras acumuladas
        'bid_vol': bid_vol,
        'ask_vol': ask_vol,
        'spread': spread,         # spread relativo
        'top_bid': top_bid,
        'top_ask': top_ask
    }


def sample_loop(iterations=10):
    """Bucle principal de monitoreo"""
    rows = []
    for i in range(iterations):
        try:
            # 1️⃣ Orderbook
            bids, asks = get_orderbook()
            f = orderbook_features(bids, asks)

            # 2️⃣ Timestamp
            f['timestamp'] = datetime.utcnow().isoformat()

            # 3️⃣ Flujo de trades recientes (proxy de bots taker)
            trades = EXCHANGE.fetch_trades(SYMBOL, limit=100)
            buys = sum(t['amount'] for t in trades if t['side'] == 'buy')
            sells = sum(t['amount'] for t in trades if t['side'] == 'sell')
            f['taker_imbalance'] = (buys - sells) / (buys + sells + 1e-9)

            rows.append(f)

            # Feedback en consola
            print(f"[{f['timestamp']}] "
                  f"imbalance={f['imbalance']:.2f} | "
                  f"taker_imb={f['taker_imbalance']:.2f} | "
                  f"spread={f['spread']:.5f}")

        except Exception as e:
            print("⚠️ Error capturando datos:", e)

        time.sleep(WINDOW_SEC)

    # 4️⃣ Guardar resultados
    df = pd.DataFrame(rows)
    df.to_csv('botdetector_features.csv', index=False)
    print("✅ Features guardadas en botdetector_features.csv")


if __name__ == '__main__':
    # Por defecto: 20 iteraciones (~10 min si WINDOW_SEC=30)
    sample_loop(iterations=20)

