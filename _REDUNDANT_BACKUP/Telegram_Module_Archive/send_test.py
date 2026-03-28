import requests
from config import Config

def send_message(text):
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        raise ValueError("⚠️ Faltan credenciales en .env")
    
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.get(url, params={"chat_id": Config.TELEGRAM_CHAT_ID, "text": text}, timeout=5)
        r.raise_for_status()
        print("OK:", r.json())
    except requests.exceptions.RequestException as e:
        print(f"❌ Error enviando mensaje: {e}")

if __name__ == "__main__":
    send_message("Prueba desde Python ✅")

