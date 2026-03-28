#!/usr/bin/env python3
"""
Script para probar la obtención de precio actual
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.binance_service import binance_service

def test_price_methods():
    """Prueba diferentes métodos para obtener precio"""
    symbol = 'BTCUSDT'
    
    print(f"🧪 Probando obtención de precio para {symbol}\n")
    
    # Test 1: Método principal
    print("1. Método get_current_price():")
    try:
        price = binance_service.get_current_price(symbol)
        if price:
            print(f"   ✅ Precio: ${price:,.4f}")
        else:
            print(f"   ❌ No se pudo obtener precio")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Método avanzado (si lo implementaste)
    print("\n2. Método get_current_price_advanced():")
    try:
        price = binance_service.get_current_price_advanced(symbol)
        if price:
            print(f"   ✅ Precio: ${price:,.4f}")
        else:
            print(f"   ❌ No se pudo obtener precio")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Market data
    print("\n3. Método get_market_data():")
    try:
        market_data = binance_service.get_market_data(symbol)
        if market_data:
            print(f"   ✅ Precio: ${market_data.close_price:,.4f}")
            print(f"   📊 Volumen: {market_data.volume:,.0f}")
            print(f"   📈 Cambio: {market_data.price_change_percent:+.2f}%")
        else:
            print(f"   ❌ No se pudo obtener market data")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    test_price_methods()