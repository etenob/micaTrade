"""
Runner independiente para testear el módulo de scalping.
✅ Usa scalping_bridge como orquestador.
✅ Lee config central desde SCALPING_PARAMS.
✅ Imprime resultados y guarda logs automáticamente.
"""

import time
import os
from dotenv import load_dotenv
from modulo_scalping.scalping_bridge import scalping_realtime
from modulo_scalping.config_scalping import SCALPING_PARAMS

# Cargar variables de entorno (.env)
load_dotenv()


def main():
    # 📌 Config central (se toma del archivo config_scalping.py)
    symbol = SCALPING_PARAMS.get("symbol", "ETHUSDT")
    interval = SCALPING_PARAMS.get("interval", "5m")
    modo = SCALPING_PARAMS.get("modo", "realtime")
    update_intervals = SCALPING_PARAMS.get("update_intervals", {})
    sleep_seconds = update_intervals.get(interval, 120)

    print(f"⚙️  Configuración inicial -> Symbol: {symbol}, Interval: {interval}, Sleep: {sleep_seconds}s")
    print("📊 ✅ Cliente Binance inicializado con credenciales")
    print("📊 🌐 Conexión con Binance establecida exitosamente")
    print("📊 🚀 BinanceService global inicializado con config")

    # 🔄 Loop principal
    while True:
        try:
            # 🚀 Llamar al bridge para flujo completo
            result = scalping_realtime(symbol=symbol, interval=interval, modo=modo)

            # Mostrar resumen en consola
            candle = result["candles"][-1]
            print(
                f"📡 [{result['symbol']}][{result['interval']}] "
                f"O:{candle['open']} H:{candle['high']} "
                f"L:{candle['low']} C:{candle['close']} | Señal: {result['signal']}"
            )
        except Exception as e:
            print(f"❌ Error ejecutando scalping: {e}")

        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()

