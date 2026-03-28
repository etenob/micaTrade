import json
import time
import os
from datetime import datetime, timedelta
from bot_multi_strategy import sync_active_trades
from trade_manager import TradeManager
from binance_manager import BinanceManager

def test_sync_protection():
    tm = TradeManager()
    bm = BinanceManager()
    path = 'active_trades.json'
    symbol = "BTCUSDT" # Usamos uno real para evitar error -1121
    
    # 1. Limpiar BTCUSDT si existe
    tm.close_trade(symbol, 1.0, "Cleanup Test")
    
    # 2. Crear un trade "NUEVO" (hace 10 segundos)
    new_trade = {
        "symbol": symbol,
        "detected_at": datetime.now().isoformat(),
        "strategy": "TEST",
        "quantity": 0.0001,
        "entry_price": 60000.0,
        "targets": [70000.0],
        "stop_loss": 50000.0,
        "usdt_value": 6.0
    }
    
    trades = []
    if os.path.exists(path):
        with open(path, 'r') as f:
            trades = json.load(f)
    
    trades.append(new_trade)
    with open(path, 'w') as f:
        json.dump(trades, f, indent=4)
        
    print(f"--- TEST PROTECCIÓN SYNC PARA {symbol} ---")
    print(f"Trade añadido con timestamp: {new_trade['detected_at']}")
    
    # 3. Ejecutar sync_active_trades
    print("Ejecutando sync_active_trades (Asumiendo que NO hay órdenes de BTC)...")
    sync_active_trades()
    
    # 4. Verificar si sigue ahí
    if tm.get_active_trade(symbol):
        print("✅ ÉXITO: El trade NUEVO fue protegido.")
    else:
        print("❌ FALLO: El trade NUEVO fue borrado prematuramente.")
        
    # 5. Simular trade VIEJO (hace 10 minutos)
    old_time = (datetime.now() - timedelta(minutes=10)).isoformat()
    with open(path, 'r') as f:
        trades = json.load(f)
    for t in trades:
        if t['symbol'] == symbol:
            t['detected_at'] = old_time
    with open(path, 'w') as f:
        json.dump(trades, f, indent=4)
        
    print(f"\nModificando {symbol} a timestamp VIEJO: {old_time}")
    sync_active_trades()
    
    if not tm.get_active_trade(symbol):
        print("✅ ÉXITO: El trade VIEJO fue procesado y borrado.")
    else:
        print("❌ FALLO: El trade VIEJO sigue ahí (¿Quizás tienes órdenes reales de BTC abiertas?)")

if __name__ == "__main__":
    test_sync_protection()
