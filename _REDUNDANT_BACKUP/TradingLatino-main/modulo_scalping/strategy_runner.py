# ==========================================================
# 📌 strategy_runner.py
# Motor central de señales para scalping
# ==========================================================
#
# Este archivo actúa como un *dispatcher* que elige qué
# estrategia correr (simple, OB+HTF, Sommi, Conker, etc.)
# según el modo que le pases.
#
# Cada bloque está pensado para ser independiente y 
# fácil de modificar.
# ==========================================================

import pandas as pd

# 🧩 Importación de módulos (cada uno es un "bloque" de estrategia)
from modulo_scalping.nadaraya_strategy import nadaraya_signal
from modulo_scalping.nadaraya_ob_htf import NadarayaOBHTF
from modulo_scalping.sommi_module import generate_signal_from_df
from modulo_scalping.scalping_bridge import dynamic_params
from modulo_scalping.conker_module import generate_conker_signal


# ==========================================================
# 🚀 Función principal -> run_nadaraya
# ==========================================================
def run_nadaraya(df: pd.DataFrame, modo: str = "ob_htf"):
    """
    Ejecuta la estrategia seleccionada y devuelve:
      - signal: la señal generada (ej: 'buy', 'sell', None)
      - debug: info adicional para entender qué pasó
    """

    # --- 📌 1. Estrategia Simple (Nadaraya clásico) ---
    if modo == "simple":
        try:
            sig = nadaraya_signal(df)
            return {
                "signal": sig,
                "debug": {"source": "nadaraya_strategy", "raw": sig}
            }
        except Exception as e:
            return {"signal": None, "debug": {"error": str(e)}}

    # --- 📌 2. Estrategia con OB + HTF ---
    elif modo == "ob_htf":
        try:
            strategy = NadarayaOBHTF(**dynamic_params)
            sig = strategy.generate_signal(df)
            return (
                sig if isinstance(sig, dict)
                else {"signal": sig, "debug": {"source": "nadaraya_ob_htf", "raw": sig}}
            )
        except Exception as e:
            return {"signal": None, "debug": {"error": str(e)}}

    # --- 📌 3. Estrategia Sommi (👽 Whale/Diamond) ---
    elif modo == "sommi":
        try:
            res = generate_signal_from_df(df)
            return {
                "signal": res.get("signal"),
                "debug": res.get("debug", {})
            }
        except Exception as e:
            return {"signal": None, "debug": {"error": str(e)}}

    # --- 📌 4. Estrategia Conker Diamond (💎) ---
    elif modo == "conker":
        try:
            res = generate_conker_signal(df)
            return {
                "signal": res.get("signal"),
                "debug": res.get("debug", {})
            }
        except Exception as e:
            return {"signal": None, "debug": {"error": str(e)}}

    # --- ❌ Caso: modo desconocido ---
    else:
        return {
            "signal": None,
            "debug": {"error": f"Modo desconocido: {modo}"}
        }


# ==========================================================
# 🧪 Ejecución directa (solo si se corre como script)
# ==========================================================
if __name__ == "__main__":
    df = pd.read_csv("datos.csv")   # <- dataset de prueba
    modo = "sommi"                  # <- elegir modo aquí
    print(f"📊 Señal ({modo}):", run_nadaraya(df, modo=modo))

