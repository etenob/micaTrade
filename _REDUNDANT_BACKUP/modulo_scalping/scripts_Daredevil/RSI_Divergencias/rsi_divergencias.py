# rsi_divergencias.py

import numpy as np
import pandas as pd
import talib

def detectar_divergencias_rsi(cierre, minimo, maximo):
    rsi = talib.RSI(cierre, timeperiod=14)

    divergencias = [''] * len(cierre)

    for i in range(2, len(cierre) - 1):
        # Divergencia alcista
        if cierre[i] < cierre[i-1] and rsi[i] > rsi[i-1] and cierre[i] < cierre[i-2] and rsi[i] > rsi[i-2]:
            divergencias[i] = '🔼 Bull Divergence'

        # Divergencia bajista
        elif cierre[i] > cierre[i-1] and rsi[i] < rsi[i-1] and cierre[i] > cierre[i-2] and rsi[i] < rsi[i-2]:
            divergencias[i] = '🔽 Bear Divergence'

    return rsi, divergencias


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    np.random.seed(42)
    n = 100
    cierre = pd.Series(np.random.randn(n).cumsum() + 100)
    maximo = cierre + np.random.rand(n)
    minimo = cierre - np.random.rand(n)

    rsi, divergencias = detectar_divergencias_rsi(cierre, minimo, maximo)

    # Mostrar RSI y marcar divergencias
    plt.figure(figsize=(10,5))
    plt.plot(rsi, label="RSI", color="purple")
    for i, texto in enumerate(divergencias):
        if texto:
            plt.text(i, rsi[i], texto, fontsize=8, color='green' if 'Bull' in texto else 'red')

    plt.title("RSI + Divergencias")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()