#!/usr/bin/env python3
# File: Telegram/poll_bot.py
# Descripción: Bot que escucha comandos de Telegram y envía alertas automáticas de señales usando AlertManager.
#              Ahora incluye comando /status para mostrar estado de la cartera.

import time
import requests
from telegram_helper import send_telegram_message  # Función segura para enviar mensajes a Telegram
from alert_manager import AlertManager             # Evita duplicados y controla cooldown
from config import Config                          # Configuración centralizada (.env)

# -----------------------------
# Configuración del bot
# -----------------------------
API_URL = "http://127.0.0.1:8000"  # Endpoint de Bot_Capital
CHAT_ID = Config.TELEGRAM_CHAT_ID  # Tomamos chat_id desde la configuración
alert_manager = AlertManager(cooldown_seconds=1200)  # 20 min de cooldown para alertas repetidas

# -----------------------------
# Funciones auxiliares
# -----------------------------

def send(chat_id, text):
    """
    Envía un mensaje a Telegram usando telegram_helper.
    """
    try:
        send_telegram_message(text)
    except Exception as e:
        print("Error al enviar mensaje a Telegram:", e)


def get_signals():
    """
    Consulta el endpoint /signals de Bot_Capital y devuelve la lista de señales.
    Retorna lista vacía en caso de error.
    """
    try:
        resp = requests.get(f"{API_URL}/signals")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print("Error al consultar signals:", e)
        return []


def send_signal_alerts():
    """
    Recorre todas las señales obtenidas y envía alertas automáticas a Telegram
    solo si AlertManager permite (evitando duplicados dentro del cooldown).
    """
    signals = get_signals()
    for s in signals:
        if alert_manager.can_send(s["symbol"], s["timeframe"], s["signal"]):
            text = f"⚡ {s['bot']} | {s['symbol']} {s['timeframe']} | {s['signal']} @ {s['price']}"
            send(CHAT_ID, text)
            # Registro interno en AlertManager para no enviar duplicados
            alert_manager.send_alert(s["symbol"], s["timeframe"], s["signal"], lambda a,b,c: None)
            print("Alerta enviada:", text)


# -----------------------------
# Función principal
# -----------------------------
def main():
    offset = None  # Último update procesado + 1
    print("Poll bot escuchando… Ctrl+C para salir.")

    while True:
        try:
            # Consultamos actualizaciones de Telegram
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getUpdates"
            resp = requests.get(url, params={"timeout": 25, "offset": offset})
            resp.raise_for_status()
            updates = resp.json().get("result", [])

            for upd in updates:
                offset = upd["update_id"] + 1  # Marcamos update como leído
                msg = upd.get("message") or upd.get("edited_message")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg.get("text", "").strip().lower()

                # -----------------------------
                # Comandos de usuario
                # -----------------------------
                if text == "/start":
                    send(chat_id, "¡Hola! Soy DaredevilAlertsBot. Comandos disponibles:\n/status\n/signals")
                elif text == "/signals":
                    signals = get_signals()
                    msg_text = "⚡ Últimas señales:\n"
                    for s in signals:
                        msg_text += f"- {s['bot']} | {s['symbol']} {s['timeframe']} | {s['signal']} @ {s['price']}\n"
                    send(chat_id, msg_text)
                elif text == "/status":
                    # Consultamos el estado de la cartera
                    try:
                        resp = requests.get(f"{API_URL}/portfolio")
                        resp.raise_for_status()
                        portfolio = resp.json()
                        msg_text = "📊 Estado de la cartera:\n"
                        for asset, data in portfolio.items():
                            msg_text += f"- {asset}: {data['amount']} ({data['percentage']}%)\n"
                        send(chat_id, msg_text)
                    except Exception as e:
                        send(chat_id, f"Error al obtener estado de la cartera: {e}")

            # -----------------------------
            # Envío automático de alertas de señales
            # -----------------------------
            send_signal_alerts()

            time.sleep(10)  # Revisar cada 10 segundos

        except KeyboardInterrupt:
            print("\nSaliendo…")
            break
        except Exception as e:
            print("Error en loop principal:", e)
            time.sleep(2)


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    main()

