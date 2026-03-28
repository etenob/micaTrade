# models/__init__.py
"""
Modelos de datos para Jaime Merino Trading Bot
Metodología Trading Latino - Análisis Técnico Avanzado
"""

# Modelos originales (mantener compatibilidad)
from .trading_analysis import TradingAnalysis, MarketData, TechnicalIndicators, create_analysis

# Modelos mejorados para metodología Jaime Merino
from .enhanced_trading_model import (
    MerinoTechnicalIndicators,
    MerinoMarketContext,
    MerinoSignal,
    MerinoRiskManagement,
    MerinoTradingLevels,
    MerinoTradingAnalysis,
    create_merino_analysis
)

__all__ = [
    # Modelos originales
    'TradingAnalysis',
    'MarketData',
    'TechnicalIndicators',
    'create_analysis',
    
    # Modelos Merino
    'MerinoTechnicalIndicators',
    'MerinoMarketContext',
    'MerinoSignal',
    'MerinoRiskManagement',
    'MerinoTradingLevels',
    'MerinoTradingAnalysis',
    'create_merino_analysis'
]

__version__ = '2.0.0'
__methodology__ = 'JAIME_MERINO'
__description__ = 'Modelos de datos para análisis técnico según metodología Jaime Merino'