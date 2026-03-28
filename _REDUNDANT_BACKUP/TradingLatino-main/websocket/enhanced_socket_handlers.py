"""
Handlers mejorados para eventos de Socket.IO según metodología Jaime Merino
"""
from flask_socketio import emit, disconnect
from flask import request
from services.enhanced_analysis_service import enhanced_analysis_service
from utils.logger import websocket_logger
from utils.json_utils import debug_json_serialization, clean_analysis_dict
from enhanced_config import merino_methodology
import threading
import time
import json
from datetime import datetime

logger = websocket_logger

class EnhancedSocketHandlers:
    """
    Manejadores mejorados de eventos Socket.IO para metodología Jaime Merino
    """
    
    def __init__(self, socketio, config):
        """
        Inicializa los handlers mejorados
        
        Args:
            socketio: Instancia de Flask-SocketIO
            config: Configuración de la aplicación
        """
        self.socketio = socketio
        self.config = config
        self.analysis_service = enhanced_analysis_service
        self.connected_clients = set()
        self.merino_analysis_cache = {}
        self.client_preferences = {}  # Preferencias por cliente
        logger.info("🔌 Handlers Socket.IO mejorados para Metodología Jaime Merino inicializados")
    
    def register_handlers(self):
        """Registra todos los event handlers mejorados"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Maneja la conexión de un nuevo cliente"""
            client_id = request.sid
            self.connected_clients.add(client_id)
            
            logger.info(f"✅ Cliente conectado: {client_id} (Total: {len(self.connected_clients)})")
            
            # Mensaje de bienvenida con filosofía de Merino
            emit('merino_welcome', {
                'msg': 'Bienvenido al Bot de Trading Jaime Merino',
                'methodology': 'JAIME_MERINO',
                'philosophy': merino_methodology.PHILOSOPHY['main_principle'],
                'discipline': merino_methodology.PHILOSOPHY['discipline'],
                'timestamp': time.time(),
                'symbols_available': self.config.TRADING_SYMBOLS,
                'timeframes': self.config.TIMEFRAMES,
                'risk_management': self.config.RISK_MANAGEMENT,
                'version': '2.0.0'
            })
            
            # Enviar análisis en cache si existen
            self._send_cached_merino_analysis(client_id)
            
            # Enviar estado del mercado
            self._send_market_overview(client_id)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Maneja la desconexión de un cliente"""
            client_id = request.sid
            self.connected_clients.discard(client_id)
            
            # Limpiar preferencias del cliente
            if client_id in self.client_preferences:
                del self.client_preferences[client_id]
            
            logger.info(f"❌ Cliente desconectado: {client_id} (Total: {len(self.connected_clients)})")
        
        @self.socketio.on('request_merino_analysis')
        def handle_request_merino_analysis(data):
            """
            Maneja solicitudes de análisis según metodología Jaime Merino
            
            Args:
                data: Dict con 'symbol' y configuraciones
            """
            try:
                client_id = request.sid
                symbol = data.get('symbol', 'BTCUSDT').upper()
                
                # Validar símbolo
                if symbol not in self.config.TRADING_SYMBOLS:
                    logger.warning(f"⚠️ Símbolo no soportado en metodología Merino: {symbol}")
                    emit('merino_analysis_error', {
                        'symbol': symbol,
                        'error': f'Símbolo {symbol} no está en la metodología Jaime Merino',
                        'supported_symbols': self.config.TRADING_SYMBOLS,
                        'methodology': 'JAIME_MERINO'
                    })
                    return
                
                logger.info(f"📊 Análisis Merino solicitado: {symbol} por cliente {client_id}")
                
                # Procesar análisis en hilo separado
                analysis_thread = threading.Thread(
                    target=self._process_merino_analysis_request,
                    args=(symbol, client_id, data.get('options', {}))
                )
                analysis_thread.daemon = True
                analysis_thread.start()
                
            except Exception as e:
                logger.error(f"❌ Error procesando solicitud análisis Merino: {e}")
                emit('merino_analysis_error', {
                    'symbol': data.get('symbol', 'UNKNOWN'),
                    'error': f'Error procesando solicitud: {str(e)}',
                    'methodology': 'JAIME_MERINO'
                })
        
        @self.socketio.on('request_all_merino_symbols')
        def handle_request_all_merino_symbols(data=None):
            """Solicita análisis Merino para todos los símbolos"""
            try:
                client_id = request.sid
                options = data.get('options', {}) if data else {}
                
                logger.info(f"📊 Análisis Merino completo solicitado por {client_id}")
                
                # Procesar todos los símbolos
                bulk_analysis_thread = threading.Thread(
                    target=self._process_all_merino_symbols_request,
                    args=(client_id, options)
                )
                bulk_analysis_thread.daemon = True
                bulk_analysis_thread.start()
                
            except Exception as e:
                logger.error(f"❌ Error procesando solicitud completa Merino: {e}")
                emit('merino_bulk_analysis_error', {
                    'error': f'Error procesando solicitud completa: {str(e)}',
                    'methodology': 'JAIME_MERINO'
                })
        
        @self.socketio.on('set_client_preferences')
        def handle_set_client_preferences(data):
            """Configura preferencias del cliente"""
            try:
                client_id = request.sid
                preferences = data.get('preferences', {})
                
                self.client_preferences[client_id] = {
                    'favorite_symbols': preferences.get('favorite_symbols', ['BTCUSDT']),
                    'alert_threshold': preferences.get('alert_threshold', 70),
                    'timeframe_preference': preferences.get('timeframe', '4h'),
                    'risk_tolerance': preferences.get('risk_tolerance', 'medium'),
                    'notifications': preferences.get('notifications', True)
                }
                
                emit('preferences_updated', {
                    'preferences': self.client_preferences[client_id],
                    'methodology': 'JAIME_MERINO'
                })
                
                logger.info(f"⚙️ Preferencias actualizadas para cliente {client_id}")
                
            except Exception as e:
                logger.error(f"❌ Error configurando preferencias: {e}")
                emit('preferences_error', {'error': str(e)})
        
        @self.socketio.on('request_merino_philosophy')
        def handle_request_philosophy():
            """Envía la filosofía completa de Jaime Merino"""
            emit('merino_philosophy', {
                'methodology': 'JAIME_MERINO',
                'philosophy': merino_methodology.PHILOSOPHY,
                'market_states': merino_methodology.MARKET_STATES,
                'confluences': merino_methodology.CONFLUENCES,
                'invalidation_rules': merino_methodology.INVALIDATION_RULES,
                'trading_hours': merino_methodology.OPTIMAL_TRADING_HOURS,
                'timestamp': time.time()
            })
        
        @self.socketio.on('request_risk_calculator')
        def handle_risk_calculator(data):
            """Calcula riesgo según reglas de Merino"""
            try:
                capital = data.get('capital', 10000)
                signal_strength = data.get('signal_strength', 50)
                symbol = data.get('symbol', 'BTCUSDT')
                
                risk_calc = self._calculate_merino_risk(capital, signal_strength, symbol)
                
                emit('risk_calculation', {
                    'methodology': 'JAIME_MERINO',
                    'input': {'capital': capital, 'signal_strength': signal_strength, 'symbol': symbol},
                    'calculation': risk_calc,
                    'philosophy': merino_methodology.PHILOSOPHY['risk_motto'],
                    'timestamp': time.time()
                })
                
            except Exception as e:
                logger.error(f"❌ Error en calculadora de riesgo: {e}")
                emit('risk_calculation_error', {'error': str(e)})
        
        @self.socketio.on('ping')
        def handle_ping():
            """Responde a ping con información de Merino"""
            emit('pong', {
                'timestamp': time.time(),
                'methodology': 'JAIME_MERINO',
                'status': 'active',
                'philosophy': merino_methodology.PHILOSOPHY['discipline']
            })
        
        @self.socketio.on('get_merino_server_status')
        def handle_get_merino_server_status():
            """Envía el estado completo del servidor Merino"""
            try:
                # Calcular estadísticas de señales
                high_probability_signals = 0
                total_cached = len(self.merino_analysis_cache)
                
                for symbol, analysis in self.merino_analysis_cache.items():
                    signal_strength = analysis.get('signal', {}).get('signal_strength', 0)
                    if signal_strength >= self.config.SIGNALS['min_strength_for_trade']:
                        high_probability_signals += 1
                
                status = {
                    'methodology': 'JAIME_MERINO',
                    'connected_clients': len(self.connected_clients),
                    'cached_analyses': total_cached,
                    'high_probability_signals': high_probability_signals,
                    'supported_symbols': self.config.TRADING_SYMBOLS,
                    'timeframes': self.config.TIMEFRAMES,
                    'update_intervals': self.config.UPDATE_INTERVALS,
                    'risk_management': self.config.RISK_MANAGEMENT,
                    'signals_config': self.config.SIGNALS,
                    'server_time': time.time(),
                    'binance_connection': self.analysis_service.binance.test_connection(),
                    'philosophy': merino_methodology.PHILOSOPHY,
                    'version': '2.0.0'
                }
                
                emit('merino_server_status', status)
                logger.debug(f"📊 Estado servidor Merino enviado a {request.sid}")
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo estado servidor Merino: {e}")
                emit('merino_server_status', {'error': str(e), 'methodology': 'JAIME_MERINO'})
    
    def _process_merino_analysis_request(self, symbol: str, client_id: str, options: dict):
        """
        Procesa solicitud de análisis Merino en hilo separado
        
        Args:
            symbol: Símbolo a analizar
            client_id: ID del cliente
            options: Opciones adicionales
        """
        try:
            # Realizar análisis completo según Merino
            analysis = self.analysis_service.analyze_symbol_merino(symbol)
            
            if analysis:
                # Limpiar y cachear análisis
                clean_analysis = self._clean_merino_analysis(analysis)
                self.merino_analysis_cache[symbol] = clean_analysis
                
                # Determinar si es una señal de alta probabilidad
                signal_strength = clean_analysis.get('signal', {}).get('signal_strength', 0)
                is_high_probability = signal_strength >= self.config.SIGNALS['min_strength_for_trade']
                
                # Enviar análisis
                self.socketio.emit('merino_analysis_update', {
                    'methodology': 'JAIME_MERINO',
                    'symbol': symbol,
                    'data': clean_analysis,
                    'timestamp': time.time(),
                    'high_probability': is_high_probability,
                    'philosophy_note': merino_methodology.PHILOSOPHY['discipline'] if is_high_probability else merino_methodology.PHILOSOPHY['risk_motto']
                })
                
                # Log según importancia
                if is_high_probability:
                    logger.info(f"🎯 SEÑAL ALTA PROBABILIDAD: {symbol} - {clean_analysis.get('signal', {}).get('signal', 'UNKNOWN')} ({signal_strength}%)")
                else:
                    logger.info(f"📊 Análisis Merino enviado: {symbol} ({signal_strength}%)")
                
            else:
                # Error en análisis
                self.socketio.emit('merino_analysis_error', {
                    'symbol': symbol,
                    'methodology': 'JAIME_MERINO',
                    'error': 'No se pudo completar el análisis según metodología Merino',
                    'details': 'Verificar conexión con Binance o intente más tarde',
                    'philosophy': merino_methodology.PHILOSOPHY['discipline']
                })
                
                logger.error(f"❌ Análisis Merino falló para {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Error en hilo análisis Merino para {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            self.socketio.emit('merino_analysis_error', {
                'symbol': symbol,
                'methodology': 'JAIME_MERINO',
                'error': f'Error interno: {str(e)}'
            })
    
    def _process_all_merino_symbols_request(self, client_id: str, options: dict):
        """
        Procesa solicitud de análisis completo Merino
        
        Args:
            client_id: ID del cliente
            options: Opciones adicionales
        """
        try:
            logger.info(f"🔄 Procesando análisis completo Merino para cliente {client_id}")
            
            # Notificar inicio
            self.socketio.emit('merino_bulk_analysis_started', {
                'methodology': 'JAIME_MERINO',
                'symbols': self.config.TRADING_SYMBOLS,
                'total': len(self.config.TRADING_SYMBOLS),
                'philosophy': merino_methodology.PHILOSOPHY['main_principle']
            }, room=client_id)
            
            completed = 0
            high_probability_count = 0
            
            for symbol in self.config.TRADING_SYMBOLS:
                try:
                    # Pausa entre análisis
                    time.sleep(2)
                    
                    analysis = self.analysis_service.analyze_symbol_merino(symbol)
                    
                    if analysis:
                        clean_analysis = self._clean_merino_analysis(analysis)
                        self.merino_analysis_cache[symbol] = clean_analysis
                        
                        # Verificar si es alta probabilidad
                        signal_strength = clean_analysis.get('signal', {}).get('signal_strength', 0)
                        is_high_probability = signal_strength >= self.config.SIGNALS['min_strength_for_trade']
                        
                        if is_high_probability:
                            high_probability_count += 1
                        
                        # Enviar análisis individual
                        self.socketio.emit('merino_analysis_update', {
                            'methodology': 'JAIME_MERINO',
                            'symbol': symbol,
                            'data': clean_analysis,
                            'timestamp': time.time(),
                            'high_probability': is_high_probability,
                            'bulk_progress': {
                                'completed': completed + 1,
                                'total': len(self.config.TRADING_SYMBOLS),
                                'high_probability_found': high_probability_count
                            }
                        })
                        
                        completed += 1
                        logger.debug(f"✅ Análisis bulk Merino: {symbol} ({completed}/{len(self.config.TRADING_SYMBOLS)})")
                        
                    else:
                        logger.warning(f"⚠️ Análisis bulk Merino falló: {symbol}")
                        
                except Exception as e:
                    logger.error(f"❌ Error en análisis bulk Merino para {symbol}: {e}")
                    continue
            
            # Notificar finalización
            success_rate = (completed / len(self.config.TRADING_SYMBOLS)) * 100
            
            self.socketio.emit('merino_bulk_analysis_completed', {
                'methodology': 'JAIME_MERINO',
                'completed': completed,
                'total': len(self.config.TRADING_SYMBOLS),
                'success_rate': success_rate,
                'high_probability_signals': high_probability_count,
                'philosophy': merino_methodology.PHILOSOPHY['discipline'],
                'recommendation': f"Encontradas {high_probability_count} señales de alta probabilidad" if high_probability_count > 0 else "Preservar capital - No hay setups claros"
            }, room=client_id)
            
            logger.info(f"🏁 Análisis bulk Merino completado: {completed}/{len(self.config.TRADING_SYMBOLS)} símbolos, {high_probability_count} alta probabilidad")
            
        except Exception as e:
            logger.error(f"❌ Error en análisis bulk Merino: {e}")
            self.socketio.emit('merino_bulk_analysis_error', {
                'methodology': 'JAIME_MERINO',
                'error': str(e)
            }, room=client_id)
    
    def _send_cached_merino_analysis(self, client_id: str):
        """
        Envía análisis Merino en cache a cliente recién conectado
        
        Args:
            client_id: ID del cliente
        """
        try:
            if self.merino_analysis_cache:
                logger.info(f"📤 Enviando {len(self.merino_analysis_cache)} análisis Merino en cache a {client_id}")
                
                high_probability_count = 0
                
                for symbol, analysis_data in self.merino_analysis_cache.items():
                    signal_strength = analysis_data.get('signal', {}).get('signal_strength', 0)
                    is_high_probability = signal_strength >= self.config.SIGNALS['min_strength_for_trade']
                    
                    if is_high_probability:
                        high_probability_count += 1
                    
                    self.socketio.emit('merino_analysis_update', {
                        'methodology': 'JAIME_MERINO',
                        'symbol': symbol,
                        'data': analysis_data,
                        'timestamp': time.time(),
                        'cached': True,
                        'high_probability': is_high_probability
                    }, room=client_id)
                    
                    # Pausa para evitar saturar
                    time.sleep(0.2)
                
                # Enviar resumen
                self.socketio.emit('cached_analysis_summary', {
                    'methodology': 'JAIME_MERINO',
                    'total_cached': len(self.merino_analysis_cache),
                    'high_probability_signals': high_probability_count,
                    'philosophy': merino_methodology.PHILOSOPHY['discipline']
                }, room=client_id)
                
            else:
                logger.debug(f"📭 No hay análisis Merino en cache para {client_id}")
                
        except Exception as e:
            logger.error(f"❌ Error enviando cache Merino a {client_id}: {e}")
    
    def _send_market_overview(self, client_id: str):
        """Envía overview del mercado al cliente"""
        try:
            # Calcular overview básico
            btc_price = self.analysis_service.binance.get_current_price('BTCUSDT')
            
            market_overview = {
                'methodology': 'JAIME_MERINO',
                'btc_price': btc_price,
                'total_symbols_monitored': len(self.config.TRADING_SYMBOLS),
                'philosophy': merino_methodology.PHILOSOPHY['main_principle'],
                'risk_management': '40-30-20-10 Capital Allocation',
                'timestamp': time.time()
            }
            
            self.socketio.emit('market_overview', market_overview, room=client_id)
            
        except Exception as e:
            logger.error(f"❌ Error enviando market overview: {e}")
    
    def _clean_merino_analysis(self, analysis_data: dict) -> dict:
        """
        Limpia los datos de análisis para el caché
        
        Args:
            analysis_data: Datos del análisis
            
        Returns:
            Datos limpios para cachear
        """
        try:
            # Asegurar que todos los valores sean serializables
            clean_data = {}
            
            for key, value in analysis_data.items():
                if key == 'timestamp' and isinstance(value, datetime):
                    clean_data[key] = value.isoformat()
                elif key == 'to_dict':
                    # Omitir el método falso
                    continue
                elif isinstance(value, (dict, list, str, int, float, bool, type(None))):
                    clean_data[key] = value
                else:
                    # Convertir otros tipos a string
                    clean_data[key] = str(value)
            
            return clean_data
            
        except Exception as e:
            logger.error(f"❌ Error limpiando datos de análisis: {e}")
            return analysis_data
    
    def _calculate_merino_risk(self, capital: float, signal_strength: int, symbol: str) -> dict:
        """
        Calcula riesgo según reglas específicas de Merino
        
        Args:
            capital: Capital total
            signal_strength: Fuerza de la señal
            symbol: Símbolo a operar
            
        Returns:
            Cálculo de riesgo detallado
        """
        try:
            # Asignación base según filosofía 40-30-20-10
            btc_long_term = capital * 0.40
            weekly_charts = capital * 0.30
            daily_trading = capital * 0.20
            futures = capital * 0.10
            
            # Determinar de qué pool tomar la operación
            if symbol == 'BTCUSDT' and signal_strength >= 70:
                # Bitcoin con señal fuerte: puede usar weekly_charts
                available_capital = weekly_charts
                allocation_source = 'weekly_charts'
            elif signal_strength >= 60:
                # Señal buena: usar daily_trading
                available_capital = daily_trading
                allocation_source = 'daily_trading'
            elif signal_strength >= 50:
                # Señal moderada: usar portion menor de daily_trading
                available_capital = daily_trading * 0.5
                allocation_source = 'daily_trading_partial'
            else:
                # Señal débil: no operar
                available_capital = 0
                allocation_source = 'none'
            
            if available_capital > 0:
                # Calcular tamaño de posición según fuerza de señal
                if signal_strength >= 80:
                    position_size_pct = 5.0  # 5% máximo para señales muy fuertes
                elif signal_strength >= 70:
                    position_size_pct = 3.0  # 3% para señales fuertes
                elif signal_strength >= 60:
                    position_size_pct = 2.0  # 2% para señales buenas
                else:
                    position_size_pct = 1.0  # 1% para señales moderadas
                
                position_size = min(available_capital * (position_size_pct / 100), capital * 0.05)  # Max 5% del capital total
                max_loss = position_size * 0.02  # 2% stop loss
                max_risk_pct = (max_loss / capital) * 100
                
                # Targets según Merino
                target_1 = position_size * 0.02  # +2%
                target_2 = position_size * 0.05  # +5%
                potential_profit = target_1 + target_2
                risk_reward = potential_profit / max_loss if max_loss > 0 else 0
                
                calculation = {
                    'can_trade': True,
                    'allocation_source': allocation_source,
                    'available_capital': available_capital,
                    'position_size': position_size,
                    'position_size_pct': (position_size / capital) * 100,
                    'max_loss': max_loss,
                    'max_risk_pct': max_risk_pct,
                    'target_1_profit': target_1,
                    'target_2_profit': target_2,
                    'total_potential_profit': potential_profit,
                    'risk_reward_ratio': risk_reward,
                    'daily_limit_remaining': self.config.RISK_MANAGEMENT['max_daily_loss_pct'],
                    'recommendation': self._get_risk_recommendation(signal_strength, max_risk_pct)
                }
            else:
                calculation = {
                    'can_trade': False,
                    'reason': 'Señal insuficiente según criterios Merino',
                    'min_required_strength': self.config.SIGNALS['min_strength_for_trade'],
                    'philosophy': merino_methodology.PHILOSOPHY['discipline'],
                    'recommendation': 'PRESERVAR CAPITAL - No forzar operaciones'
                }
            
            return calculation
            
        except Exception as e:
            logger.error(f"❌ Error calculando riesgo Merino: {e}")
            return {'error': str(e), 'can_trade': False}
    
    def _get_risk_recommendation(self, signal_strength: int, risk_pct: float) -> str:
        """Genera recomendación de riesgo"""
        if signal_strength >= 80 and risk_pct <= 1.0:
            return "EXCELENTE - Setup de muy alta probabilidad"
        elif signal_strength >= 70 and risk_pct <= 1.5:
            return "MUY BUENO - Setup sólido según Merino"
        elif signal_strength >= 60 and risk_pct <= 2.0:
            return "BUENO - Setup aceptable con gestión estricta"
        elif signal_strength >= 50:
            return "MODERADO - Considerar reducir tamaño"
        else:
            return "RECHAZAR - No cumple criterios Merino"
    
    def broadcast_merino_analysis(self, symbol: str, analysis_data: dict):
        """
        Envía actualización de análisis Merino a todos los clientes
        
        Args:
            symbol: Símbolo actualizado
            analysis_data: Datos del análisis
        """
        try:
            if self.connected_clients:
                # Limpiar datos
                clean_data = self._clean_merino_analysis(analysis_data.copy())
                
                # Determinar si es señal de alta probabilidad
                signal_strength = clean_data.get('signal', {}).get('signal_strength', 0)
                is_high_probability = signal_strength >= self.config.SIGNALS['min_strength_for_trade']
                
                broadcast_data = {
                    'methodology': 'JAIME_MERINO',
                    'symbol': symbol,
                    'data': clean_data,
                    'timestamp': time.time(),
                    'broadcast': True,
                    'high_probability': is_high_probability
                }
                
                # Agregar nota filosófica para señales importantes
                if is_high_probability:
                    broadcast_data['philosophy_note'] = merino_methodology.PHILOSOPHY['discipline']
                    broadcast_data['alert_level'] = 'HIGH'
                
                self.socketio.emit('merino_analysis_update', broadcast_data)
                
                # Actualizar cache
                self.merino_analysis_cache[symbol] = clean_data
                
                # Log diferenciado
                if is_high_probability:
                    logger.info(f"📡🎯 BROADCAST ALTA PROBABILIDAD: {symbol} - {clean_data.get('signal', {}).get('signal', 'UNKNOWN')} ({signal_strength}%) a {len(self.connected_clients)} clientes")
                else:
                    logger.info(f"📡 Análisis Merino broadcast: {symbol} ({signal_strength}%) a {len(self.connected_clients)} clientes")
            else:
                logger.debug(f"📭 No hay clientes para broadcast Merino de {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Error en broadcast Merino para {symbol}: {e}")
    
    def cache_merino_analysis(self, symbol: str, analysis_data):
        """
        Cachea análisis Merino con mejor manejo de tipos
        
        Args:
            symbol: Símbolo
            analysis_data: Datos del análisis (puede ser dict o string)
        """
        try:
            # Verificar si analysis_data es un diccionario válido
            if isinstance(analysis_data, dict):
                clean_data = self._clean_merino_analysis(analysis_data.copy())
                self.merino_analysis_cache[symbol] = clean_data
                
                signal_strength = clean_data.get('signal', {}).get('signal_strength', 0)
                if signal_strength >= 50:  # Usar threshold fijo si no hay config
                    logger.info(f"💾🎯 Análisis alta probabilidad cacheado: {symbol} ({signal_strength}%)")
                else:
                    logger.debug(f"💾 Análisis Merino cacheado: {symbol} ({signal_strength}%)")
            
            elif isinstance(analysis_data, str):
                # Si es string, crear estructura básica
                logger.warning(f"⚠️ Análisis recibido como string para {symbol}, creando estructura básica")
                basic_structure = {
                    'symbol': symbol,
                    'analysis_text': analysis_data,
                    'timestamp': time.time(),
                    'signal': {
                        'signal': 'UNKNOWN',
                        'signal_strength': 0,
                        'bias': 'NEUTRAL'
                    }
                }
                self.merino_analysis_cache[symbol] = basic_structure
                
            else:
                logger.error(f"❌ Tipo de datos inválido para caché de {symbol}: {type(analysis_data)}")
                
        except Exception as e:
            logger.error(f"❌ Error cacheando análisis Merino para {symbol}: {e}")
    def clear_merino_analysis_cache(self):
        """Limpia el cache de análisis Merino"""
        cache_size = len(self.merino_analysis_cache)
        self.merino_analysis_cache.clear()
        logger.info(f"🗑️ Cache análisis Merino limpiado ({cache_size} elementos)")
    
    def get_connected_clients_count(self) -> int:
        """Retorna el número de clientes conectados"""
        return len(self.connected_clients)
    
    def get_high_probability_signals_count(self) -> int:
        """Retorna el número de señales de alta probabilidad en cache"""
        count = 0
        for analysis in self.merino_analysis_cache.values():
            signal_strength = analysis.get('signal', {}).get('signal_strength', 0)
            if signal_strength >= self.config.SIGNALS['min_strength_for_trade']:
                count += 1
        return count
    
    def send_philosophy_reminder(self):
        """Envía recordatorio de filosofía Merino a todos los clientes"""
        try:
            if self.connected_clients:
                philosophy_reminder = {
                    'methodology': 'JAIME_MERINO',
                    'type': 'philosophy_reminder',
                    'message': merino_methodology.PHILOSOPHY['risk_motto'],
                    'discipline': merino_methodology.PHILOSOPHY['discipline'],
                    'contrarian': merino_methodology.PHILOSOPHY['contrarian'],
                    'timestamp': time.time()
                }
                
                self.socketio.emit('philosophy_reminder', philosophy_reminder)
                logger.info(f"💡 Recordatorio filosófico Merino enviado a {len(self.connected_clients)} clientes")
                
        except Exception as e:
            logger.error(f"❌ Error enviando recordatorio filosófico: {e}")
    
    def send_market_alert(self, alert_type: str, message: str, data: dict = None):
        """
        Envía alerta de mercado a todos los clientes
        
        Args:
            alert_type: Tipo de alerta
            message: Mensaje de la alerta
            data: Datos adicionales
        """
        try:
            if self.connected_clients:
                alert = {
                    'methodology': 'JAIME_MERINO',
                    'type': 'market_alert',
                    'alert_type': alert_type,
                    'message': message,
                    'data': data or {},
                    'philosophy': merino_methodology.PHILOSOPHY['discipline'],
                    'timestamp': time.time()
                }
                
                self.socketio.emit('market_alert', alert)
                logger.info(f"🚨 Alerta de mercado Merino: {alert_type} - {message}")
                
        except Exception as e:
            logger.error(f"❌ Error enviando alerta de mercado: {e}")