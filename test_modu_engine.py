import sys
import os
from datetime import datetime

# Añadimos la ruta para poder importar nuestro módulo modular
sys.path.append(os.getcwd())

from modular_strategies import StrategyManager

def test_engine():
    print("🧪 Iniciando Laboratorio de Jueces (Motor Modular)...")
    
    # Simulamos un análisis de mercado donde:
    # - La señal es LONG y fuerza 95% (OK para Alien)
    # - El precio está sobre la EMA 55 (OK para Alien)
    # - PERO: El ADX está en 24 (Debería fallar Alien que pide 25)
    fake_analysis = {
        "current_price": 105.0,
        "signal": {
            "signal": "LONG",
            "signal_strength": 95,
            "whale_alert": "BULL",
            "bias": "BULLISH"
        },
        "indicators": {
            "ema": {"ema_55": 100.0, "ema_11": 104.0},
            "adx": {"value": 24.0},
            "rsi": {"value": 45.0},
            "nadaraya": {"lower": 95.0, "upper": 115.0}
        },
        "trading_levels": {
            "order_blocks": {"bullish_ob_price": 98.0}
        },
        "multi_tf": {
            "1d": {"bias": "BULLISH"},
            "1h": {"adx": 20, "bias": "NEUTRAL", "squeeze_trend": "UP"}
        }
    }

    manager = StrategyManager()
    
    print("\n--- 🕵️ REPORTE DE JUICIO (Alien) ---")
    report = manager.get_strategy_report(fake_analysis)
    alien_report = report.get('alien', {})
    
    for judge in alien_report.get('judges', []):
        status = "✅" if judge['ok'] else "❌"
        print(f"{status} {judge['name']}: Medido {judge['val']} (Buscaba {judge['target']})")
    
    triggered = "SI" if alien_report.get('triggered') else "NO"
    print(f"\n>> ¿DISPARÓ ALIEN? {triggered}")
    if not alien_report.get('triggered'):
        print(">> MOTIVO: El Juez de ADX no dio su aprobación.")

if __name__ == "__main__":
    test_engine()
