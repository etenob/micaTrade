# modulo_scalping/helkin_confirm.py
import pandas as pd
import talib as ta

class HeikinConfirm:
    def __init__(self, ema_length=55):
        self.ema_length = ema_length

    def heikin_ohlc(self, df: pd.DataFrame):
        """Devuelve OHLC Heikin-Ashi"""
        ha_df = df.copy()
        ha_df['HA_Close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        ha_open = [(df['open'].iloc[0] + df['close'].iloc[0]) / 2]
        for i in range(1, len(df)):
            ha_open.append((ha_open[-1] + ha_df['HA_Close'].iloc[i-1]) / 2)
        ha_df['HA_Open'] = ha_open
        ha_df['HA_High'] = df[['high', 'close']].max(axis=1)
        ha_df['HA_Low']  = df[['low', 'close']].min(axis=1)
        return ha_df

    def confirm_signal(self, df: pd.DataFrame):
        """
        Devuelve CONFIRM_LONG / CONFIRM_SHORT / None
        """
        ha = self.heikin_ohlc(df)

        EMA1 = ta.EMA(ha['HA_Close'], timeperiod=self.ema_length)
        EMA2 = ta.EMA(EMA1, timeperiod=self.ema_length)
        EMA3 = ta.EMA(EMA2, timeperiod=self.ema_length)
        TMA1 = 3*EMA1 - 3*EMA2 + EMA3

        EMA4 = ta.EMA(TMA1, timeperiod=self.ema_length)
        EMA5 = ta.EMA(EMA4, timeperiod=self.ema_length)
        EMA6 = ta.EMA(EMA5, timeperiod=self.ema_length)
        TMA2 = 3*EMA4 - 3*EMA5 + EMA6

        IPEK  = TMA1 - TMA2
        YASIN = TMA1 + IPEK

        EMA7  = ta.EMA(df[['high','low','close']].mean(axis=1), timeperiod=self.ema_length)
        EMA8  = ta.EMA(EMA7, timeperiod=self.ema_length)
        EMA9  = ta.EMA(EMA8, timeperiod=self.ema_length)
        TMA3  = 3*EMA7 - 3*EMA8 + EMA9

        EMA10 = ta.EMA(TMA3, timeperiod=self.ema_length)
        EMA11 = ta.EMA(EMA10, timeperiod=self.ema_length)
        EMA12 = ta.EMA(EMA11, timeperiod=self.ema_length)
        TMA4  = 3*EMA10 - 3*EMA11 + EMA12

        IPEK1  = TMA3 - TMA4
        YASIN1 = TMA3 + IPEK1

        mavi    = YASIN1
        kirmizi = YASIN

        longCond  = mavi.iloc[-1] > kirmizi.iloc[-1] and mavi.iloc[-2] <= kirmizi.iloc[-2]
        shortCond = mavi.iloc[-1] < kirmizi.iloc[-1] and mavi.iloc[-2] >= kirmizi.iloc[-2]

        if longCond:
            return "CONFIRM_LONG"
        elif shortCond:
            return "CONFIRM_SHORT"
        else:
            return None

