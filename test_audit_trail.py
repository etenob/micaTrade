import sys
import os
import json
from datetime import datetime

# Añadimos la ruta de trabajo
sys.path.append(os.getcwd())

from modular_strategies import StrategyManager

def test_audit():
    print("🔬 Iniciando Prueba de Caja Negra (Auditoría)...")
    
    # 1. Simulamos un mercado perfecto para ALIEN
    fake_analysis = {
        "current_price": 65000.0,
        "signal": {
            "signal": "LONG",
            "signal_strength": 98,
            "whale_alert": "BULL_DETECTED",
            "bias": "BULLISH"
        },
        "indicators": {
            "ema": {"ema_55": 60000.0, "ema_11": 64000.0},
            "adx": {"value": 35.0},
            "rsi": {"value": 45.0},
            "nadaraya": {"lower": 59000.0, "upper": 71000.0}
        },
        "trading_levels": {
            "order_blocks": {"bullish_ob_price": 58000.0}
        },
        "multi_tf": {
            "1d": {"bias": "BULLISH"},
            "1h": {"adx": 20, "bias": "NEUTRAL", "squeeze_trend": "UP"}
        }
    }

    manager = StrategyManager()
    
    # 2. Verificamos si hay señal
    active_signals = manager.get_active_signals(fake_analysis)
    print(f"Estrategias disparadas: {active_signals}")

    if "ALIEN" in active_signals:
        print("\n📸 Generando Snapshot de Veredicto para ALIEN...")
        
        # Guardamos el snapshot
        filepath = manager.record_trade_snapshot("ALIEN", fake_analysis, "BTCUSDT", {"order_id": "EXAMPLE_123"})
        
        if filepath and os.path.exists(filepath):
            print(f"✅ Éxito: Snapshot guardado en {filepath}")
            
            # 3. Validamos el contenido del JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print("\n🔍 Validación del contenido del Snapshot:")
                print(f"- Estrategia: {data['metadata']['strategy']}")
                print(f"- Símbolo: {data['metadata']['symbol']}")
                print(f"- Jueces Auditados: {len(data['verdict']['judges'])}")
                
                # Mostramos un juez de ejemplo guardado
                primer_juez = data['verdict']['judges'][0]
                print(f"- Ejemplo de Auditoría: {primer_juez['name']} = {primer_juez['val']}")
        else:
            print("❌ Error: No se generó el archivo de Snapshot.")

if __name__ == "__main__":
    test_audit()
