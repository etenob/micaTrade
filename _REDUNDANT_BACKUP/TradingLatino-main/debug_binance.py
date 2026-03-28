#!/usr/bin/env python3
"""
Script de debugging para verificar conectividad con Binance
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.binance_service import binance_service
import json

def main():
    print("🔍 Debugging Binance Service\n")
    
    # Lista de símbolos para probar
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT']
    
    # Test conexión general
    print("1. Test conexión general:")
    connection_ok = binance_service.test_connection()
    print(f"   {'✅' if connection_ok else '❌'} Conexión: {'OK' if connection_ok else 'FALLA'}\n")
    
    # Test cada símbolo
    for symbol in symbols:
        print(f"2. Test {symbol}:")
        result = binance_service.test_symbol_data(symbol)
        
        print(f"   Conexión: {'✅' if result['connection_ok'] else '❌'}")
        print(f"   Símbolo válido: {'✅' if result['symbol_info'] else '❌'}")
        print(f"   Datos 1h: {result['klines_1h']} velas")
        print(f"   Datos 4h: {result['klines_4h']} velas")
        print(f"   Precio actual: {result['current_price']}")
        
        if result['errors']:
            print(f"   ❌ Errores:")
            for error in result['errors']:
                print(f"      • {error}")
        
        print()

if __name__ == '__main__':
    main()