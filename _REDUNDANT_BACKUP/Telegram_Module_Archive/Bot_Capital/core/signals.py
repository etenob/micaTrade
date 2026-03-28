# Telegram/Bot_Capital/core/signals.py
def get_recent_signals():
    """
    Devuelve un ejemplo de señales recientes de todos los bots.
    """
    return [
        {"bot": "Scalping", "symbol": "BTC/USDT", "timeframe": "15m", "signal": "LONG", "price": 58200},
        {"bot": "Intradia", "symbol": "ETH/USDT", "timeframe": "1h", "signal": "SHORT", "price": 1940},
        {"bot": "Swing", "symbol": "BTC/USDT", "timeframe": "1D", "signal": "LONG", "price": 58500}
    ]
