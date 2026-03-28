# modulo_scalping/nadaraya_strategy.py
import pandas as pd
import numpy as np
import talib as ta

class NadarayaStrategy:
    def __init__(self, h=10.0, r=10.0, lag=2, atr_length=30, atr_mult=2, rsi_length=12):
        self.h = h
        self.r = r
        self.lag = lag
        self.atr_length = atr_length
        self.atr_mult = atr_mult
        self.rsi_length = rsi_length

    def _kernel_regression(self, series: pd.Series, h, r):
        """
        Aproximación de Nadaraya-Watson Rational Quadratic Kernel
        """
        series = pd.to_numeric(series, errors="coerce").ffill().bfill()
        size = len(series)
        yhat = []
        for t in range(size):
            current_weight = 0.0
            cumulative_weight = 0.0
            for i in range(min(size - t, 50)):  # limitar ventana
                y = float(series.iloc[t + i])
                w = (1 + (i**2) / ((h**2) * 2 * r)) ** -r
                current_weight += y * w
                cumulative_weight += w
            yhat.append(current_weight / cumulative_weight if cumulative_weight != 0 else float(series.iloc[t]))
        return pd.Series(yhat, index=series.index)

    def generate_signal(self, df: pd.DataFrame):
        """
        df debe contener columnas: ['open','high','low','close']
        Retorna "LONG", "SHORT" o None
        """
        print(f"\n🔎 [DEBUG] Generando señal Nadaraya | velas: {len(df)}")

        # Convertir todas las columnas a float
        for col in ['open','high','low','close']:
            df[col] = pd.to_numeric(df[col], errors="coerce").ffill().bfill()

        close = df['close']
        high = df['high']
        low = df['low']

        try:
            # 1️⃣ Nadaraya smoothing
            yhat1 = self._kernel_regression(close, self.h, self.r)
            yhat2 = self._kernel_regression(close, self.h - self.lag, self.r)

            # 2️⃣ ATR stops
            atr = ta.ATR(high, low, close, timeperiod=self.atr_length)
            upper_band = yhat1 + self.atr_mult * atr
            lower_band = yhat1 - self.atr_mult * atr

            # 3️⃣ RSI
            rsi = ta.RSI(close, timeperiod=self.rsi_length)

            # 4️⃣ Condiciones de entrada
            buyNadaraya = (close.iloc[-1] > lower_band.iloc[-1]) and (close.iloc[-2] <= lower_band.iloc[-2])
            buyRSI = rsi.iloc[-1] < 70 or rsi.iloc[-2] < 30
            sellNadaraya = (close.iloc[-1] < upper_band.iloc[-1]) and (close.iloc[-2] >= upper_band.iloc[-2])
            sellRSI = rsi.iloc[-1] > 50 or rsi.iloc[-2] > 50

            # 🔍 Debug detallado
            print(f"📊 Último close: {close.iloc[-1]:.4f}")
            print(f"🔮 Nadaraya yhat1[-1]={yhat1.iloc[-1]:.4f}, yhat2[-1]={yhat2.iloc[-1]:.4f}")
            print(f"📈 ATR[-1]={atr.iloc[-1]:.4f}")
            print(f"📐 Bandas -> upper={upper_band.iloc[-1]:.4f}, lower={lower_band.iloc[-1]:.4f}")
            print(f"🌀 RSI[-2:]= {rsi.tail(2).to_list()}")
            print(f"✅ Flags: buyNadaraya={buyNadaraya}, buyRSI={buyRSI}, sellNadaraya={sellNadaraya}, sellRSI={sellRSI}")

            # 5️⃣ Señal final
            if buyNadaraya and buyRSI:
                print("🎯 Señal FINAL: LONG")
                return "LONG"
            elif sellNadaraya and sellRSI:
                print("🎯 Señal FINAL: SHORT")
                return "SHORT"
            else:
                print("❌ No hay señal válida")
                return None

        except Exception as e:
            print(f"[DEBUG] Error generando señal Nadaraya: {e}")
            return None


# Función simple de interfaz
def nadaraya_signal(df: pd.DataFrame):
    strategy = NadarayaStrategy()
    return strategy.generate_signal(df)
