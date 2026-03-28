# ==========================================================
# 📌 nadaraya_ob_htf.py
# Estrategia Nadaraya con Order Blocks y HTF
# ==========================================================

import pandas as pd
import talib.abstract as ta


class NadarayaOBHTF:
    def __init__(self, h=8, r=0.1, kernel_bars=10, lag=2,
                 atrLength=14, coef=1.5,
                 rsiLength=14, adx_len=14, adx_level=23,
                 htf1_enable=True, htf1_tf='1h',
                 htf2_enable=False, htf2_tf='4h'):
        # Parámetros Nadaraya
        self.h = h
        self.r = r
        self.kernel_bars = kernel_bars
        self.lag = lag

        # ATR y bandas
        self.atrLength = atrLength
        self.coef = coef

        # RSI y ADX
        self.rsiLength = rsiLength
        self.adx_len = adx_len
        self.adx_level = adx_level

        # HTF OB
        self.htf1_enable = htf1_enable
        self.htf1_tf = htf1_tf
        self.htf2_enable = htf2_enable
        self.htf2_tf = htf2_tf

    # =========================
    #   GENERADOR DE SEÑAL
    # =========================
    def generate_signal(self, df: pd.DataFrame):
        """
        df debe contener columnas: ['open','high','low','close']
        Retorna un dict con:
          - "signal": "LONG", "SHORT" o None
          - "debug": métricas internas
        """
        df = df.copy()
        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").ffill().bfill()

        close, high, low = df["close"], df["high"], df["low"]

        # Nadaraya
        yhat1 = self._kernel_regression(close, self.h, self.r, self.kernel_bars)
        yhat2 = self._kernel_regression(close, self.h - self.lag, self.r, self.kernel_bars)

        # ATR y bandas
        atr = ta.ATR(high, low, close, timeperiod=self.atrLength)
        upper, lower = yhat1 + self.coef * atr, yhat1 - self.coef * atr

        # RSI
        rsi = ta.RSI(close, timeperiod=self.rsiLength)

        # ADX
        adx = ta.ADX(high, low, close, timeperiod=self.adx_len)

        # Condiciones
        buyNadaraya = close.iloc[-1] > lower.iloc[-1] and close.iloc[-2] <= lower.iloc[-2]
        sellNadaraya = close.iloc[-1] < upper.iloc[-1] and close.iloc[-2] >= upper.iloc[-2]
        buyRSI = rsi.iloc[-1] < 35
        sellRSI = rsi.iloc[-1] > 65

        goLong_raw = buyNadaraya and buyRSI and adx.iloc[-1] > self.adx_level
        goShort_raw = sellNadaraya and sellRSI and adx.iloc[-1] > self.adx_level

        # OB locales
        ob_bull, ob_bear = self.detect_orderblocks(df)

        # OB HTF
        htf1_bull, htf1_bear = ([], [])
        htf2_bull, htf2_bear = ([], [])
        if self.htf1_enable:
            htf1_bull, htf1_bear = self.detect_htf_ob(df, self.htf1_tf)
        if self.htf2_enable:
            htf2_bull, htf2_bear = self.detect_htf_ob(df, self.htf2_tf)

        # Señal final con validación OB
        signal = None
        if goLong_raw and (ob_bull or htf1_bull or htf2_bull):
            signal = "LONG"
        elif goShort_raw and (ob_bear or htf1_bear or htf2_bear):
            signal = "SHORT"

        # Retorno unificado
        return {
            "signal": signal,
            "debug": {
                "close": float(close.iloc[-1]),
                "lower_band": float(lower.iloc[-1]),
                "upper_band": float(upper.iloc[-1]),
                "rsi": float(rsi.iloc[-1]),
                "adx": float(adx.iloc[-1]),
                "goLong_raw": bool(goLong_raw),
                "goShort_raw": bool(goShort_raw),
                "has_ob_bull": bool(len(ob_bull) > 0 or len(htf1_bull) > 0 or len(htf2_bull) > 0),
                "has_ob_bear": bool(len(ob_bear) > 0 or len(htf1_bear) > 0 or len(htf2_bear) > 0)
            }
        }

    # =========================
    # Métodos auxiliares
    # =========================
    def _kernel_regression(self, series, h, r, bars):
        # Placeholder de kernel regression
        return series.rolling(barrs).mean()
