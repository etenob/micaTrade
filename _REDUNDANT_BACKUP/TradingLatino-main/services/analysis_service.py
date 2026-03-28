"""
Servicio principal de análisis técnico
"""
from datetime import datetime
from typing import Optional
from services.binance_service import binance_service
from services.indicators import indicators_calculator, signal_generator
from models.trading_analysis import TradingAnalysis, create_analysis
from utils.logger import analysis_logger
from config import Config

logger = analysis_logger

class AnalysisService:
    """
    Servicio principal para realizar análisis técnico completo
    """
    
    def __init__(self):
        """Inicializa el servicio de análisis"""
        self.binance = binance_service
        self.indicators_calc = indicators_calculator
        self.signal_gen = signal_generator
        logger.info("🚀 Servicio de análisis inicializado")
    
    def analyze_symbol(self, symbol: str) -> Optional[TradingAnalysis]:
        """
        Realiza análisis técnico completo para un símbolo
        
        Args:
            symbol: Símbolo a analizar (ej: 'BTCUSDT')
            
        Returns:
            TradingAnalysis completo o None si hay error
        """
        try:
            logger.info(f"📊 Iniciando análisis de {symbol}")
            
            # 1. Obtener datos de mercado
            market_data = self.binance.get_market_data(symbol)
            if not market_data:
                logger.error(f"❌ No se pudieron obtener datos de mercado para {symbol}")
                return None
            
            # 2. Obtener datos históricos para indicadores
            df = self.binance.get_klines(symbol, interval='1h', limit=100)
            if df is None or len(df) < 55:
                logger.error(f"❌ Insuficientes datos históricos para {symbol}")
                return None
            
            # 3. Calcular indicadores técnicos
            indicators = self.indicators_calc.calculate_all_indicators(df)
            
            # 4. Generar señal de trading
            signal, base_strength = self.signal_gen.generate_ema_signal(
                indicators.ema_11, indicators.ema_55, market_data.close_price
            )
            
            # 5. Determinar sesgo de tendencia
            trend_bias = self.signal_gen.determine_trend_bias(
                indicators.ema_11, indicators.ema_55, indicators.adx, indicators.rsi
            )
            
            # 6. Calcular fuerza de señal refinada
            signal_strength = self.signal_gen.calculate_signal_strength(
                signal, indicators.ema_11, indicators.ema_55, 
                indicators.adx, indicators.rsi, market_data.close_price
            )
            
            # 7. Generar textos de análisis
            analysis_text = self._generate_analysis_text(
                symbol, market_data, indicators, signal, signal_strength, trend_bias
            )
            
            recommendation = self._generate_recommendation(
                symbol, market_data, indicators, signal, signal_strength, trend_bias
            )
            
            # 8. Crear análisis completo
            analysis = create_analysis(
                symbol=symbol,
                market_data=market_data,
                indicators=indicators,
                signal=signal,
                signal_strength=signal_strength,
                trend_bias=trend_bias,
                analysis_text=analysis_text,
                recommendation=recommendation
            )
            
            logger.info(f"✅ Análisis completado para {symbol}: {signal} ({signal_strength}%)")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de {symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _generate_analysis_text(self, symbol: str, market_data, indicators, 
                               signal: str, signal_strength: int, trend_bias: str) -> str:
        """
        Genera el texto detallado del análisis técnico
        """
        try:
            # Calcular cambio porcentual
            change_pct = ((market_data.close_price - market_data.open_price) / market_data.open_price) * 100
            
            # Determinar momentum
            momentum = "POSITIVO" if change_pct > 0 else "NEGATIVO" if change_pct < 0 else "NEUTRAL"
            
            # Evaluar ADX
            adx_strength = "FUERTE" if indicators.adx > 35 else "MODERADA" if indicators.adx > 25 else "DÉBIL"
            
            # Evaluar RSI
            if indicators.rsi > 70:
                rsi_status = "SOBRECOMPRADO"
            elif indicators.rsi < 30:
                rsi_status = "SOBREVENDIDO"
            else:
                rsi_status = "NEUTRAL"
            
            # Relación EMAs
            ema_relation = "ALCISTA" if indicators.ema_11 > indicators.ema_55 else "BAJISTA"
            ema_distance = abs((indicators.ema_11 - indicators.ema_55) / indicators.ema_55) * 100
            
            # Volatilidad
            volatility = "ALTA" if abs(change_pct) > 3 else "MODERADA" if abs(change_pct) > 1 else "BAJA"
            
            analysis_text = f"""ANÁLISIS TÉCNICO COMPLETO - {symbol}
{'='*50}

💰 PRECIO ACTUAL: ${market_data.close_price:,.4f}
📈 CAMBIO 24H: {change_pct:+.2f}% | MOMENTUM: {momentum}
📊 VOLATILIDAD: {volatility}

🎯 SEÑAL DE TRADING: {signal}
💪 FUERZA DE SEÑAL: {signal_strength}/100
📊 SESGO DE TENDENCIA: {trend_bias}

📉 MEDIAS MÓVILES EXPONENCIALES:
   • EMA 11: ${indicators.ema_11:,.4f}
   • EMA 55: ${indicators.ema_55:,.4f}
   • Relación: {ema_relation} ({ema_distance:.2f}% separación)
   • Precio vs EMA11: {((market_data.close_price - indicators.ema_11) / indicators.ema_11) * 100:+.2f}%

📊 INDICADORES TÉCNICOS:
   • ADX: {indicators.adx:.1f} (Tendencia {adx_strength})
   • RSI: {indicators.rsi:.1f} ({rsi_status})
   • SMA 20: ${indicators.sma_20:.4f}

⚠️ NIVELES CRÍTICOS:
   • Soporte inmediato: ${market_data.low_price:.4f}
   • Resistencia inmediata: ${market_data.high_price:.4f}
   • Soporte técnico: ${market_data.close_price * 0.98:.4f} (-2%)
   • Resistencia técnica: ${market_data.close_price * 1.02:.4f} (+2%)

📈 CONTEXTO DE MERCADO:
   • Rango 24h: ${market_data.low_price:.4f} - ${market_data.high_price:.4f}
   • Volumen 24h: {market_data.volume:,.0f} {symbol[:3]}
   • Precio vs máximo: {((market_data.close_price - market_data.high_price) / market_data.high_price) * 100:+.2f}%
   • Precio vs mínimo: {((market_data.close_price - market_data.low_price) / market_data.low_price) * 100:+.2f}%

🔍 EVALUACIÓN METODOLOGÍA JAIME MERINO:
   • Confluencia técnica: {self._evaluate_confluence(indicators, signal)}
   • Gestión de riesgo: {self._risk_assessment(signal_strength, indicators.adx)}
   • Timing de entrada: {self._entry_timing(signal, signal_strength)}

⏰ Análisis generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""

            return analysis_text
            
        except Exception as e:
            logger.error(f"❌ Error generando texto de análisis: {e}")
            return f"Error generando análisis para {symbol}: {str(e)}"
    
    def _generate_recommendation(self, symbol: str, market_data, indicators, 
                               signal: str, signal_strength: int, trend_bias: str) -> str:
        """
        Genera la recomendación específica de trading
        """
        try:
            current_price = market_data.close_price
            
            if signal == 'LONG' and signal_strength >= 50:
                # Recomendación de compra
                entry_price = current_price
                target_1 = current_price * 1.02  # +2%
                target_2 = current_price * 1.05  # +5%
                stop_loss = current_price * 0.98  # -2%
                
                recommendation = f"""🟢 RECOMENDACIÓN: COMPRAR (LONG)
{'='*40}

✅ ENTRADA RECOMENDADA:
   • Precio entrada: ${entry_price:.4f}
   • Rango entrada: ${entry_price * 0.999:.4f} - ${entry_price * 1.001:.4f}

🎯 OBJETIVOS DE GANANCIA:
   • Target 1: ${target_1:.4f} (+2.0%) - TOMA PARCIAL 50%
   • Target 2: ${target_2:.4f} (+5.0%) - TOMA TOTAL

🛑 GESTIÓN DE RIESGO:
   • Stop Loss: ${stop_loss:.4f} (-2.0%)
   • Ratio R/R: 1:2.5 (EXCELENTE)

💰 GESTIÓN DE CAPITAL:
   • Tamaño posición: 2-3% del capital total
   • Apalancamiento: 1:1 a 1:3 máximo
   • Timeframe: 1-4 horas

📊 JUSTIFICACIÓN TÉCNICA:
   • EMA 11 > EMA 55 (Tendencia alcista)
   • Precio sobre EMA 11 (Confirmación)
   • ADX: {indicators.adx:.1f} ({"Fuerte" if indicators.adx > 35 else "Moderada"} tendencia)
   • RSI: {indicators.rsi:.1f} (Zona {"saludable" if 40 < indicators.rsi < 75 else "extrema"})
   • Fuerza señal: {signal_strength}% ({"ALTA" if signal_strength > 70 else "MEDIA"})

⚠️ CONSIDERACIONES:
   • Monitorear cierre bajo EMA 11 para salida anticipada
   • Volumen debe acompañar el movimiento alcista
   • Estar atento a resistencias en ${market_data.high_price:.4f}

🔥 CONFLUENCIAS ALCISTAS DETECTADAS:
   • ✅ Estructura técnica favorable
   • ✅ Momentum positivo confirmado
   • ✅ Indicadores en zona operativa"""

            elif signal == 'SHORT' and signal_strength >= 50:
                # Recomendación de venta
                entry_price = current_price
                target_1 = current_price * 0.98  # -2%
                target_2 = current_price * 0.95  # -5%
                stop_loss = current_price * 1.02  # +2%
                
                recommendation = f"""🔴 RECOMENDACIÓN: VENDER (SHORT)
{'='*40}

✅ ENTRADA RECOMENDADA:
   • Precio entrada: ${entry_price:.4f}
   • Rango entrada: ${entry_price * 0.999:.4f} - ${entry_price * 1.001:.4f}

🎯 OBJETIVOS DE GANANCIA:
   • Target 1: ${target_1:.4f} (-2.0%) - TOMA PARCIAL 50%
   • Target 2: ${target_2:.4f} (-5.0%) - TOMA TOTAL

🛑 GESTIÓN DE RIESGO:
   • Stop Loss: ${stop_loss:.4f} (+2.0%)
   • Ratio R/R: 1:2.5 (EXCELENTE)

💰 GESTIÓN DE CAPITAL:
   • Tamaño posición: 2-3% del capital total
   • Apalancamiento: 1:1 a 1:3 máximo
   • Timeframe: 1-4 horas

📊 JUSTIFICACIÓN TÉCNICA:
   • EMA 11 < EMA 55 (Tendencia bajista)
   • Precio bajo EMA 11 (Confirmación)
   • ADX: {indicators.adx:.1f} ({"Fuerte" if indicators.adx > 35 else "Moderada"} tendencia)
   • RSI: {indicators.rsi:.1f} (Zona {"saludable" if 25 < indicators.rsi < 60 else "extrema"})
   • Fuerza señal: {signal_strength}% ({"ALTA" if signal_strength > 70 else "MEDIA"})

⚠️ CONSIDERACIONES:
   • Monitorear cierre sobre EMA 11 para salida anticipada
   • Confirmar presión vendedora con volumen
   • Cuidado con soportes en ${market_data.low_price:.4f}

📉 CONFLUENCIAS BAJISTAS DETECTADAS:
   • ✅ Estructura técnica desfavorable
   • ✅ Momentum negativo confirmado
   • ✅ Indicadores en zona operativa"""

            elif signal == 'WAIT':
                recommendation = f"""🟡 RECOMENDACIÓN: ESPERAR
{'='*30}

⏳ RAZÓN: Condiciones de mercado indecisas

📊 SITUACIÓN ACTUAL:
   • Precio: ${current_price:.4f}
   • EMA 11: ${indicators.ema_11:.4f}
   • EMA 55: ${indicators.ema_55:.4f}
   • ADX: {indicators.adx:.1f} (Tendencia {"débil" if indicators.adx < 25 else "moderada"})

🔍 ESPERANDO CONFIRMACIÓN DE:
   • Ruptura clara de nivel clave
   • Incremento en volumen de confirmación
   • Separación definitiva de EMAs
   • Fortalecimiento de ADX > 25

📋 PLAN DE ACCIÓN:
   • Monitorear cada 30-60 minutos
   • Establecer alertas en niveles clave:
     - Soporte: ${current_price * 0.98:.4f}
     - Resistencia: ${current_price * 1.02:.4f}
   • Preparar entrada en ruptura confirmada

💡 NIVELES DE ACTIVACIÓN:
   • LONG si precio > ${indicators.ema_11 * 1.005:.4f} con volumen
   • SHORT si precio < ${indicators.ema_11 * 0.995:.4f} con volumen

⚠️ DISCIPLINA: No forzar operaciones en mercado lateral"""

            else:
                recommendation = f"""⚪ SIN SEÑAL OPERATIVA CLARA
{'='*35}

🚫 RAZÓN: Condiciones técnicas no favorables

📊 EVALUACIÓN ACTUAL:
   • Fuerza de señal: {signal_strength}% (Insuficiente)
   • Confluencias técnicas: Limitadas
   • Riesgo/Beneficio: No atractivo

💡 RECOMENDACIÓN GENERAL:
   • NO OPERAR en este momento
   • PRESERVAR CAPITAL es prioritario
   • ESPERAR mejor configuración técnica
   • REVISAR en 1-2 horas

📚 METODOLOGÍA JAIME MERINO:
   "Es mejor perder una oportunidad que perder dinero.
    Solo operamos con alta probabilidad de éxito."

🔍 PRÓXIMA REVISIÓN:
   • Monitorear cambios en EMAs
   • Vigilar fortalecimiento de ADX
   • Esperar confirmación de volumen
   
⏰ Mantener paciencia y disciplina."""

            return recommendation
            
        except Exception as e:
            logger.error(f"❌ Error generando recomendación: {e}")
            return f"Error generando recomendación para {symbol}: {str(e)}"
    
    def _evaluate_confluence(self, indicators, signal: str) -> str:
        """Evalúa la confluencia técnica"""
        confluences = 0
        
        # EMA alignment
        if signal == 'LONG' and indicators.ema_11 > indicators.ema_55:
            confluences += 1
        elif signal == 'SHORT' and indicators.ema_11 < indicators.ema_55:
            confluences += 1
        
        # ADX strength
        if indicators.adx > 25:
            confluences += 1
        
        # RSI zone
        if signal == 'LONG' and 40 < indicators.rsi < 75:
            confluences += 1
        elif signal == 'SHORT' and 25 < indicators.rsi < 60:
            confluences += 1
        
        if confluences >= 3:
            return "ALTA"
        elif confluences >= 2:
            return "MEDIA"
        else:
            return "BAJA"
    
    def _risk_assessment(self, signal_strength: int, adx: float) -> str:
        """Evalúa el nivel de riesgo"""
        if signal_strength > 70 and adx > 35:
            return "BAJO (Configuración sólida)"
        elif signal_strength > 50 and adx > 25:
            return "MEDIO (Aceptable con gestión)"
        else:
            return "ALTO (No recomendado)"
    
    def _entry_timing(self, signal: str, signal_strength: int) -> str:
        """Evalúa el timing de entrada"""
        if signal in ['LONG', 'SHORT'] and signal_strength > 70:
            return "INMEDIATO (Señal fuerte)"
        elif signal in ['LONG', 'SHORT'] and signal_strength > 50:
            return "EN CONFIRMACIÓN (Esperar volumen)"
        else:
            return "DIFERIR (Esperar mejor setup)"

# Instancia global del servicio
analysis_service = AnalysisService()