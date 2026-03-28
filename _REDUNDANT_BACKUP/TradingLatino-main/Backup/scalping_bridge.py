# modulo_scalping/scalping_bridge.py
import time
import pandas as pd
from services.binance_service import binance_service
from modulo_scalping.heikin_confirm import HeikinConfirm
from modulo_scalping.nadaraya_wrapper import NadarayaWrapper
from modulo_scalping.nadaraya_strategy import NadarayaStrategy  # solo para señales

# 🔹 Parámetros dinámicos (modificables desde Next.js)
dynamic_params = {
    "h": 4.0,
    "r": 4.0,
    "lag": 2,
    "atr_length": 14,
    "atr_mult": 1.5,
    "rsi_length": 5,
    "ema_length": 40,          # para HeikinConfirm
    "backend": "statsmodels",  # podés cambiar a "custom" o "grnn"
    "confirm_with_heikin": False,  # 👈 flag (default = False)
}


def update_params(new_params: dict):
    """Actualizar parámetros dinámicos en caliente"""
    global dynamic_params
    for k, v in new_params.items():
        if k in dynamic_params:
            old_val = dynamic_params[k]

            # Mantener tipo original
            if isinstance(old_val, bool):
                if isinstance(v, str):
                    dynamic_params[k] = v.lower() in ("true", "1", "yes")
                else:
                    dynamic_params[k] = bool(v)
            elif isinstance(old_val, int):
                try:
                    dynamic_params[k] = int(v)
                except (ValueError, TypeError):
                    pass
            elif isinstance(old_val, float):
                try:
                    dynamic_params[k] = float(v)
                except (ValueError, TypeError):
                    pass
            else:
                dynamic_params[k] = v


def scalping_realtime(symbol: str = "ETHUSDT", interval: str = "5m", limit: int = 200):
    """
    Devuelve JSON con:
      - Velas normales
      - Curva Nadaraya
      - Heikin Ashi (si está activado)
      - Señal final
    Pensado para enviar al frontend (Next.js).
    """
    # 1️⃣ Velas desde Binance
    candles = binance_service.get_klines(symbol=symbol, interval=interval, limit=limit)

    if candles is None or len(candles) == 0:
        return {"success": False, "error": "No se pudieron obtener velas"}

    # Convertir a DataFrame
    df = pd.DataFrame(
        candles,
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df["time"] = pd.to_datetime(df["timestamp"], unit="ms").astype("int64") // 10**9
    df = df.drop(columns=["timestamp"])

    # 2️⃣ Nadaraya Wrapper (solo curva)
    try:
        wrapper = NadarayaWrapper(
            h=dynamic_params["h"],
            r=dynamic_params["r"],
            backend=dynamic_params.get("backend", "statsmodels"),
        )
        nadaraya_raw = wrapper.predict(range(len(df)), df["close"].values).tolist()
    except Exception as e:
        nadaraya_raw = []
        print(f"[DEBUG] Error en wrapper Nadaraya: {e}")

    # 3️⃣ Señal con estrategia clásica
    try:
        strategy = NadarayaStrategy(
            h=dynamic_params["h"],
            r=dynamic_params["r"],
            lag=dynamic_params["lag"],
            atr_length=dynamic_params["atr_length"],
            atr_mult=dynamic_params["atr_mult"],
            rsi_length=dynamic_params["rsi_length"],
        )
        signal_nadaraya = strategy.generate_signal(df)
    except Exception as e:
        print(f"[DEBUG] Error generando señal: {e}")
        signal_nadaraya = None

    # 4️⃣ Confirmación Heikin (si está activado)
    heikin_raw = []
    confirm_signal = None
    if dynamic_params.get("confirm_with_heikin", False):
        try:
            heikin = HeikinConfirm(ema_length=dynamic_params["ema_length"])
            ha_df = heikin.heikin_ohlc(df)
            confirm_signal = heikin.confirm_signal(df)
            heikin_raw = ha_df[["HA_Open", "HA_High", "HA_Low", "HA_Close"]].to_dict("records")
        except Exception as e:
            print(f"[DEBUG] Error en HeikinConfirm: {e}")

    # 5️⃣ Señal final
    final_signal = None
    if dynamic_params.get("confirm_with_heikin", False):
        if signal_nadaraya == "LONG" and confirm_signal == "CONFIRM_LONG":
            final_signal = "LONG"
        elif signal_nadaraya == "SHORT" and confirm_signal == "CONFIRM_SHORT":
            final_signal = "SHORT"
    else:
        final_signal = signal_nadaraya

    # 6️⃣ Velas limpias para frontend
    candles_clean = [
        {
            "time": int(row["time"]),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": float(row["volume"]),
        }
        for _, row in df.iterrows()
    ]

    # 7️⃣ Respuesta final
    return {
        "candles": candles_clean,
        "heikin_raw": heikin_raw,
        "nadaraya_raw": nadaraya_raw,
        "signal": final_signal,
        "symbol": symbol,
        "interval": interval,
        "timestamp": int(time.time()),
        "success": True,
    }
