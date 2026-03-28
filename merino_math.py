import pandas as pd
import pandas_ta as ta
import numpy as np
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class JaimeMerinoIndicatorsEngine:
    @staticmethod
    def get_binance_klines(symbol: str, interval: str, limit: int = 250) -> pd.DataFrame:
        """Obtiene velas de Binance con fallback a CoinGecko para precios si falla."""
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data, columns=['Open_Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_Time', 'Quote_Volume', 'Trades', 'Taker_Buy_Base', 'Taker_Buy_Quote', 'Ignore'])
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = df[col].astype(float)
            df['Date'] = pd.to_datetime(df['Close_Time'], unit='ms')
            return df
        except Exception as e:
            print(f"⚠️ Binance API Fail: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_backup_price(symbol: str) -> float:
        mapping = {'BTCUSDT': 'bitcoin', 'ETHUSDT': 'ethereum'}
        coin_id = mapping.get(symbol.upper(), 'bitcoin')
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            res = requests.get(url, timeout=5).json()
            return float(res[coin_id]['usd'])
        except:
            return 0.0

    @staticmethod
    def _kernel_regression(series: pd.Series, h=8.0, r=4.0):
        series = pd.to_numeric(series, errors="coerce").ffill().bfill()
        size = len(series)
        yhat = []
        for t in range(size):
            if size - t > 100: 
                yhat.append(series.iloc[t])
                continue
            cw, c_weight = 0.0, 0.0
            for i in range(min(size - t, 50)):
                y = float(series.iloc[t + i])
                w = (1 + (i**2) / ((h**2) * 2 * r)) ** -r
                cw += y * w
                c_weight += w
            yhat.append(cw / c_weight if c_weight != 0 else float(series.iloc[t]))
        return pd.Series(yhat, index=series.index)

    @staticmethod
    def detect_orderblocks(df: pd.DataFrame, lookback=30):
        ob_bull, ob_bear = None, None
        highs, lows = df['High'].values, df['Low'].values
        closes, opens = df['Close'].values, df['Open'].values
        for i in range(max(1, len(df) - lookback), len(df) - 2):
            if closes[i] < opens[i] and closes[i+1] > opens[i+1] and closes[i+2] > highs[i+1]:
                ob_bull = {'price': lows[i], 'top': highs[i]}
            if closes[i] > opens[i] and closes[i+1] < opens[i+1] and closes[i+2] < lows[i+1]:
                ob_bear = {'price': highs[i], 'bottom': lows[i]}
        return ob_bull, ob_bear

    @staticmethod
    def _calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['yhat'] = JaimeMerinoIndicatorsEngine._kernel_regression(df['Close'], 8.0, 4.0)
        atr = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['upper_band'] = df['yhat'] + 1.5 * atr
        df['lower_band'] = df['yhat'] - 1.5 * atr
        
        # Koncorde (Simplified Blue)
        nvi = df['Volume'].copy()
        for i in range(1, len(df)):
            nvi.iloc[i] = nvi.iloc[i-1] + df['Volume'].iloc[i] if df['Close'].iloc[i] < df['Close'].iloc[i-1] else nvi.iloc[i-1]
        nvim = nvi.ewm(span=15).mean()
        nvimax = nvim.rolling(window=90).max()
        nvimin = nvim.rolling(window=90).min()
        df['manos_fuertes'] = 100 * (nvi - nvim) / (nvimax - nvimin + 1e-6)
        
        # Whale HA
        num = (df['Close'] - df['Open'])
        den = (df['High'] - df['Low']).replace(0, np.nan)
        df['rsimfi'] = ((num / den) * 150).rolling(60).mean().fillna(0.0)
        df['whale_alert'] = 'NO'
        df.loc[(df['rsimfi'] > 0) & (df['manos_fuertes'] > 0), 'whale_alert'] = 'BULL'
        df.loc[(df['rsimfi'] < 0) & (df['manos_fuertes'] < 0), 'whale_alert'] = 'BEAR'
        
        df['ema_11'] = ta.ema(df['Close'], length=11)
        df['ema_55'] = ta.ema(df['Close'], length=55)
        df['rsi'] = ta.rsi(df['Close'], length=14)
        adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        df['adx'] = adx_df[[c for c in adx_df.columns if c.startswith('ADX')][0]]
        sqz = ta.squeeze(df['High'], df['Low'], df['Close'], lazybear=True)
        hist_col = [c for c in sqz.columns if c.startswith('SQZ_') and 'ON' not in c and 'OFF' not in c and 'NO' not in c][0]
        df['squeeze'] = sqz[hist_col]
        return df

    @staticmethod
    def get_real_trading_analysis(symbol: str) -> dict:
        # 1. Obtener datos de varias temporalidades
        df_4h_klines = JaimeMerinoIndicatorsEngine.get_binance_klines(symbol, '4h', limit=150)
        df_1h_klines = JaimeMerinoIndicatorsEngine.get_binance_klines(symbol, '1h', limit=150)
        df_1d_klines = JaimeMerinoIndicatorsEngine.get_binance_klines(symbol, '1d', limit=150)

        if df_4h_klines.empty:
            price = JaimeMerinoIndicatorsEngine.get_backup_price(symbol)
            return {
                'symbol': symbol, 'current_price': price, 
                'signal': {'signal': 'OFFLINE', 'signal_strength': 0, 'bias': 'NEUTRAL', 'whale_alert': 'NO_DATA', 'koncorde': {'strong_hands': 0}},
                'risk_management': {'recommended_leverage': '1x', 'invalidation_ema_11': 0},
                'trading_levels': {'targets': [0, 0], 'stop_loss': 0, 'order_blocks': {'bullish_ob_price': 0, 'bearish_ob_price': 0}},
                'indicators': {
                    'rsi': {'value': 50}, 'ema': {'ema_11': 0, 'ema_55': 0}, 'adx': {'value': 0}, 
                    'nadaraya': {'upper': 0, 'lower': 0}
                },
                'multi_tf': {
                    '1h': {'bias': 'NEUTRAL', 'adx': 0, 'squeeze': 0},
                    '1d': {'bias': 'NEUTRAL', 'adx': 0, 'squeeze': 0}
                },
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
        
        # 2. Procesar 4h (Temporalidad principal)
        df = JaimeMerinoIndicatorsEngine._calculate_indicators(df_4h_klines)
        current_price = df['Close'].iloc[-1]
        whale = df['whale_alert'].iloc[-1]
        mf, rsi_v, adx_v = df['manos_fuertes'].iloc[-1], df['rsi'].iloc[-1], df['adx'].iloc[-1]
        e11, e55 = df['ema_11'].iloc[-1], df['ema_55'].iloc[-1]
        sqz, sqz_prev = df['squeeze'].iloc[-1], df['squeeze'].iloc[-2]
        
        trend = 'BULLISH' if e11 > e55 else 'BEARISH'
        goLong = (whale == 'BULL') or (trend == 'BULLISH' and sqz > sqz_prev)
        goShort = (whale == 'BEAR') or (trend == 'BEARISH' and sqz < sqz_prev)
        
        if goLong and adx_v > 23: signal, strength = 'LONG', 90 if mf > 10 else 75
        elif goShort and adx_v > 23: signal, strength = 'SHORT', 90 if mf < -10 else 75
        else: signal, strength = 'WAIT', 50
        
        # 3. Procesar otras temporalidades para "Filtro de Fuerza"
        multi_tf_data = {}
        for tf, df_tf in [('1h', df_1h_klines), ('1d', df_1d_klines)]:
            if not df_tf.empty:
                df_calc = JaimeMerinoIndicatorsEngine._calculate_indicators(df_tf)
                last = df_calc.iloc[-1]
                multi_tf_data[tf] = {
                    'bias': 'BULLISH' if last['ema_11'] > last['ema_55'] else 'BEARISH',
                    'adx': float(last['adx']),
                    'squeeze': float(last['squeeze']),
                    'squeeze_trend': 'UP' if last['squeeze'] > df_calc['squeeze'].iloc[-2] else 'DOWN'
                }
            else:
                multi_tf_data[tf] = {'bias': 'NEUTRAL', 'adx': 0, 'squeeze': 0, 'squeeze_trend': 'NEUTRAL'}

        ob_bull, ob_bear = JaimeMerinoIndicatorsEngine.detect_orderblocks(df)
        leverage = 3.0 if strength >= 85 else 2.0 if strength >= 70 else 1.0
        invalidation = e11 * 1.01 if trend == 'BEARISH' else e11 * 0.99
        
        # Niveles Explícitos (LONG vs SHORT)
        # 1. Setup LONG (Compra)
        sl_l = ob_bull['price'] if ob_bull else current_price * 0.98
        tg1_l = current_price * 1.02
        
        # 2. Setup SHORT (Venta)
        sl_s = ob_bear['price'] if ob_bear else current_price * 1.02
        tg1_s = current_price * 0.98

        return {
            'symbol': symbol,
            'current_price': float(current_price),
            'signal': {
                'signal': signal,
                'signal_strength': strength,
                'bias': trend,
                'whale_alert': 'WHALE BULL ALIEN 👽' if whale == 'BULL' else 'WHALE BEAR OGRE 👹' if whale == 'BEAR' else 'NORMAL',
                'koncorde': {'strong_hands': float(mf), 'retail': 50.0}
            },
            'risk_management': {
                'recommended_leverage': f"{leverage}x",
                'invalidation_ema_11': invalidation,
                'max_position': "2% Capital"
            },
            'trading_levels': {
                'long': { 'targets': [tg1_l], 'stop_loss': sl_l, 'entry': current_price * 1.001 },
                'short': { 'targets': [tg1_s], 'stop_loss': sl_s, 'entry': current_price * 0.999 },
                'targets': [tg1_l], # Legacy/Default for LONG
                'stop_loss': sl_l,   # Legacy/Default for LONG
                'order_blocks': {'bullish_ob_price': ob_bull['price'] if ob_bull else 0.0, 'bearish_ob_price': ob_bear['price'] if ob_bear else 0.0}
            },
            'indicators': {
                'rsi': {'value': round(float(rsi_v), 1)},
                'ema': {'ema_11': round(float(e11), 4), 'ema_55': round(float(e55), 4)},
                'adx': {'value': round(float(adx_v), 1)},
                'nadaraya': {'upper': round(float(df['upper_band'].iloc[-1]), 4), 'lower': round(float(df['lower_band'].iloc[-1]), 4), 'status': 'OPTIMAL' if df['Close'].iloc[-1] > df['lower_band'].iloc[-1] else 'EXTREME'}
            },
            'multi_tf': multi_tf_data,
            'last_update': datetime.now().strftime('%H:%M:%S')
        }

    @staticmethod
    def get_chart_html(symbol: str, interval: str = '4h') -> str:
        df_klines = JaimeMerinoIndicatorsEngine.get_binance_klines(symbol, interval, limit=150)
        if df_klines.empty: return f"<h1>Error para {symbol}</h1>"
        df = JaimeMerinoIndicatorsEngine._calculate_indicators(df_klines)
        
        from trade_manager import TradeManager
        active_trade = TradeManager.get_active_trade(symbol)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3], specs=[[{"secondary_y": False}], [{"secondary_y": True}]])
        fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Precio'), row=1, col=1)
        
        # Nadaraya
        fig.add_trace(go.Scatter(x=df['Date'], y=df['upper_band'], name='Nadaraya Upper', line=dict(color='rgba(255,50,50,0.5)', dash='dot')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['lower_band'], name='Nadaraya Lower', line=dict(color='rgba(50,255,50,0.5)', dash='dot')), row=1, col=1)
        
        # EMAs
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_11'], name='EMA 11', line=dict(color='yellow')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_55'], name='EMA 55', line=dict(color='orange')), row=1, col=1)
        
        # OB
        ob_bull, ob_bear = JaimeMerinoIndicatorsEngine.detect_orderblocks(df)
        if ob_bull: fig.add_shape(type="rect", x0=df['Date'].iloc[-30], x1=df['Date'].iloc[-1], y0=ob_bull['price'], y1=ob_bull['top'], fillcolor="rgba(0,255,0,0.1)", line=dict(width=0), row=1, col=1)
        if ob_bear: fig.add_shape(type="rect", x0=df['Date'].iloc[-30], x1=df['Date'].iloc[-1], y0=ob_bear['bottom'], y1=ob_bear['price'], fillcolor="rgba(255,0,0,0.1)", line=dict(width=0), row=1, col=1)
        
        # Squeeze & ADX
        colors = ['#00ff00' if v > (df['squeeze'].shift(1).iloc[i] or 0) else '#006400' if v > 0 else '#ff0000' if v < (df['squeeze'].shift(1).iloc[i] or 0) else '#8b0000' for i, v in enumerate(df['squeeze'])]
        fig.add_trace(go.Bar(x=df['Date'], y=df['squeeze'], name='Squeeze', marker_color=colors), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['adx'], name='ADX', line=dict(color='cyan')), row=2, col=1, secondary_y=True)
        fig.update_yaxes(range=[0, 100], secondary_y=True, row=2, col=1)
        
        # Whales
        whales = df[df['whale_alert'] != 'NO']
        if not whales.empty:
            fig.add_trace(go.Scatter(x=whales['Date'], y=whales['Close'], mode='markers', name='Whale Alert', marker=dict(symbol='diamond', size=12, color='magenta')), row=1, col=1)
            
        # Órdenes Activas
        if active_trade:
            entry = active_trade.get('entry_price')
            tp = active_trade.get('targets', [0])[0]
            sl = active_trade.get('last_stop')
            
            if entry:
                fig.add_hline(y=entry, line_dash="dash", line_color="#00e676", annotation_text=f"ENTRY: ${entry}", annotation_position="top right", row=1, col=1)
            if tp:
                fig.add_hline(y=tp, line_dash="dot", line_color="#00bfff", annotation_text=f"T/P: ${tp}", annotation_position="top right", row=1, col=1)
            if sl:
                fig.add_hline(y=sl, line_dash="solid", line_color="#ff1744", annotation_text=f"S/L (Trailing): ${sl}", annotation_position="bottom right", row=1, col=1)

        fig.update_layout(height=800, template='plotly_dark', margin=dict(t=30, b=10, l=10, r=10), xaxis_rangeslider_visible=False)
        chart_div = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        current_price = df['Close'].iloc[-1]
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{symbol} Chart ({interval})</title>
            <style>
                body {{ background-color: #111; color: white; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #1a1a2e; border-bottom: 2px solid #0f3460; }}
                .header-left {{ display: flex; align-items: center; gap: 20px; }}
                .symbol-title {{ margin: 0; font-size: 1.8rem; font-weight: bold; color: #00f2ff; letter-spacing: 1px; }}
                .price {{ font-size: 1.4rem; font-weight: bold; color: #00ff88; }}
                .controls {{ display: flex; align-items: center; gap: 10px; }}
                select {{ background: #16213e; color: #00f2ff; border: 1px solid #0f3460; padding: 8px 15px; border-radius: 6px; font-size: 1rem; cursor: pointer; font-weight: bold; outline: none; }}
                select:hover {{ border-color: #00f2ff; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="header-left">
                    <h1 class="symbol-title">{symbol}</h1>
                    <div class="price">${current_price:.4f}</div>
                </div>
                <div class="controls">
                    <label style="color: #888; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Temporalidad:</label>
                    <select onchange="window.location.href='/chart/{symbol}?tf=' + this.value">
                        <option value="15m" {"selected" if interval == "15m" else ""}>15m</option>
                        <option value="1h" {"selected" if interval == "1h" else ""}>1h</option>
                        <option value="4h" {"selected" if interval == "4h" else ""}>4h</option>
                        <option value="1d" {"selected" if interval == "1d" else ""}>1d</option>
                    </select>
                </div>
            </div>
            <div class="chart-container" style="padding-top: 10px;">
                {chart_div}
            </div>
        </body>
        </html>
        """
        return html_template

    @staticmethod
    def get_multi_tf_report(symbol: str) -> dict:
        """Genera un reporte consolidado de 4 temporalidades para el Panorama 360."""
        intervals = ['1d', '4h', '1h', '15m']
        report = {'symbol': symbol, 'timeframes': {}, 'timestamp': datetime.now().strftime('%H:%M:%S')}
        
        for tf in intervals:
            df_klines = JaimeMerinoIndicatorsEngine.get_binance_klines(symbol, tf, limit=100)
            if df_klines.empty:
                report['timeframes'][tf] = {'status': 'OFFLINE'}
                continue
            
            df = JaimeMerinoIndicatorsEngine._calculate_indicators(df_klines)
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            report['timeframes'][tf] = {
                'price': round(float(last['Close']), 2),
                'bias': 'BULLISH 🟢' if last['ema_11'] > last['ema_55'] else 'BEARISH 🔴',
                'momentum': 'SUBIENDO 📈' if last['squeeze'] > prev['squeeze'] else 'BAJANDO 📉',
                'squeeze_trend': 'UP' if last['squeeze'] > prev['squeeze'] else 'DOWN',
                'whale': last['whale_alert'],
                'strength': round(float(last['adx']), 1),
                'nadaraya': 'SOBRECOMPRADO ⚠️' if last['Close'] > last['upper_band'] else 'SOBREVENDIDO ✅' if last['Close'] < last['lower_band'] else 'ZONA MEDIA'
            }
        return report

if __name__ == "__main__":
    # Test simple
    print(JaimeMerinoIndicatorsEngine.get_multi_tf_report("BTCUSDT"))
