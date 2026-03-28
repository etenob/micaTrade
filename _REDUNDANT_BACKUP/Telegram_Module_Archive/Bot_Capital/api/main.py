# Telegram/Bot_Capital/api/main.py
"""
API REST de Bot_Capital usando FastAPI.
Proporciona endpoints para:
- Consultar el estado de la cartera (/status)
- Consultar las señales recientes (/signals)
"""

from fastapi import FastAPI
from Telegram.Bot_Capital.core.portfolio import get_portfolio_status
from Telegram.Bot_Capital.core.signals import get_recent_signals

app = FastAPI(title="Bot_Capital API", version="0.1.0")

# -----------------------------
# Endpoint de cartera
# -----------------------------
@app.get("/status")
def status():
    """
    Devuelve el estado actual de la cartera.
    """
    return get_portfolio_status()

# -----------------------------
# Endpoint de señales
# -----------------------------
@app.get("/signals")
def signals():
    """
    Devuelve las señales recientes de todos los bots.
    """
    return get_recent_signals()

