# Telegram/Bot_Capital/core/portfolio.py

def get_portfolio_status():
    """
    Retorna un estado de cartera de prueba.
    """
    return {
        "portfolio": {
            "BTC": "40%",
            "ETH": "25%",
            "BNB": "10%",
            "USDT": "25%"
        },
        "balance": {
            "daily": "+3.2%",
            "monthly": "+15.0%"
        }
    }

