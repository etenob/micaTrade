"""
Indicadores técnicos mejorados siguiendo la metodología de Jaime Merino
Incluye: Squeeze Momentum, Volume Profile, ADX modificado
"""
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict
import ta
from models.trading_analysis import TechnicalIndicators
from utils.logger import analysis_logger

logger = analysis_logger

class JaimeMerinoIndicators:
    """
    Calculadora de indicadores específicos de la metodología Jaime Merino
    """
    
    @staticmethod
    def calculate_squeeze_momentum(df: pd.DataFrame, bb_length: int = 20, 
                                 kc_length: int = 20, kc_mult: float = 1.5) -> pd.Series:
        """
        Calcula el Squeeze Momentum Indicator (LazyBear version)
        Identifica períodos de baja volatilidad seguidos por movimientos explosivos
        
        Args:
            df: DataFrame con datos OHLCV
            bb_length: Período para Bollinger Bands
            kc_length: Período para Keltner Channels
            kc_mult: Multiplicador para Keltner Channels
            
        Returns:
            Serie con valores del Squeeze Momentum
        """
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # Bollinger Bands
            bb_basis = close.rolling(window=bb_length).mean()
            bb_dev = kc_mult * close.rolling(window=bb_length).std()
            bb_upper = bb_basis + bb_dev
            bb_lower = bb_basis - bb_dev
            
            # Keltner Channels
            kc_basis = close.rolling(window=kc_length).mean()
            tr = pd.concat([
                high - low,
                abs(high - close.shift(1)),
                abs(low - close.shift(1))
            ], axis=1).max(axis=1)
            
            kc_range = tr.rolling(window=kc_length).mean() * kc_mult
            kc_upper = kc_basis + kc_range
            kc_lower = kc_basis - kc_range
            
            # Squeeze detection
            squeeze_on = (bb_lower > kc_lower) & (bb_upper < kc_upper)
            squeeze_off = (bb_lower < kc_lower) | (bb_upper > kc_upper)
            
            # Momentum calculation
            highest = high.rolling(window=kc_length).max()
            lowest = low.rolling(window=kc_length).min()
            m1 = (highest + lowest) / 2
            momentum = close - ((m1 + kc_basis) / 2)
            
            logger.debug("✅ Squeeze Momentum calculado")
            return momentum, squeeze_on, squeeze_off
            
        except Exception as e:
            logger.error(f"❌ Error calculando Squeeze Momentum: {e}")
            empty_series = pd.Series([np.nan] * len(df), index=df.index)
            return empty_series, empty_series, empty_series
    
    @staticmethod
    def calculate_volume_profile_vpoc(df: pd.DataFrame, lookback: int = 100) -> Dict:
        """
        Calcula el Volume Point of Control (VPoC) y niveles de volumen
        Aproximación simplificada del Volume Profile
        
        Args:
            df: DataFrame con datos OHLCV
            lookback: Número de períodos para calcular
            
        Returns:
            Diccionario con niveles de volumen importantes
        """
        try:
            if len(df) < lookback:
                lookback = len(df)
            
            recent_df = df.tail(lookback).copy()
            
            # Crear bins de precio
            price_min = recent_df['low'].min()
            price_max = recent_df['high'].max()
            num_bins = min(50, lookback // 2)  # Número de bins adaptativo
            
            price_bins = np.linspace(price_min, price_max, num_bins)
            volume_profile = np.zeros(len(price_bins) - 1)
            
            # Distribuir volumen en bins
            for i, row in recent_df.iterrows():
                # Precio típico del período
                typical_price = (row['high'] + row['low'] + row['close']) / 3
                
                # Encontrar bin correspondiente
                bin_idx = np.digitize(typical_price, price_bins) - 1
                bin_idx = max(0, min(bin_idx, len(volume_profile) - 1))
                
                # Asignar volumen
                volume_profile[bin_idx] += row['volume']
            
            # Encontrar VPoC (precio con mayor volumen)
            vpoc_idx = np.argmax(volume_profile)
            vpoc_price = (price_bins[vpoc_idx] + price_bins[vpoc_idx + 1]) / 2
            
            # Niveles de soporte y resistencia basados en volumen
            sorted_indices = np.argsort(volume_profile)[::-1]  # Ordenar por volumen desc
            
            high_volume_levels = []
            for i in range(min(5, len(sorted_indices))):  # Top 5 niveles
                idx = sorted_indices[i]
                level_price = (price_bins[idx] + price_bins[idx + 1]) / 2
                level_volume = volume_profile[idx]
                high_volume_levels.append({
                    'price': level_price,
                    'volume': level_volume,
                    'type': 'vpoc' if i == 0 else 'high_volume'
                })
            
            result = {
                'vpoc': vpoc_price,
                'high_volume_levels': high_volume_levels,
                'current_price': df['close'].iloc[-1],
                'vpoc_distance_pct': ((df['close'].iloc[-1] - vpoc_price) / vpoc_price) * 100
            }
            
            logger.debug(f"✅ Volume Profile calculado - VPoC: ${vpoc_price:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculando Volume Profile: {e}")
            return {
                'vpoc': df['close'].iloc[-1] if len(df) > 0 else 0,
                'high_volume_levels': [],
                'current_price': df['close'].iloc[-1] if len(df) > 0 else 0,
                'vpoc_distance_pct': 0
            }
    
    @staticmethod
    def calculate_modified_adx(high: pd.Series, low: pd.Series, close: pd.Series, 
                             period: int = 14) -> Dict:
        """
        Calcula ADX modificado según la configuración de Jaime Merino
        Con punto 23 como punto 0 para facilitar lectura
        
        Args:
            high, low, close: Series de precios
            period: Período para el cálculo
            
        Returns:
            Diccionario con ADX y valores modificados
        """
        try:
            # ADX tradicional
            adx_indicator = ta.trend.ADXIndicator(high=high, low=low, close=close, window=period)
            adx = adx_indicator.adx()
            adx_pos = adx_indicator.adx_pos()
            adx_neg = adx_indicator.adx_neg()
            
            # Modificación de Merino: punto 23 como 0
            adx_modified = adx - 23
            
            # Clasificación de fuerza de tendencia según Merino
            current_adx = adx.iloc[-1] if not adx.empty else 0
            current_adx_mod = adx_modified.iloc[-1] if not adx_modified.empty else -23
            
            if current_adx > 50:
                strength = "MUY_FUERTE"
            elif current_adx > 35:
                strength = "FUERTE"
            elif current_adx > 25:
                strength = "MODERADA"
            else:
                strength = "DEBIL"
            
            # Pendiente del ADX para determinar si la tendencia se fortalece
            adx_slope = 0
            if len(adx) >= 3:
                adx_slope = (adx.iloc[-1] - adx.iloc[-3]) / 2
            
            result = {
                'adx': current_adx,
                'adx_modified': current_adx_mod,
                'adx_pos': adx_pos.iloc[-1] if not adx_pos.empty else 0,
                'adx_neg': adx_neg.iloc[-1] if not adx_neg.empty else 0,
                'strength': strength,
                'slope': adx_slope,
                'trending': current_adx > 25,
                'strengthening': adx_slope > 0.5
            }
            
            logger.debug(f"✅ ADX modificado calculado: {current_adx:.1f} ({strength})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculando ADX modificado: {e}")
            return {
                'adx': 0, 'adx_modified': -23, 'adx_pos': 0, 'adx_neg': 0,
                'strength': 'DEBIL', 'slope': 0, 'trending': False, 'strengthening': False
            }

class JaimeMerinoSignalGenerator:
    """
    Generador de señales siguiendo la metodología exacta de Jaime Merino
    """
    
    def __init__(self):
        self.indicators = JaimeMerinoIndicators()
    
    def generate_merino_signal(self, df_4h: pd.DataFrame, df_1h: pd.DataFrame, 
                             current_price: float) -> Dict:
        """
        Genera señal completa siguiendo la metodología de Jaime Merino
        
        Args:
            df_4h: DataFrame de 4 horas (timeframe principal)
            df_1h: DataFrame de 1 hora (para timing)
            current_price: Precio actual
            
        Returns:
            Diccionario con señal completa
        """
        try:
            # 1. EMAs en 4H para sesgo general
            ema_11_4h = df_4h['close'].ewm(span=11).mean().iloc[-1]
            ema_55_4h = df_4h['close'].ewm(span=55).mean().iloc[-1]
            
            # 2. ADX modificado en 4H
            adx_data = self.indicators.calculate_modified_adx(
                df_4h['high'], df_4h['low'], df_4h['close']
            )
            
            # 3. Squeeze Momentum en 4H
            momentum, squeeze_on, squeeze_off = self.indicators.calculate_squeeze_momentum(df_4h)
            current_momentum = momentum.iloc[-1] if not momentum.empty else 0
            is_squeeze = squeeze_on.iloc[-1] if not squeeze_on.empty else False
            
            # 4. Volume Profile
            volume_data = self.indicators.calculate_volume_profile_vpoc(df_4h)
            
            # 5. Determinación del sesgo (EMAs)
            if ema_11_4h > ema_55_4h:
                bias = "BULLISH"
            elif ema_11_4h < ema_55_4h:
                bias = "BEARISH"
            else:
                bias = "NEUTRAL"
            
            # 6. Validación con ADX
            trend_valid = adx_data['trending'] and adx_data['strengthening']
            
            # 7. Generación de señal principal
            signal = self._determine_signal(
                bias, trend_valid, current_momentum, is_squeeze,
                current_price, ema_11_4h, ema_55_4h, volume_data
            )
            
            # 8. Cálculo de fuerza de señal
            signal_strength = self._calculate_merino_strength(
                signal, bias, adx_data, current_momentum, volume_data, current_price, ema_11_4h
            )
            
            # 9. Niveles de trading
            levels = self._calculate_trading_levels(
                signal, current_price, volume_data, ema_11_4h, ema_55_4h
            )
            
            result = {
                'signal': signal,
                'signal_strength': signal_strength,
                'bias': bias,
                'timeframe_4h': {
                    'ema_11': ema_11_4h,
                    'ema_55': ema_55_4h,
                    'adx': adx_data,
                    'momentum': current_momentum,
                    'squeeze': is_squeeze
                },
                'volume_profile': volume_data,
                'trading_levels': levels,
                'confluence_score': self._calculate_confluence(
                    bias, trend_valid, current_momentum, volume_data
                )
            }
            
            logger.info(f"🎯 Señal Merino generada: {signal} ({signal_strength}%) - Sesgo: {bias}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generando señal de Merino: {e}")
            return self._get_empty_signal()
    
    def _determine_signal(self, bias: str, trend_valid: bool, momentum: float, 
                         is_squeeze: bool, price: float, ema_11: float, 
                         ema_55: float, volume_data: Dict) -> str:
        """Determina la señal principal"""
        
        # No operar durante squeeze (consolidación)
        if is_squeeze:
            return 'WAIT_SQUEEZE'
        
        # Señal LONG
        if (bias == 'BULLISH' and trend_valid and momentum > 0 and 
            price > ema_11 * 0.998):
            return 'LONG'
        
        # Señal SHORT
        elif (bias == 'BEARISH' and trend_valid and momentum < 0 and 
              price < ema_11 * 1.002):
            return 'SHORT'
        
        # Esperar condiciones
        else:
            return 'WAIT'
    
    def _calculate_merino_strength(self, signal: str, bias: str, adx_data: Dict,
                                  momentum: float, volume_data: Dict, 
                                  price: float, ema_11: float) -> int:
        """Calcula fuerza de señal según criterios de Merino"""
        
        if signal in ['WAIT', 'WAIT_SQUEEZE']:
            return 25
        
        strength = 0
        
        # Factor ADX (40 puntos)
        if adx_data['strength'] == 'MUY_FUERTE':
            strength += 40
        elif adx_data['strength'] == 'FUERTE':
            strength += 30
        elif adx_data['strength'] == 'MODERADA':
            strength += 20
        
        # Factor momentum (30 puntos)
        momentum_strength = min(30, abs(momentum) * 10)
        strength += int(momentum_strength)
        
        # Factor proximidad a EMA11 (20 puntos)
        distance_pct = abs((price - ema_11) / ema_11) * 100
        if distance_pct < 0.5:
            strength += 20
        elif distance_pct < 1.0:
            strength += 15
        elif distance_pct < 2.0:
            strength += 10
        
        # Factor Volume Profile (10 puntos)
        if abs(volume_data['vpoc_distance_pct']) < 2:
            strength += 10
        elif abs(volume_data['vpoc_distance_pct']) < 5:
            strength += 5
        
        return min(95, max(5, strength))
    
    def _calculate_trading_levels(self, signal: str, price: float, volume_data: Dict,
                                ema_11: float, ema_55: float) -> Dict:
        """Calcula niveles de trading según gestión de riesgo de Merino"""
        
        if signal == 'LONG':
            entry = price
            target_1 = price * 1.02  # +2%
            target_2 = price * 1.05  # +5%
            stop_loss = min(price * 0.98, ema_11 * 0.995)  # -2% o EMA11
            
        elif signal == 'SHORT':
            entry = price
            target_1 = price * 0.98  # -2%
            target_2 = price * 0.95  # -5%
            stop_loss = max(price * 1.02, ema_11 * 1.005)  # +2% o EMA11
            
        else:
            return {'entry': price, 'targets': [], 'stop_loss': None}
        
        return {
            'entry': entry,
            'targets': [target_1, target_2],
            'stop_loss': stop_loss,
            'risk_reward': 2.5,
            'position_size_pct': 2.0  # 2% del capital según Merino
        }
    
    def _calculate_confluence(self, bias: str, trend_valid: bool, 
                            momentum: float, volume_data: Dict) -> int:
        """Calcula score de confluencia técnica"""
        
        confluences = 0
        
        if bias != 'NEUTRAL':
            confluences += 1
        if trend_valid:
            confluences += 1
        if abs(momentum) > 0.5:
            confluences += 1
        if abs(volume_data['vpoc_distance_pct']) < 3:
            confluences += 1
        
        return confluences
    
    def _get_empty_signal(self) -> Dict:
        """Retorna señal vacía en caso de error"""
        return {
            'signal': 'NO_SIGNAL',
            'signal_strength': 0,
            'bias': 'NEUTRAL',
            'timeframe_4h': {},
            'volume_profile': {},
            'trading_levels': {},
            'confluence_score': 0
        }

    def generate_trading_data() -> dict:
        """
        Genera datos de trading con niveles calculados correctamente
        ACTUALIZAR esta función para incluir trading_levels
        """
        try:
            # Obtener precios reales
            real_prices = get_real_price_reference()
            binance_prices = get_binance_service_prices()
            
            # Usar precios reales si están disponibles
            current_prices = binance_prices if binance_prices else real_prices
            
            trading_data = {}
            
            for symbol in SYMBOLS:
                try:
                    current_price = current_prices.get(symbol, 50000.0)  # Precio por defecto
                    
                    # Generar análisis de señal (tu lógica existente o simulada)
                    signal_data = generate_enhanced_signal_analysis(symbol, current_price)
                    
                    # ¡IMPORTANTE! Calcular niveles de trading
                    trading_levels = calculate_trading_levels(symbol, current_price, signal_data)
                    
                    trading_data[symbol] = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'signal': signal_data,
                        'trading_levels': trading_levels,  # ¡Esto es lo que falta!
                        'last_update': datetime.now().isoformat(),
                        'data_source': 'enhanced_analysis_service'
                    }
                    
                    print(f"✅ {symbol}: ${current_price:.2f} - {signal_data['signal']} ({signal_data['signal_strength']}%) - Entrada: ${trading_levels['entry_optimal']}")
                    
                except Exception as e:
                    print(f"❌ Error procesando {symbol}: {e}")
                    # Datos por defecto en caso de error
                    trading_data[symbol] = {
                        'symbol': symbol,
                        'current_price': 50000.0,
                        'signal': {'signal': 'LOADING', 'signal_strength': 0, 'confluence_factors': 0},
                        'trading_levels': calculate_trading_levels(symbol, 50000.0, {'signal': 'NO_SIGNAL'}),
                        'last_update': datetime.now().isoformat(),
                        'data_source': 'fallback'
                    }
            
            return trading_data
            
        except Exception as e:
            print(f"❌ Error generando datos de trading: {e}")
            return {}
    def generate_enhanced_signal_analysis(symbol: str, price: float) -> dict:
        """
        Genera análisis de señal mejorado (reemplaza con tu lógica real de análisis técnico)
        """
        import random
        
        # Simular diferentes probabilidades según símbolo
        if symbol == 'BTCUSDT':
            signals = ['LONG', 'SHORT', 'WAIT']
            weights = [0.4, 0.3, 0.3]  # BTC más probabilidad de LONG
        else:
            signals = ['LONG', 'SHORT', 'WAIT', 'NO_SIGNAL']
            weights = [0.25, 0.25, 0.25, 0.25]
        
        signal = random.choices(signals, weights=weights)[0]
        
        # Fuerza de señal más realista
        if signal in ['LONG', 'SHORT']:
            strength = random.randint(60, 95)  # Señales ejecutables
        elif signal == 'WAIT':
            strength = random.randint(40, 70)  # Señales de espera
        else:
            strength = 0  # Sin señal
        
        return {
            'signal': signal,
            'signal_strength': strength,
            'confluence_factors': random.randint(1, 4),
            'timeframe_analysis': {
                '4h': signal if signal != 'NO_SIGNAL' else 'NEUTRAL',
                '1h': signal if signal != 'NO_SIGNAL' else 'NEUTRAL',
                'daily': random.choice(['BULLISH', 'BEARISH', 'NEUTRAL'])
            },
            'technical_indicators': {
                'ema_11_55': 'BULLISH' if signal == 'LONG' else 'BEARISH' if signal == 'SHORT' else 'NEUTRAL',
                'adx': random.randint(20, 40),
                'rsi': random.randint(30, 70),
                'volume_profile': 'SUPPORT' if signal == 'LONG' else 'RESISTANCE' if signal == 'SHORT' else 'NEUTRAL'
            }
        }

    def generate_signal_analysis(symbol: str, price: float) -> dict:
        """
        Simula análisis de señal (reemplaza con tu lógica real)
        """
        import random
        
        signals = ['LONG', 'SHORT', 'WAIT', 'NO_SIGNAL']
        signal = random.choice(signals)
        strength = random.randint(45, 95) if signal != 'NO_SIGNAL' else 0
        
        return {
            'signal': signal,
            'signal_strength': strength,
            'confluence_factors': random.randint(1, 4),
            'timeframe_analysis': {
                '4h': signal,
                '1h': signal,
                'daily': random.choice(['BULLISH', 'BEARISH', 'NEUTRAL'])
            }
        }
# Instancias globales
jaime_merino_indicators = JaimeMerinoIndicators()
jaime_merino_signal_generator = JaimeMerinoSignalGenerator()