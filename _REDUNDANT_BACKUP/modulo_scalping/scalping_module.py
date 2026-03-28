# modulo_scalping/scalping_module.py
"""
Módulo minimalista para Scalping
--------------------------------
✅ Devuelve velas rectificadas y listas para bridge.
✅ Soporta un solo timeframe o múltiples timeframes.
❌ No ejecuta estrategias ni envía mensajes.
"""

import pandas as pd
from services.binance_service import binance_service

# ==========================================================
# 1️⃣ Velas de un solo timeframe (limpias para bridge)
# ==========================================================
def get_candles_df(symbol: str, interval: str = "5m", limit: int = 150) -> pd.DataFrame:
    candles = binance_service.get_klines(symbol=symbol, interval=interval, limit=limit)
    if not candles:
        return pd.DataFrame(columns=["time", "open", "high", "low", "close", "volume"])

    df = pd.DataFrame(candles, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        *["x"+str(i) for i in range(len(candles[0])-6)]
    ])
    # Convertir columnas a float
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    # Timestamp en segundos UNIX
    df["time"] = (pd.to_datetime(df["timestamp"], unit="ms").astype("int64") // 10**9).astype(int)
    return df[["time", "open", "high", "low", "close", "volume"]]

# ==========================================================
# 2️⃣ Velas de múltiples timeframes listas para bridge
# ==========================================================
def get_multi_candles(symbol: str, configs: dict = None, limit: int = 150) -> dict:
    """
    Devuelve un dict { alias: DataFrame } listo para bridge.
    Ej: configs = { "entry": "5m", "context": "1h" }
    """
    if configs is None:
        configs = {"entry": "5m", "context": "1h"}

    candles_dict = {}
    for alias, tf in configs.items():
        candles_dict[alias] = get_candles_df(symbol, interval=tf, limit=limit)
    return candles_dict

# ==========================================================
# 3️⃣ Paquete directo para bridge
# ==========================================================
def prepare_for_bridge(symbol: str, configs: dict = None, limit: int = 150) -> dict:
    """
    Devuelve un paquete limpio para enviar a run_nadaraya o generate_conker_signal.
    {
        "symbol": str,
        "candles": { alias: DataFrame },
        "timestamp": int
    }
    """
    now = int(pd.Timestamp.now().timestamp())
    candles = get_multi_candles(symbol, configs=configs, limit=limit)
    return {"symbol": symbol, "candles": candles, "timestamp": now}

# ==========================================================
# 4️⃣ Ejemplo local
# ==========================================================
if __name__ == "__main__":
    package = prepare_for_bridge("ETHUSDT", {"entry": "5m", "context": "1h"}, 10)
    print("Paquete listo para bridge:\n", package)

