# squeeze_momentum.py

import numpy as np
import pandas as pd
import talib

def calcular_squeeze_momentum(cierre, alto, bajo):
    """
    Calcula el indicador Squeeze Momentum (versión simplificada).
    Devuelve:
    - squeeze_mom: array de valores del oscilador
    - squeeze_on: boolean array (True si está en squeeze)
    """
    # Bollinger Bands
    upper_bb, middle_bb, lower_bb = talib.BBANDS(cierre, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

    # Keltner Channel
    tr = np.maximum(np.maximum(alto - bajo, np.abs(alto - cierre.shift(1))), np.abs(bajo - cierre.shift(1)))
    atr = talib.SMA(tr, timeperiod=20)
    ema = talib.EMA(cierre, timeperiod=20)
    upper_kc = ema + (1.5 * atr)
    lower_kc = ema - (1.5 * atr)

    # Squeeze ON si las bandas de Bollinger están dentro del canal de Keltner
    squeeze_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)

    # Momentum = cierre - promedio de high y low (como proxy visual)
    momentum = cierre - ((alto + bajo) / 2)

    return momentum, squeeze_on


if __name__ == "__main__":
    # Demo con datos aleatorios
    import matplotlib.pyplot as plt

    np.random.seed(0)
    n = 100
    cierre = pd.Series(np.random.randn(n).cumsum() + 100)
    alto = cierre + np.random.rand(n)
    bajo = cierre - np.random.rand(n)

    mom, squeeze = calcular_squeeze_momentum(cierre, alto, bajo)

    plt.figure(figsize=(10,5))
    plt.plot(mom, label="Momentum", color="green")
    plt.fill_between(range(len(mom)), mom, where=squeeze, color="purple", alpha=0.3, label="Squeeze ON")
    plt.title("Squeeze Momentum + Área")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
