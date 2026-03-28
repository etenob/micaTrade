"""
Configuración de la aplicación de trading
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jaime_merino_trading_2025'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Configuración del servidor
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Configuración de Binance
    BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.environ.get('BINANCE_SECRET_KEY', '')

    # Configuración de Telegram
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
    
    # Símbolos a monitorear
    TRADING_SYMBOLS = [
        'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT',
        'SOLUSDT', 'XRPUSDT', 'DOTUSDT', 'LINKUSDT'
    ]
    
    # Configuración del análisis
    UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', 60))  # segundos
    EMA_PERIODS = {
        'fast': 11,
        'slow': 55
    }
    ADX_PERIOD = 14
    RSI_PERIOD = 14
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'trading_app.log')
    
    # Configuración de Socket.IO
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}