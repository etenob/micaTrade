# show_status.py - Panel visual interpretativo ADX + Momentum

from adx import interpretar_adx
from estado_momentum import interpretar_momentum


def estado_general(adx_value, adx_prev, sc1, sc2, sc3, sc4, nivel_critico=23):
    """
    Combina la interpretación del ADX, del momentum y genera una evaluación general.
    """
    # Evaluación ADX
    adx_estado = interpretar_adx([adx_prev, adx_value], nivel_critico)

    # Evaluación Momentum
    momentum_estado = interpretar_momentum(sc1, sc2, sc3, sc4)

    # Evaluación cruzada
    a1 = adx_value >= nivel_critico
    a2 = adx_value < nivel_critico
    a3 = adx_value >= adx_prev
    a4 = adx_value < adx_prev

    # Posibilidades simplificadas (pueden expandirse más adelante)
    if a1 and a3 and sc1 and sc3:
        resumen = "Fuerte movimiento alcista"
    elif a1 and a3 and sc2 and sc4:
        resumen = "Fuerte movimiento bajista"
    elif a2 and a3 and sc1 and sc3:
        resumen = "Movimiento alcista queriendo ganar fuerza"
    elif a2 and a3 and sc2 and sc4:
        resumen = "Movimiento bajista queriendo ganar fuerza"
    elif a1 and a4:
        resumen = "Pendiente negativa con fuerza"
    elif a2 and a4:
        resumen = "Movimiento débil o sin fuerza"
    else:
        resumen = "Estado indefinido"

    # Panel final
    panel = f"Info ADX: {adx_estado}\nInfo Momentum: {momentum_estado}\nEstado general: {resumen}"
    return panel
