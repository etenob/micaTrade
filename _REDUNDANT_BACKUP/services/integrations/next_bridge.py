# next_bridge.py
# ==========================================================
# Bridge entre Flask/Socket.IO y el módulo de scalping
# ----------------------------------------------------------
# 🔹 Rol:
#   - Expone endpoints REST y WebSocket (Socket.IO).
#   - Orquesta las llamadas a scalping_bridge.
#   - Mantiene coherencia de streams activos.
# ==========================================================

from flask import Blueprint, jsonify, request
import time
import modulo_scalping.scalping_bridge as scalping_bridge

next_bridge_bp = Blueprint("next_bridge", __name__)

# Símbolos soportados por ahora
SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT"]

# Streams activos para evitar duplicados
active_streams = {}

# Diccionario local de intervalos (segundos por timeframe)
UPDATE_INTERVALS = {
    "1m": 60,
    "3m": 180,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
}


# ==========================================================
# 🔹 REST ENDPOINTS
# ==========================================================
@next_bridge_bp.route("/api/realtime/<symbol>", methods=["GET"])
def api_realtime(symbol):
    """Consulta puntual en tiempo real"""
    symbol = symbol.upper()
    if symbol not in SUPPORTED_SYMBOLS:
        return jsonify({"success": False, "error": f"Solo soportado: {SUPPORTED_SYMBOLS}"}), 400

    result = scalping_bridge.scalping_realtime(symbol)
    return jsonify({"success": True, "data": result})


@next_bridge_bp.route("/api/params", methods=["GET"])
def get_params():
    """Obtiene los parámetros dinámicos"""
    return jsonify({"success": True, "params": scalping_bridge.dynamic_params})


@next_bridge_bp.route("/api/params", methods=["POST"])
def update_params():
    """Actualiza parámetros dinámicos del scalping"""
    data = request.json or {}
    if hasattr(scalping_bridge, "update_params"):
        scalping_bridge.update_params(data)
        return jsonify({"success": True, "new_params": scalping_bridge.dynamic_params})
    else:
        return jsonify({"success": False, "error": "scalping_bridge no soporta parámetros dinámicos"}), 400


# ==========================================================
# 🔹 SOCKET.IO STREAMS
# ==========================================================
def register_socketio(socketio):
    """
    Registra listeners de Socket.IO dentro de la app.
    """

    @socketio.on("subscribe_realtime")
    def handle_subscribe(data):
        symbol = str(data.get("symbol", "BTCUSDT")).upper()
        interval = str(data.get("interval", "1m"))

        if symbol not in SUPPORTED_SYMBOLS:
            socketio.emit("error", {"error": f"Solo soportado: {SUPPORTED_SYMBOLS}"})
            return

        socketio.emit("subscribed", {"symbol": symbol, "interval": interval})
        print(f"📡 Cliente suscripto a realtime {symbol} ({interval})")

        # 🔧 Evitar duplicar streams
        key = f"{symbol}_{interval}"
        if key in active_streams:
            print(f"⚠️ Stream ya activo para {symbol} ({interval})")
            return

        # 🔹 Loop en background que emite actualizaciones usando scalping_bridge
        def stream_realtime():
            while True:
                try:
                    payload = scalping_bridge.scalping_realtime(symbol, interval=interval)
                    if payload:
                        socketio.emit("realtime_update", payload)
                    else:
                        print(f"⚠️ No se pudo obtener data para {symbol}")

                    sleep_s = UPDATE_INTERVALS.get(interval, 60)
                    time.sleep(sleep_s)

                except Exception as e:
                    print(f"❌ Error en stream realtime: {e}")
                    time.sleep(10)

        # Guardar referencia al stream activo
        active_streams[key] = socketio.start_background_task(stream_realtime)

