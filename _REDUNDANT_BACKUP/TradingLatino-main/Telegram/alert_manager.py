import time

class AlertManager:
    def __init__(self, enabled=True, cooldown_seconds=900):
        self.enabled = enabled
        self.cooldown = cooldown_seconds
        self.last_alerts = {}

    def can_send(self, symbol, timeframe, signal):
        if not self.enabled:
            return True   # si está deshabilitado el filtro, permitimos
        key = (symbol, timeframe)
        now = time.time()
        if key in self.last_alerts:
            last_signal, last_time = self.last_alerts[key]
            if last_signal == signal and (now - last_time) < self.cooldown:
                return False
        self.last_alerts[key] = (signal, now)
        return True

    def send_alert(self, symbol, timeframe, signal, send_func):
        if self.can_send(symbol, timeframe, signal):
            send_func(symbol, timeframe, signal)
            return True
        return False


# ===============================
# Gestores específicos
# ===============================

# Scalping: cada 5 minutos (300s) — ajustalo si querés
alert_manager_scalping = AlertManager(enabled=True, cooldown_seconds=300)

# Swing trading: cada 1 hora (3600s)
alert_manager_swing = AlertManager(enabled=True, cooldown_seconds=3600)

# Intradía: placeholder 30 minutos (1800s)
alert_manager_intradia = AlertManager(enabled=True, cooldown_seconds=1800)
