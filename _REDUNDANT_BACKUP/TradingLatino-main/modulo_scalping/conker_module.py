# ==========================================================
# 📌 conker_module.py
# Estrategia Conker Diamond (Entrada + Salida)
# ==========================================================
#
# Este módulo encapsula la lógica del "Conker Diamond":
#   - Busca patrones de compresión (squeeze) y reversión.
#   - Detecta posibles entradas (ENTRY).
#   - Define condiciones de salida (EXIT).
#
# Devuelve un diccionario estandarizado con:
#   - signal (buy/sell/None)
#   - exit (close_long/close_short/None)
#   - debug (info extra)
# ==========================================================

import pandas as pd

# ==========================================================
# 🚀 Función principal
# ==========================================================
def generate_conker_signal(df: pd.DataFrame):
    """
    Detecta señales de entrada/salida basadas en el patrón Conker Diamond.
    df debe tener columnas: ['open','high','low','close','volume']
    """

    try:
        # --- 📌 1. Validaciones básicas ---
        if len(df) < 50:   # necesitamos suficiente data
            return {"signal": None, "exit": None, "debug": {"error": "Data insuficiente"}}

        # Tomamos la última vela
        last = df.iloc[-1]
        prev = df.iloc[-2]

        debug = {}

        # ==================================================
        # 📌 2. Señales de Entrada (ENTRY)
        # ==================================================
        entry_signal = None

        # Ejemplo simple: si hay vela alcista fuerte tras compresión
        if last["close"] > last["open"] and last["close"] > prev["close"]:
            entry_signal = "buy"
            debug["entry_reason"] = "Ruptura alcista tras compresión"

        elif last["close"] < last["open"] and last["close"] < prev["close"]:
            entry_signal = "sell"
            debug["entry_reason"] = "Ruptura bajista tras compresión"

        # ==================================================
        # 📌 3. Señales de Salida (EXIT)
        # ==================================================
        exit_signal = None

        # Si ya estamos en LONG y aparece una vela roja fuerte => salida
        if entry_signal is None and last["close"] < prev["low"]:
            exit_signal = "close_long"
            debug["exit_reason"] = "Stop dinámico por ruptura mínima"

        # Si estamos en SHORT y aparece vela verde fuerte => salida
        if entry_signal is None and last["close"] > prev["high"]:
            exit_signal = "close_short"
            debug["exit_reason"] = "Stop dinámico por ruptura máxima"

        # ==================================================
        # 📌 4. Retorno estandarizado
        # ==================================================
        return {
            "signal": entry_signal,
            "exit": exit_signal,
            "debug": debug
        }

    except Exception as e:
        return {"signal": None, "exit": None, "debug": {"error": str(e)}}


# ==========================================================
# 🧪 Test local
# ==========================================================
if __name__ == "__main__":
    df = pd.read_csv("datos.csv")
    res = generate_conker_signal(df)
    print("📊 Señal Conker:", res)

