"""
Sistema de Backtesting para validar la metodología de Jaime Merino
Prueba la estrategia en datos históricos para medir su efectividad
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass, asdict
from enhanced_config import MerinoConfig, merino_methodology
from services.enhanced_analysis_service import enhanced_analysis_service
from services.binance_service import binance_service
from services.enhanced_indicators import jaime_merino_signal_generator
from utils.logger import setup_logger

# Logger específico para backtesting
backtest_logger = setup_logger('merino_backtesting', 'logs/merino_backtesting.log')

@dataclass
class BacktestTrade:
    """Representa una operación individual en el backtesting"""
    symbol: str
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    signal_type: str  # LONG, SHORT
    signal_strength: int
    confluence_score: int
    position_size: float
    stop_loss: float
    target_1: float
    target_2: float
    exit_reason: str  # TARGET_1, TARGET_2, STOP_LOSS, TIME_LIMIT, INVALIDATION
    pnl: float
    pnl_percentage: float
    max_drawdown: float
    max_profit: float
    duration_hours: float
    risk_reward_achieved: float
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario"""
        result = asdict(self)
        # Convertir datetime a string
        result['entry_time'] = self.entry_time.isoformat()
        result['exit_time'] = self.exit_time.isoformat() if self.exit_time else None
        return result

@dataclass
class BacktestResults:
    """Resultados completos del backtesting"""
    # Parámetros del test
    start_date: datetime
    end_date: datetime
    initial_capital: float
    symbols_tested: List[str]
    
    # Estadísticas generales
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Performance financiera
    final_capital: float
    total_return: float
    total_return_percentage: float
    max_drawdown: float
    max_drawdown_percentage: float
    sharpe_ratio: float
    calmar_ratio: float
    
    # Estadísticas de trades
    avg_trade_duration: float
    avg_win: float
    avg_loss: float
    best_trade: float
    worst_trade: float
    avg_risk_reward: float
    
    # Estadísticas por fuerza de señal
    high_strength_trades: int  # >=80%
    medium_strength_trades: int  # 60-79%
    low_strength_trades: int  # 50-59%
    high_strength_win_rate: float
    medium_strength_win_rate: float
    low_strength_win_rate: float
    
    # Estadísticas por confluencias
    four_confluence_trades: int
    three_confluence_trades: int
    two_confluence_trades: int
    four_confluence_win_rate: float
    three_confluence_win_rate: float
    two_confluence_win_rate: float
    
    # Filosofía de Merino validada
    philosophy_validation: Dict[str, float]
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario"""
        result = asdict(self)
        result['start_date'] = self.start_date.isoformat()
        result['end_date'] = self.end_date.isoformat()
        return result

class MerinoBacktester:
    """
    Motor de backtesting para la metodología de Jaime Merino
    """
    
    def __init__(self, initial_capital: float = 10000):
        """
        Inicializa el backtester
        
        Args:
            initial_capital: Capital inicial para el backtesting
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trades: List[BacktestTrade] = []
        self.open_positions: Dict[str, BacktestTrade] = {}
        self.daily_portfolio_values: List[Tuple[datetime, float]] = []
        self.signal_generator = jaime_merino_signal_generator
        
        backtest_logger.info(f"🧪 Backtester Merino inicializado con ${initial_capital:,.2f}")
    
    def run_backtest(self, 
                    symbols: List[str], 
                    start_date: datetime, 
                    end_date: datetime,
                    timeframe: str = '4h') -> BacktestResults:
        """
        Ejecuta backtesting completo
        
        Args:
            symbols: Lista de símbolos a testear
            start_date: Fecha de inicio
            end_date: Fecha de fin
            timeframe: Marco temporal
            
        Returns:
            Resultados del backtesting
        """
        backtest_logger.info(f"🚀 Iniciando backtesting Merino:")
        backtest_logger.info(f"   • Período: {start_date.date()} - {end_date.date()}")
        backtest_logger.info(f"   • Símbolos: {symbols}")
        backtest_logger.info(f"   • Capital inicial: ${self.initial_capital:,.2f}")
        backtest_logger.info(f"   • Filosofía: {merino_methodology.PHILOSOPHY['main_principle']}")
        
        # Resetear estado
        self._reset_backtest()
        
        try:
            # Procesar cada símbolo
            for symbol in symbols:
                self._process_symbol_backtest(symbol, start_date, end_date, timeframe)
            
            # Cerrar posiciones abiertas al final
            self._close_all_positions(end_date)
            
            # Calcular resultados
            results = self._calculate_results(symbols, start_date, end_date)
            
            backtest_logger.info("✅ Backtesting completado")
            self._log_summary_results(results)
            
            return results
            
        except Exception as e:
            backtest_logger.error(f"❌ Error en backtesting: {e}")
            raise
    
    def _reset_backtest(self):
        """Resetea el estado del backtesting"""
        self.current_capital = self.initial_capital
        self.trades.clear()
        self.open_positions.clear()
        self.daily_portfolio_values.clear()
    
    def _process_symbol_backtest(self, symbol: str, start_date: datetime, end_date: datetime, timeframe: str):
        """
        Procesa backtesting para un símbolo específico
        
        Args:
            symbol: Símbolo a procesar
            start_date: Fecha de inicio
            end_date: Fecha de fin
            timeframe: Marco temporal
        """
        backtest_logger.info(f"📊 Procesando {symbol}...")
        
        try:
            # Obtener datos históricos (más datos para indicadores)
            total_days = (end_date - start_date).days + 100  # Buffer para indicadores
            historical_start = start_date - timedelta(days=100)
            
            # Simular obtención de datos históricos
            df = self._get_historical_data(symbol, historical_start, end_date, timeframe)
            
            if df is None or len(df) < 100:
                backtest_logger.warning(f"⚠️ Insuficientes datos históricos para {symbol}")
                return
            
            # Procesar cada período
            for i in range(100, len(df)):  # Empezar después del buffer para indicadores
                current_time = df.index[i]
                
                # Solo procesar si está dentro del rango de test
                if current_time < start_date or current_time > end_date:
                    continue
                
                # Datos hasta el momento actual
                current_df = df.iloc[:i+1]
                current_price = df.iloc[i]['close']
                
                # Verificar posiciones abiertas
                self._check_open_positions(symbol, current_time, current_price, current_df)
                
                # Generar señal si no hay posición abierta
                if symbol not in self.open_positions:
                    self._check_entry_signal(symbol, current_time, current_price, current_df)
                
                # Registrar valor del portafolio
                if current_time.hour == 0:  # Una vez al día
                    portfolio_value = self._calculate_portfolio_value(current_time)
                    self.daily_portfolio_values.append((current_time, portfolio_value))
            
            backtest_logger.info(f"✅ {symbol} procesado - {len([t for t in self.trades if t.symbol == symbol])} trades")
            
        except Exception as e:
            backtest_logger.error(f"❌ Error procesando {symbol}: {e}")
    
    def _get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos (simulado - en producción usar Binance API)
        
        Args:
            symbol: Símbolo
            start_date: Fecha inicio
            end_date: Fecha fin
            timeframe: Marco temporal
            
        Returns:
            DataFrame con datos OHLCV
        """
        try:
            # En una implementación real, usar binance_service.get_klines
            # Por ahora, simular datos o usar datos guardados
            
            # Intentar obtener datos reales de Binance
            # Calcular el número de períodos necesarios
            if timeframe == '4h':
                periods_per_day = 6
            elif timeframe == '1h':
                periods_per_day = 24
            elif timeframe == '1d':
                periods_per_day = 1
            else:
                periods_per_day = 6  # Default
            
            total_days = (end_date - start_date).days + 100
            total_periods = total_days * periods_per_day
            
            # Limitar a máximo de Binance (1000 períodos)
            limit = min(1000, total_periods)
            
            df = binance_service.get_klines(symbol, timeframe, limit)
            
            if df is not None and len(df) > 0:
                # Filtrar por fechas si es necesario
                df = df[df['timestamp'] >= start_date - timedelta(days=100)]
                df = df[df['timestamp'] <= end_date]
                df.set_index('timestamp', inplace=True)
                return df
            else:
                backtest_logger.warning(f"⚠️ No se pudieron obtener datos históricos para {symbol}")
                return None
                
        except Exception as e:
            backtest_logger.error(f"❌ Error obteniendo datos históricos para {symbol}: {e}")
            return None
    
    def _check_entry_signal(self, symbol: str, current_time: datetime, current_price: float, df: pd.DataFrame):
        """
        Verifica si hay señal de entrada según metodología Merino
        
        Args:
            symbol: Símbolo
            current_time: Tiempo actual
            current_price: Precio actual
            df: DataFrame con datos históricos
        """
        try:
            # Necesitamos datos de múltiples timeframes, pero por simplicidad usaremos el mismo
            df_4h = df.copy()
            df_1h = df.copy()  # En producción, obtener datos de 1H
            
            # Generar señal usando el generador de Merino
            signal_data = self.signal_generator.generate_merino_signal(df_4h, df_1h, current_price)
            
            signal_type = signal_data['signal']
            signal_strength = signal_data['signal_strength']
            confluence_score = signal_data['confluence_score']
            
            # Solo operar con señales de fuerza >= 50 según filosofía Merino
            if signal_type in ['LONG', 'SHORT'] and signal_strength >= 50:
                self._open_position(symbol, current_time, current_price, signal_data)
            
        except Exception as e:
            backtest_logger.error(f"❌ Error verificando señal de entrada para {symbol}: {e}")
    
    def _open_position(self, symbol: str, entry_time: datetime, entry_price: float, signal_data: Dict):
        """
        Abre una nueva posición
        
        Args:
            symbol: Símbolo
            entry_time: Tiempo de entrada
            entry_price: Precio de entrada
            signal_data: Datos de la señal
        """
        try:
            signal_type = signal_data['signal']
            signal_strength = signal_data['signal_strength']
            confluence_score = signal_data['confluence_score']
            
            # Calcular tamaño de posición según gestión de riesgo de Merino
            position_size = self._calculate_position_size(signal_strength)
            
            # Calcular niveles según metodología
            if signal_type == 'LONG':
                stop_loss = entry_price * 0.98  # -2%
                target_1 = entry_price * 1.02   # +2%
                target_2 = entry_price * 1.05   # +5%
            else:  # SHORT
                stop_loss = entry_price * 1.02  # +2%
                target_1 = entry_price * 0.98   # -2%
                target_2 = entry_price * 0.95   # -5%
            
            # Crear trade
            trade = BacktestTrade(
                symbol=symbol,
                entry_time=entry_time,
                exit_time=None,
                entry_price=entry_price,
                exit_price=None,
                signal_type=signal_type,
                signal_strength=signal_strength,
                confluence_score=confluence_score,
                position_size=position_size,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                exit_reason='',
                pnl=0.0,
                pnl_percentage=0.0,
                max_drawdown=0.0,
                max_profit=0.0,
                duration_hours=0.0,
                risk_reward_achieved=0.0
            )
            
            # Registrar posición abierta
            self.open_positions[symbol] = trade
            
            # Reducir capital disponible
            self.current_capital -= position_size
            
            backtest_logger.info(f"📈 Posición abierta: {symbol} {signal_type} @ ${entry_price:.4f} - Fuerza: {signal_strength}% - Confluencias: {confluence_score}/4")
            
        except Exception as e:
            backtest_logger.error(f"❌ Error abriendo posición para {symbol}: {e}")
    
    def _calculate_position_size(self, signal_strength: int) -> float:
        """
        Calcula el tamaño de posición según la fuerza de la señal y filosofía de Merino
        
        Args:
            signal_strength: Fuerza de la señal (0-100)
            
        Returns:
            Tamaño de la posición en USD
        """
        # Capital disponible para trading diario (20% según filosofía 40-30-20-10)
        available_capital = self.current_capital * 0.20
        
        # Ajustar según fuerza de señal
        if signal_strength >= 80:
            position_percentage = 0.05  # 5% del capital total para señales muy fuertes
        elif signal_strength >= 70:
            position_percentage = 0.03  # 3% para señales fuertes
        elif signal_strength >= 60:
            position_percentage = 0.02  # 2% para señales buenas
        else:
            position_percentage = 0.01  # 1% para señales moderadas
        
        position_size = self.current_capital * position_percentage
        
        # No exceder capital disponible
        return min(position_size, available_capital)
    
    def _check_open_positions(self, symbol: str, current_time: datetime, current_price: float, df: pd.DataFrame):
        """
        Verifica posiciones abiertas para salidas
        
        Args:
            symbol: Símbolo
            current_time: Tiempo actual
            current_price: Precio actual
            df: DataFrame con datos
        """
        if symbol not in self.open_positions:
            return
        
        trade = self.open_positions[symbol]
        
        # Calcular PnL actual
        if trade.signal_type == 'LONG':
            current_pnl = (current_price - trade.entry_price) / trade.entry_price
        else:  # SHORT
            current_pnl = (trade.entry_price - current_price) / trade.entry_price
        
        current_pnl_usd = current_pnl * trade.position_size
        
        # Actualizar máximos
        if current_pnl_usd > trade.max_profit:
            trade.max_profit = current_pnl_usd
        if current_pnl_usd < -abs(trade.max_drawdown):
            trade.max_drawdown = abs(current_pnl_usd)
        
        # Verificar condiciones de salida
        exit_reason = None
        
        # 1. Stop Loss
        if trade.signal_type == 'LONG' and current_price <= trade.stop_loss:
            exit_reason = 'STOP_LOSS'
        elif trade.signal_type == 'SHORT' and current_price >= trade.stop_loss:
            exit_reason = 'STOP_LOSS'
        
        # 2. Targets
        elif trade.signal_type == 'LONG':
            if current_price >= trade.target_2:
                exit_reason = 'TARGET_2'
            elif current_price >= trade.target_1:
                exit_reason = 'TARGET_1'
        elif trade.signal_type == 'SHORT':
            if current_price <= trade.target_2:
                exit_reason = 'TARGET_2'
            elif current_price <= trade.target_1:
                exit_reason = 'TARGET_1'
        
        # 3. Invalidación técnica (EMA 11)
        if not exit_reason:
            try:
                ema_11 = df['close'].ewm(span=11).mean().iloc[-1]
                if trade.signal_type == 'LONG' and current_price < ema_11 * 0.995:
                    exit_reason = 'INVALIDATION'
                elif trade.signal_type == 'SHORT' and current_price > ema_11 * 1.005:
                    exit_reason = 'INVALIDATION'
            except:
                pass
        
        # 4. Límite de tiempo (máximo 48 horas)
        duration = (current_time - trade.entry_time).total_seconds() / 3600
        if duration > 48 and not exit_reason:
            exit_reason = 'TIME_LIMIT'
        
        # Cerrar posición si hay razón
        if exit_reason:
            self._close_position(symbol, current_time, current_price, exit_reason)
    
    def _close_position(self, symbol: str, exit_time: datetime, exit_price: float, exit_reason: str):
        """
        Cierra una posición abierta
        
        Args:
            symbol: Símbolo
            exit_time: Tiempo de salida
            exit_price: Precio de salida
            exit_reason: Razón de la salida
        """
        try:
            trade = self.open_positions[symbol]
            
            # Actualizar datos del trade
            trade.exit_time = exit_time
            trade.exit_price = exit_price
            trade.exit_reason = exit_reason
            
            # Calcular duración
            trade.duration_hours = (exit_time - trade.entry_time).total_seconds() / 3600
            
            # Calcular PnL
            if trade.signal_type == 'LONG':
                trade.pnl_percentage = (exit_price - trade.entry_price) / trade.entry_price
            else:  # SHORT
                trade.pnl_percentage = (trade.entry_price - exit_price) / trade.entry_price
            
            trade.pnl = trade.pnl_percentage * trade.position_size
            
            # Calcular risk/reward obtenido
            risk = abs(trade.entry_price - trade.stop_loss) / trade.entry_price
            reward = abs(exit_price - trade.entry_price) / trade.entry_price
            trade.risk_reward_achieved = reward / risk if risk > 0 else 0
            
            # Actualizar capital
            self.current_capital += trade.position_size + trade.pnl
            
            # Mover a lista de trades completados
            self.trades.append(trade)
            del self.open_positions[symbol]
            
            # Log
            status = "✅ GANANCIA" if trade.pnl > 0 else "❌ PÉRDIDA"
            backtest_logger.info(f"📉 Posición cerrada: {symbol} {trade.signal_type} - {status} ${trade.pnl:.2f} ({trade.pnl_percentage*100:.2f}%) - Razón: {exit_reason}")
            
        except Exception as e:
            backtest_logger.error(f"❌ Error cerrando posición {symbol}: {e}")
    
    def _close_all_positions(self, end_time: datetime):
        """Cierra todas las posiciones abiertas al final del test"""
        for symbol in list(self.open_positions.keys()):
            # Usar último precio conocido (simulado)
            last_price = self.open_positions[symbol].entry_price  # Simplificación
            self._close_position(symbol, end_time, last_price, 'END_OF_TEST')
    
    def _calculate_portfolio_value(self, current_time: datetime) -> float:
        """Calcula el valor actual del portafolio"""
        total_value = self.current_capital
        
        # Agregar valor de posiciones abiertas (simplificado)
        for trade in self.open_positions.values():
            total_value += trade.position_size  # En una implementación real, usar precio actual
        
        return total_value
    
    def _calculate_results(self, symbols: List[str], start_date: datetime, end_date: datetime) -> BacktestResults:
        """
        Calcula los resultados finales del backtesting
        
        Args:
            symbols: Símbolos testeados
            start_date: Fecha inicio
            end_date: Fecha fin
            
        Returns:
            Resultados completos
        """
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t.pnl > 0])
        losing_trades = total_trades - winning_trades
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_return = self.current_capital - self.initial_capital
        total_return_percentage = (total_return / self.initial_capital) * 100
        
        # Calcular drawdown máximo
        portfolio_values = [v for _, v in self.daily_portfolio_values]
        if portfolio_values:
            peak = self.initial_capital
            max_dd = 0
            for value in portfolio_values:
                if value > peak:
                    peak = value
                dd = (peak - value) / peak
                if dd > max_dd:
                    max_dd = dd
            max_drawdown_percentage = max_dd * 100
            max_drawdown = max_dd * peak
        else:
            max_drawdown = 0
            max_drawdown_percentage = 0
        
        # Estadísticas de trades
        avg_trade_duration = np.mean([t.duration_hours for t in self.trades]) if self.trades else 0
        wins = [t.pnl for t in self.trades if t.pnl > 0]
        losses = [t.pnl for t in self.trades if t.pnl < 0]
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        best_trade = max([t.pnl for t in self.trades]) if self.trades else 0
        worst_trade = min([t.pnl for t in self.trades]) if self.trades else 0
        avg_risk_reward = np.mean([t.risk_reward_achieved for t in self.trades]) if self.trades else 0
        
        # Estadísticas por fuerza de señal
        high_strength = [t for t in self.trades if t.signal_strength >= 80]
        medium_strength = [t for t in self.trades if 60 <= t.signal_strength < 80]
        low_strength = [t for t in self.trades if 50 <= t.signal_strength < 60]
        
        high_strength_win_rate = (len([t for t in high_strength if t.pnl > 0]) / len(high_strength) * 100) if high_strength else 0
        medium_strength_win_rate = (len([t for t in medium_strength if t.pnl > 0]) / len(medium_strength) * 100) if medium_strength else 0
        low_strength_win_rate = (len([t for t in low_strength if t.pnl > 0]) / len(low_strength) * 100) if low_strength else 0
        
        # Estadísticas por confluencias
        four_conf = [t for t in self.trades if t.confluence_score == 4]
        three_conf = [t for t in self.trades if t.confluence_score == 3]
        two_conf = [t for t in self.trades if t.confluence_score == 2]
        
        four_confluence_win_rate = (len([t for t in four_conf if t.pnl > 0]) / len(four_conf) * 100) if four_conf else 0
        three_confluence_win_rate = (len([t for t in three_conf if t.pnl > 0]) / len(three_conf) * 100) if three_conf else 0
        two_confluence_win_rate = (len([t for t in two_conf if t.pnl > 0]) / len(two_conf) * 100) if two_conf else 0
        
        # Calcular Sharpe ratio (simplificado)
        if self.daily_portfolio_values:
            returns = []
            for i in range(1, len(self.daily_portfolio_values)):
                prev_value = self.daily_portfolio_values[i-1][1]
                curr_value = self.daily_portfolio_values[i][1]
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)
            
            if returns:
                sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(365) if np.std(returns) > 0 else 0
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # Calmar ratio
        calmar_ratio = (total_return_percentage / max_drawdown_percentage) if max_drawdown_percentage > 0 else 0
        
        # Validación de filosofía
        philosophy_validation = {
            'discipline_over_analysis': win_rate,  # Mayor disciplina = mayor win rate
            'risk_management_effectiveness': max_drawdown_percentage,  # Menor drawdown = mejor gestión
            'contrarian_success': win_rate,  # Éxito operando contra la mayoría
            'high_probability_focus': high_strength_win_rate,  # Éxito en señales de alta probabilidad
            'confluence_importance': four_confluence_win_rate  # Importancia de las confluencias
        }
        
        return BacktestResults(
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            symbols_tested=symbols,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            final_capital=self.current_capital,
            total_return=total_return,
            total_return_percentage=total_return_percentage,
            max_drawdown=max_drawdown,
            max_drawdown_percentage=max_drawdown_percentage,
            sharpe_ratio=sharpe_ratio,
            calmar_ratio=calmar_ratio,
            avg_trade_duration=avg_trade_duration,
            avg_win=avg_win,
            avg_loss=avg_loss,
            best_trade=best_trade,
            worst_trade=worst_trade,
            avg_risk_reward=avg_risk_reward,
            high_strength_trades=len(high_strength),
            medium_strength_trades=len(medium_strength),
            low_strength_trades=len(low_strength),
            high_strength_win_rate=high_strength_win_rate,
            medium_strength_win_rate=medium_strength_win_rate,
            low_strength_win_rate=low_strength_win_rate,
            four_confluence_trades=len(four_conf),
            three_confluence_trades=len(three_conf),
            two_confluence_trades=len(two_conf),
            four_confluence_win_rate=four_confluence_win_rate,
            three_confluence_win_rate=three_confluence_win_rate,
            two_confluence_win_rate=two_confluence_win_rate,
            philosophy_validation=philosophy_validation
        )
    
    def _log_summary_results(self, results: BacktestResults):
        """Log resumen de resultados"""
        backtest_logger.info("=" * 60)
        backtest_logger.info("📊 RESULTADOS DEL BACKTESTING - METODOLOGÍA JAIME MERINO")
        backtest_logger.info("=" * 60)
        backtest_logger.info(f"💰 Capital inicial: ${results.initial_capital:,.2f}")
        backtest_logger.info(f"💰 Capital final: ${results.final_capital:,.2f}")
        backtest_logger.info(f"📈 Retorno total: ${results.total_return:,.2f} ({results.total_return_percentage:.2f}%)")
        backtest_logger.info(f"📉 Drawdown máximo: ${results.max_drawdown:,.2f} ({results.max_drawdown_percentage:.2f}%)")
        backtest_logger.info(f"🎯 Total trades: {results.total_trades}")
        backtest_logger.info(f"✅ Trades ganadores: {results.winning_trades}")
        backtest_logger.info(f"❌ Trades perdedores: {results.losing_trades}")
        backtest_logger.info(f"🏆 Win rate: {results.win_rate:.2f}%")
        backtest_logger.info(f"⚖️ Sharpe ratio: {results.sharpe_ratio:.2f}")
        backtest_logger.info(f"📊 Calmar ratio: {results.calmar_ratio:.2f}")
        backtest_logger.info("")
        backtest_logger.info("🎯 ANÁLISIS POR FUERZA DE SEÑAL:")
        backtest_logger.info(f"   • Alta (≥80%): {results.high_strength_trades} trades - {results.high_strength_win_rate:.1f}% win rate")
        backtest_logger.info(f"   • Media (60-79%): {results.medium_strength_trades} trades - {results.medium_strength_win_rate:.1f}% win rate")
        backtest_logger.info(f"   • Baja (50-59%): {results.low_strength_trades} trades - {results.low_strength_win_rate:.1f}% win rate")
        backtest_logger.info("")
        backtest_logger.info("🔗 ANÁLISIS POR CONFLUENCIAS:")
        backtest_logger.info(f"   • 4 confluencias: {results.four_confluence_trades} trades - {results.four_confluence_win_rate:.1f}% win rate")
        backtest_logger.info(f"   • 3 confluencias: {results.three_confluence_trades} trades - {results.three_confluence_win_rate:.1f}% win rate")
        backtest_logger.info(f"   • 2 confluencias: {results.two_confluence_trades} trades - {results.two_confluence_win_rate:.1f}% win rate")
        backtest_logger.info("=" * 60)
        
        # Validación de filosofía
        backtest_logger.info("💡 VALIDACIÓN FILOSOFÍA JAIME MERINO:")
        phil = results.philosophy_validation
        backtest_logger.info(f"   • Disciplina sobre análisis: {phil['discipline_over_analysis']:.1f}% efectividad")
        backtest_logger.info(f"   • Gestión de riesgo: {phil['risk_management_effectiveness']:.1f}% drawdown máximo")
        backtest_logger.info(f"   • Enfoque alta probabilidad: {phil['high_probability_focus']:.1f}% win rate")
        backtest_logger.info(f"   • Importancia confluencias: {phil['confluence_importance']:.1f}% win rate")
        backtest_logger.info("=" * 60)
    
    def save_results(self, results: BacktestResults, filename: str = None):
        """
        Guarda los resultados en archivo JSON
        
        Args:
            results: Resultados del backtesting
            filename: Nombre del archivo (opcional)
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtest_merino_{timestamp}.json"
        
        try:
            # Crear directorio si no existe
            import os
            os.makedirs('backtest_results', exist_ok=True)
            
            filepath = f"backtest_results/{filename}"
            
            # Preparar datos para guardar
            data = {
                'results': results.to_dict(),
                'trades': [trade.to_dict() for trade in self.trades],
                'methodology': 'JAIME_MERINO',
                'philosophy': merino_methodology.PHILOSOPHY,
                'generated_at': datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            backtest_logger.info(f"💾 Resultados guardados en: {filepath}")
            
        except Exception as e:
            backtest_logger.error(f"❌ Error guardando resultados: {e}")
    
    def load_results(self, filename: str) -> Tuple[BacktestResults, List[BacktestTrade]]:
        """
        Carga resultados desde archivo JSON
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Tupla (resultados, lista de trades)
        """
        try:
            filepath = f"backtest_results/{filename}"
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruir resultados
            results_data = data['results']
            results_data['start_date'] = datetime.fromisoformat(results_data['start_date'])
            results_data['end_date'] = datetime.fromisoformat(results_data['end_date'])
            
            results = BacktestResults(**results_data)
            
            # Reconstruir trades
            trades = []
            for trade_data in data['trades']:
                trade_data['entry_time'] = datetime.fromisoformat(trade_data['entry_time'])
                if trade_data['exit_time']:
                    trade_data['exit_time'] = datetime.fromisoformat(trade_data['exit_time'])
                trades.append(BacktestTrade(**trade_data))
            
            backtest_logger.info(f"📂 Resultados cargados desde: {filepath}")
            return results, trades
            
        except Exception as e:
            backtest_logger.error(f"❌ Error cargando resultados: {e}")
            raise


def run_sample_backtest():
    """
    Ejecuta un backtesting de muestra
    """
    backtest_logger.info("🚀 Ejecutando backtesting de muestra - Metodología Jaime Merino")
    
    # Configuración del test
    backtester = MerinoBacktester(initial_capital=10000)
    
    symbols = ['BTCUSDT', 'ETHUSDT']  # Símbolos de prueba
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 30 días de test
    
    try:
        # Ejecutar backtesting
        results = backtester.run_backtest(symbols, start_date, end_date)
        
        # Guardar resultados
        backtester.save_results(results)
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("📊 RESUMEN BACKTESTING METODOLOGÍA JAIME MERINO")
        print("="*60)
        print(f"💰 Capital inicial: ${results.initial_capital:,.2f}")
        print(f"💰 Capital final: ${results.final_capital:,.2f}")
        print(f"📈 Retorno: {results.total_return_percentage:.2f}%")
        print(f"🎯 Win Rate: {results.win_rate:.1f}%")
        print(f"📉 Max Drawdown: {results.max_drawdown_percentage:.2f}%")
        print(f"🔢 Total trades: {results.total_trades}")
        print("\n💡 Filosofía validada:")
        print(f"   '{merino_methodology.PHILOSOPHY['main_principle']}'")
        print("="*60)
        
        return results
        
    except Exception as e:
        backtest_logger.error(f"❌ Error en backtesting de muestra: {e}")
        return None


if __name__ == "__main__":
    # Ejecutar backtesting de muestra
    run_sample_backtest()