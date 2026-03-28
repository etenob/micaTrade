# estado_momentum.py - Evalúa la dirección del momentum a partir de 4 señales booleanas

# sc1 = tendencia alcista de corto
# sc2 = tendencia bajista de corto
# sc3 = confirmación alcista de largo
# sc4 = confirmación bajista de largo

def interpretar_momentum(sc1: bool, sc2: bool, sc3: bool, sc4: bool) -> str:
    """
    Devuelve una interpretación textual de la direccionalidad del mercado
    en base a 4 condiciones binarias.
    """
    if sc1 and sc3:
        return "Direccionalidad alcista"
    elif sc1 and sc4:
        return "Direccionalidad bajista"
    elif sc2 and sc4:
        return "Direccionalidad bajista"
    elif sc2 and sc3:
        return "Direccionalidad alcista"
    else:
        return "Direccionalidad indefinida"
