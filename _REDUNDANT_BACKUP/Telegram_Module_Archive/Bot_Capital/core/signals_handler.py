# Telegram/Bot_Capital/signals_handler.py
from Telegram.alert_manager import AlertManager
from Telegram.telegram_helper import send_telegram_message

alert_manager = AlertManager(cooldown_seconds=1200)

def handle_signal(bot_type, symbol, timeframe, signal, price, stop=None, target=None):
    """
    Recibe señales de los bots hijos y las envía a Telegram si corresponde
    """
    message = f"⚡ {bot_type.upper()} | {symbol} {timeframe} | {signal} @ {price}"
    if stop and target:
        message += f" | Stop: {stop} | Target: {target}"

    # Enviar solo si AlertManager lo permite
    alert_manager.send_alert(symbol, timeframe, signal, lambda s, t, sig: send_telegram_message(message))

