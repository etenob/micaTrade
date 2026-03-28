# modulo_scalping/scalping_bridge.py
import os, json, datetime, random, requests
from modulo_scalping.config_scalping import SCALPING_PARAMS

# 🔧 Copia dinámica de los parámetros de config
dynamic_params = SCALPING_PARAMS.copy()
LOG_FILE = "scalping_log.jsonl"

# 🔗 Endpoints externos
NEXT_ENDPOINT = os.getenv("NEXT_ENDPOINT")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ===============================
# 🔧 Utilidades internas
# ===============================
def update_params(new_params: dict):
    """Permite actualizar parámetros dinámicamente sin tocar config central."""
    global dynamic_params
    dynamic_params.update(new_params)


def send_to_next(package: dict):
    """Envia paquete JSON al servidor NEXT.js (si está configurado)."""
    if not NEXT_ENDPOINT:
        return {"ok": False, "error": "NEXT_ENDPOINT not set"}
    try:
        r = requests.post(NEXT_ENDPOINT, json=package, timeout=6)
        return {"ok": True, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def send_telegram_message(text: str):
    """Manda mensaje a Telegram usando BOT_TOKEN y CHAT_ID del .env"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {"ok": False, "error": "telegram env not set"}
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=6)
        return {"ok": True, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ===============================
# 🚀 Loop principal de scalping
# ===============================
def scalping_realtime(symbol: str, interval: str = "15m", modo: str = "sommi"):
    """Simula/ejecuta scalping en tiempo real usando la estrategia seleccionada (modo)."""
    now = int(datetime.datetime.now().timestamp())
    price = random.uniform(25000, 28000) if symbol == "BTCUSDT" else random.uniform(1800, 2000)

    # Candle simulado (en el futuro: real desde BinanceService)
    candle = {
        "time": now,
        "open": price,
        "high": price * 1.01,
        "low": price * 0.99,
        "close": price * 1.002
    }

    # 🟢 Mostrar qué estrategia corre + parámetros activos
    print(f"\n📊 Ejecutando estrategia: {modo.upper()} | Symbol: {symbol}, Interval: {interval}")
    print(f"⚙️ Params activos: {json.dumps(dynamic_params, indent=2)}")

    # Resultado de la estrategia (placeholder)
    result = {
        "symbol": symbol,
        "interval": interval,
        "modo": modo,
        "candles": [candle],
        "signal": random.choice(["LONG", "SHORT", None]),
        "timestamp": now
    }

    # Guardar en log
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(result) + "\n")
    except:
        pass

    # Enviar a Next.js
    send_to_next(result)

    # Debug + Telegram
    print("DEBUG: enviando señal a Telegram:", result["signal"])
    if result["signal"]:
        send_telegram_message(
            f"🔔 Señal {result['signal']} - {symbol} {interval}\n"
            f"Estrategia: {modo.upper()}"
        )

    return result

