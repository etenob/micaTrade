"""
Modelos de datos para análisis de trading
"""
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class MarketData:
    """Datos de mercado para un símbolo"""
    symbol: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    timestamp: datetime

@dataclass
class TechnicalIndicators:
    """Indicadores técnicos calculados"""
    ema_11: float
    ema_55: float
    sma_20: float
    rsi: float
    adx: float
    bb_upper: float
    bb_middle: float
    bb_lower: float

@dataclass
class TradingAnalysis:
    """Análisis completo de trading"""
    symbol: str
    market_data: MarketData
    indicators: TechnicalIndicators
    signal: str
    signal_strength: float
    trend_bias: str
    analysis_text: str
    timestamp: datetime

def create_analysis(symbol: str, market_data: MarketData, 
                   indicators: TechnicalIndicators, signal: str,
                   signal_strength: float, trend_bias: str,
                   analysis_text: str) -> TradingAnalysis:
    """Crea un objeto TradingAnalysis"""
    return TradingAnalysis(
        symbol=symbol,
        market_data=market_data,
        indicators=indicators,
        signal=signal,
        signal_strength=signal_strength,
        trend_bias=trend_bias,
        analysis_text=analysis_text,
        timestamp=datetime.now()
    )