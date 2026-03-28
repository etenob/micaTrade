# ao_awesome.py

import pandas as pd

def calcular_ao(alto, bajo):
    """
    Calcula el Awesome Oscillator (AO)
    AO = SMA(5) del punto medio - SMA(34) del punto medio
    """
    media = (alto + bajo) / 2
    ao = media.rolling(window=5).mean() - media.rolling(window=34).mean()
    return ao


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # Datos aleatorios para demo
    n = 200
    alto = pd.Series(np.random.randn(n).cumsum() + 100)
    bajo = alto - np.random.rand(n)

    ao = calcular_ao(alto, bajo)

    colores = ["green" if v > 0 else "red" for v in ao]

    plt.figure(figsize=(10, 4))
    plt.bar(range(len(ao)), ao, color=colores)
    plt.title("Awesome Oscillator (AO)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
