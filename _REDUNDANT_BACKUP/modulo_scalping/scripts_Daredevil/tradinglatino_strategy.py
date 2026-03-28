"""
tradinglatino_strategy.py
Implementa estrategia estilo TradingLatino:
 - EMA10 / EMA55 crossover + MACD confirm + RSI filter
 - Exit on EMA cross down OR RSI > 80
 - Calcula soportes/resistencias simples (rolling)
 - Descarga velas vía ccxt, calcula indicadores con pandas_ta,
   detecta señales y guarda CSV con resultados y resumen en consola.
"""

import os
import time
from datetime import datetime
import ccxt
import pandas as pd

# === CONFIG (modifica aquí) ===
MARKET = 'spot'                       # 'spot' o 'futures'
EXCHANGE_ID_SPOT = 'binance'
EXCHANGE_ID_FUTURES = 'binanceusdm'   # intento, puede variar según versión ccxt
SYMBOL = 'BTC/USDT'
TIMEFRAME = '15m'
START_LOCAL = '2025-08-07 14:30:00'   # en America/Argentina/Buenos_Aires
END_LOCAL   = '2025-08-07 17:00:00'   # en America/Argentina/Buenos_Aires
TZ_LOCAL = 'America/Argentina/Buenos_Aires'

OUTPUT_DIR = './Scripts_Daredevil/Bitacora'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Indicator params
EMA_FAST = 10
EMA_SLOW = 55
RSI_LEN = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Support/Resistance window (simple rolling)
SR_WINDOW = 20

# === Imports for indicators (defer to runtime for clearer error) ===
try:
    import pandas_ta as ta
except Exception as e:
    raise ImportError("Necesitas instalar pandas_ta: pip install pandas_ta") from e

# === Helper: connect to exchange ===
def get_exchange(market='spot'):
    if market == 'futures':
        try:
            return getattr(ccxt, EXCHANGE_ID_FUTURES)()
        except Exception:
            print("Advertencia: no se pudo instanciar exchange futures; usando spot como fallback.")
            return getattr(ccxt, EXCHANGE_ID_SPOT)()
    else:
        return getattr(ccxt, EXCHANGE_ID_SPOT)()

# === Convert local times to UTC ms ===
def to_utc_ms(local_str):
    ts = pd.Timestamp(local_str, tz=TZ_LOCAL)
    return int(ts.tz_convert('UTC').timestamp() * 1000)

# === Fetch OHLCV in a safe loop (fills all klines in range) ===
def fetch_ohlcv_range(exchange, symbol, timeframe, start_ms, end_ms):
    all_klines = []
    since = start_ms
    while since < end_ms:
        try:
            klines = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=1000)
        except Exception as e:
            print("Error fetch_ohlcv, retrying in 1s:", e)
            time.sleep(1)
            continue
        if not klines:
            break
        for k in klines:
            t = int(k[0])
            if t >= end_ms:
                break
            all_klines.append(k)
        # advance since to last returned timestamp + 1 ms
        since = klines[-1][0] + 1
        time.sleep(exchange.rateLimit / 1000.0 if hasattr(exchange, 'rateLimit') else 0.1)
    df = pd.DataFrame(all_klines, columns=['timestamp','open','high','low','close','volume'])
    if df.empty:
        return df
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_convert(TZ_LOCAL)
    # reorder
    df = df[['datetime','timestamp','open','high','low','close','volume']]
    # numeric types
    for c in ['open','high','low','close','volume']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

# === Indicators calculation ===
def add_indicators(df):
    # EMA
    df[f'EMA_{EMA_FAST}'] = ta.ema(df['close'], length=EMA_FAST)
    df[f'EMA_{EMA_SLOW}'] = ta.ema(df['close'], length=EMA_SLOW)
    # RSI
    df[f'RSI_{RSI_LEN}'] = ta.rsi(df['close'], length=RSI_LEN)
    # MACD (returns macd, macd_signal, macd_hist)
    macd = ta.macd(df['close'], fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    # pandas_ta returns columns like MACD_12_26_9, MACDs_12_26_9, MACDh_12_26_9
    macd_col = f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
    macds_col = f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
    macdh_col = f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
    df[macd_col] = macd[macd_col]
    df[macds_col] = macd[macds_col]
    df[macdh_col] = macd[macdh_col]
    # Support / Resistance (simple rolling min/max)
    df['SR_support'] = df['low'].rolling(window=SR_WINDOW, min_periods=1).min()
    df['SR_resistance'] = df['high'].rolling(window=SR_WINDOW, min_periods=1).max()
    return df

# === Signal detection ===
def detect_signals(df):
    df = df.copy()
    signal_list = []
    position = None  # None or dict with entry info
    trades = []

    ema_fast_col = f'EMA_{EMA_FAST}'
    ema_slow_col = f'EMA_{EMA_SLOW}'
    rsi_col = f'RSI_{RSI_LEN}'
    macdh_col = f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"

    df['signal'] = ''       # 'entry' or 'exit' markers
    df['position'] = ''     # 'long' when in position

    # Iterate rows by index order
    for i in range(1, len(df)):
        prev = df.iloc[i-1]
        cur = df.iloc[i]

        # Skip if indicators NaN
        if pd.isna(prev[ema_fast_col]) or pd.isna(prev[ema_slow_col]) or pd.isna(cur[macdh_col]):
            continue

        # Entry condition:
        # - EMA fast crossed above EMA slow (prev <=, cur >)
        # - MACD histogram positive (cur)
        # - RSI below 70 at entry (cur)
        ema_cross_up = (prev[ema_fast_col] <= prev[ema_slow_col]) and (cur[ema_fast_col] > cur[ema_slow_col])
        macd_conf = cur[macdh_col] > 0
        rsi_ok = (not pd.isna(cur[rsi_col])) and (cur[rsi_col] < 70)

        if position is None and ema_cross_up and macd_conf and rsi_ok:
            # Enter long at next candle open (we'll use current 'close' as execution proxy)
            entry_price = cur['close']
            entry_time = cur['datetime']
            position = {'entry_price': entry_price, 'entry_time': entry_time, 'entry_index': i}
            df.at[df.index[i], 'signal'] = 'entry'
            df.at[df.index[i], 'position'] = 'long'
            signal_list.append(('entry', entry_time, entry_price))
            continue

        # If in position, evaluate exit:
        if position is not None:
            # Exit if EMA fast crosses below EMA slow OR RSI > 80
            ema_cross_down = (prev[ema_fast_col] >= prev[ema_slow_col]) and (cur[ema_fast_col] < cur[ema_slow_col])
            rsi_exit = (not pd.isna(cur[rsi_col])) and (cur[rsi_col] > 80)

            if ema_cross_down or rsi_exit:
                exit_price = cur['close']
                exit_time = cur['datetime']
                # record trade
                trade = {
                    'entry_time': position['entry_time'],
                    'entry_price': position['entry_price'],
                    'exit_time': exit_time,
                    'exit_price': exit_price,
                    'return_pct': (exit_price - position['entry_price']) / position['entry_price'] * 100,
                    'exit_reason': 'ema_cross_down' if ema_cross_down else 'rsi>80'
                }
                trades.append(trade)
                df.at[df.index[i], 'signal'] = 'exit'
                df.at[df.index[i], 'position'] = ''
                position = None
                signal_list.append(('exit', exit_time, exit_price))
                continue

        # maintain position label
        if position is not None:
            df.at[df.index[i], 'position'] = 'long'

    # If open position at the end, close it at last close (optional: consider as open)
    if position is not None:
        last = df.iloc[-1]
        trade = {
            'entry_time': position['entry_time'],
            'entry_price': position['entry_price'],
            'exit_time': last['datetime'],
            'exit_price': last['close'],
            'return_pct': (last['close'] - position['entry_price']) / position['entry_price'] * 100,
            'exit_reason': 'closed_at_end'
        }
        trades.append(trade)
        # mark last row as exit
        df.at[df.index[-1], 'signal'] = 'exit'
        df.at[df.index[-1], 'position'] = ''
        signal_list.append(('exit', last['datetime'], last['close']))

    return df, trades

# === Main execution ===
def main():
    print("Inicio - estrategia TradingLatino style")
    exchange = get_exchange(MARKET)
    start_ms = to_utc_ms(START_LOCAL) - 15 * 60 * 1000  # extend 15m back
    end_ms = to_utc_ms(END_LOCAL) + 15 * 60 * 1000     # extend 15m forward

    print(f"Exchange: {exchange.id} | Symbol: {SYMBOL} | TF: {TIMEFRAME}")
    print("Rango local:", START_LOCAL, "->", END_LOCAL, f"({TZ_LOCAL})")
    print("Rango UTC ms:", start_ms, "->", end_ms)

    df = fetch_ohlcv_range(exchange, SYMBOL, TIMEFRAME, start_ms, end_ms)
    if df.empty:
        print("No se obtuvieron velas. Revisa los parámetros o la conexión.")
        return

    df = add_indicators(df)
    df_signals, trades = detect_signals(df)

    # Guardar CSV
    stamp0 = pd.to_datetime(start_ms, unit='ms', utc=True).tz_convert(TZ_LOCAL).strftime('%Y%m%d_%H%M')
    stamp1 = pd.to_datetime(end_ms, unit='ms', utc=True).tz_convert(TZ_LOCAL).strftime('%H%M')
    file_name = f"{SYMBOL.replace('/','')}_{TIMEFRAME}_{stamp0}-{stamp1}.csv"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    df_signals.to_csv(file_path, index=False)
    print(f"CSV guardado: {file_path} | Velas: {df_signals.shape[0]}")

    # Resumen en consola
    print("\n=== RESUMEN DE OPERACIONES DETECTADAS ===")
    print(f"Total trades cerrados: {len(trades)}")
    wins = [t for t in trades if t['return_pct'] > 0]
    losses = [t for t in trades if t['return_pct'] <= 0]
    print(f"Wins: {len(wins)} | Losses: {len(losses)}")
    if trades:
        avg_ret = sum(t['return_pct'] for t in trades) / len(trades)
        print(f"Retorno medio por trade: {avg_ret:.2f}%")
        print("\nTrades detail:")
        for i, t in enumerate(trades, 1):
            print(f"{i:02d}) Entry: {t['entry_time']} @{t['entry_price']:.2f} | Exit: {t['exit_time']} @{t['exit_price']:.2f} | Return: {t['return_pct']:.3f}% | Reason: {t['exit_reason']}")

    # Quick head of CSV for debug
    print("\nCSV head:")
    print(df_signals.head(10).to_string(index=False))

if __name__ == '__main__':
    main()
