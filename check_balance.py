import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")

def check_account():
    try:
        client = Client(api_key, api_secret)
        account = client.get_account()
        
        balances = account.get('balances', [])
        print("\n💰 --- SALDOS ENCONTRADOS ---")
        found = False
        for b in balances:
            free = float(b['free'])
            locked = float(b['locked'])
            if free > 0 or locked > 0:
                print(f"🔹 {b['asset']}: Disponible: {free} | Bloqueado: {locked}")
                found = True
        
        if not found:
            print("❗ No se encontraron saldos mayores a cero.")
        print("----------------------------\n")
            
    except Exception as e:
        print(f"❌ Error al conectar con Binance: {e}")

if __name__ == "__main__":
    if not api_key or not api_secret:
        print("❌ Faltan llaves en el archivo .env")
    else:
        check_account()
