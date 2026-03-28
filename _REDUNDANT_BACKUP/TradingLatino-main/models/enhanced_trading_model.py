"""
Modelos de datos mejorados para análisis según metodología Jaime Merino
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, List, Any
import json

@dataclass
class MerinoTechnicalIndicators:
    """
    Indicadores técnicos específicos de la metodología Jaime Merino
    """
    # EMAs principales - TODOS sin valores por defecto
    ema_11_4h: float
    ema_55_4h: float
    ema_11_1h: float
    ema_55_1h: float
    ema_11_daily: float
    ema_55_daily: float
    
    # ADX modificado (punto 23 como 0)
    adx: float
    adx_modified: float
    adx_strength: str  # DEBIL, MODERADA, FUERTE, MUY_FUERTE
    adx_slope: float
    adx_trending: bool
    adx_strengthening: bool
    
    # Squeeze Momentum (LazyBear)
    squeeze_momentum: float
    squeeze_on: bool  # True = consolidación, False = movimiento
    squeeze_just_released: bool
    
    # Volume Profile
    vpoc: float  # Volume Point of Control
    vpoc_distance_pct: float
    high_volume_levels: List[Dict]
    
    # Indicadores adicionales
    rsi_4h: float
    
    # Campos opcionales AL FINAL
    macd_4h: Optional[float] = None
    bollinger_squeeze: bool = False

@dataclass
class MerinoMarketContext:
    """
    Contexto de mercado multi-temporal
    """
    # Argumentos SIN valores por defecto PRIMERO
    macro_trend: str  # BULL_MARKET, BEAR_MARKET, SIDEWAYS
    weekly_bias: str  # BULLISH, BEARISH, NEUTRAL
    daily_bias: str
    resistance_20d: float
    support_20d: float
    volatility_20d: float
    volume_avg_20d: float
    price_vs_resistance_pct: float
    price_vs_support_pct: float
    
    # Campos opcionales AL FINAL
    resistance_weekly: Optional[float] = None
    support_weekly: Optional[float] = None

@dataclass
class MerinoSignal:
    """
    Señal de trading según metodología Jaime Merino
    """
    # Argumentos SIN valores por defecto PRIMERO
    signal: str  # LONG, SHORT, WAIT, WAIT_SQUEEZE, NO_SIGNAL
    signal_strength: int  # 0-100
    bias_4h: str  # BULLISH, BEARISH, NEUTRAL
    confluence_score: int  # 0-4
    reasons: List[str]
    invalidation_conditions: List[str]
    optimal_timeframe: str  # 4h, 1h, daily
    entry_timing: str  # IMMEDIATE, ON_CONFIRMATION, WAIT_BETTER_SETUP

@dataclass
class MerinoRiskManagement:
    """
    Gestión de riesgo según filosofía 40-30-20-10 de Merino
    """
    # Argumentos SIN valores por defecto PRIMERO
    position_size_pct: float  # % del capital total
    
    # Argumentos CON valores por defecto AL FINAL
    btc_long_term_pct: float = 40.0
    weekly_charts_pct: float = 30.0
    daily_trading_pct: float = 20.0
    futures_pct: float = 10.0
    max_risk_per_trade_pct: float = 1.0
    risk_reward_ratio: float = 2.5
    max_daily_loss_pct: float = 6.0
    max_weekly_loss_pct: float = 8.0
    max_monthly_loss_pct: float = 10.0
    max_leverage: float = 3.0
    recommended_leverage: float = 1.0

@dataclass
class MerinoTradingLevels:
    """
    Niveles de trading específicos
    """
    # Argumentos SIN valores por defecto PRIMERO
    entry_price: float
    entry_range_low: float
    entry_range_high: float
    target_1: float
    target_2: float
    stop_loss: float
    technical_stop: float
    invalidation_level: float
    invalidation_reason: str
    
    # Argumentos CON valores por defecto AL FINAL
    target_1_pct: float = 2.0
    target_2_pct: float = 5.0
    stop_loss_pct: float = 2.0

@dataclass
class MerinoTradingAnalysis:
    """
    Análisis completo según metodología Jaime Merino
    """
    # Argumentos SIN valores por defecto PRIMERO
    symbol: str
    timestamp: datetime
    current_price: float
    indicators: MerinoTechnicalIndicators
    market_context: MerinoMarketContext
    signal: MerinoSignal
    risk_management: MerinoRiskManagement
    analysis_text: str
    recommendation: str
    confidence_level: str  # LOW, MEDIUM, HIGH
    
    # Argumentos CON valores por defecto AL FINAL
    methodology: str = "JAIME_MERINO"
    trading_levels: Optional[MerinoTradingLevels] = None
    suggested_review_hours: int = 4
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para JSON"""
        result = asdict(self)
        # Convertir datetime a string
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def to_json(self) -> str:
        """Convierte a JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumen ejecutivo"""
        return {
            'symbol': self.symbol,
            'signal': self.signal.signal,
            'strength': self.signal.signal_strength,
            'bias': self.signal.bias_4h,
            'confluences': self.signal.confluence_score,
            'confidence': self.confidence_level,
            'position_size': self.risk_management.position_size_pct,
            'risk_reward': self.risk_management.risk_reward_ratio,
            'entry': self.trading_levels.entry_price if self.trading_levels else self.current_price,
            'stop': self.trading_levels.stop_loss if self.trading_levels else None,
            'target_1': self.trading_levels.target_1 if self.trading_levels else None
        }

def create_merino_analysis(
    symbol: str,
    current_price: float,
    df_4h, df_1h, df_daily,
    merino_signal_data: Dict
) -> MerinoTradingAnalysis:
    """
    Factory function para crear análisis completo de Merino
    """
    try:
        # Crear indicadores básicos
        indicators = MerinoTechnicalIndicators(
            ema_11_4h=0,
            ema_55_4h=0,
            ema_11_1h=0,
            ema_55_1h=0,
            ema_11_daily=0,
            ema_55_daily=0,
            adx=0,
            adx_modified=-23,
            adx_strength='DEBIL',
            adx_slope=0,
            adx_trending=False,
            adx_strengthening=False,
            squeeze_momentum=0,
            squeeze_on=True,
            squeeze_just_released=False,
            vpoc=current_price,
            vpoc_distance_pct=0,
            high_volume_levels=[],
            rsi_4h=50
        )
        
        # Crear contexto de mercado
        market_context = MerinoMarketContext(
            macro_trend='UNKNOWN',
            weekly_bias='NEUTRAL',
            daily_bias='NEUTRAL',
            resistance_20d=current_price * 1.05,
            support_20d=current_price * 0.95,
            volatility_20d=0,
            volume_avg_20d=0,
            price_vs_resistance_pct=0,
            price_vs_support_pct=0
        )
        
        # Crear señal
        signal = MerinoSignal(
            signal='NO_SIGNAL',
            signal_strength=0,
            bias_4h='NEUTRAL',
            confluence_score=0,
            reasons=[],
            invalidation_conditions=[],
            optimal_timeframe='4h',
            entry_timing='WAIT_BETTER_SETUP'
        )
        
        # Crear gestión de riesgo
        risk_mgmt = MerinoRiskManagement(
            position_size_pct=0.0
        )
        
        # Crear análisis completo
        analysis = MerinoTradingAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            current_price=current_price,
            indicators=indicators,
            market_context=market_context,
            signal=signal,
            risk_management=risk_mgmt,
            analysis_text=f'Análisis básico para {symbol}',
            recommendation='WAIT - Análisis en desarrollo',
            confidence_level='LOW'
        )
        
        return analysis
        
    except Exception as e:
        # En caso de error, crear análisis de error
        return MerinoTradingAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            current_price=current_price,
            indicators=MerinoTechnicalIndicators(
                ema_11_4h=0, ema_55_4h=0, ema_11_1h=0, ema_55_1h=0,
                ema_11_daily=0, ema_55_daily=0, adx=0, adx_modified=-23,
                adx_strength='DEBIL', adx_slope=0, adx_trending=False,
                adx_strengthening=False, squeeze_momentum=0, squeeze_on=True,
                squeeze_just_released=False, vpoc=current_price,
                vpoc_distance_pct=0, high_volume_levels=[], rsi_4h=50
            ),
            market_context=MerinoMarketContext(
                macro_trend='UNKNOWN', weekly_bias='NEUTRAL', daily_bias='NEUTRAL',
                resistance_20d=current_price*1.05, support_20d=current_price*0.95,
                volatility_20d=0, volume_avg_20d=0, price_vs_resistance_pct=0,
                price_vs_support_pct=0
            ),
            signal=MerinoSignal(
                signal='NO_SIGNAL', signal_strength=0, bias_4h='NEUTRAL',
                confluence_score=0, reasons=[], invalidation_conditions=[],
                optimal_timeframe='4h', entry_timing='WAIT_BETTER_SETUP'
            ),
            risk_management=MerinoRiskManagement(position_size_pct=0.0),
            analysis_text=f'Error generando análisis para {symbol}: {str(e)}',
            recommendation='ERROR - Revisar logs del sistema',
            confidence_level='LOW'
        )