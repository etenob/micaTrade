"""
Aplicación principal mejorada - Bot de Trading Jaime Merino
Implementa la metodología completa de Trading Latino
"""
import os
import threading
import time
from flask_cors import CORS
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from enhanced_config import merino_config, MerinoConfig, merino_methodology
from utils.logger import setup_logger, app_logger
from websocket.enhanced_socket_handlers import EnhancedSocketHandlers
from services.enhanced_analysis_service import enhanced_analysis_service
from services.binance_service import binance_service
from Telegram.telegram_helper import send_telegram_message
import os
print("DEBUG BINANCE_API_KEY:", os.getenv("BINANCE_API_KEY")[:8], "...")
print("DEBUG BINANCE_SECRET_KEY:", os.getenv("BINANCE_SECRET_KEY")[:8], "...")

# Configurar logging mejorado
logger = app_logger

def setup_merino_logging(log_level: str):
    """Configura logging específico para la metodología Merino"""
    os.makedirs('logs', exist_ok=True)
    
    loggers = {
        'merino_app': MerinoConfig.LOG_FILES['app'],
        'merino_analysis': MerinoConfig.LOG_FILES['analysis'],
        'merino_signals': MerinoConfig.LOG_FILES['signals'],
        'merino_trades': MerinoConfig.LOG_FILES['trades'],
        'merino_websocket': MerinoConfig.LOG_FILES['websocket'],
        'merino_binance': MerinoConfig.LOG_FILES['binance']
    }
    
    for logger_name, log_file in loggers.items():
        setup_logger(logger_name, log_file, log_level)

def create_merino_app(config_name=None):
    """Factory function para crear la aplicación Jaime Merino Bot"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    config_class = merino_config.get(config_name, merino_config['default'])
    app.config.from_object(config_class)

    # ✅ Habilitar CORS (por si se conecta dashboard externo)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    setup_merino_logging(config_class.LOG_LEVEL)
    
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode=app.config['SOCKETIO_ASYNC_MODE'],
        logger=False,
        engineio_logger=False
    )
    
    socket_handlers = EnhancedSocketHandlers(socketio, config_class)
    socket_handlers.register_handlers()
    
    # ✅ Solo Merino (sin bridge de scalping)
    register_merino_routes(app, config_class)
    setup_merino_background_services(socketio, socket_handlers, config_class)
    
    logger.info("🚀 Jaime Merino Trading Bot creado exitosamente")
    logger.info(f"📈 Metodología: {merino_methodology.PHILOSOPHY['main_principle']}")
    
    print("✅ app.py arrancó correctamente y los servicios fueron creados")
    
    return app, socketio, socket_handlers

def register_merino_routes(app, config):
    """Registra las rutas mejoradas de la aplicación"""
    
    @app.route('/')
    def index():
        try:
            symbols_data = {symbol: enhanced_analysis_service.analyze_symbol_merino(symbol)
                            for symbol in config.TRADING_SYMBOLS}
            return render_template('merino_dashboard.html', 
                                   config=config,
                                   methodology=merino_methodology,
                                   symbols_data=symbols_data)
        except Exception as e:
            logger.error(f"❌ Error sirviendo dashboard: {e}")
            return f"Error cargando dashboard: {str(e)}", 500
    
    @app.route('/health')
    def health_check():
        try:
            binance_status = binance_service.test_connection()
            analysis_status = enhanced_analysis_service is not None
            
            health_data = {
                'status': 'healthy' if binance_status and analysis_status else 'degraded',
                'timestamp': datetime.now().isoformat(),
                'methodology': 'JAIME_MERINO',
                'version': '2.0.0',
                'services': {
                    'binance': 'connected' if binance_status else 'disconnected',
                    'analysis_service': 'active' if analysis_status else 'inactive',
                    'websocket': 'active',
                    'enhanced_indicators': 'active'
                },
                'configuration': {
                    'symbols': config.TRADING_SYMBOLS,
                    'timeframes': config.TIMEFRAMES,
                    'update_intervals': config.UPDATE_INTERVALS,
                    'risk_management': config.RISK_MANAGEMENT,
                    'signals_config': config.SIGNALS
                },
                'philosophy': merino_methodology.PHILOSOPHY['main_principle']
            }
            
            return jsonify(health_data)
        except Exception as e:
            logger.error(f"❌ Error en health check: {e}")
            return jsonify({'status': 'unhealthy', 'error': str(e), 'timestamp': datetime.now().isoformat()}), 500
    
    @app.route('/api/merino/symbols')
    def get_merino_symbols():
        return jsonify({
            'symbols': config.TRADING_SYMBOLS,
            'count': len(config.TRADING_SYMBOLS),
            'timeframes': config.TIMEFRAMES,
            'methodology': 'JAIME_MERINO'
        })
    
    @app.route('/api/merino/analysis/<symbol>')
    def get_merino_analysis(symbol):
        try:
            symbol = symbol.upper()
            if symbol not in config.TRADING_SYMBOLS:
                return jsonify({
                    'success': False,
                    'error': f'Símbolo {symbol} no está en la metodología Merino',
                    'supported_symbols': config.TRADING_SYMBOLS
                }), 400
            
            analysis = enhanced_analysis_service.analyze_symbol_merino(symbol)
            
            if analysis:
                return jsonify({'success': True, 'symbol': symbol, 'data': analysis, 'timestamp': datetime.now().isoformat()})
            else:
                return jsonify({'success': False, 'symbol': symbol, 'error': 'No se pudo completar el análisis'}), 500
        except Exception as e:
            logger.error(f"❌ Error en API análisis Merino para {symbol}: {e}")
            return jsonify({'success': False, 'symbol': symbol, 'error': str(e), 'timestamp': datetime.now().isoformat()}), 500

def setup_merino_background_services(socketio, socket_handlers, config):
    """Configura los servicios de fondo mejorados"""
    
    def merino_auto_analysis():
        logger.info("🔄 Servicio de análisis automático Merino iniciado")
        while True:
            try:
                interval = config.UPDATE_INTERVALS['4h']
                time.sleep(interval)
                
                if socket_handlers.get_connected_clients_count() > 0:
                    logger.info(f"🔄 Iniciando análisis automático Merino para {len(config.TRADING_SYMBOLS)} símbolos")
                    
                    for symbol in config.TRADING_SYMBOLS:
                        try:
                            analysis = enhanced_analysis_service.analyze_symbol_merino(symbol)
                            if analysis:
                                socket_handlers.broadcast_merino_analysis(symbol, analysis)
                                
                                signal_strength = analysis.get('signal', {}).get('signal_strength', 0)
                                if signal_strength >= config.SIGNALS['min_strength_for_trade']:
                                    text = f"🎯 SEÑAL MERINO: {symbol} - {analysis.get('signal', {}).get('signal', 'UNKNOWN')} ({signal_strength}%)"
                                    logger.info(text)
                                    send_telegram_message(text)
                                
                                time.sleep(5)
                            else:
                                logger.warning(f"⚠️ Análisis Merino falló para {symbol}")
                        except Exception as e:
                            logger.error(f"❌ Error en análisis automático de {symbol}: {e}")
                            continue
                else:
                    logger.debug("📭 No hay clientes conectados, saltando análisis automático")
            except Exception as e:
                logger.error(f"❌ Error en servicio de análisis automático Merino: {e}")
                time.sleep(300)
    
    def merino_market_monitor():
        logger.info("👁️ Monitor de mercado Merino iniciado")
        while True:
            try:
                time.sleep(config.UPDATE_INTERVALS['realtime'])
                btc_price = binance_service.get_current_price('BTCUSDT')
                if btc_price:
                    socketio.emit('btc_price_update', {'price': btc_price, 'timestamp': time.time()})
            except Exception as e:
                logger.error(f"❌ Error en monitor de mercado: {e}")
                time.sleep(60)
    
    def merino_risk_monitor():
        logger.info("🛡️ Monitor de riesgo Merino iniciado")
        while True:
            try:
                time.sleep(1800)
                risk_status = {
                    'timestamp': time.time(),
                    'limits': config.RISK_MANAGEMENT,
                    'status': 'MONITORING'
                }
                socketio.emit('risk_status', risk_status)
            except Exception as e:
                logger.error(f"❌ Error en monitor de riesgo: {e}")
                time.sleep(300)
    
    for target in [merino_auto_analysis, merino_market_monitor, merino_risk_monitor]:
        t = threading.Thread(target=target)
        t.daemon = True
        t.start()
    
    logger.info("✅ Servicios de fondo Merino iniciados")

def main():
    """Función principal"""
    try:
        config_name = os.environ.get('FLASK_ENV', 'development')
        config_class = merino_config.get(config_name, merino_config['default'])
        print(f"🧠 Modo activo: {config_name}")
        
        app, socketio, _ = create_merino_app(config_name)
        
        print(f"🌐 Servidor Merino disponible en http://{config_class.HOST}:{config_class.PORT}")
        
        socketio.run(app, host=config_class.HOST, port=config_class.PORT, debug=config_class.DEBUG, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("⏹️ Deteniendo Jaime Merino Bot por solicitud del usuario...")
    except Exception as e:
        logger.error(f"❌ Error crítico al iniciar Jaime Merino Bot: {e}")

if __name__ == '__main__':
    main()

