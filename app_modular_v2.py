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

# Cache simple de análisis (se refresca cada vez que el usuario entra, como pediste)
analysis_cache = {}

def get_full_analysis(symbol):
    """Obtiene el análisis completo cruzando todas las temporalidades."""
    # Obtenemos el reporte multi-Temporalidad (1d, 4h, 1h, 15m)
    data = TradingEngineV2.get_real_trading_analysis(symbol)
    multi_tf = TradingEngineV2.get_multi_tf_report(symbol)
    return data, multi_tf

import threading
# Caché global para el Radar
radar_cache = []
is_scanning = False

def get_coin_report(symbol):
    """Función de apoyo para el escaneo en paralelo."""
    try:
        data = TradingEngineV2.get_real_trading_analysis(symbol)
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
        
        return render_template('analyzer_v2.html',
                             symbol=symbol,
                             data=data,
                             multi_tf=multi_tf,
                             strategies=report)
    except Exception as e:
        log.error(f"Error en análisis de {symbol}: {e}")
        return f"Error analizando {symbol}: {str(e)}", 500

@app.route('/tecnico/<symbol>')
def technical_view(symbol):
    """Estación Técnica 360: Grid de 4 gráficos TradingView."""
    symbol = symbol.upper()
    return render_template('technical_v2.html', symbol=symbol)

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
