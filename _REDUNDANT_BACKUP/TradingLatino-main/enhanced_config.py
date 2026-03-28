#TradingLatino-main/enhanced_config.py
"""
Configuración mejorada para la metodología Jaime Merino
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class MerinoConfig:
    """Configuración específica para metodología"""
    
    # Configuración base de la aplicación
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jaime_merino_trading_latino_2025'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Servidor
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # APIs de Exchange
    BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.environ.get('BINANCE_SECRET_KEY', '')
    
    # Símbolos principales según (foco en Bitcoin y principales altcoins)
    TRADING_SYMBOLS = [
        'BTCUSDT',    # Bitcoin - Principal
        'ETHUSDT',    # Ethereum
        #'BNBUSDT',    # Binance Coin
        'ADAUSDT',    # Cardano
        #'XRPUSDT',    # Ripple
        #'DOGEUSDT',   # Dogecoin
        #'TRXUSDT',    # TRON
        #'ALGOUSDT'    # Algorand
    ]
    
    # Configuración de timeframes (multi-temporal + scalping)

    TIMEFRAMES = {
        'primary': '4h',      # Timeframe principal para decisiones
        'timing': '1h',       # Para timing preciso de entradas
        'context': '1d',      # Para contexto macro
        'confirmation': '15m', # Para confirmaciones rápidas
        'scalping' : '5m'      # 🔥 Scalping'
    }
    
    # Intervalos de actualización por timeframe

    UPDATE_INTERVALS = {
        '4h': int(os.environ.get('UPDATE_INTERVAL_4H', 3600)),    # 1 hora
        '1h': int(os.environ.get('UPDATE_INTERVAL_1H', 900)),    # 15 minutos
        '1d': int(os.environ.get('UPDATE_INTERVAL_1D', 86400)),   # 1 dia
        '15m': int(os.environ.get('UPDATE_INTERVAL_15M', 900)),   # 15 minutos
        '5m': int(os.environ.get('UPDATE_INTERVAL_5M', 200)),     # 5 segundos
        'realtime': int(os.environ.get('UPDATE_INTERVAL_RT', 30)) # 1 minuto
    }
    
    # Configuración de indicadores
    INDICATORS = {
        # EMAs principales
        'ema_fast': 10,    # EMA rápida
        'ema_slow': 55,    # EMA lenta
        'ema_trend': 100,  # EMA de tendencia principal
        'ema_long': 200,   # EMA de largo plazo
        
        # ADX (configuración)
        'adx_period': 14,
        'adx_smoothing': 14,
        'adx_zero_point': 23,  # Punto 23 como 0 
        'adx_trending_threshold': 25,
        'adx_strong_trend': 35,
        'adx_very_strong': 50,
        
        # Squeeze Momentum (LazyBear version)
        'squeeze_bb_length': 20,
        'squeeze_kc_length': 20,
        'squeeze_kc_mult': 1.5,
        
        # Volume Profile
        'vpvr_lookback': 100,
        'vpvr_bins': 50,
        
        # RSI
        'rsi_period': 14,
        'rsi_overbought': 70,
        'rsi_oversold': 30

        # Otros indicadores pueden añadirse según necesidad

        # (MACD, Stochastic, etc.)
         }
    
    # Gestión de riesgo según filosofía 40-30-20-10 de Merino
    RISK_MANAGEMENT = {
        # Asignación de capital
        'btc_long_term_pct': 40.0,    # 40% Bitcoin largo plazo
        'weekly_charts_pct': 30.0,    # 30% gráficos semanales
        'daily_trading_pct': 20.0,    # 20% trading diario
        'futures_pct': 10.0,          # 10% futuros
        
        # Límites de riesgo por operación
        'max_position_size_pct': 5.0,    # 5% máximo por posición
        'default_position_size_pct': 2.0, # 2% posición estándar
        'max_risk_per_trade_pct': 1.0,   # 1% riesgo máximo por trade
        
        # Límites de pérdida según Merino
        'max_daily_loss_pct': 6.0,     # 6% pérdida máxima diaria
        'max_weekly_loss_pct': 8.0,    # 8% pérdida máxima semanal
        'max_monthly_loss_pct': 10.0,  # 10% pérdida máxima mensual
        
        # Apalancamiento
        'max_leverage': 3.0,            # Máximo 1:3
        'recommended_leverage': 1.0,    # Recomendado sin apalancamiento
        
        # Targets y stops estándar
        'default_target_1_pct': 2.0,   # +2% primer objetivo
        'default_target_2_pct': 5.0,   # +5% segundo objetivo
        'default_stop_loss_pct': 2.0,  # -2% stop loss
        'default_risk_reward': 2.5     # Ratio riesgo/beneficio
    }
    # Configuración Scalping
    SCALPING = {
        
        'enabled': True,                # Habilitar scalping
        'max_trades_per_day': 3,        # Máximo 3 trades diarios
        'timeframe': '5m',     # Timeframe para scalping
        'scalping_risk_per_trade_pct': 0.5, # Riesgo 0.5% por trade
        'scalping_target_pct': 1.0,  # Target 3%
        'scalping_stop_loss_pct': 1 , # Stop loss 1%

        # indicadores básicos, luego cambiamos a Nadaraya
        
        'ema_fast': 5,
        'ema_slow': 20,
        'rsi_period': 7,
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'max_signals_per_hour': 10
    }
    # Configuración de señales
    SIGNALS = {
        'min_strength_for_trade': 50,      # Fuerza mínima para operar
        'high_strength_threshold': 70,     # Fuerza alta
        'min_confluence_score': 2,         # Confluencias mínimas
        'optimal_confluence_score': 3,     # Confluencias óptimas
        
        # Filtros adicionales
        'require_adx_trending': True,      # Requiere ADX > 25
        'avoid_squeeze': True,             # Evitar operar durante squeeze
        'require_volume_confirmation': False, # Confirmar con volumen
        
        # Invalidación de señales
        'signal_timeout_hours': 8,         # Señal expira en 8 horas
        'max_signals_per_day': 5          # Máximo 5 señales por día
    }
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILES = {
        'app': 'logs/merino_trading_app.log',
        'analysis': 'logs/merino_analysis.log',
        'signals': 'logs/merino_signals.log',
        'trades': 'logs/merino_trades.log',
        'websocket': 'logs/merino_websocket.log',
        'binance': 'logs/merino_binance.log'
    }
    
    # Socket.IO
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Configuración de alertas
    ALERTS = {
        'telegram_enabled': os.environ.get('TELEGRAM_ENABLED', 'False').lower() == 'true',
        'telegram_bot_token': os.environ.get('TELEGRAM_BOT_TOKEN', ''),
        'telegram_chat_id': os.environ.get('TELEGRAM_CHAT_ID', ''),
        'email_enabled': os.environ.get('EMAIL_ENABLED', 'False').lower() == 'true',
        'email_smtp_server': os.environ.get('EMAIL_SMTP_SERVER', ''),
        'email_from': os.environ.get('EMAIL_FROM', ''),
        'email_to': os.environ.get('EMAIL_TO', '')
    }
    
    # Configuración de backtesting
    BACKTESTING = {
        'enabled': os.environ.get('BACKTESTING_ENABLED', 'False').lower() == 'true',
        'start_date': os.environ.get('BACKTEST_START_DATE', '2023-01-01'),
        'end_date': os.environ.get('BACKTEST_END_DATE', '2024-12-31'),
        'initial_capital': float(os.environ.get('BACKTEST_CAPITAL', 10000)),
        'commission_pct': float(os.environ.get('BACKTEST_COMMISSION', 0.1))
    }

    @staticmethod
    def get_socketio_config():
        """Configuración específica para SocketIO en producción"""
        return {
            'cors_allowed_origins': os.environ.get('CORS_ORIGINS', '*'),
            'async_mode': 'eventlet',
            'logger': False,
            'engineio_logger': False,
            'ping_timeout': 60,
            'ping_interval': 25
        }
class ProductionMerinoConfig(MerinoConfig):
    """Configuración para producción en Render"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # URLs permitidas para CORS
    SOCKETIO_CORS_ALLOWED_ORIGINS = [
        "https://*.onrender.com",
        "https://your-app-name.onrender.com"  # Reemplaza con tu URL
    ]
    
    # Configuración optimizada para Render
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # Timeouts más largos para conexiones remotas
    UPDATE_INTERVALS = {
        '4h': 1800,  # 30 minutos
        '1h': 600,   # 10 minutos
        '1d': 3600,  # 1 hora
        'realtime': 300  # 5 minutos
    }

class DevelopmentMerinoConfig(MerinoConfig):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    # Intervalos más frecuentes para desarrollo
    UPDATE_INTERVALS = {
        '4h': 300,   # 5 minutos
        '1h': 120,   # 2 minutos
        '1d': 600,   # 10 minutos
        'realtime': 30  # 30 segundos
    }

class TestingMerinoConfig(MerinoConfig):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    # Símbolos reducidos para testing
    TRADING_SYMBOLS = ['BTCUSDT', 'ETHUSDT']
    # Intervalos rápidos para testing
    UPDATE_INTERVALS = {
        '4h': 60,
        '1h': 30, 
        '1d': 120,
        'realtime': 10
    }

# Diccionario de configuraciones
merino_config = {
    'development': DevelopmentMerinoConfig,
    'production': ProductionMerinoConfig,
    'testing': TestingMerinoConfig,
    'default': DevelopmentMerinoConfig
}

# Configuración adicional específica para la metodología
class MerinoMethodology:
    """
    Constantes y reglas específicas de la estrategia
    """
    
    # Frases y filosofía
    PHILOSOPHY = {
        'main_principle': "El arte de tomar dinero de otros legalmente",
        'risk_motto': "Es mejor perder una oportunidad que perder dinero",
        'discipline': "Solo operamos con alta probabilidad de éxito",
        'contrarian': "Operamos contra el 90% que pierde dinero",
        'patience': "No forzar operaciones - preservar capital es prioritario"
    }
    
    # Estados de mercado según Merino
    MARKET_STATES = {
        'TRENDING': 'Mercado en tendencia - operable',
        'SQUEEZE': 'Consolidación - esperar ruptura',
        'CHOPPY': 'Mercado errático - evitar',
        'BREAKOUT': 'Ruptura - oportunidad inmediata',
        'REVERSAL': 'Posible reversión - cautela'
    }
    
    # Confluencias técnicas requeridas
    CONFLUENCES = [
        'EMAs alineadas (11 vs 55)',
        'ADX confirma tendencia (>25)',
        'Momentum direccional claro',
        'Sin squeeze (volatilidad presente)',
        'Precio respeta EMA 11',
        'Volume Profile favorable'
    ]
    
    # Reglas de invalidación
    INVALIDATION_RULES = {
        'LONG': [
            'Cierre bajo EMA 11 en 4H',
            'ADX cae bajo 20',
            'Momentum negativo persistente',
            'Ruptura soporte clave'
        ],
        'SHORT': [
            'Cierre sobre EMA 11 en 4H', 
            'ADX cae bajo 20',
            'Momentum positivo persistente',
            'Ruptura resistencia clave'
        ]
    }
    
    # Horarios óptimos de trading (UTC)
    OPTIMAL_TRADING_HOURS = {
        'crypto': '24/7',  # Cripto opera 24/7
        'high_volume': ['08:00-12:00', '13:00-17:00', '20:00-00:00'],
        'avoid': ['02:00-06:00']  # Volumen muy bajo
    }

# Instancia de la metodología
merino_methodology = MerinoMethodology()
