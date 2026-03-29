import pandas as pd
import pandas_ta as ta
import numpy as np
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modular_strategies.base import Trend, Signal, Squeeze

class TradingEngineV2:
    @staticmethod
    def _normalize_status(val):
        """Limpia strings de estados para lógica de trading (remueve emojis y espacios)."""
        if not isinstance(val, str): return val
        # Removemos emojis comunes y limpiamos espacios
        clean = val.split(' ')[0].strip().upper()
        return clean

    @staticmethod
    def get_binance_klines(symbol: str, interval: str, limit: int = 250) -> pd.DataFrame:
        """Obtiene velas de Binance (Igual que V1)."""
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
    def _calculate_volume_profile(df, lookback=100):
        """Calcula el VPoC (Volume Point of Control) simplificado."""
        try:
            subset = df.tail(lookback).copy()
            # Bins de precio (25 niveles entre min y max de los 100 periodos)
            p_min, p_max = subset['Low'].min(), subset['High'].max()
            bins = np.linspace(p_min, p_max, 25)
            
            # Sumar volumen por bin
            bin_vols = np.zeros(len(bins)-1)
            for i in range(len(bins)-1):
                mask = (subset['Close'] >= bins[i]) & (subset['Close'] < bins[i+1])
                bin_vols[i] = subset.loc[mask, 'Volume'].sum()
            
            # El bin con más volumen es el VPoC
            max_idx = np.argmax(bin_vols)
            vpoc_price = (bins[max_idx] + bins[max_idx+1]) / 2
            
            current_price = df['Close'].iloc[-1]
            dist_pct = ((current_price / vpoc_price) - 1) * 100
            
            return {
                'vpoc': round(float(vpoc_price), 2),
                'distance_pct': round(float(dist_pct), 2),
                'in_value_area': abs(dist_pct) < 5.0
            }
        except Exception:
            return {'vpoc': 0, 'distance_pct': 0, 'in_value_area': True}

    @staticmethod
    def _calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['yhat'] = TradingEngineV2._kernel_regression(df['Close'], 8.0, 4.0)
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
        df['whale_alert'] = Trend.NO_WHALE
        df.loc[(df['rsimfi'] > 0) & (df['manos_fuertes'] > 0), 'whale_alert'] = Trend.BULL
        df.loc[(df['rsimfi'] < 0) & (df['manos_fuertes'] < 0), 'whale_alert'] = Trend.BEAR
        
        df['ema_11'] = ta.ema(df['Close'], length=11)
        df['ema_55'] = ta.ema(df['Close'], length=55)
        df['ema_20'] = ta.ema(df['Close'], length=20)
        
        # BOLLINGER vs KELTNER (Detección de Squeeze ON)
        std_dev = df['Close'].rolling(window=20).std()
        df['bb_upper'] = df['ema_20'] + (2 * std_dev)
        df['bb_lower'] = df['ema_20'] - (2 * std_dev)
        
        tr = pd.concat([df['High']-df['Low'], (df['High']-df['Close'].shift(1)).abs(), (df['Low']-df['Close'].shift(1)).abs()], axis=1).max(axis=1)
        df['tr_range'] = tr.rolling(window=20).mean() * 1.5
        df['kc_upper'] = df['ema_20'] + df['tr_range']
        df['kc_lower'] = df['ema_20'] - df['tr_range']
        
        df['squeeze_on'] = (df['bb_lower'] > df['kc_lower']) & (df['bb_upper'] < df['kc_upper'])
        
        df['rsi'] = ta.rsi(df['Close'], length=14)
        
        # Bloque Seguro: ADX
        adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        adx_cols = [c for c in adx_df.columns if c.startswith('ADX')] if adx_df is not None else []
        df['adx'] = adx_df[adx_cols[0]] if adx_cols else 0
        
        # Bloque Seguro: Squeeze
        sqz = ta.squeeze(df['High'], df['Low'], df['Close'], lazybear=True)
        sqz_cols = [c for c in sqz.columns if c.startswith('SQZ_') and 'ON' not in c and 'OFF' not in c] if sqz is not None else []
        df['squeeze'] = sqz[sqz_cols[0]] if sqz_cols else 0
        
        # --- MONSTRUOS V2: Cálculos Avanzados ---
        # 1. Heikin-Ashi (Vectorizado rápido)
        o, h, l, c = df['Open'].values, df['High'].values, df['Low'].values, df['Close'].values
        ha_c = (o + h + l + c) / 4.0
        ha_o = np.zeros_like(o)
        ha_o[0] = (o[0] + c[0]) / 2.0
        for i in range(1, len(o)): ha_o[i] = (ha_o[i-1] + ha_c[i-1]) / 2.0
        ha_h = np.maximum.reduce([ha_o, ha_c, h])
        ha_l = np.minimum.reduce([ha_o, ha_c, l])
        df['HA_Close'] = ha_c
        df['HA_Open'] = ha_o
        df['HA_High'] = ha_h
        df['HA_Low'] = ha_l
        df['HA_Color'] = np.where(ha_c > ha_o, 1, -1) # 1 Verde, -1 Rojo
        
        # 2. Caza-Liquidaciones (Mechas de Absorción)
        vol_ma = df['Volume'].rolling(20).mean()
        df['Vol_Spike_Ratio'] = df['Volume'] / (vol_ma.replace(0, np.nan) + 1e-8)
        
        total_candle = (df['High'] - df['Low']).replace(0, np.nan)
        lower_wick = np.where(df['Close'] > df['Open'], df['Open'] - df['Low'], df['Close'] - df['Low'])
        df['Lower_Wick_Pct'] = (lower_wick / total_candle) * 100
        
        # 3. Trackeador de Divergencias Ocultas
        # Guardaremos el low y rsi históricos más profundos de las ultimas 30 velas (sin contar la vela actual)
        df['Rolling_Min_Low'] = df['Low'].shift(1).rolling(30).min()
        
        return df

    @staticmethod
    def get_real_trading_analysis(symbol: str) -> dict:
        """Versión Evolucionada (V2) con datos normalizados."""
        df_4h_klines = TradingEngineV2.get_binance_klines(symbol, '4h', limit=150)
        df_1h_klines = TradingEngineV2.get_binance_klines(symbol, '1h', limit=150)
        df_1d_klines = TradingEngineV2.get_binance_klines(symbol, '1d', limit=150)
        df_15m_klines = TradingEngineV2.get_binance_klines(symbol, '15m', limit=150)

        if df_4h_klines.empty or len(df_4h_klines) < 2:
            price = TradingEngineV2.get_backup_price(symbol)
            return {
                'symbol': symbol, 'current_price': price, 
                'signal': {'signal': 'OFFLINE', 'signal_strength': 0, 'bias': 'NEUTRAL', 'whale_alert': 'NORMAL'},
                'indicators': {'rsi': {'value': 50}, 'ema': {'ema_11': 0, 'ema_55': 0}, 'adx': {'value': 0}, 'nadaraya': {'upper': 0, 'lower': 0}},
                'multi_tf': {'1h': {'bias': 'NEUTRAL'}, '1d': {'bias': 'NEUTRAL'}},
                'report': {'ema_55': 0, 'time_info': 'OFFLINE'},
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
        
        df = TradingEngineV2._calculate_indicators(df_4h_klines)
        current_price = df['Close'].iloc[-1]
        whale = df['whale_alert'].iloc[-1]
        mf, rsi_v, adx_v = df['manos_fuertes'].iloc[-1], df['rsi'].iloc[-1], df['adx'].iloc[-1]
        e11, e55 = df['ema_11'].iloc[-1], df['ema_55'].iloc[-1]
        sqz, sqz_prev = df['squeeze'].iloc[-1], df['squeeze'].iloc[-2]
        
        # Detección de Divergencia Alcista Directa (Precio Low Más bajo, RSI Más alto que el valle anterior)
        # Buscamos el índice del mínimo de las últimas 30 velas
        bullish_divergence = False
        if len(df) > 30:
            hist_min_idx = df['Low'].iloc[-30:-2].idxmin() # Mínimo anterior
            hist_low = df.loc[hist_min_idx, 'Low']
            hist_rsi = df.loc[hist_min_idx, 'rsi']
            if current_price < hist_low and rsi_v > hist_rsi + 3.0: 
                bullish_divergence = True
        
        # Lógica Normalizada V2 con Constantes
        trend = Trend.BULLISH if e11 > e55 else Trend.BEARISH
        goLong = (whale == Trend.BULL) or (trend == Trend.BULLISH and sqz > sqz_prev)
        goShort = (whale == Trend.BEAR) or (trend == Trend.BEARISH and sqz < sqz_prev)
        
        if goLong and adx_v > 23: signal = Signal.LONG
        elif goShort and adx_v > 23: signal = Signal.SHORT
        else: signal = Signal.WAIT
        
        # 3. PUNTOS MERINO (Cálculo de Fuerza Profesional)
        # Sistema de 100 Puntos (Redistribuido para dar peso a Ballenas)
        vol_data = TradingEngineV2._calculate_volume_profile(df)
        m_pts = 0
        m_breakdown = {}
        
        # A. FACTOR BALLENA (Máx 30)
        _wp = 30 if whale == Trend.BULL else (15 if mf > 15 else 0)
        m_pts += _wp
        m_breakdown['ballena'] = {'name': '🐋 Factor Ballena', 'pts': _wp, 'max': 30, 'val': str(whale),
            'desc': 'Capital institucional detectado vía Koncorde + Heikin-Ashi.\n✅ Ballena BULL → 30pts (máximo). Manos fuertes > 15 → 15pts.\n⚠️ 0 pts: sin institucionales.'}
        
        # B. ADX (Máx 30)
        _dp = 30 if adx_v >= 50 else (20 if adx_v >= 35 else (10 if adx_v >= 23 else 0))
        m_pts += _dp
        m_breakdown['adx'] = {'name': '📈 ADX (Fuerza)', 'pts': _dp, 'max': 30, 'val': round(adx_v, 1),
            'desc': 'Intensidad cuantificada de la tendencia (ADX).\n✅ ≥50→30pts (extrema), ≥35→20pts (fuerte), ≥23→10pts (válida).\n⚠️ <23 → 0 pts: tendencia lateral, no operar.'}
        
        # C. MOMENTUM Squeeze (Máx 20)
        squeeze_val = abs(df['squeeze'].iloc[-1])
        _mp = min(20, int(squeeze_val * 10))
        m_pts += _mp
        m_breakdown['momentum'] = {'name': '💥 Squeeze Momentum', 'pts': _mp, 'max': 20, 'val': round(squeeze_val, 3),
            'desc': 'Magnitud del squeeze LazyBear liberado. Mide la energía comprimida que se está liberando ahora.\n✅ squeeze × 10, máximo 20pts.\n⚠️ ~0: sin compresión previa, entrada sin catalizador.'}
        
        # D. EMA 11 (Máx 10) — orden corregido: < 0.5 > < 2.0 > < 7.0
        dist_e11 = abs((current_price - e11) / e11) * 100
        _ep = 10 if dist_e11 < 0.5 else (5 if dist_e11 < 2.0 else (7 if dist_e11 < 7.0 else 0))
        m_pts += _ep
        m_breakdown['ema11'] = {'name': '🎯 Proximidad EMA11', 'pts': _ep, 'max': 10, 'val': f"{dist_e11:.1f}%",
            'desc': 'Distancia del precio a la EMA 11 (corto plazo). Cerca = entrada precisa.\n✅ <0.5%→10pts, <2%→5pts, <7%→7pts.\n⚠️ >7%: lejos de base, entrada tardía o sobreextendida.'}
        
        # E. VPoC (Máx 10)
        _vp = 10 if abs(vol_data['distance_pct']) < 2.0 else (5 if abs(vol_data['distance_pct']) < 5.0 else 0)
        m_pts += _vp
        m_breakdown['vpoc'] = {'name': '🧲 VPoC Cercanía', 'pts': _vp, 'max': 10, 'val': f"{vol_data['distance_pct']:.1f}%",
            'desc': 'Cercanía al Point of Control de volumen (zona de mayor actividad histórica).\n✅ <2%→10pts, <5%→5pts: hay soporte volumétrico real.\n⚠️ >5% → 0pts: sin respaldo de volumen.'}


        
        strength = m_pts # Nuestra fuerza profesional definitiva con ballenas incluidas
        
        multi_tf_data = {}
        for tf, df_tf in [('15m', df_15m_klines), ('1h', df_1h_klines), ('1d', df_1d_klines)]:
            if not df_tf.empty:
                df_calc = TradingEngineV2._calculate_indicators(df_tf)
                last = df_calc.iloc[-1]
                multi_tf_data[tf] = {
                    'bias': Trend.BULLISH if last['ema_11'] > last['ema_55'] else Trend.BEARISH,
                    'adx': float(last['adx']),
                    'squeeze_trend': Squeeze.UP if last['squeeze'] > df_calc['squeeze'].iloc[-2] else Squeeze.DOWN
                }
            else:
                multi_tf_data[tf] = {'bias': Trend.NEUTRAL, 'adx': 0, 'squeeze_trend': Squeeze.NEUTRAL}

        ob_bull, ob_bear = TradingEngineV2.detect_orderblocks(df)
        
        # 4. Volume Profile (RESURRECCIÓN PRO)
        vol_data = TradingEngineV2._calculate_volume_profile(df)
        
        leverage = 3.0 if strength >= 85 else 2.0 if strength >= 70 else 1.0
        
        return {
            'symbol': symbol,
            'current_price': float(current_price),
            'signal': {
                'signal': signal,
                'signal_strength': strength,
                'bias': trend,
                'whale_alert': whale,
                'whale_display': '👽 WHALE BULL' if whale == Trend.BULL else '👹 WHALE BEAR' if whale == Trend.BEAR else 'NORMAL',
                'volume_profile': vol_data,
                'squeeze_on': bool(df['squeeze_on'].iloc[-1]),
                'koncorde': {'strong_hands': float(mf), 'retail': 50.0}
            },
            'risk_management': {
                'recommended_leverage': f"{leverage}x",
                'invalidation_ema_11': e11 * 1.01 if trend == Trend.BEARISH else e11 * 0.99
            },
            'trading_levels': {
                'order_blocks': {'bullish_ob_price': ob_bull['price'] if ob_bull else 0.0, 'bearish_ob_price': ob_bear['price'] if ob_bear else 0.0}
            },
            'indicators': {
                'rsi': {'value': round(float(rsi_v), 1), 'bullish_divergence': bullish_divergence},
                'ema': {'ema_11': round(float(e11), 4), 'ema_55': round(float(e55), 4)},
                'adx': {'value': round(float(adx_v), 1)},
                'nadaraya': {'upper': round(float(df['upper_band'].iloc[-1]), 4), 'lower': round(float(df['lower_band'].iloc[-1]), 4)},
                'heikin_ashi': {
                    'color': int(df['HA_Color'].iloc[-1]),
                    'prev_color': int(df['HA_Color'].iloc[-2]),
                    'prev2_color': int(df['HA_Color'].iloc[-3]),
                    'open': float(df['HA_Open'].iloc[-1]),
                    'low': float(df['HA_Low'].iloc[-1])
                },
                'volume_spike': {
                    'ratio': round(float(df['Vol_Spike_Ratio'].iloc[-1]), 2),
                    'lower_wick_pct': round(float(df['Lower_Wick_Pct'].iloc[-1]), 2)
                }
            },
            'multi_tf': multi_tf_data,
            'report': {'ema_55': round(float(e55), 2), 'time_info': 'V2 ESCANEO OK'},
            'merino_breakdown': list(m_breakdown.values()),
            'last_update': datetime.now().strftime('%H:%M:%S')
        }

    @staticmethod
    def get_multi_tf_report(symbol: str) -> dict:
        """Reporte 360 Normalizado."""
        intervals = ['1d', '4h', '1h', '15m']
        report = {'symbol': symbol, 'timeframes': {}, 'timestamp': datetime.now().strftime('%H:%M:%S')}
        
        for tf in intervals:
            df_klines = TradingEngineV2.get_binance_klines(symbol, tf, limit=100)
            if df_klines.empty:
                report['timeframes'][tf] = {'status': 'OFFLINE'}
                continue
            
            df = TradingEngineV2._calculate_indicators(df_klines)
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            bias = Trend.BULLISH if last['ema_11'] > last['ema_55'] else Trend.BEARISH
            sqz_trend = Squeeze.UP if last['squeeze'] > prev['squeeze'] else Squeeze.DOWN

            report['timeframes'][tf] = {
                'price': round(float(last['Close']), 2),
                'bias': bias,
                'bias_display': f"{bias} 🟢" if bias == Trend.BULLISH else f"{bias} 🔴",
                'momentum': sqz_trend,
                'momentum_display': "SUBIENDO 📈" if sqz_trend == Squeeze.UP else "BAJANDO 📉",
                'squeeze_trend': sqz_trend,
                'whale': last['whale_alert'],
                'strength': round(float(last['adx']), 1),
                'nadaraya': 'SOBRECOMPRADO' if last['Close'] > last['upper_band'] else 'SOBREVENDIDO' if last['Close'] < last['lower_band'] else 'NORMAL'
            }
        return report

    @staticmethod
    def get_chart_html(symbol: str, interval: str = '4h', include_header: bool = True) -> str:
        """Gráfico Plotly (Idéntico a V1 pero compatible con V2)."""
        df_klines = TradingEngineV2.get_binance_klines(symbol, interval, limit=150)
        if df_klines.empty: return f"<h1>Error para {symbol}</h1>"
        df = TradingEngineV2._calculate_indicators(df_klines)
        
        from trade_manager_v2 import TradeManager
        active_trade = TradeManager.get_active_trade(symbol)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3], specs=[[{"secondary_y": False}], [{"secondary_y": True}]])
        fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Precio'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_11'], name='EMA 11', line=dict(color='yellow')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_55'], name='EMA 55', line=dict(color='orange')), row=1, col=1)
        
        colors = ['#00ff00' if v > (df['squeeze'].shift(1).iloc[i] or 0) else '#006400' if v > 0 else '#ff0000' if v < (df['squeeze'].shift(1).iloc[i] or 0) else '#8b0000' for i, v in enumerate(df['squeeze'])]
        fig.add_trace(go.Bar(x=df['Date'], y=df['squeeze'], name='Squeeze', marker_color=colors), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['adx'], name='ADX', line=dict(color='cyan')), row=2, col=1, secondary_y=True)
        
        fig.update_layout(height=800, template='plotly_dark', margin=dict(t=30, b=10, l=10, r=10), xaxis_rangeslider_visible=False)
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

if __name__ == "__main__":
    print(TradingEngineV2.get_multi_tf_report("BTCUSDT"))
