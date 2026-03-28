# Telegram/alert_manager.py

import time

class AlertManager:
    """
    Gestor de alertas plug & play para Telegram.
    Evita duplicados y controla el intervalo entre envíos.
    Funciona con tu flujo 4h -> 1h -> 15m sin tocar nada de la lógica de señales.
    """

    def __init__(self, enabled=True, cooldown_seconds=900):
        """
        :param enabled: Activar/desactivar filtrado de alertas
        :param cooldown_seconds: Tiempo mínimo entre alertas idénticas (segundos)
        """
        self.enabled = enabled
        self.cooldown = cooldown_seconds
        self.last_alerts = {}  # clave = (symbol, timeframe), valor = (signal, timestamp)

    def can_send(self, symbol, timeframe, signal):
        """
        Retorna True si la alerta debe enviarse.
        """
        if not self.enabled:
            return False  # enviar siempre si está deshabilitado

        key = (symbol, timeframe)
        now = time.time()

        if key in self.last_alerts:
            last_signal, last_time = self.last_alerts[key]
            if last_signal == signal and (now - last_time) < self.cooldown:
                return False  # misma señal y dentro del cooldown

        self.last_alerts[key] = (signal, now)
        return True

    def send_alert(self, symbol, timeframe, signal, send_func):
        """
        Envía la alerta usando send_func si corresponde.
        :param send_func: función que envía la alerta a Telegram
        """
        if self.can_send(symbol, timeframe, signal):
            send_func(symbol, timeframe, signal)
            return True
        return False


# ===============================
# Gestores específicos
# ===============================

# Scalping: cada 5 minutos
alert_manager_scalping = AlertManager(enabled=True, cooldown_seconds=300)

# Swing trading: cada 1 hora
alert_manager_swing = AlertManager(enabled=True, cooldown_seconds=3600)

# Intradía: cada 30 minutos (placeholder)
alert_manager_intradia = AlertManager(enabled=True, cooldown_seconds=1800)

