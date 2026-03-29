import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

class Config:
    """Configuración central para el bot de Merino"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jaime_merino_trading_2026')
    
    # Credenciales de Binance
    BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.environ.get('BINANCE_SECRET_KEY', '')

    # Configuración de Telegram
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
    
    # Configuración de Trading y Riesgo (V2 MODO PAPEL)
    IS_LIVE_TRADING = False  # True: Operar real | False: Solo monitoreo
    TRADING_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'LINKUSDT', 
        'AVAXUSDT', 'ATOMUSDT', 'DOTUSDT', 'ADAUSDT', 'XRPUSDT', 
        'DOGEUSDT', 'MATICUSDT', 'LTCUSDT', 'NEARUSDT', 'FTMUSDT', 
        'INJUSDT', 'FETUSDT', 'RENDERUSDT', 'ARUSDT', 'OPUSDT',
        'SEIUSDT', 'TIAUSDT', 'SUIUSDT', 'APTUSDT', 'FILUSDT',
        'ICPUSDT', 'STXUSDT', 'PEPEUSDT', 'SHIBUSDT', 'UNIUSDT',
        'LDOUSDT', 'AAVEUSDT', 'MKRUSDT', 'SNXUSDT', 'GRTUSDT',
        'THETAUSDT', 'IMXUSDT', 'ROSEUSDT', 'ALGOUSDT', 'HBARUSDT'
    ]
    DEFAULT_LEVERAGE = 2
    
    # 🕵️ LÍMITES DE CAPITAL (Fase 4.1)
    BASE_CAPITAL = 99.0         # Capital inicial para cálculos de rendimiento
    MAX_USDT_ORDER = 6.0       # Monto por cada compra individual
    MAX_USDT_TOTAL_EXPOSURE = 100.0  # Monto máximo total en trades abiertos
    
    # 🧠 CONFIGURACIÓN DE ESTRATEGIAS
    STRATEGY_CONFIG = {
        'ALIEN_90':       {'order_amount': 11.0, 'sl_pct': 0.10, 'tp_pct': 0.05, 'active': True},
        'TENDENCIA_CIEGA':{'order_amount': 11.0, 'sl_pct': 0.08, 'tp_pct': 0.05, 'active': True},
        'REBOTE_SUELO':   {'order_amount': 11.0, 'sl_pct': 0.03, 'tp_pct': 0.02, 'active': True},
        'GATILLO_11':     {'order_amount': 11.0, 'sl_pct': 0.05, 'tp_pct': 0.02, 'active': True},
        'BLOCK_PINGPONG': {'order_amount': 11.0, 'sl_pct': 0.04, 'tp_pct': 0.02, 'active': True},
        # 👹 MONSTRUOS FASE 3 (Apagados por defecto para pruebas visuales en UI)
        'SWEEP_HUNTER':   {'order_amount': 11.0, 'sl_pct': 0.03, 'tp_pct': 0.08, 'active': True},
        'HA_FANTASMA':    {'order_amount': 11.0, 'sl_pct': 0.05, 'tp_pct': 0.15, 'active': True},
        'DIVERGENCIA_3D': {'order_amount': 11.0, 'sl_pct': 0.04, 'tp_pct': 0.06, 'active': True}
    }
    
    # Intervalos
    UPDATE_SECONDS = 30
    TELEGRAM_COOLDOWN = 600  # 10 minutos entre alertas del mismo par
