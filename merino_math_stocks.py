import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf
import time
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Silenciar advertencia de downcasting en pandas 2.2+
pd.set_option('future.no_silent_downcasting', True)

class MerinoStockEngine:
    @staticmethod
    def get_stock_klines(symbol: str, interval: str = '1h', period: str = None) -> pd.DataFrame:
        """Obtiene velas de Yahoo Finance."""
        if period is None:
            # Seleccionar periodo inteligente según temporalidad
            if interval == '15m': period = '5d'
            elif interval == '1h': period = '1mo'
            elif interval == '4h': period = '3mo'
            else: period = '1y'
            
        # Convertir intervalos de Binance a yfinance
        tf_map = {'15m': '15m', '1h': '1h', '4h': '1h', '1d': '1d'}
        yf_interval = tf_map.get(interval, '1h')
        
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(interval=yf_interval, period=period)
            if df.empty: return pd.DataFrame()
            
            # Reset index para tener 'Date' como columna
            df = df.reset_index()
            
            # 🟢 Arreglo Robusto: yfinance a veces llama a la columna 'Date' o 'Datetime'
            if 'Datetime' in df.columns:
                df = df.rename(columns={'Datetime': 'Date'})
            elif 'Date' not in df.columns: # Si el índice no tenía nombre
                df = df.rename(columns={df.columns[0]: 'Date'})
                
            # Asegurar tipos
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = df[col].astype(float)
            
            return df
        except Exception as e:
            print(f"⚠️ Yahoo Finance Error: {e}")
            return pd.DataFrame()

    @staticmethod
    def _calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        
        # 1. Koncorde (Simplificado basado en volumen y media)
        df['nvi'] = ta.nvi(df['Close'], df['Volume'])
        df['pvi'] = ta.pvi(df['Close'], df['Volume'])
        df['strong_hands'] = ta.ema(df['nvi'], length=15)
        
        # 2. Squeeze Momentum (Custom LazyBear Style)
        basis = ta.sma(df['Close'], length=20)
        dev = 2.0 * ta.stdev(df['Close'], length=20)
        upper_bb = basis + dev
        lower_bb = basis - dev
        
        ma_kc = ta.sma(df['Close'], length=20)
        range_kc = ta.true_range(df['High'], df['Low'], df['Close'])
        tr_sma = ta.sma(range_kc, length=20)
        upper_kc = ma_kc + tr_sma * 1.5
        lower_kc = ma_kc - tr_sma * 1.5
        
        df['squeeze'] = ta.linreg(df['Close'] - (ta.sma(df['High'].rolling(20).max() + df['Low'].rolling(20).min(), 20)/2 + ta.sma(df['Close'], 20))/2, length=20)
        
        # 3. ADX
        adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        df['adx'] = adx_df['ADX_14'] if adx_df is not None else 0
        
        # 4. EMAs
        df['ema_11'] = ta.ema(df['Close'], length=11)
        df['ema_55'] = ta.ema(df['Close'], length=55)
        
        # 5. Nadaraya-Watson (Kernel Regression)
        df['upper_band'] = df['Close'] + (ta.atr(df['High'], df['Low'], df['Close'], length=10) * 2)
        df['lower_band'] = df['Close'] - (ta.atr(df['High'], df['Low'], df['Close'], length=10) * 2)
        
        # 🟢 Lógica de seguridad: Solo quitamos lo que no tenga EMA calculada aún.
        # No usamos dropna() a ciegas porque si un solo indicador falla (como ADX o NVI) nos borra todo el dataframe.
        df = df.dropna(subset=['ema_11', 'ema_55']).reset_index(drop=True)
        return df

    @staticmethod
    def get_chart_html(symbol: str, interval: str = '1h') -> str:
        df_klines = MerinoStockEngine.get_stock_klines(symbol, interval)
        if df_klines.empty: return f"<h1>Error obteniendo datos para {symbol}</h1>"
        df = MerinoStockEngine._calculate_indicators(df_klines)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3], specs=[[{"secondary_y": False}], [{"secondary_y": True}]])
        fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Precio'), row=1, col=1)
        
        # Nadaraya
        fig.add_trace(go.Scatter(x=df['Date'], y=df['upper_band'], name='Band Upper', line=dict(color='rgba(255,50,50,0.5)', dash='dot')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['lower_band'], name='Band Lower', line=dict(color='rgba(50,255,50,0.5)', dash='dot')), row=1, col=1)
        
        # EMAs
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_11'], name='EMA 11', line=dict(color='yellow')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_55'], name='EMA 55', line=dict(color='orange')), row=1, col=1)
        
        # Squeeze & ADX
        colors = ['#00ff00' if v > (df['squeeze'].shift(1).iloc[i] or 0) else '#006400' if v > 0 else '#ff0000' if v < (df['squeeze'].shift(1).iloc[i] or 0) else '#8b0000' for i, v in enumerate(df['squeeze'])]
        fig.add_trace(go.Bar(x=df['Date'], y=df['squeeze'], name='Squeeze', marker_color=colors), row=2, col=1, secondary_y=False)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['adx'], name='ADX', line=dict(color='cyan')), row=2, col=1, secondary_y=True)
        fig.update_yaxes(range=[0, 100], secondary_y=True, row=2, col=1)

        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]), # hide weekends
                dict(bounds=[16, 9.5], pattern="hour"), # hide hours outside 9:30am - 4pm
            ]
        )
        fig.update_layout(height=800, template='plotly_dark', margin=dict(t=10, b=10, l=10, r=10), xaxis_rangeslider_visible=False)
        chart_div = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        if df.empty: return f"<h1>Datos insuficientes para {symbol}</h1>"
        current_price = df['Close'].iloc[-1]
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{symbol} Stock Chart</title>
            <style>
                body {{ background: #0a0a0f; color: white; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; overflow-x: hidden; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; padding: 15px 25px; background: #14141f; border-bottom: 2px solid #1a1a2e; }}
                .h-left {{ display: flex; align-items: center; gap: 20px; }}
                .symbol-title {{ margin: 0; font-size: 1.8rem; font-weight: 800; color: #ffcc00; }}
                .price {{ font-size: 1.4rem; font-weight: bold; color: #00ff88; }}
                .controls {{ display: flex; align-items: center; gap: 10px; }}
                select {{ background: #1a1a2e; color: #ffcc00; border: 1px solid #333; padding: 10px 15px; border-radius: 8px; font-size: 1rem; cursor: pointer; font-weight: bold; outline: none; }}
                select:hover {{ border-color: #ffcc00; }}
                .chart-container {{ padding: 0; margin: 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="h-left">
                    <h1 class="symbol-title">{symbol}</h1>
                    <div class="price">${current_price:.2f}</div>
                </div>
                <div class="controls">
                    <label style="color: #666; font-size: 0.8rem; font-weight: 800;">TEMPORALIDAD:</label>
                    <select onchange="window.location.href='/chart/{symbol}?tf=' + this.value">
                        <option value="15m" {"selected" if interval == "15m" else ""}>15m</option>
                        <option value="1h" {"selected" if interval == "1h" else ""}>1h</option>
                        <option value="4h" {"selected" if interval == "4h" else ""}>4h</option>
                        <option value="1d" {"selected" if interval == "1d" else ""}>1D</option>
                    </select>
                </div>
            </div>
            <div class="chart-container">
                {chart_div}
            </div>
        </body>
        </html>
        """
        return html_template
