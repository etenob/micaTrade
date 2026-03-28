# koncorde_colores.py

import pandas as pd

def calcular_koncorde_colores(cierre, alto, bajo, volumen, longitud=90, media_periodo=15):
    """
    Calcula las curvas base del indicador Koncorde (verde, marrón, azul).
    No incluye los puntos (diamond), solo las curvas visuales.
    """

    # PVI y NVI (Positive y Negative Volume Index)
    pvi = volumen.copy()
    pvi[1:] = [pvi[i-1] + volumen[i] if cierre[i] > cierre[i-1] else pvi[i-1]
               for i in range(1, len(cierre))]
    nvi = volumen.copy()
    nvi[1:] = [nvi[i-1] + volumen[i] if cierre[i] < cierre[i-1] else nvi[i-1]
               for i in range(1, len(cierre))]

    # Promedios y normalizaciones
    pvim = pvi.ewm(span=media_periodo).mean()
    nvim = nvi.ewm(span=media_periodo).mean()

    pvimax = pvim.rolling(window=longitud).max()
    pvimin = pvim.rolling(window=longitud).min()
    nvimax = nvim.rolling(window=longitud).max()
    nvimin = nvim.rolling(window=longitud).min()

    oscp = 100 * (pvi - pvim) / (pvimax - pvimin)
    azul = 100 * (nvi - nvim) / (nvimax - nvimin)

    # RSI, MFI, BollOscillator (simplificados)
    rsi = cierre.rolling(window=14).apply(lambda x: 100 - 100 / (1 + ((x.diff().clip(lower=0).sum()) / (-x.diff().clip(upper=0).sum()))), raw=False)
    mfi = ((cierre - bajo) / (alto - bajo + 1e-6)) * 100
    bollosc = ((cierre - cierre.rolling(20).mean()) / (2 * cierre.rolling(20).std(ddof=0))) * 100

    stoch = ((cierre - bajo.rolling(21).min()) / (alto.rolling(21).max() - bajo.rolling(21).min() + 1e-6)) * 100

    marron = (rsi + mfi + bollosc + (stoch / 3)) / 2
    verde = marron + oscp

    return verde, marron, azul


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    n = 150
    cierre = pd.Series(np.random.randn(n).cumsum() + 100)
    alto = cierre + np.random.rand(n)
    bajo = cierre - np.random.rand(n)
    volumen = pd.Series(np.random.rand(n) * 1000)

    verde, marron, azul = calcular_koncorde_colores(cierre, alto, bajo, volumen)

    plt.figure(figsize=(10, 5))
    plt.plot(verde, label='Verde (compradores)', color='green')
    plt.plot(marron, label='Marrón (masa)', color='saddlebrown')
    plt.plot(azul, label='Azul (manos fuertes)', color='blue')
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.title("Koncorde Colores")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
