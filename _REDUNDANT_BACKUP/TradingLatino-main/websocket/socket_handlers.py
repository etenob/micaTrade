"""
Handlers para eventos de Socket.IO
"""
from flask_socketio import emit, disconnect
from flask import request
from services.analysis_service import analysis_service
from utils.logger import websocket_logger
from utils.json_utils import debug_json_serialization, clean_analysis_dict
from config import Config
import threading
import time

logger = websocket_logger

class SocketHandlers:
    """
    Manejadores de eventos Socket.IO
    """
    
    def __init__(self, socketio):
        """
        Inicializa los handlers con la instancia de socketio
        
        Args:
            socketio: Instancia de Flask-SocketIO
        """
        self.socketio = socketio
        self.analysis_service = analysis_service
        self.connected_clients = set()
        self.analysis_cache = {}
        logger.info("🔌 Socket handlers inicializados")
    
    def register_handlers(self):
        """Registra todos los event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Maneja la conexión de un nuevo cliente"""
            client_id = request.sid
            self.connected_clients.add(client_id)
            
            logger.info(f"✅ Cliente conectado: {client_id} (Total: {len(self.connected_clients)})")
            
            # Enviar mensaje de bienvenida
            emit('status', {
                'msg': 'Conectado al servidor de análisis - Metodología Jaime Merino',
                'timestamp': time.time(),
                'symbols_available': Config.TRADING_SYMBOLS
            })
            
            # Enviar análisis en cache si existen
            self._send_cached_analysis(client_id)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Maneja la desconexión de un cliente"""
            client_id = request.sid
            self.connected_clients.discard(client_id)
            
            logger.info(f"❌ Cliente desconectado: {client_id} (Total: {len(self.connected_clients)})")
        
        @self.socketio.on('request_analysis')
        def handle_request_analysis(data):
            """
            Maneja solicitudes de análisis para símbolos específicos
            
            Args:
                data: Dict con 'symbol' y opcionalmente otros parámetros
            """
            try:
                client_id = request.sid
                symbol = data.get('symbol', 'BTCUSDT').upper()
                
                # Validar símbolo
                if symbol not in Config.TRADING_SYMBOLS:
                    logger.warning(f"⚠️ Símbolo no soportado solicitado: {symbol} por {client_id}")
                    emit('analysis_error', {
                        'symbol': symbol,
                        'error': f'Símbolo {symbol} no está en la lista de símbolos soportados',
                        'supported_symbols': Config.TRADING_SYMBOLS
                    })
                    return
                
                logger.info(f"📊 Análisis solicitado: {symbol} por cliente {client_id}")
                
                # Realizar análisis en hilo separado para no bloquear
                analysis_thread = threading.Thread(
                    target=self._process_analysis_request,
                    args=(symbol, client_id)
                )
                analysis_thread.daemon = True
                analysis_thread.start()
                
            except Exception as e:
                logger.error(f"❌ Error procesando solicitud de análisis: {e}")
                emit('analysis_error', {
                    'symbol': data.get('symbol', 'UNKNOWN'),
                    'error': f'Error procesando solicitud: {str(e)}'
                })
        
        @self.socketio.on('request_all_symbols')
        def handle_request_all_symbols():
            """Solicita análisis para todos los símbolos configurados"""
            try:
                client_id = request.sid
                logger.info(f"📊 Análisis de todos los símbolos solicitado por {client_id}")
                
                # Procesar todos los símbolos en hilo separado
                all_symbols_thread = threading.Thread(
                    target=self._process_all_symbols_request,
                    args=(client_id,)
                )
                all_symbols_thread.daemon = True
                all_symbols_thread.start()
                
            except Exception as e:
                logger.error(f"❌ Error procesando solicitud de todos los símbolos: {e}")
                emit('analysis_error', {
                    'error': f'Error procesando solicitud completa: {str(e)}'
                })
        
        @self.socketio.on('ping')
        def handle_ping():
            """Responde a ping del cliente para mantener conexión"""
            emit('pong', {'timestamp': time.time()})
        
        @self.socketio.on('get_server_status')
        def handle_get_server_status():
            """Envía el estado del servidor"""
            try:
                status = {
                    'connected_clients': len(self.connected_clients),
                    'cached_analyses': len(self.analysis_cache),
                    'supported_symbols': Config.TRADING_SYMBOLS,
                    'update_interval': Config.UPDATE_INTERVAL,
                    'server_time': time.time(),
                    'binance_connection': self.analysis_service.binance.test_connection()
                }
                
                emit('server_status', status)
                logger.debug(f"📊 Estado del servidor enviado a {request.sid}")
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo estado del servidor: {e}")
                emit('server_status', {'error': str(e)})
    
    def _process_analysis_request(self, symbol: str, client_id: str):
        """
        Procesa una solicitud de análisis en hilo separado
        
        Args:
            symbol: Símbolo a analizar
            client_id: ID del cliente que solicitó
        """
        try:
            # Realizar análisis
            analysis = self.analysis_service.analyze_symbol(symbol)
            
            if analysis:
                # Convertir a diccionario y limpiar
                analysis_dict = analysis.to_dict()
                
                # Debug de serialización
                if not debug_json_serialization(analysis_dict, f"análisis de {symbol}"):
                    logger.warning(f"⚠️ Problemas de serialización detectados para {symbol}")
                    analysis_dict = clean_analysis_dict(analysis_dict)
                
                # Cachear análisis
                self.analysis_cache[symbol] = analysis_dict
                
                # Enviar a todos los clientes conectados
                self.socketio.emit('analysis_update', {
                    'symbol': symbol,
                    'data': analysis_dict,
                    'timestamp': time.time()
                })
                
                logger.info(f"✅ Análisis enviado para {symbol}")
                
            else:
                # Error en análisis
                self.socketio.emit('analysis_error', {
                    'symbol': symbol,
                    'error': 'No se pudo completar el análisis técnico',
                    'details': 'Verifique la conexión con Binance o intente más tarde'
                })
                
                logger.error(f"❌ Análisis falló para {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Error en hilo de análisis para {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            self.socketio.emit('analysis_error', {
                'symbol': symbol,
                'error': f'Error interno: {str(e)}'
            })
    
    def _process_all_symbols_request(self, client_id: str):
        """
        Procesa solicitud de análisis para todos los símbolos
        
        Args:
            client_id: ID del cliente que solicitó
        """
        try:
            logger.info(f"🔄 Procesando análisis completo para cliente {client_id}")
            
            # Notificar inicio
            self.socketio.emit('bulk_analysis_started', {
                'symbols': Config.TRADING_SYMBOLS,
                'total': len(Config.TRADING_SYMBOLS)
            }, room=client_id)
            
            completed = 0
            
            for symbol in Config.TRADING_SYMBOLS:
                try:
                    # Pequeña pausa entre análisis para no sobrecargar
                    time.sleep(0.5)
                    
                    analysis = self.analysis_service.analyze_symbol(symbol)
                    
                    if analysis:
                        analysis_dict = analysis.to_dict()
                        
                        # Limpiar si es necesario
                        if not debug_json_serialization(analysis_dict, f"análisis bulk {symbol}"):
                            analysis_dict = clean_analysis_dict(analysis_dict)
                        
                        # Cachear y enviar
                        self.analysis_cache[symbol] = analysis_dict
                        
                        self.socketio.emit('analysis_update', {
                            'symbol': symbol,
                            'data': analysis_dict,
                            'timestamp': time.time(),
                            'bulk_progress': {
                                'completed': completed + 1,
                                'total': len(Config.TRADING_SYMBOLS)
                            }
                        })
                        
                        completed += 1
                        logger.debug(f"✅ Análisis bulk completado: {symbol} ({completed}/{len(Config.TRADING_SYMBOLS)})")
                        
                    else:
                        logger.warning(f"⚠️ Análisis bulk falló para {symbol}")
                        
                except Exception as e:
                    logger.error(f"❌ Error en análisis bulk para {symbol}: {e}")
                    continue
            
            # Notificar finalización
            self.socketio.emit('bulk_analysis_completed', {
                'completed': completed,
                'total': len(Config.TRADING_SYMBOLS),
                'success_rate': (completed / len(Config.TRADING_SYMBOLS)) * 100
            }, room=client_id)
            
            logger.info(f"🏁 Análisis bulk completado: {completed}/{len(Config.TRADING_SYMBOLS)} símbolos")
            
        except Exception as e:
            logger.error(f"❌ Error en análisis bulk: {e}")
            self.socketio.emit('bulk_analysis_error', {
                'error': str(e)
            }, room=client_id)
    
    def _send_cached_analysis(self, client_id: str):
        """
        Envía análisis en cache a un cliente recién conectado
        
        Args:
            client_id: ID del cliente
        """
        try:
            if self.analysis_cache:
                logger.info(f"📤 Enviando {len(self.analysis_cache)} análisis en cache a {client_id}")
                
                for symbol, analysis_data in self.analysis_cache.items():
                    self.socketio.emit('analysis_update', {
                        'symbol': symbol,
                        'data': analysis_data,
                        'timestamp': time.time(),
                        'cached': True
                    }, room=client_id)
                    
                    # Pequeña pausa para evitar saturar
                    time.sleep(0.1)
            else:
                logger.debug(f"📭 No hay análisis en cache para enviar a {client_id}")
                
        except Exception as e:
            logger.error(f"❌ Error enviando cache a {client_id}: {e}")
    
    def broadcast_analysis_update(self, symbol: str, analysis_data: dict):
        """
        Envía actualización de análisis a todos los clientes conectados
        
        Args:
            symbol: Símbolo actualizado
            analysis_data: Datos del análisis
        """
        try:
            if self.connected_clients:
                # Limpiar datos antes de enviar
                clean_data = clean_analysis_dict(analysis_data.copy())
                
                self.socketio.emit('analysis_update', {
                    'symbol': symbol,
                    'data': clean_data,
                    'timestamp': time.time(),
                    'broadcast': True
                })
                
                # Actualizar cache
                self.analysis_cache[symbol] = clean_data
                
                logger.info(f"📡 Análisis broadcast para {symbol} a {len(self.connected_clients)} clientes")
            else:
                logger.debug(f"📭 No hay clientes conectados para broadcast de {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Error en broadcast para {symbol}: {e}")
    
    def clear_analysis_cache(self):
        """Limpia el cache de análisis"""
        self.analysis_cache.clear()
        logger.info("🗑️ Cache de análisis limpiado")
    
    def get_connected_clients_count(self) -> int:
        """Retorna el número de clientes conectados"""
        return len(self.connected_clients)