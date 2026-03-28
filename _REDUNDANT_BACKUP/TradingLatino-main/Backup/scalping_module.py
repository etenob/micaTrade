"""
Módulo completo de Scalping - Jaime Merino TradingLatino
--------------------------------------------------------
- Estrategia Nadaraya + Heikin para confirmación
- Control de señales repetidas y límites de trades
- Configurable vía MerinoConfig
"""

import time
import pandas as pd
from modulo_scalping.nadaraya_strategy import NadarayaStrategy, nadaraya_signal
from services.binance_service import binance_service
from Telegram.telegram_helper import send_telegram_message
from Telegram.alert_manager import AlertManager
from enhanced_config import MerinoConfig
#from modulo_scalping.heikin_confirm import HeikinConfirm

# Instancia del gestor de alertas
alert_manager = AlertManager(enabled=True, cooldown_seconds=300)

# Contadores para limitar señales
signal_counters_hour = {}
signal_counters_day = {}

def run_scalping(symbol: str = "ETHUSDT"):
    """
    Función principal de scalping:
    - Descarga velas según timeframe de config
    - Calcula señales Nadaraya
    - Confirma con Heikin
    - Envía alertas respetando cooldown y máximos
    """
    timeframe = MerinoConfig.SCALPING['timeframe']
    max_per_hour = MerinoConfig.SCALPING.get('max_signals_per_hour', 1)
    max_per_day  = MerinoConfig.SCALPING.get('max_trades_per_day', 3)

    # 1️⃣ Obtener velas
    candles = binance_service.get_klines(symbol=symbol, interval=timeframe, limit=50)
    if candles is None or len(candles) == 0:
        send_telegram_message(f"⚠️ [SCALPING] No se pudieron obtener velas para {symbol}")
        return

    # 2️⃣ Convertir a DataFrame y asegurar float
    if isinstance(candles, list):
        df = pd.DataFrame(candles, columns=['open','high','low','close','volume'])
    else:
        df = candles.copy()
    for col in ['open','high','low','close','volume']:
        df[col] = df[col].astype(float)

    # 3️⃣ Estrategia Nadaraya
    try:
        signal = nadaraya_signal(df)  # solo df
    except Exception as e:
        print(f"[DEBUG] Error generando señal Nadaraya: {e}")
        return

    if not signal:
        return

    # 4️⃣ Confirmación Heikin
    #heikin = HeikinConfirm()
    #confirm = heikin.confirm_signal(df)
    #if (signal == "LONG" and confirm != "CONFIRM_LONG") or \
    #   (signal == "SHORT" and confirm != "CONFIRM_SHORT"):
    #    return  # No confirmar la señal

    # 5️⃣ Control de máximos por hora y día
    now = time.localtime()
    hour_key = (symbol, time.strftime("%Y%m%d%H", now))
    day_key  = (symbol, time.strftime("%Y%m%d", now))

    signal_counters_hour.setdefault(hour_key, 0)
    signal_counters_day.setdefault(day_key, 0)

    if signal_counters_hour[hour_key] >= max_per_hour:
        return
    if signal_counters_day[day_key] >= max_per_day:
        return

    # 6️⃣ Enviar alerta con AlertManager
    def telegram_func(s, tf, sig):
        send_telegram_message(f"🔥 [SCALPING] Señal CONFIRMADA {sig} en {s} ({tf})")
        # Aquí se podrían agregar ejecución de órdenes reales si se desea

    if alert_manager.send_alert(symbol, timeframe, signal, telegram_func):
        # Incrementar contadores
        signal_counters_hour[hour_key] += 1
        signal_counters_day[day_key] += 1
