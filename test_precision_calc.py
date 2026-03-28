from binance_manager import BinanceManager
from config import Config

def test_precision():
    bm = BinanceManager()
    
    # Simular PEPEUSDT (Precio muy bajo)
    symbol = "PEPEUSDT"
    price = 0.00000854
    
    print(f"--- TEST DE PRECISIÓN PARA {symbol} ---")
    print(f"Precio Base: {price}")
    
    # 1. Calcular niveles %
    tp = price * 1.03
    sl = price * 0.97
    lp = sl * 0.998
    
    print(f"TP Bruto: {tp}")
    print(f"SL Bruto: {sl}")
    print(f"LP Bruto: {lp}")
    
    # 2. Formatear usando la nueva lógica
    tp_str = bm.format_price_str(symbol, tp)
    sl_str = bm.format_price_str(symbol, sl)
    lp_str = bm.format_price_str(symbol, lp)
    
    print(f"\nTP Formateado: {tp_str}")
    print(f"SL Formateado: {sl_str}")
    print(f"LP Formateado: {lp_str}")
    
    if float(sl_str) == 0:
        print("❌ FALLO: El SL se redondeó a cero.")
    else:
        print("✅ ÉXITO: El SL mantiene precisión.")

if __name__ == "__main__":
    test_precision()
