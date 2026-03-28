# test_scalping.py
import pandas as pd
from modulo_scalping.scalping_module import run_scalping
from services.binance_service import binance_service
from modulo_scalping.nadaraya_strategy import NadarayaStrategy
from modulo_scalping.heikin_confirm import HeikinConfirm

# Mock de la función de alertas (no envía Telegram)
def mock_send_alert(symbol, timeframe, signal):
    print(f"🔥 Señal CONFIRMADA {signal} en {symbol} ({timeframe})")

def test_run(symbol="ETHUSDT", timeframe="5m"):
    # 1️⃣ Traer velas de Binance
    candles = binance_service.get_klines(symbol=symbol, interval=timeframe, limit=50)
    if candles is None or len(candles) == 0:
        print(f"⚠️ No se pudieron obtener velas para {symbol}")
        return

    if isinstance(candles, list):
        df = pd.DataFrame(candles, columns=['open','high','low','close','volume'])
    else:
        df = candles

    # 2️⃣ Generar señal Nadaraya
    strategy = NadarayaStrategy()
    signal = strategy.generate_signal(df)
    if not signal:
        print("❌ No hay señal Nadaraya")
        return

    # 3️⃣ Confirmación Heikin
    heikin = HeikinConfirm()
    confirm = heikin.confirm_signal(df)
    if (signal == "LONG" and confirm != "CONFIRM_LONG") or \
       (signal == "SHORT" and confirm != "CONFIRM_SHORT"):
        print("❌ Señal NO confirmada por Heikin")
        return

    # 4️⃣ Mostrar señal confirmada
    mock_send_alert(symbol, timeframe, signal)

if __name__ == "__main__":
    test_run()

