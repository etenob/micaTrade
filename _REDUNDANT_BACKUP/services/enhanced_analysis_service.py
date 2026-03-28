"""
Servicio de análisis mejorado implementando la metodología completa de Jaime Merino
"""
import pandas as pd
from datetime import datetime
from typing import Optional, Dict
from services.binance_service import binance_service
from services.enhanced_indicators import jaime_merino_signal_generator
from models.trading_analysis import TradingAnalysis, create_analysis
from utils.logger import analysis_logger
from enhanced_config import MerinoConfig

logger = analysis_logger

class EnhancedAnalysisService:
    """
    Servicio de análisis mejorado siguiendo la metodología exacta de Jaime Merino
    """
    
    def __init__(self):
        self.binance = binance_service
        self.merino_generator = jaime_merino_signal_generator
        logger.info("🚀 Servicio de análisis mejorado inicializado - Metodología Jaime Merino")

    def _to_dataframe(self, data):
        """Convierte lista de velas en DataFrame con columnas numéricas"""
        if data is None or len(data) == 0:
            return None
        df = pd.DataFrame(data, columns=[
            "timestamp","open","high","low","close","volume","close_time",
            "qav","num_trades","taker_base_vol","taker_quote_vol","ignore"
        ])
        for col in ["open","high","low","close","volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def analyze_symbol_merino(self, symbol: str) -> Optional[Dict]:
        try:
            logger.info(f"📊 Iniciando análisis Merino para {symbol}")

            # 1. Obtener datos multi-temporales y convertirlos a DataFrame
            df_4h = self._to_dataframe(self.binance.get_klines(symbol, interval='4h', limit=100))
            df_1h = self._to_dataframe(self.binance.get_klines(symbol, interval='1h', limit=50))
            df_daily = self._to_dataframe(self.binance.get_klines(symbol, interval='1d', limit=30))

            if df_4h is None or df_1h is None or len(df_4h) < 20 or len(df_1h) < 20:
                logger.error(f"❌ Insuficientes datos históricos para {symbol}")
                return None

            # 2. Obtener precio actual
            current_price = self.binance.get_current_price(symbol)
            if not current_price:
                logger.error(f"❌ No se pudo obtener precio actual de {symbol}")
                return None
            current_price = float(current_price)

            # 3. Generar señal completa de Merino
            merino_signal = self.merino_generator.generate_merino_signal(
                df_4h, df_1h, current_price
            )

            # 4. Análisis básico de contexto (temporal)
            market_context = {
                'macro_trend': 'NEUTRAL',
                'ema_11_daily': current_price,
                'ema_55_daily': current_price,
                'volatility_pct': 2.0
            }

            # 5. Gestión básica de capital
            capital_allocation = {
                'current_trade': {
                    'position_size': 2.0 if merino_signal['signal'] in ['LONG', 'SHORT'] else 0.0,
                    'max_risk_per_trade': 2.0
                },
                'philosophy': '40-30-20-10'
            }

            # 6. Análisis textual
            analysis_text = f"Análisis Merino para {symbol}: {merino_signal['signal']} ({merino_signal['signal_strength']}%)"

            # 7. Crear estructura compatible
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'signal': merino_signal,
                'market_context': market_context,
                'capital_allocation': capital_allocation,
                'analysis_text': analysis_text,
                'current_price': current_price,
                'signal_type': merino_signal['signal'],
                'signal_strength': merino_signal['signal_strength'],
                'bias': merino_signal['bias'],
                'confluence_score': merino_signal['confluence_score'],
                'trading_levels': merino_signal['trading_levels'],
                'to_dict': lambda: result
            }

            logger.info(f"✅ Análisis Merino completado para {symbol}: {merino_signal['signal']} ({merino_signal['signal_strength']}%)")
            return result

        except Exception as e:
            logger.error(f"❌ Error en análisis Merino de {symbol}: {e}")
            return None

    # ... resto del código igual (contexto, capital, texto, recomendación, riesgo, etc.)

# Instancia global del servicio mejorado
enhanced_analysis_service = EnhancedAnalysisService()

