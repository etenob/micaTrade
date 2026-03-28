# services/enhanced_indicators.py
"""
Indicadores mejorados para la metodología de Jaime Merino
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional, Tuple
from utils.logger import analysis_logger

logger = analysis_logger

class JaimeMerinoSignalGenerator:
    """
    Generador de señales siguiendo la metodología de Jaime Merino
    """
    
    def __init__(self):
        logger.info("🎯 Generador de señales Jaime Merino inicializado")
        self._last_signal_strength = 50
    
    def generate_merino_signal(self, df_4h: pd.DataFrame, df_1h: pd.DataFrame, 
                             current_price: float) -> Dict:
        """
        Genera señal básica siguiendo la metodología de Jaime Merino
        
        Args:
            df_4h: DataFrame de 4 horas
            df_1h: DataFrame de 1 hora
            current_price: Precio actual
            
        Returns:
            Diccionario con señal completa
        """
        try:
            logger.debug(f"🔍 Generando señal Merino para precio: ${current_price:,.4f}")
            
            # 1. Calcular EMAs en 4H
            ema_11_4h = df_4h['close'].ewm(span=11).mean().iloc[-1]
            ema_55_4h = df_4h['close'].ewm(span=55).mean().iloc[-1]
            
            # 2. Calcular EMAs en 1H para timing
            ema_11_1h = df_1h['close'].ewm(span=11).mean().iloc[-1]
            ema_55_1h = df_1h['close'].ewm(span=55).mean().iloc[-1]
            
            # 3. Determinar sesgo principal (4H)
            if ema_11_4h > ema_55_4h * 1.001:  # 0.1% de separación mínima
                bias = "BULLISH"
            elif ema_11_4h < ema_55_4h * 0.999:
                bias = "BEARISH"
            else:
                bias = "NEUTRAL"
            
            # 4. Calcular RSI para momentum
            rsi = self._calculate_rsi(df_4h['close'])
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # 5. Calcular volumen promedio
            avg_volume = df_4h['volume'].rolling(20).mean().iloc[-1]
            current_volume = df_4h['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # ✅ CREAR VOLUME_DATA AQUÍ
            volume_data = {
                'vpoc_distance_pct': float((current_price - ema_11_4h) / ema_11_4h * 100),
                'volume_ratio': float(volume_ratio),
                'avg_volume': float(avg_volume),
                'current_volume': float(current_volume)
            }
            # 6. Generar señal principal
            signal = self._determine_basic_signal(
                bias, current_price, ema_11_4h, ema_55_4h, 
                ema_11_1h, ema_55_1h, current_rsi, volume_ratio
            )
            
            # 7. Calcular fuerza de señal
            signal_strength = self._calculate_basic_strength(
                signal, bias, current_rsi, volume_ratio, 
                current_price, ema_11_4h, ema_55_4h
            )
            
            # 8. Calcular niveles de trading
            trading_levels = self._calculate_merino_trading_levels(
                signal, current_price, ema_11_4h, ema_55_4h, volume_data
            )
            self._last_signal_strength = signal_strength
            # 9. Calcular confluencias
            confluence_score = self._calculate_basic_confluence(
                bias, current_rsi, volume_ratio, signal_strength
            )
            
            result = {
                'signal': signal,
                'signal_strength': int(signal_strength),
                'bias': bias,
                'timeframe_4h': {
                    'ema_11': float(ema_11_4h),
                    'ema_55': float(ema_55_4h),
                    'rsi': float(current_rsi),
                    'volume_ratio': float(volume_ratio)
                },
                'timeframe_1h': {
                    'ema_11': float(ema_11_1h),
                    'ema_55': float(ema_55_1h)
                },
                'volume_profile': {
                    'vpoc_distance_pct': float((current_price - ema_11_4h) / ema_11_4h * 100),
                    'volume_ratio': float(volume_ratio)
                },
                'trading_levels': trading_levels,
                'confluence_score': confluence_score
            }
            
            logger.info(f"🎯 Señal generada: {signal} ({signal_strength}%) - Sesgo: {bias}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generando señal Merino: {e}")
            return self._get_empty_signal()
    
    def _determine_basic_signal(self, bias: str, price: float, ema_11_4h: float, 
                               ema_55_4h: float, ema_11_1h: float, ema_55_1h: float, 
                               rsi: float, volume_ratio: float) -> str:
        """Determina la señal básica"""
        
        # Condiciones para LONG
        if (bias == "BULLISH" and 
            price > ema_11_4h and 
            ema_11_1h > ema_55_1h and 
            rsi > 40 and rsi < 80 and 
            volume_ratio > 0.8):
            return "LONG"
        
        # Condiciones para SHORT
        elif (bias == "BEARISH" and 
              price < ema_11_4h and 
              ema_11_1h < ema_55_1h and 
              rsi < 60 and rsi > 20 and 
              volume_ratio > 0.8):
            return "SHORT"
        
        # Sin señal clara
        elif bias == "NEUTRAL" or volume_ratio < 0.5:
            return "WAIT"
        
        else:
            return "NO_SIGNAL"
    
    def _calculate_basic_strength(self, signal: str, bias: str, rsi: float, 
                                 volume_ratio: float, price: float, 
                                 ema_11: float, ema_55: float) -> float:
        """Calcula la fuerza básica de la señal"""
        
        if signal in ["NO_SIGNAL", "WAIT"]:
            return 0
        
        strength = 0
        
        # Base por sesgo
        if bias != "NEUTRAL":
            strength += 25
        
        # RSI en zona favorable
        if signal == "LONG" and 40 < rsi < 70:
            strength += 20
        elif signal == "SHORT" and 30 < rsi < 60:
            strength += 20
        
        # Volumen adecuado
        if volume_ratio > 1.2:
            strength += 25
        elif volume_ratio > 0.8:
            strength += 15
        
        # Distancia de EMAs
        ema_separation = abs(ema_11 - ema_55) / ema_55 * 100
        if ema_separation > 1:
            strength += 20
        elif ema_separation > 0.5:
            strength += 10
        
        # Posición respecto a EMA 11
        price_ema_distance = abs(price - ema_11) / ema_11 * 100
        if price_ema_distance < 0.5:
            strength += 10
        
        return min(100, max(0, strength))
    
    def _calculate_basic_levels(self, signal: str, price: float, 
                               ema_11: float, ema_55: float) -> Dict:
        """Calcula niveles básicos de trading"""
        
        if signal == "LONG":
            return {
                'entry': price,
                'targets': [price * 1.02, price * 1.05],  # +2%, +5%
                'stop_loss': min(price * 0.98, ema_11 * 0.995)  # -2% o cerca de EMA11
            }
        elif signal == "SHORT":
            return {
                'entry': price,
                'targets': [price * 0.98, price * 0.95],  # -2%, -5%
                'stop_loss': max(price * 1.02, ema_11 * 1.005)  # +2% o cerca de EMA11
            }
        else:
            return {'entry': price, 'targets': [], 'stop_loss': None}
    
    def _calculate_basic_confluence(self, bias: str, rsi: float, 
                                   volume_ratio: float, strength: float) -> int:
        """Calcula score básico de confluencia"""
        
        confluences = 0
        
        if bias != "NEUTRAL":
            confluences += 1
        if 30 < rsi < 70:
            confluences += 1
        if volume_ratio > 1.0:
            confluences += 1
        if strength > 50:
            confluences += 1
        
        return confluences
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcula RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception:
            return pd.Series([50] * len(prices), index=prices.index)
    
    def _get_empty_signal(self) -> Dict:
        """Retorna señal vacía"""
        return {
            'signal': 'NO_SIGNAL',
            'signal_strength': 0,
            'bias': 'NEUTRAL',
            'timeframe_4h': {},
            'timeframe_1h': {},
            'volume_profile': {},
            'trading_levels': {'entry': 0, 'targets': [], 'stop_loss': None},
            'confluence_score': 0
        }
    def _calculate_merino_trading_levels(self, signal: str, current_price: float, 
                                    ema_11: float, ema_55: float, volume_data: Dict) -> Dict:
        """
        Calcula niveles de trading según metodología específica de Jaime Merino para futuros
        
        Args:
            signal: Tipo de señal
            current_price: Precio actual
            ema_11: EMA 11
            ema_55: EMA 55
            volume_data: Datos de volumen
            
        Returns:
            Diccionario con niveles completos para futuros
        """
        try:
            if signal == 'LONG':
                # ENTRADA LONG según Merino
                entry_optimal = max(current_price * 1.001, ema_11 * 1.002)  # 0.1% arriba del precio o 0.2% arriba de EMA11
                entry_range_low = current_price * 0.999  # -0.1%
                entry_range_high = current_price * 1.005  # +0.5%
                
                # TARGETS según filosofía Merino
                target_1 = current_price * 1.02    # +2% (toma parcial 50%)
                target_2 = current_price * 1.05    # +5% (toma total)
                target_3 = current_price * 1.08    # +8% (objetivo extendido)
                
                # STOP LOSS conservador según Merino
                stop_loss_price = min(current_price * 0.98, ema_11 * 0.995)  # -2% o 0.5% bajo EMA11
                technical_stop = ema_55 * 0.998  # Stop técnico en EMA55
                
                # INVALIDACIÓN
                invalidation_level = ema_11 * 0.99  # Cierre bajo EMA11 con 1% buffer
                invalidation_reason = "Cierre bajo EMA 11 en 4H invalida setup alcista"
                
                # APALANCAMIENTO según Merino
                recommended_leverage = 2.0 if current_price > ema_11 * 1.01 else 1.5
                max_leverage = 3.0
                
                # GESTIÓN DE POSICIÓN
                position_size_base = 2.0  # 2% del capital base
                position_size_aggressive = 3.0  # Para señales > 80%
                
            elif signal == 'SHORT':
                # ENTRADA SHORT según Merino
                entry_optimal = min(current_price * 0.999, ema_11 * 0.998)  # 0.1% abajo del precio o 0.2% abajo de EMA11
                entry_range_low = current_price * 0.995  # -0.5%
                entry_range_high = current_price * 1.001  # +0.1%
                
                # TARGETS según filosofía Merino
                target_1 = current_price * 0.98    # -2% (toma parcial 50%)
                target_2 = current_price * 0.95    # -5% (toma total)
                target_3 = current_price * 0.92    # -8% (objetivo extendido)
                
                # STOP LOSS conservador según Merino
                stop_loss_price = max(current_price * 1.02, ema_11 * 1.005)  # +2% o 0.5% arriba de EMA11
                technical_stop = ema_55 * 1.002  # Stop técnico en EMA55
                
                # INVALIDACIÓN
                invalidation_level = ema_11 * 1.01  # Cierre arriba EMA11 con 1% buffer
                invalidation_reason = "Cierre arriba EMA 11 en 4H invalida setup bajista"
                
                # APALANCAMIENTO según Merino
                recommended_leverage = 2.0 if current_price < ema_11 * 0.99 else 1.5
                max_leverage = 3.0
                
                # GESTIÓN DE POSICIÓN
                position_size_base = 2.0  # 2% del capital base
                position_size_aggressive = 3.0  # Para señales > 80%
                
            else:
                # Sin señal - sin niveles
                return {
                    'signal': signal,
                    'entry_optimal': current_price,
                    'entry_range': {'low': current_price, 'high': current_price},
                    'targets': [],
                    'stop_loss': None,
                    'position_size_pct': 0.0,
                    'leverage': {'recommended': 1.0, 'max': 1.0},
                    'risk_reward': 0.0,
                    'invalidation': {'level': current_price, 'reason': 'Sin setup válido'}
                }
            
            # CÁLCULOS COMUNES
            risk_amount = abs(entry_optimal - stop_loss_price)
            reward_amount = abs(target_2 - entry_optimal)
            risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
            
            # Ajustar tamaño de posición según fuerza de señal
            signal_strength = getattr(self, '_last_signal_strength', 50)
            if signal_strength >= 80:
                position_size = position_size_aggressive
            elif signal_strength >= 60:
                position_size = position_size_base * 1.5
            else:
                position_size = position_size_base
            
            return {
                'signal': signal,
                'entry_optimal': float(entry_optimal),
                'entry_range': {
                    'low': float(entry_range_low),
                    'high': float(entry_range_high)
                },
                'targets': [
                    {'level': float(target_1), 'percentage': 2.0, 'action': 'Toma parcial 50%'},
                    {'level': float(target_2), 'percentage': 5.0, 'action': 'Toma total'},
                    {'level': float(target_3), 'percentage': 8.0, 'action': 'Objetivo extendido'}
                ],
                'stop_loss': {
                    'price': float(stop_loss_price),
                    'percentage': abs((stop_loss_price - entry_optimal) / entry_optimal * 100),
                    'technical_stop': float(technical_stop)
                },
                'position_size_pct': float(position_size),
                'leverage': {
                    'recommended': float(recommended_leverage),
                    'max': float(max_leverage),
                    'note': 'Nunca exceder 1:3 según filosofía Merino'
                },
                'risk_reward': float(round(risk_reward_ratio, 2)),
                'invalidation': {
                    'level': float(invalidation_level),
                    'reason': invalidation_reason
                },
                'execution_plan': {
                    'entry_method': 'Entrada gradual en 2-3 tramos',
                    'stop_management': 'Mover a breakeven en +1%',
                    'profit_taking': 'Seguir targets sin emociones',
                    'time_limit': '4-8 horas para confirmación'
                },
                'merino_rules': {
                    'max_daily_loss': '6% del capital total',
                    'max_weekly_loss': '8% del capital total',
                    'position_correlation': 'Max 2 posiciones correlacionadas',
                    'review_frequency': 'Cada 4 horas mínimo'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculando niveles de trading Merino: {e}")
            return {
                'signal': 'ERROR',
                'entry_optimal': current_price,
                'error': str(e)
            }
# Instancia global
jaime_merino_signal_generator = JaimeMerinoSignalGenerator()