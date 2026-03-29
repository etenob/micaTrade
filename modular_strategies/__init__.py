from .base import BaseStrategy
from .alien import AlienStrategy
from .ciega import CiegaStrategy
from .rebote import ReboteStrategy
from .gatillo import GatilloStrategy
from .pingpong import PingPongStrategy
from .sweep_hunter import SweepHunterStrategy
from .heikin_ashi import HeikinAshiStrategy
from .divergence import DivergenceStrategy
from .manager import StrategyManager

# Exponemos las clases para que sea fácil importarlas
__all__ = [
    'BaseStrategy',
    'AlienStrategy',
    'CiegaStrategy',
    'ReboteStrategy',
    'GatilloStrategy',
    'PingPongStrategy',
    'SweepHunterStrategy',
    'HeikinAshiStrategy',
    'DivergenceStrategy',
    'StrategyManager'
]
