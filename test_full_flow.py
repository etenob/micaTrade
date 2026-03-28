import logging
import sys
import os
from datetime import datetime
from binance_manager import BinanceManager
from trade_manager import TradeManager
from merino_math import JaimeMerinoIndicatorsEngine
from config import Config

# Simular que estamos en vivo para este test especifico
os.environ['IS_LIVE_TRADING'] = 'True'

# Configuración de Logging básica para ver qué pasa
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger("TestFlow")

def run_test_order(symbol="SOLUSDT"):
    print(f"\n🧪 --- INICIANDO TEST DE FLUJO COMPLETO PARA {symbol} ---")
    
    bm = BinanceManager()
    tm = TradeManager()
    
    # 1. Obtener Análisis Real
    print(f"🔍 1. Obteniendo análisis real de {symbol}...")
    analysis = JaimeMerinoIndicatorsEngine.get_real_trading_analysis(symbol)
    if not analysis:
        print("❌ Error: No se pudo obtener el análisis.")
        return

    # 2. Forzar Parámetros de Estrategia (Simulando GATILLO_11)
    strat_name = "GATILLO_11"
    cfg = Config.STRATEGY_CONFIG[strat_name]
    order_amount = cfg['order_amount']
    
    print(f"🚀 2. Simulando SEÑAL {strat_name} detectada. Procediendo a compra de {order_amount} USDT...")
    
    # 3. COMPRA A MERCADO
    # (Esto usará saldo real si la API Key es real)
    buy_order = bm.place_market_buy(symbol, order_amount)
    
    if not buy_order:
        print("❌ Error en la compra. Abortando test.")
        return

    # 4. Procesar Resultados de Compra
    entry_price = float(buy_order['fills'][0]['price']) if buy_order.get('fills') else analysis['current_price']
    qty = float(buy_order['executedQty'])
    print(f"✅ 4. Compra realizada. Precio Entrada: {entry_price} | Qty: {qty}")

    # 5. REGISTRO LOCAL
    # FORZAR NIVELES DE LONG para que el dashboard se vea bien en el test
    print(f"💾 5. Registrando trade en active_trades.json...")
    # Solo para el test, forzamos niveles de LONG reales basados en el precio de entrada
    stop_loss = round(entry_price * 0.99, 2)
    targets = [round(entry_price * 1.01, 2)]
    
    tm.add_active_trade(symbol, strat_name, qty, order_amount, entry_price, targets, stop_loss)
    
    # 6. COLOCAR OCO (Venta de Seguridad)
    print(f"🛡️ 6. Colocando orden OCO (TP y SL)...")
    # Calculamos el limit_price exactamente como lo hace el bot ahora
    limit_price = round(stop_loss * 0.998, 2)
    
    result_oco = bm.place_oco_sell(symbol, qty, targets[0], stop_loss, limit_price)
    
    if result_oco:
        print(f"🌟 TEST EXITOSO: Flujo completado de principio a fin para {symbol}")
        print(f"Id OCO: {result_oco.get('orderListId')}")
    else:
        print("❌ Error al colocar la OCO. Revisa si los precios están demasiado cerca o si falta saldo.")

if __name__ == "__main__":
    # Puedes cambiar el símbolo aquí si preferís probar con otro
    sym = sys.argv[1] if len(sys.argv) > 1 else "SOLUSDT"
    run_test_order(sym)
