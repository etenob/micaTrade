import ccxt
import pandas as pd
import os

# === CONFIGURACIÓN POR DEFECTO ===
SYMBOL = 'BTC/USDT'
TIMEFRAME = '15m'
START_LOCAL = '2025-08-07 14:30:00'
END_LOCAL = '2025-08-07 17:00:00'
TZ_LOCAL = 'America/Argentina/Buenos_Aires'

# Carpeta de salida
OUTPUT_DIR = './Scripts_Daredevil/Bitacora'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === CONEXIÓN A BINANCE ===
exchange = ccxt.binance()

# === CONVERSIÓN DE FECHAS ===
start_ts = pd.Timestamp(START_LOCAL, tz=TZ_LOCAL) - pd.Timedelta(minutes=15)
end_ts = pd.Timestamp(END_LOCAL, tz=TZ_LOCAL) + pd.Timedelta(minutes=15)
start_ms = int(start_ts.tz_convert('UTC').timestamp() * 1000)
end_ms = int(end_ts.tz_convert('UTC').timestamp() * 1000)

# === DESCARGA DE VELAS ===
all_klines = []
since = start_ms

while since < end_ms:
    klines = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, since=since, limit=1000)
    if not klines:
        break
    for k in klines:
        t = int(k[0])
        if t >= end_ms:
            break
        all_klines.append(k)
    since = klines[-1][0] + 1

# === CREAR DATAFRAME ===
df = pd.DataFrame(all_klines, columns=['timestamp','open','high','low','close','volume'])
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_convert(TZ_LOCAL)

# === GUARDAR CSV ===
file_name = f"{SYMBOL.replace('/','')}_{TIMEFRAME}_{start_ts.strftime('%Y%m%d_%H%M')}-{end_ts.strftime('%H%M')}.csv"
file_path = os.path.join(OUTPUT_DIR, file_name)
df.to_csv(file_path, index=False)

# === SALIDA EN CONSOLA ===
print(f"Archivo guardado: {file_path} | Velas capturadas: {df.shape[0]}")
print(df)
