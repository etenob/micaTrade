# adx.py - Estado del ADX respecto al nivel crítico 23

import pandas as pd

def interpretar_adx(adx_series: pd.Series, nivel_critico: float = 23):
    """
    Interpreta el estado del ADX con respecto a su pendiente y al nivel crítico definido.
    Devuelve un string con el estado textual.
    """
    if len(adx_series) < 2:
        return "Datos insuficientes"

    actual = adx_series.iloc[-1]
    previo = adx_series.iloc[-2]

    if actual > previo and actual > nivel_critico:
        return "ADX con pendiente positiva por encima del punto 23"
    elif actual > previo and actual < nivel_critico:
        return "ADX con pendiente positiva por debajo del punto 23"
    elif actual < previo and actual < nivel_critico:
        return "ADX con pendiente negativa por debajo del punto 23"
    elif actual < previo and actual > nivel_critico:
        return "ADX con pendiente negativa por encima del punto 23"
    else:
        return "ADX sin cambio relevante"
