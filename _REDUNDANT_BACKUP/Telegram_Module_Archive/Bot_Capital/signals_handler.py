from Telegram.alert_manager import AlertManager
from Telegram.telegram_helper import send_telegram_message
from datetime import datetime

# Instancia global de AlertManager
alert_manager = AlertManager(enabled=True, cooldown_seconds=1200)  # 20 minutos de cooldown

def handle_signal(
    symbol: str,
    timeframe: str,
    signal: str,
    price: float = None,
    stop: float = None,
    target: float = None,
    strength: float = None,
    balance: str = None
):
    """
    Recibe señales de cualquier módulo (Scalping, Intradía, Swing)
    y envía a Telegram solo si no es un duplicado reciente.
    """
    # Comprobamos con AlertManager si podemos enviar la alerta
    alert_sent = alert_manager.send_alert(symbol, timeframe, signal,
                                         lambda s, tf, sig: send_alert(s, tf, sig, price, stop, target, strength, balance))
    if alert_sent:
        print(f"✅ Alerta enviada: {symbol} {signal} ({timeframe})")
    else:
        print(f"⏳ Alerta filtrada por cooldown: {symbol} {signal} ({timeframe})")

def send_alert(
    symbol: str,
    timeframe: str,
    signal: str,
    price: float = None,
    stop: float = None,
    target: float = None,
    strength: float = None,
    balance: str = None
):
    """
    Función de envío a Telegram, usada por AlertManager.
    Genera mensaje completo con todos los datos relevantes.
    """
    emoji = "🟢" if signal.upper() == "LONG" else "🔴"
    text_lines = [f"{emoji} [{signal.upper()}] {symbol} ({timeframe})"]

    if strength is not None:
        text_lines.append(f"📊 Fuerza señal: {strength}%")
    if price is not None:
        text_lines.append(f"💰 Precio entrada: {price}")
    if stop is not None:
        text_lines.append(f"🛑 Stop: {stop}")
    if target is not None:
        text_lines.append(f"🎯 Target: {target}")
    if balance is not None:
        text_lines.append(f"💼 Balance actual: {balance}")

    text_lines.append(f"⏱️ Tiempo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    text = "\n".join(text_lines)
    send_telegram_message(text)
