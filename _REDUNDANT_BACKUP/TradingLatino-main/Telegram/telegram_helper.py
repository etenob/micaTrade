# telegram_heper.py
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

"Test prueba en consola"
#def send_telegram_message(text):
    #print(f"[TELEGRAM DEBUG] {text}")

def send_telegram_message(text):
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        raise ValueError("⚠️ Configuración de Telegram faltante en .env")
    
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.get(url, params={"chat_id": Config.TELEGRAM_CHAT_ID, "text": text})
    resp.raise_for_status()
    return resp.json()

