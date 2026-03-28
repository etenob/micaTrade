"""
Indicadores técnicos para análisis de trading
"""
import pandas as pd
import numpy as np
from typing import Optional, Tuple
import ta
from models.trading_analysis import TechnicalIndicators
from utils.logger import analysis_logger

logger = analysis_logger

class TechnicalIndicatorsCalculator:
    """
    Calculadora de indicadores técnicos
    """
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """
        Calcula la Media Móvil Exponencial (EMA)
        
        Args:
            data: Serie de precios
            period: Período para el cálculo
            
        Returns:
            Serie con valores EMA
        """
        try:
            ema = data.ewm(span=period, adjust=False).mean()
            logger.debug(f"✅ EMA {period} calculada")
            return ema
        except Exception as e:
            logger.error(f"❌ Error calculando EMA {period}: {e}")
            return pd.Series([np.nan] * len(data), index=data.index)
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """
        Calcula la Media Móvil Simple (SMA)
        
        Args:
            data: Serie de precios
            period: Período para el cálculo
            
        Returns:
            Serie con valores SMA
        """
        try:
            sma = data.rolling(window=period).mean()
            logger.debug(f"✅ SMA {period} calculada")
            return sma
        except Exception as e:
            logger.error(f"❌ Error calculando SMA {period}: {e}")
            return pd.Series([np.nan] * len(data), index=data.index)
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calcula el Índice de Fuerza Relativa (RSI)
        
        Args:
            data: Serie de precios de cierre
            period: Período para el cálculo (default: 14)
            
        Returns:
            Serie con valores RSI
        """
        try:
            rsi = ta.momentum.RSIIndicator(close=data, window=period).rsi()
            logger.debug(f"✅ RSI {period} calculado")
            return rsi
        except Exception as e:
            logger.error(f"❌ Error calculando RSI: {e}")
            return pd.Series([np.nan] * len(data), index=data.index)
    
    @staticmethod
    def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calcula el Average Directional Index (ADX)
        
        Args:
            high: Serie de precios máximos
            low: Serie de precios mínimos  
            close: Serie de precios de cierre
            period: Período para el cálculo (default: 14)
            
        Returns:
            Serie con valores ADX
        """
        try:
            adx = ta.trend.ADXIndicator(high=high, low=low, close=close, window=period).adx()
            logger.debug(f"✅ ADX {period} calculado")
            return adx
        except Exception as e:
            logger.error(f"❌ Error calculando ADX: {e}")
            return pd.Series([np.nan] * len(close), index=close.index)
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcula MACD (Moving Average Convergence Divergence)
        
        Args:
            data: Serie de precios de cierre
            fast: Período EMA rápida (default: 12)
            slow: Período EMA lenta (default: 26)
            signal: Período para línea de señal (default: 9)
            
        Returns:
            Tupla (MACD line, Signal line, Histogram)
        """
        try:
            macd_indicator = ta.trend.MACD(close=data, window_fast=fast, window_slow=slow, window_sign=signal)
            macd_line = macd_indicator.macd()
            signal_line = macd_indicator.macd_signal()
            histogram = macd_indicator.macd_diff()
            
            logger.debug("✅ MACD calculado")
            return macd_line, signal_line, histogram
        except Exception as e:
            logger.error(f"❌ Error calculando MACD: {e}")
            empty_series = pd.Series([np.nan] * len(data), index=data.index)
            return empty_series, empty_series, empty_series
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calcula las Bandas de Bollinger
        
        Args:
            data: Serie de precios de cierre
            period: Período para SMA (default: 20)
            std_dev: Desviaciones estándar (default: 2)
            
        Returns:
            Tupla (Upper band, Middle band, Lower band)
        """
        try:
            bb_indicator = ta.volatility.BollingerBands(close=data, window=period, window_dev=std_dev)
            upper = bb_indicator.bollinger_hband()
            middle = bb_indicator.bollinger_mavg()
            lower = bb_indicator.bollinger_lband()
            
            logger.debug(f"✅ Bandas de Bollinger calculadas (período: {period})")
            return upper, middle, lower
        except Exception as e:
            logger.error(f"❌ Error calculando Bandas de Bollinger: {e}")
            empty_series = pd.Series([np.nan] * len(data), index=data.index)
            return empty_series, empty_series, empty_series
    
    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                           k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Calcula el Oscilador Estocástico
        
        Args:
            high: Serie de precios máximos
            low: Serie de precios mínimos
            close: Serie de precios de cierre
            k_period: Período para %K (default: 14)
            d_period: Período para %D (default: 3)
            
        Returns:
            Tupla (%K, %D)
        """
        try:
            stoch_indicator = ta.momentum.StochasticOscillator(
                high=high, low=low, close=close, 
                window=k_period, smooth_window=d_period
            )
            k_percent = stoch_indicator.stoch()
            d_percent = stoch_indicator.stoch_signal()
            
            logger.debug("✅ Estocástico calculado")
            return k_percent, d_percent
        except Exception as e:
            logger.error(f"❌ Error calculando Estocástico: {e}")
            empty_series = pd.Series([np.nan] * len(close), index=close.index)
            return empty_series, empty_series
    
    @classmethod
    def calculate_all_indicators(cls, df: pd.DataFrame) -> TechnicalIndicators:
        """
        Calcula todos los indicadores técnicos para un DataFrame
        
        Args:
            df: DataFrame con columnas OHLCV
            
        Returns:
            TechnicalIndicators con todos los valores calculados
        """
        try:
            if len(df) < 55:  # Necesitamos suficientes datos
                logger.warning(f"⚠️ Insuficientes datos para indicadores: {len(df)} velas")
                return cls._get_empty_indicators()
            
            # Calcular EMAs
            ema_11 = cls.calculate_ema(df['close'], 11).iloc[-1]
            ema_55 = cls.calculate_ema(df['close'], 55).iloc[-1]
            
            # Calcular ADX
            adx = cls.calculate_adx(df['high'], df['low'], df['close'], 14).iloc[-1]
            
            # Calcular RSI
            rsi = cls.calculate_rsi(df['close'], 14).iloc[-1]
            
            # Calcular SMA 20
            sma_20 = cls.calculate_sma(df['close'], 20).iloc[-1]
            
            # Calcular Bandas de Bollinger
            bb_upper, bb_middle, bb_lower = cls.calculate_bollinger_bands(df['close'], 20, 2)
            
            # Calcular MACD
            macd_line, macd_signal, macd_hist = cls.calculate_macd(df['close'])
            
            indicators = TechnicalIndicators(
                ema_11=ema_11,
                ema_55=ema_55,
                adx=adx,
                rsi=rsi,
                sma_20=sma_20,
                bollinger_upper=bb_upper.iloc[-1] if not bb_upper.empty else None,
                bollinger_lower=bb_lower.iloc[-1] if not bb_lower.empty else None,
                macd=macd_line.iloc[-1] if not macd_line.empty else None,
                macd_signal=macd_signal.iloc[-1] if not macd_signal.empty else None
            )
            
            logger.debug("✅ Todos los indicadores calculados exitosamente")
            return indicators
            
        except Exception as e:
            logger.error(f"❌ Error calculando indicadores: {e}")
            return cls._get_empty_indicators()
    
    @staticmethod
    def _get_empty_indicators() -> TechnicalIndicators:
        """Retorna indicadores vacíos en caso de error"""
        return TechnicalIndicators(
            ema_11=0.0,
            ema_55=0.0,
            adx=0.0,
            rsi=50.0,  # RSI neutral
            sma_20=0.0,
            bollinger_upper=None,
            bollinger_lower=None,
            macd=None,
            macd_signal=None
        )

class SignalGenerator:
    """
    Generador de señales de trading basado en indicadores técnicos
    """
    
    @staticmethod
    def generate_ema_signal(ema_11: float, ema_55: float, price: float) -> Tuple[str, int]:
        """
        Genera señal basada en EMAs
        
        Args:
            ema_11: EMA de 11 períodos
            ema_55: EMA de 55 períodos
            price: Precio actual
            
        Returns:
            Tupla (señal, fuerza)
        """
        try:
            # Verificar valores válidos
            if any(pd.isna([ema_11, ema_55, price])) or any(x <= 0 for x in [ema_11, ema_55, price]):
                return 'NO_SIGNAL', 0
            
            # Calcular distancias relativas
            ema_diff_pct = ((ema_11 - ema_55) / ema_55) * 100
            price_from_ema11_pct = ((price - ema_11) / ema_11) * 100
            
            # Señal LONG: EMA11 > EMA55 y precio cerca o sobre EMA11
            if ema_11 > ema_55 and price >= ema_11 * 0.999:
                strength = min(95, max(20, int(abs(ema_diff_pct) * 20 + abs(price_from_ema11_pct) * 10)))
                return 'LONG', strength
            
            # Señal SHORT: EMA11 < EMA55 y precio cerca o bajo EMA11
            elif ema_11 < ema_55 and price <= ema_11 * 1.001:
                strength = min(95, max(20, int(abs(ema_diff_pct) * 20 + abs(price_from_ema11_pct) * 10)))
                return 'SHORT', strength
            
            # Zona de espera
            else:
                return 'WAIT', 30
                
        except Exception as e:
            logger.error(f"❌ Error generando señal EMA: {e}")
            return 'NO_SIGNAL', 0
    
    @staticmethod
    def determine_trend_bias(ema_11: float, ema_55: float, adx: float, rsi: float) -> str:
        """
        Determina el sesgo de tendencia general
        
        Args:
            ema_11: EMA de 11 períodos
            ema_55: EMA de 55 períodos
            adx: Valor ADX
            rsi: Valor RSI
            
        Returns:
            'BULLISH', 'BEARISH', o 'NEUTRAL'
        """
        try:
            # Verificar valores válidos
            if any(pd.isna([ema_11, ema_55, adx, rsi])):
                return 'NEUTRAL'
            
            # Criterios para tendencia alcista
            bullish_conditions = [
                ema_11 > ema_55,  # EMA11 sobre EMA55
                adx > 25,         # ADX indica tendencia fuerte
                rsi > 45,         # RSI no oversold
                rsi < 80          # RSI no overbought extremo
            ]
            
            # Criterios para tendencia bajista
            bearish_conditions = [
                ema_11 < ema_55,  # EMA11 bajo EMA55
                adx > 25,         # ADX indica tendencia fuerte  
                rsi < 55,         # RSI no overbought
                rsi > 20          # RSI no oversold extremo
            ]
            
            bullish_score = sum(bullish_conditions)
            bearish_score = sum(bearish_conditions)
            
            if bullish_score >= 3:
                return 'BULLISH'
            elif bearish_score >= 3:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            logger.error(f"❌ Error determinando sesgo de tendencia: {e}")
            return 'NEUTRAL'
    
    @staticmethod
    def calculate_signal_strength(signal: str, ema_11: float, ema_55: float, 
                                adx: float, rsi: float, price: float) -> int:
        """
        Calcula la fuerza de la señal basada en múltiples factores
        
        Args:
            signal: Señal generada
            ema_11: EMA de 11 períodos
            ema_55: EMA de 55 períodos
            adx: Valor ADX
            rsi: Valor RSI
            price: Precio actual
            
        Returns:
            Fuerza de la señal (0-100)
        """
        try:
            if signal == 'NO_SIGNAL':
                return 0
            
            strength = 0
            
            # Factor ADX (30 puntos máximo)
            if adx > 50:
                strength += 30
            elif adx > 35:
                strength += 20
            elif adx > 25:
                strength += 10
            
            # Factor EMA separation (25 puntos máximo)
            ema_diff_pct = abs((ema_11 - ema_55) / ema_55) * 100
            strength += min(25, int(ema_diff_pct * 25))
            
            # Factor RSI (25 puntos máximo)
            if signal == 'LONG' and 45 <= rsi <= 75:
                strength += int((75 - abs(rsi - 60)) / 15 * 25)
            elif signal == 'SHORT' and 25 <= rsi <= 55:
                strength += int((75 - abs(rsi - 40)) / 15 * 25)
            
            # Factor precio vs EMA (20 puntos máximo)
            price_ema_alignment = abs((price - ema_11) / ema_11) * 100
            if price_ema_alignment < 1:  # Precio muy cerca de EMA11
                strength += 20
            elif price_ema_alignment < 2:
                strength += 10
            
            return min(95, max(5, strength))
            
        except Exception as e:
            logger.error(f"❌ Error calculando fuerza de señal: {e}")
            return 25  # Fuerza por defecto

# Instancias globales
indicators_calculator = TechnicalIndicatorsCalculator()
signal_generator = SignalGenerator()