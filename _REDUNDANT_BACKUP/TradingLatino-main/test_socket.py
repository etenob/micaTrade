import socketio

# Cliente socket
sio = socketio.Client()

# Evento al conectar
@sio.event
def connect():
    print("✅ Conectado al servidor")
    # Te suscribís como lo haría Next.js
    sio.emit("subscribe_realtime", {"channel": "bot_status"})

# Evento al desconectar
@sio.event
def disconnect():
    print("❌ Desconectado del servidor")

# Escucha los eventos "realtime_update"
@sio.on("realtime_update")
def handle_realtime_update(data):
    print("📡 Realtime update recibido:", data)

if __name__ == "__main__":
    try:
        sio.connect("http://localhost:5000")  # mismo puerto que app.py
        sio.wait()
    except Exception as e:
        print("⚠️ Error al conectar:", e)

