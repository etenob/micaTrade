import os
import sys
import time
import requests
import threading
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, jsonify
from datetime import datetime
from merino_math import JaimeMerinoIndicatorsEngine
from config import Config
from binance_manager import BinanceManager
from trade_manager import TradeManager

# ── Logging a archivo (bot_merino.log, máx 5MB, 3 backups) ──────────────────
log_formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = RotatingFileHandler('bot_merino.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
file_handler.setFormatter(log_formatter)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
log = logging.getLogger()

# Redirigir print() al logger
class PrintToLog:
    def write(self, msg):
        if msg.strip(): log.info(msg.strip())
    def flush(self): pass
sys.stdout = PrintToLog()

# Inicializar Flask e Instancias
app = Flask(__name__)
bm = BinanceManager()
tm = TradeManager()

# Cache global para datos
latest_analysis = {}
last_alerts_state = {}


def check_trailing_stop(symbol, analysis):
    """Sube el Stop Loss si el precio avanza a favor de la tendencia."""
    active = tm.get_active_trade(symbol)
    if not active: return
    
    # Verificar si la orden sigue abierta en Binance
    open_ocos = bm.get_open_oco_orders(symbol)
    if not open_ocos:
        # Se cerró el trade (por TP o SL)
        print(f"🏁 Trade cerrado para {symbol}. Moviendo al historial.")
        tm.close_trade(symbol, {'price': analysis['current_price'], 'reason': 'MARKET_FILL'})
        
        # Notificación de Cierre
        msg_close = f"🏁 *OPERACIÓN CERRADA: {symbol}*\n💰 Salida: ${analysis['current_price']}\n✅ Saldo liberado."
        requests.get(f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage", 
                     params={"chat_id": Config.TELEGRAM_CHAT_ID, "text": msg_close, "parse_mode": "Markdown"})
        return

    current_price = analysis['current_price']
    last_stop = active['last_stop']
    entry_price = active['entry_price']
    last_tp = active['targets'][0]

    # Trailing Adaptativo: Calculamos el % de distancia original (stop vs entrada)
    # y lo mantenemos fijo conforme el precio sube. SOLO SE MUEVE PARA ARRIBA.
    stop_distance_pct = (entry_price - active['last_stop']) / entry_price  # ej: 0.10 = 10%
    tp_distance_pct   = (last_tp - entry_price) / entry_price              # ej: 0.05 = 5%

    candidate_stop = round(current_price * (1 - stop_distance_pct), 2)
    candidate_tp   = round(current_price * (1 + tp_distance_pct), 2)

    # Solo actualizamos si el candidato es MAYOR que el stop actual (nunca bajamos)
    if candidate_stop > last_stop:
        new_stop = candidate_stop
        new_tp   = candidate_tp
        new_limit = round(new_stop * 0.998, 2)

        print(f"🛡️ Trailing Adaptativo {symbol}: Stop {last_stop} -> {new_stop} | TP {last_tp} -> {new_tp}")

        bm.cancel_open_orders(symbol)
        oco = bm.place_oco_sell(symbol, active['quantity'], new_tp, new_stop, new_limit)
        if oco:
            active['last_stop'] = new_stop
            active['targets'][0] = new_tp
            tm.save_active_trade(symbol, active)
    else:
        print(f"📊 {symbol} | Precio: {current_price} | Stop actual: {last_stop} (sin cambio)")
last_alerts_state = {}

def send_panorama_report(symbol):
    """Envía el Panorama 360 Multi-Temporalidad."""
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID: return
    try:
        report = JaimeMerinoIndicatorsEngine.get_multi_tf_report(symbol)
        msg = f"🪐 *PANORAMA 360: {symbol}*\n\n"
        for tf in ['1d', '4h', '1h', '15m']:
            data = report['timeframes'].get(tf, {})
            if data.get('status') == 'OFFLINE': continue
            msg += f"*{tf.upper()}*: {data['bias']} | {data['momentum']} | {data['whale']}\n"
        
        msg += f"\n🎯 _Gatillo 15m: {report['timeframes']['15m']['nadaraya']}_"
        
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": Config.TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"🚨 Error enviando Panorama: {e}")

def telegram_listener():
    """Hilo para escuchar comandos de Telegram."""
    last_update_id = 0
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getUpdates"
    print("📡 Listener de Telegram iniciado...")
    while True:
        try:
            res = requests.get(url, params={"offset": last_update_id + 1, "timeout": 20}, timeout=25).json()
            if res.get("ok"):
                for update in res.get("result", []):
                    last_update_id = update["update_id"]
                    msg = update.get("message", {})
                    text = msg.get("text", "").lower()
                    chat_id = msg.get("chat", {}).get("id")
                    
                    if str(chat_id) != str(Config.TELEGRAM_CHAT_ID): continue
                    
                    if text == "/panorama":
                        for s in Config.TRADING_SYMBOLS:
                            send_panorama_report(s)
                    elif text == "/resumen":
                        # Resumen compacto de todas las monedas ordenado por confianza
                        items = []
                        for s in Config.TRADING_SYMBOLS:
                            d = latest_analysis.get(s)
                            if not d: continue
                            sig = d['signal']['signal']
                            strength = d['signal']['signal_strength']
                            price = d['current_price']
                            emoji = '🟢' if sig == 'LONG' else '🔴' if sig == 'SHORT' else '⚪'
                            items.append((strength, f"{emoji} *{s.replace('USDT','')}* ${price} | {sig} {strength}%"))
                        items.sort(key=lambda x: x[0], reverse=True)
                        msg_res = "📊 *RANKING DE SEÑALES*\n" + "\n".join([i[1] for i in items])
                        requests.get(f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage",
                                     params={"chat_id": chat_id, "text": msg_res, "parse_mode": "Markdown"})
                    elif text.startswith("/"):
                        sym_raw = text.replace("/", "").upper()
                        symbol = sym_raw + "USDT" if "USDT" not in sym_raw else sym_raw
                        if symbol in Config.TRADING_SYMBOLS:
                            send_panorama_report(symbol)
                        elif text == "/balance":
                            balances = []
                            for s in Config.TRADING_SYMBOLS:
                                b = bm.get_symbol_balance(s)
                                if b > 0: balances.append(f"🔹 {s.replace('USDT','')}: {b}")
                            usdt = bm.get_symbol_balance("USDT")
                            msg_bal = "💰 *Tus Saldos:*\n" + "\n".join(balances) + f"\n💵 USDT: {usdt}"
                            requests.get(f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage", 
                                         params={"chat_id": chat_id, "text": msg_bal, "parse_mode": "Markdown"})
                        elif text == "/start":
                            requests.get(f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage", 
                                         params={"chat_id": chat_id, "text": "🤖 *Bot Merino PRO Activo*\nComandos:\n/panorama - Ver todo\n/balance - Ver dinero\n/btc - Ver Bitcoin\n/eth - Ver Ethereum", "parse_mode": "Markdown"})
        except Exception:
            pass
        time.sleep(3)

def send_telegram_alert(symbol, analysis):
    """Envía una alerta OCO clara a Telegram."""
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID: return
    
    sig = analysis.get('signal', {})
    levels = analysis.get('trading_levels', {})
    risk = analysis.get('risk_management', {})
    
    # Precios OCO
    tp = levels.get('targets', [0, 0])[0]
    stop_trigger = levels.get('stop_loss', 0)
    stop_limit = round(float(stop_trigger) * 0.998, 2) if stop_trigger else 0
    
    whale = str(sig.get('whale_alert', 'NORMAL')).replace("_", " ")
    
    msg = f"""
🚀 *[{symbol}] {sig.get('signal')} ({sig.get('signal_strength')}%)*

💰 Precio Actual: *${analysis.get('current_price')}*
💎 Whale: *{whale}*

📊 *CONFIGURACIÓN OCO:*
🏆 Ganancia: *{tp}*
🔔 Alarma (Stop): *{stop_trigger}*
🏃 Salida (Limit): *{stop_limit}*

🛡️ Apalancamiento: *{risk.get('recommended_leverage')}*
    """
    
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        res = requests.get(url, params={
            "chat_id": Config.TELEGRAM_CHAT_ID, 
            "text": msg, 
            "parse_mode": "Markdown"
        }, timeout=10)
        if res.status_code != 200:
            requests.get(url, params={"chat_id": Config.TELEGRAM_CHAT_ID, "text": msg.replace("*", "")}, timeout=10)
    except Exception as e:
        print(f"❌ Error excepcional Telegram: {e}")

def update_signals():
    """Bucle de fondo para actualizar señales, ejecutar trades y disparar alertas."""
    global latest_analysis, last_alerts_state
    symbols = Config.TRADING_SYMBOLS
    
    while True:
        try:
            print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Escaneando mercado...")
            new_data = {}
            for s in symbols:
                analysis = JaimeMerinoIndicatorsEngine.get_real_trading_analysis(s)
                new_data[s] = analysis
                
                # 1. Gestión de Alertas Telegram
                current_sig = analysis['signal']['signal']
                last_sig = last_alerts_state.get(s)
                
                if current_sig != last_sig and current_sig in ["LONG", "SHORT"]:
                    send_telegram_alert(s, analysis)
                    last_alerts_state[s] = current_sig
                elif current_sig == "WAIT":
                    last_alerts_state[s] = "WAIT"

                # 2. Protección: Trailing Stop
                check_trailing_stop(s, analysis)

                # 3. 🤖 EJECUCIÓN AUTÓNOMA (Fase 4)
                # Solo entramos si es un ALIEN (90%+) y NO hay trade activo
                if current_sig == "LONG" and analysis['signal']['signal_strength'] >= 90:
                    active_trades = tm.get_all_active()
                    total_exposure = sum([t.get('usdt_value', 0) for t in active_trades])
                    
                    # Verificar Límites de Riesgo (Config.MAX_USDT_TOTAL_EXPOSURE)
                    if not tm.get_active_trade(s) and (total_exposure + Config.MAX_USDT_ORDER) <= Config.MAX_USDT_TOTAL_EXPOSURE:
                        print(f"💰 SEÑAL ALIEN 👽 DETECTADA en {s}. Ejecutando Compra...")
                        
                        # Usar el monto configurado (MAX_USDT_ORDER)
                        buy_amount = Config.MAX_USDT_ORDER
                        
                        buy_order = bm.place_market_buy(s, buy_amount)
                        if buy_order:
                            qty = float(buy_order['executedQty'])
                            
                            # Notificación Inmediata de Compra
                            msg_buy = f"🛒 *BOT COMPRANDO: {s}*\n💵 Inversión: ${buy_amount} USDT\n📊 Exposición Total: ${total_exposure + buy_amount} USDT"
                            requests.get(f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage", 
                                         params={"chat_id": Config.TELEGRAM_CHAT_ID, "text": msg_buy, "parse_mode": "Markdown"})
                            
                            # Poner OCO inicial
                            tp = analysis['trading_levels']['targets'][0]
                            sl = analysis['trading_levels']['stop_loss']
                            bm.place_oco_sell(s, qty, tp, sl, round(sl * 0.998, 4))
                            
                            tm.save_active_trade(s, {
                                'quantity': qty,
                                'usdt_value': buy_amount,
                                'entry_price': analysis['current_price'],
                                'last_stop': sl,
                                'targets': analysis['trading_levels']['targets'],
                                'signals': analysis['signal']
                            })
            
            latest_analysis = new_data
            time.sleep(Config.UPDATE_SECONDS)
        except Exception as e:
            print(f"🚨 Error en loop de señales: {e}")
            time.sleep(30)

@app.route('/')
def dashboard():
    try:
        display_data = latest_analysis if latest_analysis else {}
        # Ordenar por confianza descendente
        sorted_data = dict(sorted(
            display_data.items(),
            key=lambda x: x[1]['signal']['signal_strength'],
            reverse=True
        ))
        return render_template('merino_dashboard.html', 
                              symbols_data=sorted_data, 
                              server_time=datetime.now().strftime('%H:%M:%S'),
                              stats={'symbols_analyzed': len(sorted_data), 'active_signals': len([x for x in sorted_data.values() if x['signal']['signal'] != 'WAIT'])},
                              philosophy={'risk_principle': "No operamos por emoción, operamos por confirmación institucional."})
    except Exception as e:
        return f"<h1>Error Interno</h1>", 500

@app.route('/api/data')
def api_data():
    return jsonify(latest_analysis)

@app.route('/chart/<symbol>')
def technical_chart(symbol):
    from flask import request
    timeframe = request.args.get('tf', '4h')
    return JaimeMerinoIndicatorsEngine.get_chart_html(symbol, timeframe)

if __name__ == '__main__':
    import threading
    
    # Hilo para el escáner
    scanner_thread = threading.Thread(target=update_signals, daemon=True)
    scanner_thread.start()
    
    # Hilo para comandos de Telegram
    listener_thread = threading.Thread(target=telegram_listener, daemon=True)
    listener_thread.start()
    
    print(f"🚀 Dashboard Online en http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
