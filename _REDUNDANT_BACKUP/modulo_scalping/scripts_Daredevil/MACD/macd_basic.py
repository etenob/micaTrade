# macd_basic.py - Cálculo de MACD con cruce y colores

import pandas as pd
import talib

def calcular_macd(cierre):
    """
    Calcula MACD, Signal y Histograma.
    También detecta cruce y color del histograma:
    - Verde oscuro: hist > hist[-1] y positivo
    - Verde claro: hist < hist[-1] y positivo
    - Rojo claro:  hist > hist[-1] y negativo
    - Bordó:       hist < hist[-1] y negativo
    """
    macd, signal, hist = talib.MACD(cierre, fastperiod=12, slowperiod=26, signalperiod=9)

    color = []
    cruce = []

    for i in range(len(hist)):
        if i == 0:
            color.append("sin datos")
            cruce.append("no")
            continue

        if hist[i] > 0:
            color.append("verde oscuro" if hist[i] > hist[i-1] else "verde claro")
        else:
            color.append("bordó" if hist[i] < hist[i-1] else "rojo claro")

        if macd[i-1] < signal[i-1] and macd[i] > signal[i]:
            cruce.append("cruce alcista")
        elif macd[i-1] > signal[i-1] and macd[i] < signal[i]:
            cruce.append("cruce bajista")
        else:
            cruce.append("no")

    return macd, signal, hist, color, cruce