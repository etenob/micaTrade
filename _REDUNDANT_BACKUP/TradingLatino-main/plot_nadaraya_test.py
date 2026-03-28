# plot_nadaraya_test.py
import matplotlib.pyplot as plt
import pandas as pd
import talib as ta
from modulo_scalping.nadaraya_strategy import NadarayaStrategy

# ⚠️ Ejemplo de dataset
# Si ya tenés un df de velas en tu flujo, reemplazalo acá.
# Supongamos que cargamos velas desde un CSV temporal:
df = pd.read_csv("sample_data.csv")  # columnas: time, open, high, low, close, volume

# Usar la estrategia
strategy = NadarayaStrategy(h=16.0, r=8.0, lag=2, atr_length=14, atr_mult=0.5, rsi_length=5)

close = df["close"]
high = df["high"]
low = df["low"]

# Generar curvas
yhat1 = strategy._kernel_regression(close, strategy.h, strategy.r)
atr = ta.ATR(high, low, close, timeperiod=strategy.atr_length)
upper_band = yhat1 + strategy.atr_mult * atr
lower_band = yhat1 - strategy.atr_mult * atr

# --- PLOT ---
plt.figure(figsize=(12,6))
plt.plot(close.index, close, label="Close", color="black", linewidth=1)
plt.plot(yhat1.index, yhat1, label="Nadaraya yhat1", color="blue", linewidth=2)
plt.plot(upper_band.index, upper_band, "--", label="Upper Band", color="red")
plt.plot(lower_band.index, lower_band, "--", label="Lower Band", color="red")

plt.title("Nadaraya Strategy - Test")
plt.legend()
plt.grid(True)
plt.show()

