# app.py
import streamlit as st
import pandas as pd
import numpy as np
import datetime
from binance.client import Client
from math import exp

# --- Configuración Binance (completa tus keys si deseas descargar velas) ---
API_KEY = "TU_API_KEY"
API_SECRET = "TU_API_SECRET"
client = Client(API_KEY, API_SECRET)

st.set_page_config(layout="wide", page_title="Estrategia SZ+ADX+Whale+Nadaraya Backtest")

# -----------------------
# Utilidades y cálculos
# -----------------------
def linreg(series, length):
    """Regresión lineal 'slope' sobre `series` con ventana `length`.
       Devuelve la última estimación (similar a ta.linreg(..., length, 0))"""
    if length <= 1 or len(series) < length:
        return np.nan
    y = series[-length:]
    x = np.arange(length)
    xm = x.mean()
    ym = y.mean()
    num = ((x - xm) * (y - ym)).sum()
    den = ((x - xm) ** 2).sum()
    slope = num / den if den != 0 else 0.0
    # returns slope * (length-1) + intercept equivalent? we will return slope (proxy)
    return slope

def rolling_linreg(arr, length):
    out = np.full(len(arr), np.nan)
    for i in range(length-1, len(arr)):
        out[i] = linreg(arr[i-length+1:i+1], length)
    return out

def custom_dirmov(high, low, length):
    up = high.diff().fillna(0)
    down = -low.diff().fillna(0)
    tr = pd.concat([high - low, high - high.shift(1).abs(), low - low.shift(1).abs()], axis=1).abs().max(axis=1)
    # rma (exponential moving average of TR)
    tr_rma = tr.ewm(span=length, adjust=False).mean()
    plus = ((up.where((up > down) & (up > 0), 0)).ewm(span=length, adjust=False).mean() * 100) / tr_rma.replace(0, np.nan)
    minus = ((down.where((down > up) & (down > 0), 0)).ewm(span=length, adjust=False).mean() * 100) / tr_rma.replace(0, np.nan)
    return plus.fillna(0), minus.fillna(0)

def custom_adx(high, low, close, dilen=14, adxlen=14):
    plus, minus = custom_dirmov(high, low, dilen)
    s = plus + minus
    adx = (abs(plus - minus) / s.replace(0, np.nan)).ewm(span=adxlen, adjust=False).mean() * 100
    return adx.fillna(0), plus, minus

def pivot_high(series, left=1, right=1):
    # True if current bar is highest among left previous and right forward
    ph = np.zeros(len(series), dtype=bool)
    for i in range(left, len(series)-right):
        window = series[i-left:i+right+1]
        if series[i] == window.max() and (series[i] > window.drop(i).max() if len(window.drop(i))>0 else True):
            ph[i] = True
    return pd.Series(ph, index=series.index)

def pivot_low(series, left=1, right=1):
    pl = np.zeros(len(series), dtype=bool)
    for i in range(left, len(series)-right):
        window = series[i-left:i+right+1]
        if series[i] == window.min() and (series[i] < window.drop(i).min() if len(window.drop(i))>0 else True):
            pl[i] = True
    return pd.Series(pl, index=series.index)

def compute_sz(df, period=20):
    # sz = linreg(close - avg(avg(highest(high,20), lowest(low,20)), sma(close,20)), 20, 0)
    h20 = df['high'].rolling(period).max()
    l20 = df['low'].rolling(period).min()
    s20 = df['close'].rolling(period).mean()
    adj = (h20 + l20) / 2.0
    adj = (adj + s20) / 2.0
    diff = df['close'] - adj
    # apply rolling linear reg slope on diff
    sz = rolling_linreg(diff.values, period)
    return pd.Series(sz, index=df.index)

# -----------------------
# Nadaraya-Watson smoothing (kernel)
# O(n^2) for window length; keep window razonable (<=500)
# -----------------------
def nadaraya_envelope(src, lengthN=200, h=8.0, multn=3.0, show=False):
    n = len(src)
    y = np.full(n, np.nan)
    mae_arr = np.full(n, np.nan)
    # compute for each last index only (to speed, we compute rolling with vectorized kernel when possible)
    # naive implementation but fine for backtests with moderate sizes
    for t in range(lengthN-1, n):
        window = src[t-lengthN+1:t+1].values
        weights = np.exp(- ( (np.arange(lengthN) - (lengthN-1))**2 ) / (2 * h * h))
        # for each i in window compute leave-one? The pine code computes y2 for every i inside loop,
        # but for confirmation we mostly need current smoothed y and mae over window
        # compute y2 series within window:
        ys = []
        sum_e = 0.0
        for i in range(lengthN):
            # center at i -> kernel weights relative to i
            w = np.exp(- ( (i - np.arange(lengthN))**2 ) / (2 * h * h))
            y2 = (window * w).sum() / w.sum()
            ys.append(y2)
            sum_e += abs(window[i] - y2)
        ys = np.array(ys)
        y[t] = ys[-1]  # last
        mae = (sum_e / lengthN) * multn
        mae_arr[t] = mae
    upper = y + mae_arr
    lower = y - mae_arr
    return pd.Series(y, index=src.index), pd.Series(upper, index=src.index), pd.Series(lower, index=src.index)

# -----------------------
# Whale detector (versión simplificada/interpretativa)
# Detecta picos en volatilidad relativos y rupturas en extremos
# -----------------------
def whale_detector(df, ema_window=30, lookback_extreme=58):
    low = df['low']
    high = df['high']
    close = df['close']
    # volatility proxy (abs diff)
    volp = (low - low.shift(1)).abs().rolling(3).mean().fillna(0)
    # local lowest and highest
    lowest_look = low.rolling(ema_window).min()
    highest_look = high.rolling(ema_window).max()
    # relative metric
    rel_low = (volp / (volp.rolling(ema_window).mean().replace(0, np.nan))).fillna(0)
    rel_high = rel_low  # symmetric for simplicity
    # conditions:
    whale = (low <= lowest_look) & (rel_low > rel_low.rolling(ema_window).median().fillna(0)*1.5)
    whale_invert = (high >= highest_look) & (rel_high > rel_high.rolling(ema_window).median().fillna(0)*1.5)
    # also require it to be recent extreme
    whale = whale & (low == low.rolling(lookback_extreme).min())
    whale_invert = whale_invert & (high == high.rolling(lookback_extreme).max())
    return whale.fillna(False), whale_invert.fillna(False)

# -----------------------
# Señales combinadas (según definiciones discutidas)
# -----------------------
def generate_signals(df,
                     adx_dilen=14,
                     adx_len=14,
                     pivot_left=1,
                     pivot_right=1,
                     nad_length=200,
                     nad_h=8.0,
                     nad_mult=3.0,
                     require_nadaraya_confirm=False):
    df = df.copy()
    df['sz'] = compute_sz(df, period=20)
    df['adx'], df['diplus'], df['diminus'] = custom_adx(df['high'], df['low'], df['close'], adx_dilen, adx_len)
    # pivots on sz and adx
    df['ph_sz'] = pivot_high(df['sz'].fillna(0), left=pivot_left, right=pivot_right)
    df['pl_sz'] = pivot_low(df['sz'].fillna(0), left=pivot_left, right=pivot_right)
    df['ph_adx'] = pivot_high(df['adx'].fillna(0), left=pivot_left, right=pivot_right)
    df['pl_adx'] = pivot_low(df['adx'].fillna(0), left=pivot_left, right=pivot_right)

    # buy/sell components
    # buy_cond1 = plFound(sz) and adxValue < adxValue[1]
    df['buy_cond1'] = df['pl_sz'] & (df['adx'] < df['adx'].shift(1))
    # buy_cond2 = phFound(adxValue) and sz >= sz[1] and sz < 0
    df['buy_cond2'] = df['ph_adx'] & (df['sz'] >= df['sz'].shift(1)) & (df['sz'] < 0)
    df['buy_c'] = df['buy_cond1'] | df['buy_cond2']

    # sell
    df['sell_cond1'] = df['ph_sz'] & (df['adx'] < df['adx'].shift(1))
    df['sell_cond2'] = df['ph_adx'] & (df['sz'] < df['sz'].shift(1)) & (df['sz'] > 0)
    df['sell_c'] = df['sell_cond1'] | df['sell_cond2']

    # whale detector
    df['whale'], df['whale_invert'] = whale_detector(df, ema_window=30, lookback_extreme=58)

    # Nadaraya envelope + confirmation
    nad_y, nad_up, nad_dn = nadaraya_envelope(df['close'], lengthN=min(nad_length, 500), h=nad_h, multn=nad_mult)
    df['nad_y'] = nad_y
    df['nad_up'] = nad_up
    df['nad_dn'] = nad_dn
    # Cross signals: price crosses below nad_up (from above -> bearish confirmation),
    # price crosses above nad_dn (from below -> bullish confirmation)
    df['nad_cross_bear'] = (df['close'].shift(1) > df['nad_up'].shift(1)) & (df['close'] < df['nad_up'])
    df['nad_cross_bull'] = (df['close'].shift(1) < df['nad_dn'].shift(1)) & (df['close'] > df['nad_dn'])

    # Final signals:
    if require_nadaraya_confirm:
        df['signal_buy'] = df['buy_c'] & df['nad_cross_bull']
        df['signal_sell'] = df['sell_c'] & df['nad_cross_bear']
    else:
        df['signal_buy'] = df['buy_c']
        df['signal_sell'] = df['sell_c']

    # combined strong signals
    df['strong_buy'] = df['signal_buy'] & df['whale']
    df['strong_sell'] = df['signal_sell'] & df['whale_invert']

    return df

# -----------------------
# Backtest similar a tu ejemplo
# -----------------------
def backtest_strategy(df_signals):
    trades = []
    position = None
    entry_price = None
    entry_time = None

    for i in range(1, len(df_signals)):
        row = df_signals.iloc[i]
        time = df_signals.index[i]
        # entry
        if position is None:
            if row['signal_buy']:
                position = 'long'
                entry_price = row['close']
                entry_time = time
                trades.append({'time': entry_time, 'signal': 'BUY', 'price': entry_price})
            elif row['signal_sell']:
                position = 'short'
                entry_price = row['close']
                entry_time = time
                trades.append({'time': entry_time, 'signal': 'SELL', 'price': entry_price})
        else:
            # close long
            if position == 'long' and row['signal_sell']:
                exit_price = row['close']
                profit = (exit_price - entry_price) / entry_price * 100
                trades.append({'time': time, 'signal': 'CLOSE_LONG', 'price': exit_price, 'profit%': round(profit, 2)})
                position = None
            # close short
            elif position == 'short' and row['signal_buy']:
                exit_price = row['close']
                profit = (entry_price - exit_price) / entry_price * 100
                trades.append({'time': time, 'signal': 'CLOSE_SHORT', 'price': exit_price, 'profit%': round(profit, 2)})
                position = None

    return pd.DataFrame(trades)

def calculate_metrics(trade_log: pd.DataFrame):
    if trade_log.empty:
        return {"total": 0, "wins": 0, "losses": 0, "winrate": 0.0, "avg_profit": 0.0}
    closed = trade_log[trade_log['signal'].str.contains("CLOSE")]
    total = len(closed)
    if total == 0:
        return {"total": 0, "wins": 0, "losses": 0, "winrate": 0.0, "avg_profit": 0.0}
    wins = (closed['profit%'] > 0).sum()
    losses = (closed['profit%'] <= 0).sum()
    winrate = round((wins / total) * 100, 2)
    avg_profit = round(closed['profit%'].mean(), 2)
    return {"total": total, "wins": int(wins), "losses": int(losses), "winrate": winrate, "avg_profit": avg_profit}

# -----------------------
# Interfaz Streamlit
# -----------------------
st.title("🧭 Estrategia: SZ + ADX + Whale + Nadaraya (Backtest)")

col1, col2 = st.columns([2,1])
with col1:
    symbol = st.text_input("Par de trading", "BTCUSDT")
    interval = st.selectbox("Intervalo", ["5m", "15m", "1h", "4h", "1d"])
    start_date = st.date_input("Fecha inicio", datetime.date(2025, 9, 20))
    end_date = st.date_input("Fecha fin", datetime.date(2025, 10, 4))

with col2:
    require_nada = st.checkbox("Exigir confirmación Nadaraya para entradas", value=False)
    nad_len = st.number_input("Nadaraya: length (<=500)", min_value=50, max_value=500, value=200)
    nad_h = st.number_input("Nadaraya: h (bandwidth)", min_value=1.0, max_value=50.0, value=8.0)
    nad_mult = st.number_input("Nadaraya: multn", min_value=0.5, max_value=10.0, value=3.0)

if st.button("📥 Descargar velas y ejecutar backtest"):
    start_dt = datetime.datetime.combine(start_date, datetime.time(0, 0))
    end_dt = datetime.datetime.combine(end_date, datetime.time(23, 59))
    start_str = start_dt.strftime("%d %b %Y %H:%M:%S")
    end_str = end_dt.strftime("%d %b %Y %H:%M:%S")

    klines = client.get_historical_klines(symbol, interval, start_str, end_str)
    if not klines:
        st.error("No se descargaron velas. Revisa el par/intervalo/fechas y tu conexión a Binance.")
    else:
        df = pd.DataFrame(klines, columns=[
            "timestamp","open","high","low","close","volume",
            "close_time","quote_asset_volume","trades",
            "taker_buy_base","taker_buy_quote","ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df = df[["open","high","low","close","volume"]].astype(float)

        st.subheader(f"📊 Velas descargadas (Total: {len(df)})")
        st.dataframe(df.tail(10))

        st.info("Calculando señales... (puede tardar si Nadaraya length es grande)")

        df_sig = generate_signals(df,
                                  adx_dilen=14,
                                  adx_len=14,
                                  pivot_left=1,
                                  pivot_right=1,
                                  nad_length=nad_len,
                                  nad_h=nad_h,
                                  nad_mult=nad_mult,
                                  require_nadaraya_confirm=require_nada)

        trade_log = backtest_strategy(df_sig)
        metrics = calculate_metrics(trade_log)

        st.subheader("📒 Historial de operaciones")
        st.dataframe(trade_log)

        st.subheader("📌 Métricas")
        st.markdown(f"""
        - Total operaciones cerradas: **{metrics['total']}**
        - Ganadoras: **{metrics['wins']}**
        - Perdedoras: **{metrics['losses']}**
        - Winrate: **{metrics['winrate']}%**
        - Profit promedio (cerradas): **{metrics['avg_profit']}%**
        """)

        # mostrar algunas series con señales
        st.subheader("📈 Señales / Visual check (últimas filas)")
        cols_show = ['close','sz','adx','signal_buy','signal_sell','strong_buy','strong_sell','whale','whale_invert','nad_y','nad_up','nad_dn','nad_cross_bull','nad_cross_bear']
        st.dataframe(df_sig[cols_show].tail(50))

        # quick counts
        st.write("Señales detectadas (totales):")
        st.write({
            'signal_buy': int(df_sig['signal_buy'].sum()),
            'signal_sell': int(df_sig['signal_sell'].sum()),
            'strong_buy (buy+whale)': int(df_sig['strong_buy'].sum()),
            'strong_sell (sell+whale_invert)': int(df_sig['strong_sell'].sum())
        })

        st.success("Backtest finalizado.")

# Footer / notas
st.markdown("""
---

**Notas técnicas y limitaciones**
- La implementación de Nadaraya es computacionalmente costosa (O(n * lengthN)). Usar length <= 500 para evitar demoras.
- El `whale_detector` está simplificado e interpretado a partir del Pine original; puede afinarse.
- Las pivotes y ADX están aproximadas; comportamiento puede diferir levemente del Pine Script original.
- Este backtest es muy básico (sin comisiones, sl/tp, tamaño de posición). Consideralo como **prueba de concepto**.
""")

