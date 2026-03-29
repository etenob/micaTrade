import os
import sys
import threading
import time
import concurrent.futures
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Añadimos la ruta de trabajo para importar nuestros módulos
sys.path.append(os.getcwd())

from merino_math_v2 import TradingEngineV2
from config import Config
from modular_strategies import StrategyManager
from trade_manager import TradeManager

# Configuración básica
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("LaboratorioV2")

app = Flask(__name__)
# Evitar que Flask ordene las llaves de los JSON alfabéticamente
app.config['JSON_SORT_KEYS'] = False

# Inicializamos el motor modular
manager = StrategyManager()

# Cache de análisis completo: {symbol: {data, multi_tf, timestamp}}
analysis_cache = {}

def get_full_analysis(symbol):
    """Obtiene el análisis completo. Usa caché si tiene menos de 4 minutos."""
    import time
    cached = analysis_cache.get(symbol)
    if cached and (time.time() - cached['ts']) < 240:  # 4 minutos = fresco
        return cached['data'], cached['multi_tf']
    
    # Caché vencido o inexistente: llamar API
    data = TradingEngineV2.get_real_trading_analysis(symbol)
    multi_tf = TradingEngineV2.get_multi_tf_report(symbol)
    analysis_cache[symbol] = {'data': data, 'multi_tf': multi_tf, 'ts': time.time()}
    return data, multi_tf

import threading
# Caché global para el Radar
radar_cache = []
is_scanning = False

def get_coin_report(symbol):
    """Función de apoyo para el escaneo en paralelo. Actualiza Caché al terminar."""
    try:
        import time
        data = TradingEngineV2.get_real_trading_analysis(symbol)
        multi_tf = TradingEngineV2.get_multi_tf_report(symbol)
        # Guardar en caché para que /analisis lo use instantáneamente
        analysis_cache[symbol] = {'data': data, 'multi_tf': multi_tf, 'ts': time.time()}
        # Obtenemos qué estrategias están disparadas positivamente
        
        # V2: Obtenemos el reporte rico de confluencia para todas las estrategias
        sig = data.get('signal', {})
        report = manager.get_radar_report(data)
        
        return {
            'symbol': symbol,
            'price': f"{data.get('current_price', 0):.2f}",
            'signal': sig.get('signal'),
            'strength': sig.get('signal_strength'),
            'vpoc': sig.get('volume_profile', {}),
            'squeeze_on': sig.get('squeeze_on', False),
            'whale_display': sig.get('whale_display', 'NORMAL'),
            'report': report
        }
    except Exception as e:
        log.error(f"Error en radar para {symbol}: {e}")
        return None

def scanner_loop():
    """Hilo infinito que actualiza el radar en segundo plano."""
    global radar_cache, is_scanning
    symbols = Config.TRADING_SYMBOLS
    
    while True:
        try:
            is_scanning = True
            log.info(f"🔄 [Caja Negra] Iniciando escaneo de {len(symbols)} activos...")
            temp_data = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_symbol = {executor.submit(get_coin_report, s): s for s in symbols}
                for future in concurrent.futures.as_completed(future_to_symbol):
                    res = future.result()
                    if res:
                        temp_data.append(res)
            
            # Ordenar por fuerza y actualizar caché
            radar_cache = sorted(temp_data, key=lambda x: x['strength'], reverse=True)
            log.info(f"✅ Escaneo completado. {len(radar_cache)} monedas listas.")
            is_scanning = False
        except Exception as e:
            log.error(f"Error en loop de escaneo: {e}")
            is_scanning = False
            
        time.sleep(30) # Esperar 30 segundos entre escaneos

@app.route('/')
def dashboard():
    """Vista de Radar Modular (Carga Instantánea desde Caché)."""
    return render_template('dashboard_v2.html', 
                         radar=radar_cache, 
                         is_scanning=is_scanning,
                         server_time=datetime.now().strftime('%H:%M:%S'))

@app.route('/analisis/<symbol>')
def strategy_detail(symbol):
    """Vista del Tribunal de Jueces: Desglose técnico de una moneda específica."""
    symbol = symbol.upper()
    try:
        data, multi_tf = get_full_analysis(symbol)
        # Integramos el multi_tf en el diccionario principal para los jueces que lo necesiten
        data['multi_tf'] = multi_tf.get('timeframes', {})
        
        # Obtener el snapshot del TradeManager y pasarlo a get_ui_report
        active_trade = TradeManager.get_active_trade(symbol)
        snapshot = active_trade if active_trade else None
        
        # Generar reporte completo de TODO el tribunal (todas las estrategias simultáneamente)
        report = manager.get_strategy_report_all(data)
        
        # Calcular desglose de confianza (Puntos Merino)
        from merino_math_v2 import Trend
        sig  = data.get('signal', {})
        inds = data.get('indicators', {})
        price = data.get('current_price', 0)

        whale  = sig.get('whale_alert', 'NORMAL')
        mf     = sig.get('koncorde', {}).get('strong_hands', 0)
        adx_v  = inds.get('adx', {}).get('value', 0)
        rsi_v  = inds.get('rsi', {}).get('value', 50)
        ema_11 = inds.get('ema', {}).get('ema_11', price)
        vol_dist = sig.get('volume_profile', {}).get('distance_pct', 99)

        # A. FACTOR BALLENA (Máx 30)
        whale_pts = 30 if whale == Trend.BULL else (15 if mf > 15 else 0)
        # B. ADX / Fuerza (Máx 30)
        adx_pts = 30 if adx_v >= 50 else (20 if adx_v >= 35 else (10 if adx_v >= 23 else 0))
        # C. MOMENTUM RSI (Máx 20) - proxy: RSI < 50 con margen hacia sobreventa
        mom_pts = min(20, max(0, int((50 - rsi_v) / 2.5))) if rsi_v < 50 else 0
        # D. EMA 11 Cercanía (Máx 10)
        dist_e11 = abs((price - ema_11) / ema_11) * 100 if ema_11 > 0 else 99
        ema_pts = 10 if dist_e11 < 0.5 else (7 if dist_e11 < 2.0 else (5 if dist_e11 < 7.0 else 0))
        # E. VPoC Cercanía (Máx 10)
        vpoc_pts = 10 if abs(vol_dist) < 2.0 else (5 if abs(vol_dist) < 5.0 else 0)

        conf_breakdown = [
            {'name': '🐋 Factor Ballena',   'pts': whale_pts, 'max': 30},
            {'name': '📈 ADX (Fuerza)',      'pts': adx_pts,   'max': 30},
            {'name': '💥 Momentum (RSI)',    'pts': mom_pts,   'max': 20},
            {'name': '🎯 Proximidad EMA 11', 'pts': ema_pts,   'max': 10},
            {'name': '🧲 VPoC Cercanía',    'pts': vpoc_pts,  'max': 10},
        ]
        total_conf = sig.get('signal_strength', 0)
        
        return render_template('analyzer_v2.html',
                             symbol=symbol,
                             data=data,
                             multi_tf=multi_tf,
                             strategies=report,
                             conf_breakdown=conf_breakdown,
                             total_conf=total_conf)
    except Exception as e:
        log.error(f"Error en análisis de {symbol}: {e}")
        return f"Error analizando {symbol}: {str(e)}", 500

@app.route('/tecnico/<symbol>')
def technical_view(symbol):
    """Estación Técnica 360: Grid de 4 gráficos TradingView."""
    symbol = symbol.upper()
    data = TradingEngineV2.get_real_trading_analysis(symbol)
    price = data['current_price']
    return render_template('technical_v2.html', symbol=symbol, price=price)

@app.route('/plotly_fragment/<symbol>')
def plotly_fragment(symbol):
    """Devuelve el HTML puro del gráfico de Plotly para incrustar en iframes."""
    symbol = symbol.upper()
    tf = request.args.get('tf', '4h')
    # Usamos el motor nativo sin cabecera interna
    return TradingEngineV2.get_chart_html(symbol, tf, include_header=False)

@app.route('/api/radar')
def api_radar():
    """Endpoint para obtener los datos crudos del radar (precios, etc)."""
    return jsonify(radar_cache)

if __name__ == '__main__':
    # ARRANCAR EL ESCÁNER EN SEGUNDO PLANO (Solo una vez)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Thread(target=scanner_loop, daemon=True).start()
    
    # Arrancamos en el puerto 5001 como puerto de Laboratorio/V2
    print("\n" + "="*50)
    print("      🚀 LABORATORIO DE ANÁLISIS V2 INICIADO")
    print("      Acceso: http://localhost:5001")
    print("="*50 + "\n")
    app.run(port=5001, debug=True)
