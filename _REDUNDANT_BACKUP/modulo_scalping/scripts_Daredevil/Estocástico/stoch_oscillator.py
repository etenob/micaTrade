# stoch_oscillator.py

import pandas as pd

def calcular_estocastico(cierre, alto, bajo, k_periodo=14, d_suavizado=3):
    """
    Calcula el Estocástico %K y %D (líneas rápidas y lentas).
    """
    lowest_low = bajo.rolling(window=k_periodo).min()
    highest_high = alto.rolling(window=k_periodo).max()

    k = 100 * (cierre - lowest_low) / (highest_high - lowest_low)
    d = k.rolling(window=d_suavizado).mean()

    return k, d


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # Datos demo
    n = 200
    cierre = pd.Series(np.random.randn(n).cumsum() + 100)
    alto = cierre + np.random.rand(n)
    bajo = cierre - np.random.rand(n)

    k, d = calcular_estocastico(cierre, alto, bajo)

    plt.figure(figsize=(10, 5))
    plt.plot(k, label="%K", color="blue")
    plt.plot(d, label="%D", color="orange")
    plt.axhline(80, color="gray", linestyle="--", alpha=0.5)
    plt.axhline(20, color="gray", linestyle="--", alpha=0.5)
    plt.title("Estocástico")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
