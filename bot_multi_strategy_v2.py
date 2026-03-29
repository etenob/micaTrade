import os
import sys
import time
import requests
import threading
import logging
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import concurrent.futures
from flask import Flask, render_template, jsonify, request

from merino_math_v2 import TradingEngineV2
from config_v2 import Config
from binance_manager import BinanceManager
from trade_manager_v2 import TradeManager
from modular_strategies import StrategyManager
from Telegram.telegram_helper import send_telegram_message, send_telegram_document

# ── Logging a archivo (1 por día en carpeta /logs) ──────────────────
if not os.path.exists('logs'): os.makedirs('logs')
log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# TimedRotatingFileHandler: Crea un archivo nuevo cada día ('D') y NO borra los viejos (backupCount=0)
file_handler = TimedRotatingFileHandler('logs/bot_multi.log', when='D', interval=1, backupCount=0, encoding='utf-8')
file_handler.setFormatter(log_formatter)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
log = logging.getLogger()

class PrintToLog:
    def write(self, msg):
        if msg.strip(): log.info(msg.strip())
    def flush(self): pass
sys.stdout = PrintToLog()

# Silenciar logs de Flask/Werkzeug (127.0.0.1 - -)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Inicializar Flask e Instancias
app = Flask(__name__)
bm = BinanceManager()
tm = TradeManager()

# Cache global
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """Encoder que convierte tipos numpy a Python nativo para json.dump."""
    def default(self, obj):
        if isinstance(obj, (np.bool_,)): return bool(obj)
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if hasattr(obj, 'value'): return obj.value  # Enums (Flag, Signal, Trend)
        try: return str(obj)
        except: return super().default(obj)

latest_analysis = {}
last_alerts_state = {}
radar_cache = []
try:
    if os.path.exists('radar_cache_v2.json'):
        with open('radar_cache_v2.json', 'r') as f:
            data = json.load(f)
            radar_cache = data.get('radar', [])
except Exception as e:
    print(f"No se pudo cargar caché previo: {e}")
manager = StrategyManager()

def check_trailing_stop(symbol, analysis):
    """Trailing stop adaptativo que escala con el precio."""
    active = tm.get_active_trade(symbol)
    if not active: return

    current_price = analysis['current_price']    # 1. Recuperar info del trade
    last_stop = active.get('last_stop', active['stop_loss'])
    entry_price = active.get('entry_price')
    # Use the original statically saved percentages
    stop_dist_pct = active.get('sl_pct', 0.05)
    
    # Trailing Stop: Mantiene la distancia original del SL respecto al precio actual
    candidate_stop = round(current_price * (1 - stop_dist_pct), 4)
    # El Take Profit es estático desde el precio de entrada, no se mueve
    candidate_tp = active['targets'][0] 
    
    # Solo actualizamos si el nuevo stop es al menos 0.03% más alto
    # para evitar "parpadeo" constante de órdenes por movimientos mínimos
    update_threshold = current_price * 0.0003
    
    if candidate_stop > (last_stop + update_threshold):
        print(f"🛡️ [{symbol}] {active['strategy']} Actualizando Stop: {last_stop} -> {candidate_stop}")
        bm.cancel_open_orders(symbol)
        new_limit = round(candidate_stop * 0.998, 4)
        oco = bm.place_oco_sell(symbol, active['quantity'], candidate_tp, candidate_stop, new_limit)
        if oco:
            active['last_stop'] = candidate_stop
            active['targets'][0] = candidate_tp
            active['oco_id'] = oco['orderListId'] if 'orderListId' in oco else 0
            tm.save_active_trade(symbol, active)

def sync_active_trades():
    """Detecta trades cerrados en Binance y los mueve al historial."""
    active_trades = tm.get_all_active()
    for active in active_trades:
        symbol = active['symbol']
        
        # --- PROTECCIÓN ANTI-RACE-CONDITION / OCO ERROR ---
        # Si el trade se abrió hace menos de 5 minutos, NO lo cerramos aunque no tenga órdenes.
        # Esto previene el loop de compra infinita si la OCO falló.
        det = active.get('detected_at')
        if det:
            try:
                age = datetime.now() - datetime.fromisoformat(det)
                if age.total_seconds() < 300: # 5 minutos de gracia
                    continue
            except: pass

        try:
            open_orders = bm.client.get_open_orders(symbol=symbol)
            
            # Si no hay órdenes abiertas pero tenemos el trade activo localmente,
            # es porque se ejecutó el OCO (o se cerró manualmente)
            if not open_orders:
                # Obtener precio de salida (promedio del último minuto o actual)
                ticker = bm.client.get_symbol_ticker(symbol=symbol)
                exit_price = float(ticker['price'])
                tm.close_trade(symbol, exit_price, reason="Fills OCO / Manual")
                
                # 🔔 Notificación Telegram: CIERRE
                pnl_msg = f"📉 [{symbol}] TRADE CERRADO\nPrecio: ${exit_price}\nMotivo: OCO / Manual"
                try:
                    send_telegram_message(pnl_msg)
                except: pass
        except Exception as e:
            print(f"⚠️ Error sincronizando {symbol}: {e}")

last_blocked_alerts = {} # Para no spamear avisos de "oportunidad bloqueada"

def update_signals():
    global latest_analysis
    symbols = Config.TRADING_SYMBOLS
    
    # 🧠 Mostrar Configuración Inicial
    print("\n" + "="*50)
    print("      ESTADO DEL MOTOR MULTI-ESTRATEGIA")
    print("="*50)
    for name, cfg in Config.STRATEGY_CONFIG.items():
        status = "✅ ACTIVA" if cfg.get('active') else "❌ INACTIVA"
        print(f"  {name:15} | {status} | $: {cfg['order_amount']:4} | SL: {cfg['sl_pct']*100}%")
    print("="*50 + "\n")
    
    while True:
        try:
            # 0. Sincronizar trades cerrados
            sync_active_trades()
            
            print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Escaneando mercado (MULTI-STRAT)...")
            # 1. Obtención de datos en paralelo
            new_data = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Mapear cada símbolo a su función de análisis (AHORA V2)
                future_to_symbol = {executor.submit(TradingEngineV2.get_real_trading_analysis, s): s for s in symbols}
                
                for future in concurrent.futures.as_completed(future_to_symbol):
                    s = future_to_symbol[future]
                    try:
                        analysis = future.result()
                        new_data[s] = analysis
                    except Exception as e:
                        print(f"⚠️ Error obteniendo análisis para {s}: {e}")

            # 2. Procesamiento secuencial de señales y trailing
            active_trades = tm.get_all_active()
            total_exposure = tm.get_total_exposure()

            # Procesamos en el orden original de TRADING_SYMBOLS para consistencia
            for s in symbols:
                if s not in new_data: continue
                analysis = new_data[s]
                
                # 1. Monitoreo de Trailing
                check_trailing_stop(s, analysis)

                # 2. Evaluación de Estrategias V2 (Tribunal de Jueces)
                report = manager.get_radar_report(analysis)
                analysis['report'] = report
                
                # Reconstruimos 'triggered' para la lógica nativa del bot de Binance
                triggered = [name for name, details in report.items() if details['triggered']]
                analysis['active_strategies'] = triggered 
                
                for strat_name in triggered:
                    cfg = Config.STRATEGY_CONFIG.get(strat_name)
                    if not cfg or not cfg.get('active'): continue
                    
                    # --- AVISO DE OPORTUNIDAD BLOQUEADA ---
                    active_trade = tm.get_active_trade(s)
                    if active_trade and strat_name in ['ALIEN', 'GATILLO_11']:
                        if active_trade['strategy'] != strat_name:
                            alert_key = f"{s}_{strat_name}"
                            if alert_key not in last_blocked_alerts or time.time() - last_blocked_alerts[alert_key] > 3600:
                                send_telegram_message(f"⚠️ OPORTUNIDAD BLOQUEADA\nActivo: {s}\nNueva señal: {strat_name} 👽\nTrade actual: {active_trade['strategy']}\n\nSi querés cambiar, cerrá el trade actual en el dashboard.")
                                last_blocked_alerts[alert_key] = time.time()

                    # Verificamos si ya hay un trade para este símbolo
                    # (Por ahora 1 trade por moneda, la primera estrategia que pegue)
                    if not tm.get_active_trade(s):
                        if (total_exposure + cfg['order_amount']) <= Config.MAX_USDT_TOTAL_EXPOSURE:
                            
                            # 🔮 FILTRO PANORAMA 360 (Ya incluido en StrategyEngine)
                            if Config.IS_LIVE_TRADING:
                                print(f"🚀 GATILLO {strat_name} detectado en {s}! Comprando...")
                                
                                # 🔔 Notificación Telegram: APERTURA V2
                                try:
                                    send_telegram_message(f"🤖 [V2] 🚀 [{s}] ENTRADA DETECTADA\nEstrategia: {strat_name}\nPrecio aprox: ${analysis['current_price']}")
                                except: pass
                                
                                buy_order = bm.place_market_buy(s, cfg['order_amount'])
                                if buy_order:
                                    # Registro inmediato para evitar duplicados
                                    entry_price = float(buy_order['fills'][0]['price']) if buy_order.get('fills') else analysis['current_price']
                                    qty = float(buy_order['executedQty'])
                                    
                                    # 1. Registrar trade con niveles LONG explícitos (nuestras estrategias actuales son todas LONG)
                                    long_levels = analysis['trading_levels']['long']
                                    tm.add_active_trade(s, strat_name, qty, cfg['order_amount'], entry_price, long_levels['targets'], long_levels['stop_loss'])
                                    
                                    # 2. Actualizar exposición local inmediatamente
                                    total_exposure += cfg['order_amount']

                                    # 3. Colocar OCO (Take Profit y Stop Loss)
                                    stop_loss = long_levels['stop_loss']
                                    target_p1 = long_levels['targets'][0]
                                    limit_price = stop_loss * 0.998
                                    bm.place_oco_sell(s, qty, target_p1, stop_loss, limit_price)
                                    
                                    break # Una compra por ciclo máximo por par
                            else:
                                message = f"📝 [MODO MONITOR] {strat_name} detectado en {s} (Omitiendo compra)"
                                print(message)
                                try:
                                    send_telegram_message(f"📝 {s} | SEÑAL DETECTADA\nEstrategia: {strat_name}\nModo: SOLO MONITOR (No se ejecutó compra)")
                                except: pass
                                qty = cfg['order_amount'] / analysis['current_price'] if analysis['current_price'] > 0 else 0
                                entry = analysis['current_price']
                                
                                # Formatear cantidad para OCO y salvar
                                formatted_qty = float(bm.format_quantity_str(s, qty))
                                tp = round(entry * (1 + cfg['tp_pct']), 4)
                                sl = round(entry * (1 - cfg['sl_pct']), 4)

                                # 1. SALVAR EL TRADE PRIMERO (para que el bot sepa que ya compró)
                                tm.save_active_trade(s, {
                                    'strategy': strat_name,
                                    'quantity': formatted_qty if formatted_qty > 0 else qty,
                                    'usdt_value': cfg['order_amount'],
                                    'entry_price': entry,
                                    'targets': [tp],
                                    'stop_loss': sl,
                                    'last_stop': sl,
                                    'sl_pct': cfg['sl_pct'],
                                    'tp_pct': cfg['tp_pct'],
                                    'detected_at': datetime.now().isoformat()
                                })
                                print(f"✅ Trade {s} registrado localmente. Intentando OCO...")

                                # 2. INTENTAR OCO (con cantidad validada)
                                if formatted_qty > 0:
                                    bm.place_oco_sell(s, formatted_qty, tp, sl, round(sl * 0.998, 4))
                                else:
                                    print(f"⚠️ Cantidad insuficiente para OCO en {s} ({qty}). Trade queda abierto sin OCO.")
                                 
                                total_exposure += cfg['order_amount']
                                break # Una compra por ciclo máximo por par
                        else:
                            # Loguear que la señal fue detectada pero no entramos por capital
                            print(f"⚠️ [{s}] SEÑAL {strat_name} DETECTADA PERO LÍMITE DE EXPOSICIÓN ALCANZADO ({total_exposure}/{Config.MAX_USDT_TOTAL_EXPOSURE} USDT)")

            # --- RESUMEN DE CICLO EN CONSOLA ---
            summary_list = []
            for s in symbols:
                if s not in new_data: continue
                ana = new_data[s]
                sigs = ana.get('active_strategies', [])
                sig_text = ana['signal']['signal']
                if sigs:
                    sig_text += f" ({'/'.join(sigs)})"
                summary_list.append(f"{s.replace('USDT','')}: {sig_text}")
            
            # Imprimir en grupos de 8 para legibilidad (con 40 monedas)
            for i in range(0, len(summary_list), 8):
                print("   " + " | ".join(summary_list[i:i+8]))
            
            print(f"📊 EXPOSICIÓN TOTAL: {total_exposure}/{Config.MAX_USDT_TOTAL_EXPOSURE} USDT")
            print("-" * 50)
            
            # --- CONSTRUIR CACHÉ DE RADAR PARA EL FRONTEND V2 ---
            global radar_cache
            temp_radar = []
            for s in symbols:
                if s not in new_data: continue
                ana = new_data[s]
                sig = ana.get('signal', {})
                temp_radar.append({
                    'symbol': s,
                    'price': f"{ana.get('current_price', 0):.2f}",
                    'signal': sig.get('signal'),
                    'strength': sig.get('signal_strength'),
                    'vpoc': sig.get('volume_profile', {}),
                    'squeeze_on': sig.get('squeeze_on', False),
                    'whale_display': sig.get('whale_display', 'NORMAL'),
                    'report': ana.get('report', {})
                })
            radar_cache = sorted(temp_radar, key=lambda x: x.get('strength', 0), reverse=True)
            
            latest_analysis = new_data
            
            # Guardamos caché local para reboots limpios (solo radar, no analysis completo)
            try:
                with open('radar_cache_v2.json', 'w') as f:
                    json.dump({'radar': radar_cache}, f, cls=NumpyEncoder)
            except Exception as e:
                print(f"⚠️ Error guardando radar_cache_v2.json: {e}")
                
            time.sleep(Config.UPDATE_SECONDS)
        except Exception:
            print(f"🚨 Error en loop de señales:\n{traceback.format_exc()}")
            time.sleep(10)

@app.route('/')
def dashboard():
    """Vista de Radar Modular V2 (Inyectada al bot en vivo)."""
    return render_template('dashboard_v2.html', 
                         radar=radar_cache, 
                         is_scanning=False,
                         server_time=datetime.now().strftime('%H:%M:%S'))

@app.route('/analisis/<symbol>')
def strategy_detail(symbol):
    """Vista del Tribunal de Jueces."""
    symbol = symbol.upper()
    data = latest_analysis.get(symbol)
    if not data:
        data = TradingEngineV2.get_real_trading_analysis(symbol)
    
    multi_tf = TradingEngineV2.get_multi_tf_report(symbol)
    data['multi_tf'] = multi_tf.get('timeframes', {})
    
    report = manager.get_strategy_report_all(data)
    
    return render_template('analyzer_v2.html',
                         symbol=symbol,
                         data=data,
                         multi_tf=multi_tf,
                         strategies=report)

@app.route('/tecnico/<symbol>')
def technical_view(symbol):
    symbol = symbol.upper()
    return render_template('technical_v2.html', symbol=symbol)

@app.route('/plotly_fragment/<symbol>')
def plotly_fragment(symbol):
    symbol = symbol.upper()
    tf = request.args.get('tf', '4h')
    return TradingEngineV2.get_chart_html(symbol, tf, include_header=False)

@app.route('/chart/<symbol>')
def technical_chart(symbol):
    from flask import request
    timeframe = request.args.get('tf', '4h')
    return TradingEngineV2.get_chart_html(symbol, timeframe)

@app.route('/historial')
def order_history():
    history = TradeManager.get_history()
    
    # Agrupar estadísticas por estrategia, símbolo y mes
    stats_strat = {}
    stats_symbol = {}
    stats_month = {}
    for h in history:
        strat = h.get('strategy', 'UNKNOWN')
        symbol = h.get('symbol', 'UNKNOWN')
        exit_time = h.get('exit_time', '')
        pnl = h.get('pnl_neto', 0)
        
        # Stats por Estrategia
        if strat not in stats_strat: stats_strat[strat] = {'count': 0, 'pnl': 0, 'wins': 0}
        stats_strat[strat]['count'] += 1
        stats_strat[strat]['pnl'] += pnl
        if pnl > 0: stats_strat[strat]['wins'] += 1
        
        # Stats por Símbolo
        if symbol not in stats_symbol: stats_symbol[symbol] = {'count': 0, 'pnl': 0, 'wins': 0}
        stats_symbol[symbol]['count'] += 1
        stats_symbol[symbol]['pnl'] += pnl
        if pnl > 0: stats_symbol[symbol]['wins'] += 1

        # Stats por Mes
        if exit_time:
            try:
                m_key = exit_time[:7] # "2026-03"
                if m_key not in stats_month: stats_month[m_key] = {'count': 0, 'pnl': 0, 'wins': 0}
                stats_month[m_key]['count'] += 1
                stats_month[m_key]['pnl'] += pnl
                if pnl > 0: stats_month[m_key]['wins'] += 1
            except: pass
        
    return render_template('results_dashboard.html', 
                           history=history[::-1], 
                           stats_strat=stats_strat,
                           stats_symbol=dict(sorted(stats_symbol.items(), key=lambda item: item[1]['pnl'], reverse=True)),
                           stats_month=dict(sorted(stats_month.items(), reverse=True)),
                           total_pnl=sum([h.get('pnl_neto', 0) for h in history]),
                           active_page='historial',
                           live_mode=Config.IS_LIVE_TRADING)

@app.route('/activas')
def active_positions():
    active_trades = TradeManager.get_all_active()
    for t in active_trades:
        symbol = t['symbol']
        try:
            ticker = bm.client.get_symbol_ticker(symbol=symbol)
            current = float(ticker['price'])
        except:
            current = t.get('entry_price', 0)
            
        t['current_price'] = current
        entry = t.get('entry_price', current)
        
        # --- NUEVO: DETECCIÓN DE NUEVAS SEÑALES PARA ESTE ACTIVO ---
        analysis = latest_analysis.get(symbol)
        t['new_signals'] = []
        if analysis:
            current_signals = [name for name, details in analysis.get('report', {}).items() if details['triggered']]
            # Solo avisar si hay una señal DISTINTA a la que ya abrió el trade
            t['new_signals'] = [s for s in current_signals if s != t['strategy']]
        
        # --- NUEVO: CÁLCULO DE DURACIÓN ---
        # Aceptar tanto detected_at como el viejo timestamp para compatibilidad
        detected_at = t.get('detected_at') or t.get('timestamp')
        if detected_at:
            try:
                start_time = datetime.fromisoformat(detected_at)
                diff = datetime.now() - start_time
                hours, remainder = divmod(int(diff.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                t['duration'] = f"{hours}h {minutes}m"
            except:
                t['duration'] = "---"
        else:
            t['duration'] = "---"
            
        if entry > 0:
            t['pnl_pct'] = ((current - entry) / entry) * 100
            t['pnl_usdt'] = (current - entry) * t.get('quantity', 0)
        else:
            t['pnl_pct'] = 0
            t['pnl_usdt'] = 0
            
    return render_template('active_trades.html', 
                           trades=active_trades,
                           active_page='activas',
                           live_mode=Config.IS_LIVE_TRADING)

@app.route('/cerrar/<symbol>')
def close_manual(symbol):
    trade = tm.get_active_trade(symbol)
    if not trade:
        return "Trade not found", 404
        
    print(f"🛑 CIERRE MANUAL solicitado para {symbol}")
    
    # 1. Cancelar todas las órdenes (OCO)
    bm.cancel_open_orders(symbol)
    
    # 2. Vender a mercado
    sell_order = bm.place_market_sell(symbol, trade['quantity'])
    
    if sell_order:
        # 3. Calcular precio de salida real (promedio de fills)
        if 'fills' in sell_order and len(sell_order['fills']) > 0:
            exit_price = sum(float(f['price']) * float(f['qty']) for f in sell_order['fills']) / sum(float(f['qty']) for f in sell_order['fills'])
        else:
            # Fallback a precio de ticker si no hay fills (raro en market order)
            ticker = bm.client.get_symbol_ticker(symbol=symbol)
            exit_price = float(ticker['price'])
            
        # 4. Cerrar en el Manager
        tm.close_trade(symbol, exit_price, reason="Manual (Afraid/Exit) ✋")
        
        # 🔔 Notificación Telegram: CIERRE
        try:
            send_telegram_message(f"✋ [{symbol}] CIERRE MANUAL (AFRAID/EXIT)\nPrecio Salida: ${exit_price:.4f}")
        except: pass
        
        return f"Trade {symbol} cerrado con éxito", 200
    else:
        return f"Error al vender {symbol}", 500

@app.route('/resumen')
def financial_summary():
    history = TradeManager.get_history()
    base_capital = Config.BASE_CAPITAL
    
    # Agrupar por día y mes
    daily_stats = {}
    monthly_stats = {}
    
    for h in history:
        exit_time_str = h.get('exit_time', '')
        if not exit_time_str: continue
        
        try:
            dt = datetime.strptime(exit_time_str, "%Y-%m-%d %H:%M:%S")
            day_key = dt.strftime("%Y-%m-%d")
            month_key = dt.strftime("%Y-%m")
            
            pnl = h.get('pnl_neto', 0)
            
            if day_key not in daily_stats: daily_stats[day_key] = 0
            daily_stats[day_key] += pnl
            
            if month_key not in monthly_stats: monthly_stats[month_key] = 0
            monthly_stats[month_key] += pnl
        except: continue

    # Ordenar cronológicamente
    daily_sorted = dict(sorted(daily_stats.items(), reverse=True))
    monthly_sorted = dict(sorted(monthly_stats.items(), reverse=True))
    
    # Cálculos de Proyección
    total_pnl = sum([h.get('pnl_neto', 0) for h in history])
    num_days = len(daily_stats) if daily_stats else 1
    daily_avg = total_pnl / num_days
    
    annual_est = daily_avg * 365
    annual_pct = (annual_est / base_capital) * 100 if base_capital > 0 else 0
    monthly_avg = daily_avg * 30
    
    return render_template('financial_summary.html',
                           daily=daily_sorted,
                           monthly=monthly_sorted,
                           total_pnl=total_pnl,
                           daily_avg=daily_avg,
                           monthly_avg=monthly_avg,
                           annual_est=annual_est,
                           annual_pct=annual_pct,
                           base_capital=base_capital,
                           active_page='resumen',
                           live_mode=Config.IS_LIVE_TRADING)

@app.route('/manual_trade', methods=['POST'])
def manual_trade():
    """Ejecucción manual de trade (Market Buy + OCO Sell)."""
    data = request.json
    symbol = data.get('symbol')
    amount = float(data.get('amount', 0))
    tp = float(data.get('tp', 0))
    sl = float(data.get('sl', 0))
    
    if not symbol or amount <= 0:
        return jsonify({"error": "Datos inválidos"}), 400
        
    print(f"⚡ [MANUAL] Ejecutando en {symbol} - Monto: {amount} USDT")
    
    # 1. Comprar Mercado
    buy_order = bm.place_market_buy(symbol, amount)
    if not buy_order:
        return jsonify({"error": "Falló la compra a mercado"}), 500
        
    qty = float(buy_order['executedQty'])
    # Precio promedio de entrada real
    if 'fills' in buy_order and len(buy_order['fills']) > 0:
        entry = sum(float(f['price']) * float(f['qty']) for f in buy_order['fills']) / sum(float(f['qty']) for f in buy_order['fills'])
    else:
        # Fallback si no hay fills visibles (raro)
        ticker = bm.client.get_symbol_ticker(symbol=symbol)
        entry = float(ticker['price'])

    # 2. Colocar OCO Sell 
    formatted_qty = float(bm.format_quantity_str(symbol, qty))
    sl_limit = round(sl * 0.998, 4) # Un poco de margen para asegurar ejecución
    
    oco = bm.place_oco_sell(symbol, formatted_qty, tp, sl, sl_limit)
    
    # 3. Registrar localmente para seguimiento
    tm.save_active_trade(symbol, {
        'strategy': 'MANUAL ⚡',
        'quantity': formatted_qty,
        'usdt_value': amount,
        'entry_price': entry,
        'last_stop': sl,
        'sl_pct': round(abs((sl - entry)/entry),2) if entry > 0 else 0.05,
        'tp_pct': round(abs((tp - entry)/entry),2) if entry > 0 else 0.03,
        'targets': [tp],
        'detected_at': datetime.now().isoformat()
    })
    
    # 🔔 Notificación Telegram
    try:
        send_telegram_message(f"⚡ [{symbol}] ENTRADA MANUAL\nMonto: {amount} USDT\nEntrada: ${entry:.4f}\nTP: ${tp:.4f} | SL: ${sl:.4f}")
    except: pass
    
    return jsonify({"success": True}), 200

def telegram_polling_loop():
    """Hilo que escucha comandos de Telegram y responde."""
    offset = None
    bot_token = Config.TELEGRAM_BOT_TOKEN
    chat_id = str(Config.TELEGRAM_CHAT_ID)

    print("📡 Monitor de Comandos Telegram iniciado...")

    while True:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            # Timeout largo (Long Polling) para no saturar la CPU
            resp = requests.get(url, params={"timeout": 20, "offset": offset}, timeout=30)
            
            if resp.status_code != 200:
                time.sleep(10)
                continue

            updates = resp.json().get("result", [])
            for upd in updates:
                offset = upd["update_id"] + 1
                msg = upd.get("message")
                if not msg or "text" not in msg:
                    continue

                # Validar que sea el dueño del bot
                sender_id = str(msg["chat"]["id"])
                if sender_id != chat_id:
                    print(f"🔒 Bloqueado comando de ID desconocido: {sender_id}")
                    continue

                text = msg["text"].strip().lower()
                cmd_parts = text.split()
                if not cmd_parts: continue
                cmd = cmd_parts[0]

                if cmd in ["/start", "/help", "/ayuda"]:
                    help_text = (
                        "🤖 *MicoTrading Bot Interactivo*\n\n"
                        "📌 *Comandos:*\n"
                        "💰 /resumen - Resultado hoy y mensual.\n"
                        "🟢 /activas - Mis trades abiertos.\n"
                        "🌍 /panorama [moneda] - Analisis 1d-15m (ej: /panorama btc).\n"
                        "📊 /[moneda] - Ver señal de moneda (ej: /btc, /sol).\n"
                        "📄 /logs - Descargar log del bot.\n"
                        "❓ /help - Esta lista de ayuda."
                    )
                    send_telegram_message(help_text)

                elif cmd in ["/logs", "/log"]:
                    try:
                        send_telegram_message("⏳ Preparando y enviando log...")
                        send_telegram_document('logs/bot_multi.log')
                    except Exception as e:
                        send_telegram_message(f"❌ Error al enviar log: {e}")

                elif cmd == "/resumen":
                    history = tm.get_history()
                    now = datetime.now()
                    today = now.strftime('%Y-%m-%d')
                    month = now.strftime('%Y-%m')
                    
                    p_today = sum(h.get('pnl_neto', 0) for h in history if h.get('exit_time', '').startswith(today))
                    p_month = sum(h.get('pnl_neto', 0) for h in history if h.get('exit_time', '').startswith(month))
                    
                    res_text = (
                        "💰 *RESUMEN DE CUENTA*\n\n"
                        f"📅 *Hoy:* `{p_today:+.4f} USDT`\n"
                        f"🗓️ *Mes:* `{p_month:+.4f} USDT`\n"
                        f"📈 *Capital Base:* `{Config.BASE_CAPITAL} USDT`"
                    )
                    send_telegram_message(res_text)

                elif cmd == "/activas":
                    active = tm.get_all_active()
                    if not active:
                        send_telegram_message("📭 No hay trades abiertos.")
                    else:
                        msg_text = "🟢 *POSICIONES ABIERTAS*\n\n"
                        for t in active:
                            sym = t['symbol']
                            price = latest_analysis.get(sym, {}).get('current_price', t.get('entry_price', 0))
                            entry = t.get('entry_price', 0)
                            pnl_pct = ((price - entry) / entry) * 100 if entry > 0 else 0
                            
                            # Duración
                            det = t.get('detected_at')
                            dur = "---"
                            if det:
                                try:
                                    diff = datetime.now() - datetime.fromisoformat(det)
                                    h, m = divmod(int(diff.total_seconds()), 3600)
                                    mm, _ = divmod(m, 60)
                                    dur = f"{h}h {mm}m"
                                except: pass

                            msg_text += f"🔸 *{sym}* (`{t['strategy']}`)\n"
                            msg_text += f"   PNL: `{pnl_pct:+.2f}%` | ⏳ `{dur}`\n\n"
                        send_telegram_message(msg_text)

                elif cmd == "/lista":
                    coins = sorted(list(latest_analysis.keys()))
                    if not coins:
                        send_telegram_message("📭 Radar vacío. Esperando datos del primer ciclo...")
                    else:
                        clean_list = [c.replace("USDT", "") for c in coins]
                        msg_text = "🛰️ *MONEDAS EN RADAR:*\n\n" + ", ".join(clean_list)
                        send_telegram_message(msg_text)
                        
                elif cmd == "/panorama":
                    if len(cmd_parts) > 1:
                        coin = cmd_parts[1].upper()
                        if not coin.endswith("USDT"): coin += "USDT"
                        send_telegram_message(f"🔍 Generando Panorama 360 para {coin}...")
                        try:
                            multi_tf = TradingEngineV2.get_multi_tf_report(coin)
                            tfs = multi_tf.get('timeframes', {})
                            if not tfs or '1d' not in tfs or 'status' in tfs.get('1d', {}):
                                send_telegram_message(f"❌ Error al generar reporte para {coin}")
                            else:
                                text = f"🌍 *PANORAMA 360: {coin}*\n\n"
                                d1 = tfs.get('1d', {})
                                text += f"📅 *1D (Macro)*\nDir: `{d1.get('bias', 'N/A')}` | ADX: `{d1.get('strength', 'N/A')}`\n\n"
                                h4 = tfs.get('4h', {})
                                text += f"🕒 *4H (Estrategia)*\nPrecio: `${h4.get('price', 0):.4f}` | 🐳 `{h4.get('whale', 'NO')}`\nEstado: `{h4.get('nadaraya', 'N/A')}`\n\n"
                                h1 = tfs.get('1h', {})
                                text += f"⏱️ *1H (Confirmación)*\nDir: `{h1.get('bias', 'N/A')}`\n\n"
                                m15 = tfs.get('15m', {})
                                text += f"⚡ *15m (Gatillo)*\nMomentum: `{m15.get('momentum', 'N/A')}`"
                                send_telegram_message(text)
                        except Exception as e:
                            send_telegram_message(f"⚠️ Error interno: {e}")
                    else:
                        send_telegram_message("⚠️ Faltó la moneda. Uso: `/panorama btc`")

                elif cmd.startswith("/") and len(cmd) > 2:
                    # Ver el radar de una moneda específica (ej: /btc)
                    coin = cmd[1:].upper()
                    if not coin.endswith("USDT"): coin += "USDT"
                    
                    analysis = latest_analysis.get(coin)
                    if analysis:
                        active_sigs = [name for name, details in analysis.get('report', {}).items() if details['triggered']]
                        sig_str = ", ".join(active_sigs) if active_sigs else "Sin señales"
                        
                        rsi_val = analysis.get('rsi', 'N/A')
                        if isinstance(rsi_val, float): rsi_val = f"{rsi_val:.1f}"
                        
                        info_text = (
                            f"📊 *RADAR: {coin}*\n\n"
                            f"💵 Precio: `${analysis['current_price']:.4f}`\n"
                            f"⚡ Señales: `{sig_str}`\n"
                            f"📈 RSI: `{rsi_val}`"
                        )
                        send_telegram_message(info_text)
                    else:
                        # Si es un comando desconocido que no es moneda, ignorar
                        if len(coin) > 3: # Ignorar ruidos cortos
                            send_telegram_message(f"❌ Moneda `{coin}` no está en el radar.")

        except Exception as e:
            print(f"⚠️ Error en Telegram Polling: {e}")
            time.sleep(5)

if __name__ == '__main__':
    # Hilos secundarios
    threading.Thread(target=update_signals, daemon=True).start()
    threading.Thread(target=telegram_polling_loop, daemon=True).start()
    
    # Servidor Web V2
    print("🚀 BOT V2 INICIADO - ESCUCHANDO EN PUERTO 5001")
    app.run(port=5001, debug=False, host="0.0.0.0")
    
