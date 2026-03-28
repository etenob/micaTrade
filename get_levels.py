from merino_math import JaimeMerinoIndicatorsEngine
import json
a = JaimeMerinoIndicatorsEngine.get_real_trading_analysis('FETUSDT')
print(f"TP1: {a['trading_levels']['targets'][0]}")
print(f"SL: {a['trading_levels']['stop_loss']}")
