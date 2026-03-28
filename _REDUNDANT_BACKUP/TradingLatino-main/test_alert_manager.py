# test_alert_manager.py
import time
from Telegram.alert_manager import alert_manager_scalping

def fake_send(symbol, timeframe, signal):
    print(f"📨 Enviada a Telegram: {symbol} {timeframe} {signal}")

def main():
    symbol = "BTCUSDT"
    timeframe = "5m"
    signal = "LONG"

    print("=== Test AlertManager Scalping ===")
    print(f"Cooldown configurado: {alert_manager_scalping.cooldown} segundos\n")

    # Primer intento -> debería enviarse
    print("🔔 Intento 1")
    sent = alert_manager_scalping.send_alert(symbol, timeframe, signal, fake_send)
    print("Resultado:", sent)
    print()

    # Segundo intento inmediato -> debería bloquearse
    print("🔔 Intento 2 (inmediato)")
    sent = alert_manager_scalping.send_alert(symbol, timeframe, signal, fake_send)
    print("Resultado:", sent)
    print()

    # Esperamos 6 segundos (para test rápido, podés cambiar a 300)
    print("⏳ Esperando 6 segundos...")
    time.sleep(6)

    # Tercer intento -> debería enviarse de nuevo porque pasó el cooldown (si lo seteaste en 5s para test)
    print("🔔 Intento 3 (tras cooldown)")
    sent = alert_manager_scalping.send_alert(symbol, timeframe, signal, fake_send)
    print("Resultado:", sent)

if __name__ == "__main__":
    main()

