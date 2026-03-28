import sys
import os
from datetime import datetime, timedelta

# Añadimos la ruta de trabajo
sys.path.append(os.getcwd())

from modular_strategies import StrategyManager

def test_salud_v2():
    print("🔬 Probando Tribunal de Salud Estructurado...")
    
    manager = StrategyManager()
    alien = manager.strategies[0] # Alien
    
    # Simulación de un trade que se está 'agriando':
    # - 9 horas abiertas (540m > 480m)
    # - Precio cayó un poco (bajo EMA 55)
    # - ADX bajó un poco (momentum débil)
    fake_snapshot = {
        "entry_time": (datetime.now() - timedelta(minutes=540)).isoformat()
    }
    
    fake_analysis = {
        "current_price": 99.0, # Soporte EMA era 100.0
        "indicators": {
            "ema": {"ema_55": 100.0},
            "adx": {"value": 19.5}, # Umbral era 20
            "rsi": {"value": 45.0}
        },
        "signal": {
            "whale_alert": "BULL_GONE" # Las ballenas ya no están
        }
    }

    print("\n--- 🩺 AUDITORÍA DE SALUD (Alien) ---")
    report = alien.evaluate_performance(fake_snapshot, fake_analysis)
    
    print(f"Salud Final: {report['health_score']}%")
    print(f"Recomendación: {report['recommendation']}")
    
    print("\nVERDICTOS DEL TRIBUNAL:")
    for judge in report.get('judges', []):
        status = "✅" if judge['ok'] else "❌"
        print(f"{status} {judge['name']}: {judge['val']} (Meta {judge['target']})")
    
    print("\nMOTIVOS DE PENALIZACIÓN:")
    for reason in report.get('reasons', []):
        print(f">> {reason}")

if __name__ == "__main__":
    test_salud_v2()
