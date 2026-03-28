import sys
import os
from datetime import datetime, timedelta

# Añadimos la ruta de trabajo
sys.path.append(os.getcwd())

from modular_strategies import StrategyManager

def test_paciencia():
    print("⏳ Iniciando Prueba de Paciencia Temporal...")
    
    # 1. Simulamos un trade de ALIEN que lleva 9 horas abierto (540 minutos)
    # Su límite configurado es de 480 minutos (8 horas).
    fake_snapshot = {
        "entry_time": (datetime.now() - timedelta(minutes=540)).isoformat()
    }
    
    # 2. El mercado sigue "bien" (EMA 55 OK, ADX OK, Ballena OK)
    fake_analysis = {
        "current_price": 105.0,
        "indicators": {
            "ema": {"ema_55": 100.0},
            "adx": {"value": 25.0},
            "rsi": {"value": 45.0}
        },
        "signal": {
            "whale_alert": "BULL"
        }
    }

    manager = StrategyManager()
    alien = manager.strategies[0] # Alien
    
    print("\n--- 🩺 EXAMEN DE SALUD (Vigencia Superada) ---")
    report = alien.evaluate_performance(fake_snapshot, fake_analysis)
    
    print(f"Salud Total: {report['health_score']}%")
    print(f"Recomendación: {report['recommendation']}")
    
    for reason in report.get('reasons', []):
        print(f">> {reason}")
        
    for judge in report.get('judges', []):
        status = "✅" if judge['ok'] else "❌"
        print(f"{status} {judge['name']}: {judge['val']} (Meta {judge['target']})")

if __name__ == "__main__":
    test_paciencia()
