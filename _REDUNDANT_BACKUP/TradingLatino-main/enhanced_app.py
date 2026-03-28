"""
🚀 Jaime Merino Trading Bot - Usando template merino_dashboard.html
📈 Conectado con el dashboard profesional existente
"""

import os
import sys
import json
import time
import random
import threading
import requests
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import sys
from typing import Dict, Optional, List
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.binance_service import BinanceService
    BINANCE_SERVICE_AVAILABLE = True
    print("✅ BinanceService importado correctamente")
except ImportError as e:
    BINANCE_SERVICE_AVAILABLE = False
    binance_service = None
    print(f"⚠️ No se pudo importar BinanceService: {e}")

# Importar el servicio de Binance refactorizado
# Inicializar servicio real de Binance
binance_service = BinanceService()

BASE_PRICES = {
    'BTCUSDT': 67000,   # Actualizado - precio aproximado actual
    'ETHUSDT': 3200,    # Actualizado - precio aproximado actual
    'BNBUSDT': 580,
    'ADAUSDT': 0.45,
    'SOLUSDT': 185,
    'XRPUSDT': 0.62,
    'DOGEUSDT': 0.12,
    'MATICUSDT': 0.55,
    'LINKUSDT': 15.50,
    'AVAXUSDT': 28.00
}
# Importar SocketIO con manejo de errores
try:
    from flask_socketio import SocketIO, emit
    SOCKETIO_AVAILABLE = True
    print("✅ SocketIO disponible")
except ImportError:
    SOCKETIO_AVAILABLE = False
    print("⚠️ SocketIO no disponible - modo básico")

print("🚀 Iniciando Jaime Merino Trading Bot")
print(f"🐍 Python: {sys.version}")
print(f"📡 SocketIO: {SOCKETIO_AVAILABLE}")

# Configuración de Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'jaime-merino-2024')

# Configurar SocketIO si está disponible
if SOCKETIO_AVAILABLE:
    socketio = SocketIO(app, cors_allowed_origins="*")
else:
    socketio = None

# Variables globales
trading_data = {}
clients_connected = 0
server_start_time = datetime.now()
last_prices = {}

# Configuración específica para template merino_dashboard.html
SYMBOLS = ['BTCUSDT', 'ETHUSDT']  # Simplificado para coincidir con el template


def get_real_price_reference() -> Dict[str, float]:
    """
    FUNCIÓN PRINCIPAL: Obtiene precios reales de Binance con fallbacks robustos
    
    Returns:
        Diccionario con precios reales {symbol: price}
    """
    print(f"🔍 Obteniendo precios reales para {len(SYMBOLS)} símbolos...")
    
    # Método 1: BinanceService refactorizado (PREFERIDO)
    if BINANCE_SERVICE_AVAILABLE and binance_service:
        binance_prices = _get_binance_service_prices()
        if binance_prices and len(binance_prices) >= len(SYMBOLS) * 0.8:  # 80% éxito
            print(f"✅ Precios de BinanceService: {len(binance_prices)}/{len(SYMBOLS)}")
            return _complete_missing_prices(binance_prices)
    
    # Método 2: API directa de Binance (BACKUP)
    binance_api_prices = _get_binance_api_direct()
    if binance_api_prices and len(binance_api_prices) >= len(SYMBOLS) * 0.6:  # 60% éxito
        print(f"✅ Precios de Binance API directa: {len(binance_api_prices)}/{len(SYMBOLS)}")
        return _complete_missing_prices(binance_api_prices)
    
    # Método 3: CoinGecko (BACKUP EXTERNO)
    coingecko_prices = _get_coingecko_prices()
    if coingecko_prices and len(coingecko_prices) >= 2:  # Al menos BTC y ETH
        print(f"⚠️ Usando precios de CoinGecko: {len(coingecko_prices)}/{len(SYMBOLS)}")
        return _complete_missing_prices(coingecko_prices)
    
    # Método 4: Precios base actualizados (ÚLTIMO RECURSO)
    print("🚨 USANDO PRECIOS BASE - REVISAR CONEXIÓN A INTERNET")
    return BASE_PRICES

def _get_binance_service_prices() -> Optional[Dict[str, float]]:
    """
    Obtiene precios usando el BinanceService refactorizado
    """
    try:
        # Test de conexión rápido
        if not binance_service.test_connection():
            print("❌ BinanceService: conexión fallida")
            return None
        
        # Obtener precios múltiples de manera eficiente
        prices = binance_service.get_multiple_prices(SYMBOLS)
        
        if not prices:
            print("❌ BinanceService: no se obtuvieron precios")
            return None
        
        # Validar precios obtenidos
        valid_prices = {}
        for symbol, price in prices.items():
            if price and price > 0:
                # Validación adicional: precio debe estar en rango razonable
                base_price = BASE_PRICES.get(symbol, 0)
                if base_price > 0:
                    # Precio no puede estar más de 50% fuera del rango esperado
                    price_ratio = price / base_price
                    if 0.5 <= price_ratio <= 2.0:
                        valid_prices[symbol] = price
                    else:
                        print(f"⚠️ Precio sospechoso para {symbol}: ${price:,.2f} (esperado ~${base_price:,.2f})")
                else:
                    valid_prices[symbol] = price
        
        failed_symbols = set(SYMBOLS) - set(valid_prices.keys())
        if failed_symbols:
            print(f"⚠️ No se obtuvieron precios válidos para: {failed_symbols}")
        
        return valid_prices if valid_prices else None
        
    except Exception as e:
        print(f"❌ Error en _get_binance_service_prices: {e}")
        return None

def _get_binance_api_direct() -> Optional[Dict[str, float]]:
    """
    Obtiene precios directamente de la API de Binance sin usar el servicio
    """
    try:
        print("🔄 Intentando API directa de Binance...")
        
        # Obtener todos los precios de una vez
        url = "https://api.binance.com/api/v3/ticker/price"
        
        headers = {
            'User-Agent': 'JaimeMerino-TradingBot/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        all_tickers = response.json()
        
        # Filtrar solo los símbolos que necesitamos
        prices = {}
        for ticker in all_tickers:
            symbol = ticker['symbol']
            if symbol in SYMBOLS:
                price = float(ticker['price'])
                if price > 0:
                    prices[symbol] = price
        
        print(f"📈 API directa: {len(prices)}/{len(SYMBOLS)} precios obtenidos")
        return prices if prices else None
        
    except requests.exceptions.Timeout:
        print("❌ API directa: Timeout")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ API directa: Error de conexión")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ API directa: Error HTTP {e}")
        return None
    except Exception as e:
        print(f"❌ Error en API directa: {e}")
        return None

def _get_coingecko_prices() -> Optional[Dict[str, float]]:
    """
    Obtiene precios de CoinGecko como backup externo
    """
    try:
        print("🔄 Intentando CoinGecko como backup...")
        
        # Mapeo de símbolos de trading a IDs de CoinGecko
        coingecko_mapping = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'BNBUSDT': 'binancecoin',
            'ADAUSDT': 'cardano',
            'SOLUSDT': 'solana',
            'XRPUSDT': 'ripple',
            'DOGEUSDT': 'dogecoin',
            'MATICUSDT': 'matic-network',
            'LINKUSDT': 'chainlink',
            'AVAXUSDT': 'avalanche-2'
        }
        
        # Obtener solo los IDs que necesitamos y están disponibles
        needed_ids = []
        available_symbols = []
        for symbol in SYMBOLS:
            if symbol in coingecko_mapping:
                needed_ids.append(coingecko_mapping[symbol])
                available_symbols.append(symbol)
        
        if not needed_ids:
            print("⚠️ CoinGecko: No hay símbolos mapeados")
            return None
        
        ids_param = ','.join(needed_ids)
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids_param}&vs_currencies=usd'
        
        headers = {
            'User-Agent': 'JaimeMerino-TradingBot/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        # Convertir de vuelta a símbolos de trading
        prices = {}
        reverse_mapping = {v: k for k, v in coingecko_mapping.items()}
        
        for coin_id, price_data in data.items():
            symbol = reverse_mapping.get(coin_id)
            if symbol and symbol in SYMBOLS:
                price = price_data.get('usd')
                if price and price > 0:
                    prices[symbol] = price
        
        print(f"🦎 CoinGecko: {len(prices)}/{len(available_symbols)} precios obtenidos")
        return prices if prices else None
        
    except Exception as e:
        print(f"❌ Error en CoinGecko: {e}")
        return None

def _complete_missing_prices(partial_prices: Dict[str, float]) -> Dict[str, float]:
    """
    Completa precios faltantes con precios base actualizados
    
    Args:
        partial_prices: Diccionario con algunos precios obtenidos
        
    Returns:
        Diccionario completo con todos los símbolos
    """
    complete_prices = partial_prices.copy()
    
    missing_symbols = []
    for symbol in SYMBOLS:
        if symbol not in complete_prices:
            complete_prices[symbol] = BASE_PRICES.get(symbol, 1000.0)  # Fallback genérico
            missing_symbols.append(symbol)
    
    if missing_symbols:
        print(f"⚠️ Usando precios base para: {missing_symbols}")
    
    return complete_prices

def validate_prices(prices: Dict[str, float]) -> Dict[str, float]:
    """
    Valida que los precios sean lógicos y no estén fuera de rango
    
    Args:
        prices: Diccionario de precios a validar
        
    Returns:
        Diccionario de precios validados
    """
    validated_prices = {}
    
    for symbol, price in prices.items():
        if not price or price <= 0:
            print(f"❌ Precio inválido para {symbol}: {price}")
            price = BASE_PRICES.get(symbol, 1000.0)
        
        # Validaciones específicas por tipo de activo
        if symbol == 'BTCUSDT':
            if price < 20000 or price > 150000:  # Rango razonable para BTC
                print(f"⚠️ Precio BTC fuera de rango: ${price:,.2f}")
                price = BASE_PRICES['BTCUSDT']
        elif symbol == 'ETHUSDT':
            if price < 1000 or price > 10000:  # Rango razonable para ETH
                print(f"⚠️ Precio ETH fuera de rango: ${price:,.2f}")
                price = BASE_PRICES['ETHUSDT']
        elif 'USDT' in symbol:
            # Para otros pares USDT, verificar que no sean extremos
            base_price = BASE_PRICES.get(symbol, 0)
            if base_price > 0:
                ratio = price / base_price
                if ratio < 0.1 or ratio > 10:  # Variación máxima 10x
                    print(f"⚠️ Precio {symbol} fuera de rango: ${price:,.6f}")
                    price = base_price
        
        validated_prices[symbol] = price
    
    return validated_prices

def get_price_statistics(prices: Dict[str, float]) -> Dict[str, any]:
    """
    Genera estadísticas de los precios obtenidos
    
    Args:
        prices: Diccionario de precios
        
    Returns:
        Diccionario con estadísticas
    """
    stats = {
        'total_symbols': len(SYMBOLS),
        'prices_obtained': len(prices),
        'success_rate': (len(prices) / len(SYMBOLS)) * 100,
        'timestamp': datetime.now().isoformat(),
        'price_summary': {}
    }
    
    # Calcular cambios respecto a precios base
    for symbol in SYMBOLS:
        current_price = prices.get(symbol, 0)
        base_price = BASE_PRICES.get(symbol, 0)
        
        if current_price > 0 and base_price > 0:
            change_pct = ((current_price - base_price) / base_price) * 100
            stats['price_summary'][symbol] = {
                'current': current_price,
                'base': base_price,
                'change_pct': round(change_pct, 2),
                'status': 'updated' if abs(change_pct) > 1 else 'stable'
            }
        else:
            stats['price_summary'][symbol] = {
                'current': current_price,
                'base': base_price,
                'status': 'error'
            }
    
    return stats


# CORRECCIÓN EXACTA PARA enhanced_app.py
# ===================================
# Reemplaza la función generate_enhanced_analysis() existente

def generate_enhanced_analysis(symbol, current_price):
    """
    Genera análisis completo para el template merino_dashboard.html
    *** VERSIÓN CORREGIDA CON ESTRUCTURA TRADING_LEVELS ***
    """
    
    # Indicadores técnicos simulados (mantén tu lógica existente)
    rsi = random.uniform(25, 75)
    ema_11 = current_price * random.uniform(0.98, 1.02)
    ema_55 = current_price * random.uniform(0.95, 1.05)
    adx = random.uniform(20, 60)
    macd = (current_price - BASE_PRICES.get(symbol, current_price)) * 0.001
    
    # Bollinger Bands
    bb_middle = current_price
    bb_upper = current_price * 1.02
    bb_lower = current_price * 0.98
    
    # Determinar trend
    trend = 'BULLISH' if ema_11 > ema_55 else 'BEARISH'
    
    # Generar señal
    signals = ['LONG', 'SHORT', 'WAIT', 'NO_SIGNAL']
    
    # Probabilidades diferentes por símbolo para variedad
    if symbol == 'BTCUSDT':
        weights = [0.4, 0.3, 0.2, 0.1]  # BTC más probabilidad LONG
    else:
        weights = [0.3, 0.3, 0.2, 0.2]
    
    signal = random.choices(signals, weights=weights)[0]
    
    # Calcular signal strength
    if signal in ['LONG', 'SHORT']:
        signal_strength = random.randint(60, 95)
    elif signal == 'WAIT':
        signal_strength = random.randint(40, 70)
    else:
        signal_strength = 0
    
    # *** CALCULAR NIVELES DE TRADING - AQUÍ ESTÁ EL FIX ***
    if signal == 'LONG':
        entry_optimal = current_price * 1.001  # Entrada ligeramente arriba
        entry_range_low = current_price * 0.999
        entry_range_high = current_price * 1.005
        target_1 = current_price * 1.02  # +2%
        target_2 = current_price * 1.05  # +5%
        target_3 = current_price * 1.08  # +8%
        stop_loss = current_price * 0.98  # -2%
        
    elif signal == 'SHORT':
        entry_optimal = current_price * 0.999  # Entrada ligeramente abajo
        entry_range_low = current_price * 0.995
        entry_range_high = current_price * 1.001
        target_1 = current_price * 0.98  # -2%
        target_2 = current_price * 0.95  # -5%
        target_3 = current_price * 0.92  # -8%
        stop_loss = current_price * 1.02  # +2%
        
    else:
        # Sin señal válida - usar precio actual
        entry_optimal = current_price
        entry_range_low = current_price
        entry_range_high = current_price
        target_1 = current_price
        target_2 = current_price
        target_3 = current_price
        stop_loss = current_price
    
    # Calcular risk/reward
    risk_amount = abs(entry_optimal - stop_loss)
    reward_amount = abs(target_1 - entry_optimal)
    risk_reward = reward_amount / risk_amount if risk_amount > 0 else 0
    
    # *** ESTRUCTURA CORREGIDA - LO QUE EL FRONTEND ESPERA ***
    return {
        'symbol': symbol,
        'current_price': current_price,
        'signal': {
            'signal': signal,
            'signal_strength': signal_strength,
            'confluence_score': random.randint(0, 4),
            'bias': trend
        },
        'indicators': {
            'rsi': {
                'value': round(rsi, 1),
                'status': 'OVERSOLD' if rsi < 30 else 'OVERBOUGHT' if rsi > 70 else 'NEUTRAL'
            },
            'ema': {
                'ema_11': round(ema_11, 2),
                'ema_55': round(ema_55, 2),
                'trend': trend
            },
            'adx': {
                'value': round(adx, 1),
                'strength': 'STRONG' if adx > 25 else 'WEAK'
            },
            'macd': {
                'value': round(macd, 6),
                'signal': 'BULLISH' if macd > 0 else 'BEARISH'
            },
            'bollinger': {
                'upper': round(bb_upper, 2),
                'middle': round(bb_middle, 2),
                'lower': round(bb_lower, 2)
            }
        },
        # *** ✅ ESTA ES LA ESTRUCTURA QUE EL FRONTEND BUSCA ***
        'trading_levels': {
            'entry_optimal': round(entry_optimal, 2),
            'entry_range': {
                'low': round(entry_range_low, 2),
                'high': round(entry_range_high, 2)
            },
            'targets': [
                round(target_1, 2),
                round(target_2, 2),
                round(target_3, 2)
            ],
            'stop_loss': round(stop_loss, 2),
            'position_size_pct': 2.0,
            'leverage': {
                'recommended': 2.0 if signal != 'NO_SIGNAL' else 1.0,
                'max': 3.0
            },
            'risk_reward': round(risk_reward, 2)
        },
        # *** MANTENER TAMBIÉN LA ESTRUCTURA ORIGINAL PARA COMPATIBILIDAD ***
        'futures_setup': {
            'entry': {
                'optimal': round(entry_optimal, 2),
                'range_low': round(entry_range_low, 2),
                'range_high': round(entry_range_high, 2)
            },
            'targets': {
                'target_1': round(target_1, 2),
                'target_2': round(target_2, 2),
                'target_3': round(target_3, 2)
            },
            'risk_management': {
                'stop_loss': round(stop_loss, 2),
                'invalidation': round(stop_loss * 1.005, 2),
                'risk_reward': round(risk_reward, 2)
            }
        },
        'last_update': datetime.now().strftime('%H:%M:%S'),
        'timestamp': int(time.time())
    }

# *** INSTRUCCIONES DE IMPLEMENTACIÓN ***
# =====================================
# 1. Busca la función generate_enhanced_analysis() en tu enhanced_app.py
# 2. Reemplázala COMPLETAMENTE con esta versión
# 3. Guarda el archivo
# 4. Reinicia el servidor: python enhanced_app.py
# 5. Las entradas deberían aparecer correctamente

# *** CÓMO VERIFICAR QUE FUNCIONÓ ***
# =================================
# 1. Abre el navegador en tu dashboard
# 2. Presiona F12 para abrir las herramientas de desarrollador
# 3. Ve a la pestaña Console
# 4. Deberías ver logs como: "✅ Entrada optimal BTCUSDT: 45123.45"
# 5. Las tarjetas ya no deberían mostrar $0.00 en las entradas

# FUNCIÓN PARA ACTUALIZAR generate_trading_data()
def generate_trading_data():
    """
    Versión corregida que genera la estructura correcta
    """
    global last_prices
    
    # Obtener precios reales
    raw_prices = get_real_price_reference()
    validated_prices = validate_prices(raw_prices)
    
    # Generar estadísticas
    price_stats = get_price_statistics(validated_prices)
    print(f"📊 Tasa de éxito: {price_stats['success_rate']:.1f}%")
    
    # Generar datos de trading con estructura corregida
    data = {}
    for symbol in SYMBOLS:
        current_price = validated_prices.get(symbol, BASE_PRICES.get(symbol, 1000))
        
        # Verificar cambio de precio
        if symbol in last_prices:
            price_change = ((current_price - last_prices[symbol]) / last_prices[symbol]) * 100
            if abs(price_change) > 0.1:
                print(f"💹 {symbol}: ${last_prices[symbol]:,.2f} → ${current_price:,.2f} ({price_change:+.2f}%)")
        
        # ✅ GENERAR ANÁLISIS CON ESTRUCTURA CORREGIDA
        try:
            data[symbol] = generate_trading_analysis(symbol, current_price)
            entry_price = data[symbol]['trading_levels']['entry_optimal']
            signal_info = data[symbol]['signal']
            print(f"✅ {symbol}: ${current_price:.2f} - {signal_info['signal']} ({signal_info['signal_strength']}%) - Entrada: ${entry_price}")
            
        except Exception as e:
            print(f"❌ Error procesando {symbol}: {e}")
            # Datos de fallback con estructura correcta
            data[symbol] = {
                'symbol': symbol,
                'current_price': current_price,
                'signal': {'signal': 'LOADING', 'signal_strength': 0, 'confluence_score': 0},
                'trading_levels': {
                    'entry_optimal': current_price,
                    'entry_range': {'low': current_price, 'high': current_price},
                    'targets': [current_price, current_price, current_price],
                    'stop_loss': current_price
                },
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
        
        # Actualizar last_prices
        last_prices[symbol] = current_price
    
    return data

def generate_trading_analysis(symbol, current_price):
    """
    Genera análisis de trading con estructura corregida para el frontend
    """
    
    # Simular datos de EMA (reemplaza con tu lógica real)
    ema_11 = current_price * random.uniform(0.995, 1.005)
    ema_55 = current_price * random.uniform(0.990, 1.010)
    
    # Determinar trend básico
    trend = 'BULLISH' if ema_11 > ema_55 else 'BEARISH'
    
    # Generar señal
    signals = ['LONG', 'SHORT', 'WAIT', 'NO_SIGNAL']
    weights = [0.3, 0.3, 0.2, 0.2]
    signal = random.choices(signals, weights=weights)[0]
    
    # Calcular strength
    if signal in ['LONG', 'SHORT']:
        signal_strength = random.randint(60, 95)
    elif signal == 'WAIT':
        signal_strength = random.randint(40, 70)
    else:
        signal_strength = 0
    
    # CALCULAR NIVELES DE TRADING (ESTRUCTURA CORREGIDA)
    if signal == 'LONG':
        entry_optimal = current_price * 1.001  # Entrada ligeramente arriba
        entry_range_low = current_price * 0.999
        entry_range_high = current_price * 1.005
        target_1 = current_price * 1.02  # +2%
        target_2 = current_price * 1.05  # +5%
        target_3 = current_price * 1.08  # +8%
        stop_loss = current_price * 0.98  # -2%
        
    elif signal == 'SHORT':
        entry_optimal = current_price * 0.999  # Entrada ligeramente abajo
        entry_range_low = current_price * 0.995
        entry_range_high = current_price * 1.001
        target_1 = current_price * 0.98  # -2%
        target_2 = current_price * 0.95  # -5%
        target_3 = current_price * 0.92  # -8%
        stop_loss = current_price * 1.02  # +2%
        
    else:
        # Sin señal válida - usar precio actual como base
        entry_optimal = current_price
        entry_range_low = current_price
        entry_range_high = current_price
        target_1 = current_price
        target_2 = current_price
        target_3 = current_price
        stop_loss = current_price
    
    # ESTRUCTURA CORREGIDA - Lo que el frontend espera
    return {
        'symbol': symbol,
        'current_price': current_price,
        'signal': {
            'signal': signal,
            'signal_strength': signal_strength,
            'confluence_score': random.randint(0, 4),
            'bias': trend,
            'timeframe_4h': {'trend': trend},
            'timeframe_1h': {'trend': trend},
            'volume_profile': {'vpoc': current_price * random.uniform(0.98, 1.02)}
        },
        # ✅ ESTA ES LA ESTRUCTURA QUE EL FRONTEND ESPERA
        'trading_levels': {
            'entry_optimal': round(entry_optimal, 2),
            'entry_range': {
                'low': round(entry_range_low, 2),
                'high': round(entry_range_high, 2)
            },
            'targets': [
                round(target_1, 2),
                round(target_2, 2),
                round(target_3, 2)
            ],
            'stop_loss': round(stop_loss, 2),
            'position_size_pct': 2.0,
            'leverage': {
                'recommended': 2.0 if signal != 'NO_SIGNAL' else 1.0,
                'max': 3.0
            },
            'risk_reward': round(abs(target_1 - entry_optimal) / abs(stop_loss - entry_optimal), 2) if stop_loss != entry_optimal else 0.0
        },
        'indicators': {
            'rsi': {
                'value': round(random.uniform(25, 75), 1),
                'status': 'OVERSOLD' if random.uniform(25, 75) < 30 else 'OVERBOUGHT' if random.uniform(25, 75) > 70 else 'NEUTRAL'
            },
            'ema': {
                'ema_11': round(ema_11, 2),
                'ema_55': round(ema_55, 2),
                'trend': trend
            },
            'adx': {
                'value': round(random.uniform(15, 45), 1),
                'strength': 'STRONG' if random.uniform(15, 45) > 25 else 'WEAK'
            },
            'macd': {
                'value': round(random.uniform(-0.01, 0.01), 6),
                'signal': 'BULLISH' if random.uniform(-0.01, 0.01) > 0 else 'BEARISH'
            }
        },
        'last_update': datetime.now().strftime('%H:%M:%S'),
        'timestamp': int(time.time())
    }
def background_worker():
    """Hilo de trabajo optimizado"""
    global trading_data, clients_connected
    
    print("🔄 Iniciando worker de análisis para dashboard Merino...")
    
    while True:
        try:
            # Generar nuevos datos
            trading_data = generate_trading_data()
            
            # Emitir datos si hay SocketIO y clientes
            if SOCKETIO_AVAILABLE and socketio and clients_connected > 0:
                socketio.emit('analysis_update', {
                    'data': trading_data,
                    'timestamp': datetime.now().isoformat(),
                    'clients': clients_connected,
                    'philosophy': "El arte de tomar dinero de otros legalmente",
                    'update_type': 'background'
                })
                print(f"📊 Análisis enviado a {clients_connected} clientes")
            
            # Pausa de 2 minutos
            time.sleep(120)
            
        except Exception as e:
            print(f"❌ Error en worker: {e}")
            time.sleep(180)

def get_real_prices():
    """Obtiene precios reales de Binance"""
    real_prices = {}
    
    for symbol in SYMBOLS:
        try:
            # Método 1: Precio directo
            price = binance_service.get_current_price(symbol)
            if price:
                real_prices[symbol] = price
                continue
                
            # Método 2: Market data completo
            market_data = binance_service.get_market_data(symbol)
            if market_data:
                real_prices[symbol] = market_data.close_price
                continue
                
            # Método 3: Solo como último recurso usar fallback
            real_prices[symbol] = BASE_PRICES.get(symbol, 0)
            print(f"⚠️ Usando precio fallback para {symbol}")
            
        except Exception as e:
            print(f"❌ Error obteniendo precio real {symbol}: {e}")
            real_prices[symbol] = BASE_PRICES.get(symbol, 0)
    
    return real_prices

def test_all_price_sources():
    """
    Función de prueba completa para verificar todas las fuentes
    """
    print("\n" + "="*60)
    print("🧪 PROBANDO TODAS LAS FUENTES DE PRECIOS")
    print("="*60)
    
    test_symbols = ['BTCUSDT', 'ETHUSDT']
    
    # Test 1: BinanceService
    print("\n1. 🔹 BinanceService:")
    if BINANCE_SERVICE_AVAILABLE:
        start_time = time.time()
        binance_prices = _get_binance_service_prices()
        elapsed = time.time() - start_time
        
        if binance_prices:
            print(f"   ✅ Éxito en {elapsed:.2f}s:")
            for symbol in test_symbols:
                price = binance_prices.get(symbol)
                if price:
                    print(f"      {symbol}: ${price:,.2f}")
        else:
            print("   ❌ No disponible")
    else:
        print("   ❌ Servicio no importado")
    
    # Test 2: API directa
    print("\n2. 🔹 Binance API Directa:")
    start_time = time.time()
    api_prices = _get_binance_api_direct()
    elapsed = time.time() - start_time
    
    if api_prices:
        print(f"   ✅ Éxito en {elapsed:.2f}s:")
        for symbol in test_symbols:
            price = api_prices.get(symbol)
            if price:
                print(f"      {symbol}: ${price:,.2f}")
    else:
        print("   ❌ No disponible")
    
    # Test 3: CoinGecko
    print("\n3. 🔹 CoinGecko:")
    start_time = time.time()
    gecko_prices = _get_coingecko_prices()
    elapsed = time.time() - start_time
    
    if gecko_prices:
        print(f"   ✅ Éxito en {elapsed:.2f}s:")
        for symbol in test_symbols:
            price = gecko_prices.get(symbol)
            if price:
                print(f"      {symbol}: ${price:,.2f}")
    else:
        print("   ❌ No disponible")
    
    # Test 4: Función principal
    print("\n4. 🔹 Función Principal:")
    start_time = time.time()
    final_prices = get_real_price_reference()
    elapsed = time.time() - start_time
    
    print(f"   ✅ Completado en {elapsed:.2f}s:")
    for symbol in test_symbols:
        price = final_prices.get(symbol, 0)
        print(f"      {symbol}: ${price:,.2f}")
    
    # Estadísticas finales
    stats = get_price_statistics(final_prices)
    print(f"\n📈 Estadísticas:")
    print(f"   • Tasa de éxito: {stats['success_rate']:.1f}%")
    print(f"   • Símbolos: {stats['prices_obtained']}/{stats['total_symbols']}")
    
    print("\n✅ Prueba completada")
    print("="*60)


@app.route('/')
def home():
    """Página principal usando merino_dashboard.html"""
    global trading_data
    
    try:
        # Generar datos iniciales si no existen
        if not trading_data:
            print("🔄 Generando datos de trading iniciales...")
            trading_data = generate_trading_data()  # Llamará a la versión actualizada
            print(f"✅ Datos generados para {len(trading_data)} símbolos")
        
        # Debug: Verificar que tenemos trading_levels
        for symbol, data in trading_data.items():
            if 'trading_levels' not in data:
                print(f"⚠️ FALTA trading_levels en {symbol}")
            else:
                entry = data['trading_levels'].get('entry_optimal', 0)
                print(f"✅ {symbol}: Entrada = ${entry}")
        
        # Preparar datos para el template
        template_data = {
            'symbols_data': trading_data,
            'server_time': datetime.now().strftime('%H:%M:%S'),
            'socketio_enabled': SOCKETIO_AVAILABLE,
            'philosophy': {
                'main_principle': "El arte de tomar dinero de otros legalmente",
                'risk_principle': "Es mejor perder una oportunidad que perder dinero",
                'probability_principle': "Solo operamos con alta probabilidad de éxito",
                'market_principle': "Operamos contra el 90% que pierde dinero"
            },
            'stats': {
                'active_signals': len([s for s in trading_data.values() if s.get('signal', {}).get('signal', 'WAIT') not in ['WAIT', 'NO_SIGNAL']]),
                'high_prob_signals': len([s for s in trading_data.values() if s.get('signal', {}).get('signal_strength', 0) >= 70]),
                'symbols_analyzed': f"{len(trading_data)}/{len(SYMBOLS)}"
            }
        }
        
        return render_template('merino_dashboard.html', **template_data)
        
    except Exception as e:
        print(f"❌ Error cargando template merino_dashboard.html: {e}")
        import traceback
        traceback.print_exc()  # Para debug completo
        # Fallback a template simple
        return f"""
        <h1>🚀 Jaime Merino Trading Bot</h1>
        <p>Error cargando dashboard: {str(e)}</p>
        <p>📊 <a href="/api/data">Ver datos JSON</a></p>
        <p>💡 <a href="/health">Health Check</a></p>
        <p><strong>Template esperado:</strong> templates/merino_dashboard.html</p>
        """

@app.route('/health')
def health():
    """Health check mejorado"""
    uptime = datetime.now() - server_start_time
    
    return jsonify({
        'status': 'healthy',
        'app': 'Jaime Merino Trading Bot',
        'version': '2.2.0',
        'template': 'merino_dashboard.html',
        'uptime_seconds': int(uptime.total_seconds()),
        'socketio_enabled': SOCKETIO_AVAILABLE,
        'clients_connected': clients_connected,
        'symbols_tracked': len(SYMBOLS),
        'last_data_update': trading_data.get('BTCUSDT', {}).get('last_update', 'never'),
        'real_prices_enabled': True,
        'timestamp': datetime.now().isoformat(),
        'philosophy': "Es mejor perder una oportunidad que perder dinero"
    })

@app.route('/api/data')
def api_data():
    """API de datos compatible con dashboard"""
    global trading_data
    
    if not trading_data:
        trading_data = generate_trading_data()
    
    return jsonify({
        'success': True,
        'data': trading_data,
        'timestamp': datetime.now().isoformat(),
        'template': 'merino_dashboard.html',
        'data_source': 'enhanced_analysis_service',
        'philosophy': "Solo operamos con alta probabilidad de éxito"
    })

@app.route('/api/analysis/<symbol>')
def api_analysis(symbol):
    """API para análisis específico de símbolo"""
    symbol = symbol.upper()
    if symbol in trading_data:
        return jsonify({
            'success': True,
            'symbol': symbol,
            'analysis': trading_data[symbol],
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': f'Símbolo {symbol} no encontrado',
            'available_symbols': list(trading_data.keys())
        }), 404

# Rutas adicionales para compatibilidad con el dashboard

@app.route('/api/symbols')
def api_symbols():
    """Lista de símbolos soportados"""
    return jsonify({
        'success': True,
        'symbols': SYMBOLS,
        'count': len(SYMBOLS),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/philosophy')
def api_philosophy():
    """Filosofía Merino para el dashboard"""
    return jsonify({
        'success': True,
        'philosophy': {
            'main_principle': "El arte de tomar dinero de otros legalmente",
            'risk_principle': "Es mejor perder una oportunidad que perder dinero",
            'probability_principle': "Solo operamos con alta probabilidad de éxito",
            'market_principle': "Operamos contra el 90% que pierde dinero",
            'discipline': "Disciplina > Análisis técnico perfecto"
        },
        'methodology': {
            'timeframes': ['4H', '1H', '1D'],
            'key_indicators': ['EMA11/55', 'RSI', 'ADX', 'MACD', 'Bollinger Bands'],
            'risk_management': 'Metodología 40-30-20-10'
        },
        'timestamp': datetime.now().isoformat()
    })

# Eventos SocketIO compatibles con el dashboard
if SOCKETIO_AVAILABLE:
    @socketio.on('connect')
    def on_connect():
        global clients_connected
        clients_connected += 1
        print(f"🔗 Cliente conectado al dashboard Merino. Total: {clients_connected}")
        
        # Enviar datos iniciales compatibles con el dashboard
        emit('analysis_update', {
            'data': trading_data,
            'timestamp': datetime.now().isoformat(),
            'message': 'Conectado al Dashboard Jaime Merino',
            'philosophy': "Operamos contra el 90% que pierde dinero",
            'update_type': 'initial'
        })
    
    @socketio.on('disconnect')
    def on_disconnect():
        global clients_connected
        clients_connected = max(0, clients_connected - 1)
        print(f"❌ Cliente desconectado del dashboard. Total: {clients_connected}")
    
    @socketio.on('request_analysis')
    def on_request_analysis(data):
        """Evento específico del dashboard para solicitar análisis"""
        symbol = data.get('symbol', '').upper()
        print(f"📊 Análisis solicitado para {symbol}")
        
        if symbol in SYMBOLS:
            global trading_data
            trading_data = generate_trading_data()
            
            emit('analysis_update', {
                'data': trading_data,
                'timestamp': datetime.now().isoformat(),
                'message': f'Análisis actualizado para {symbol}',
                'update_type': 'manual'
            })
        else:
            emit('analysis_error', {
                'error': f'Símbolo {symbol} no soportado',
                'available_symbols': SYMBOLS
            })
    
    @socketio.on('request_all_symbols')
    def on_request_all_symbols():
        """Evento para solicitar análisis de todos los símbolos"""
        print("📊 Análisis completo solicitado")
        
        global trading_data
        trading_data = generate_trading_data()
        
        emit('analysis_update', {
            'data': trading_data,
            'timestamp': datetime.now().isoformat(),
            'message': 'Análisis completo actualizado',
            'update_type': 'complete'
        })

def check_template_exists():
    """Verificar que el template merino_dashboard.html existe"""
    template_path = 'templates/merino_dashboard.html'
    if os.path.exists(template_path):
        print("✅ Template merino_dashboard.html encontrado")
        return True
    else:
        print("⚠️ Template merino_dashboard.html NO encontrado")
        print(f"   Esperado en: {os.path.abspath(template_path)}")
        return False

if __name__ == '__main__':
    print("🚀 Configurando Jaime Merino Trading Bot...")
    print("📋 Usando template: merino_dashboard.html")
    SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']
    
    # Ejecutar pruebas
    test_all_price_sources()
    # Verificar template
    template_exists = check_template_exists()
    
    # Generar datos iniciales
    trading_data = generate_trading_data()
    
    # Iniciar worker en segundo plano
    worker = threading.Thread(target=background_worker, daemon=True)
    worker.start()
    
    # Configuración para Render
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"🌍 Iniciando servidor en {host}:{port}")
    print("💡 Filosofía: El arte de tomar dinero de otros legalmente")
    print(f"📡 SocketIO: {'Habilitado' if SOCKETIO_AVAILABLE else 'Deshabilitado'}")
    print(f"📋 Template: {'✅ Encontrado' if template_exists else '❌ Faltante'}")
    print(f"📊 Símbolos: {', '.join(SYMBOLS)}")
    
    # Ejecutar aplicación
    if SOCKETIO_AVAILABLE and socketio:
        socketio.run(
            app,
            host=host,
            port=port,
            debug=False,
            allow_unsafe_werkzeug=True
        )
    else:
        app.run(
            host=host,
            port=port,
            debug=False
        )