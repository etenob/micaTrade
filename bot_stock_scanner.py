import os
import sys
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request

from merino_math_stocks import MerinoStockEngine
from config import Config

app = Flask(__name__)

# Configuración de símbolos para la bolsa
STOCK_SYMBOLS = [
    'AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMD', 
    'META', 'GOOGL', 'AMZN', 'NFLX', 'COIN',
    'BABA', 'PYPL', 'INTC', 'DIS', 'ORCL'
]

# Cache para señales
latest_stock_data = {}

def update_stock_signals():
    global latest_stock_data
    while True:
        print(f"\n🔄 Actualizando señales de Bolsa: {datetime.now().strftime('%H:%M:%S')}")
        new_data = {}
        for s in STOCK_SYMBOLS:
            try:
                # Obtenemos 1 mes para tener suficiente data para EMA 55
                df = MerinoStockEngine.get_stock_klines(s, interval='1h', period='1mo')
                if not df.empty:
                    df = MerinoStockEngine._calculate_indicators(df)
                    if df.empty: continue # Salta si dropna() dejó vacio el DF
                    last = df.iloc[-1]
                    
                    # Lógica de señales básica (Merino Style)
                    signal = "WAIT"
                    conf = 50
                    
                    # Gatillo 11 & Squeeze
                    if last['Close'] > last['ema_11'] and last['squeeze'] > 0:
                        signal = "LONG"
                        conf = 75
                        if last['adx'] > 20: conf = 90
                    elif last['Close'] < last['ema_11'] and last['squeeze'] < 0:
                        signal = "SHORT"
                        conf = 75
                    
                    new_data[s] = {
                        'symbol': s,
                        'price': last['Close'],
                        'signal': signal,
                        'confidence': conf,
                        'ema_11': last['ema_11'],
                        'ema_55': last['ema_55'],
                        'adx': last['adx'],
                        'squeeze': last['squeeze']
                    }
            except Exception as e:
                print(f"❌ Error en {s}: {e}")
        
        latest_stock_data = new_data
        # Actualizamos cada 5 minutos (la bolsa es más lenta)
        time.sleep(300)

@app.route('/')
def stock_dashboard():
    # Ordenar por confianza descendente
    sorted_stocks = dict(sorted(latest_stock_data.items(), 
                                key=lambda x: x[1]['confidence'], 
                                reverse=True))
    return render_template('stock_dashboard.html', 
                           stocks=sorted_stocks,
                           server_time=datetime.now().strftime('%H:%M:%S'),
                           active_page='stocks')

@app.route('/chart/<symbol>')
def stock_chart(symbol):
    tf = request.args.get('tf', '1h')
    return MerinoStockEngine.get_chart_html(symbol, tf)

if __name__ == '__main__':
    # Hilo para escaneo de fondo
    threading.Thread(target=update_stock_signals, daemon=True).start()
    # Puerto 5001 para no chocar con el de Crypto
    print("🚀 Stock Scanner Station iniciado en http://127.0.0.1:5001")
    app.run(port=5001, debug=False)
