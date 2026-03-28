# koncorde.py - Módulo Koncorde Diamond ✅❌

import pandas as pd

# --- Configuración
SHOW_KD = True

# --- Señal de Koncorde Diamond

def detectar_koncorde_diamond(marron: pd.Series, media: pd.Series, show_kd: bool = SHOW_KD):
    """
    Devuelve una señal textual si se produce un cruce de Koncorde Diamond:
    - ✅ punto verde (bullish)
    - ❌ punto rojo (bearish)
    """
    if not show_kd or len(marron) < 2 or len(media) < 2:
        return None

    cruce_alcista = marron.iloc[-2] < media.iloc[-2] and marron.iloc[-1] > media.iloc[-1]
    cruce_bajista = marron.iloc[-2] > media.iloc[-2] and marron.iloc[-1] < media.iloc[-1]

    if cruce_alcista:
        return "✅ Punto verde - Señal Koncorde Bull"
    elif cruce_bajista:
        return "❌ Punto rojo - Señal Koncorde Bear"
    else:
        return None
