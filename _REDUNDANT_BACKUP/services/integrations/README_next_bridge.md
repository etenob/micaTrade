# services/integrations/next_bridge.py

📡 Next Bridge – Jaime Merino Bot  

Este módulo conecta **Flask ↔ Next.js** para exponer en tiempo real las señales del scalping (Nadaraya, etc.).  
Se apoya en `scalping_bridge.py` para el cálculo de velas e indicadores y las entrega vía **REST API** y **Socket.IO** al frontend (`RealtimeChart.tsx`).  

---

## 🚀 Endpoints disponibles

### 1) REST API – Realtime
**URL:**  
GET /api/realtime/<symbol>?interval=<timeframe>

markdown
Copiar código

**Parámetros:**  
- `symbol`: `BTCUSDT` o `ETHUSDT`  
- `interval`: opcional (por defecto usa `MerinoConfig.SCALPING['timeframe']`, ej. `"5m"`)  

**Ejemplo:**  
```bash
curl "http://localhost:5000/api/realtime/BTCUSDT?interval=5m"
Respuesta:

json
Copiar código
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "interval": "5m",
    "candles": [
      {"time": 1736012300, "open": 38000, "high": 38200, "low": 37900, "close": 38100, "volume": 120.3},
      ...
    ],
    "nadaraya_raw": [...],
    "heikin_raw": [...],
    "signal": "LONG",   // "LONG" | "SHORT" | null
    "timestamp": 1736012345
  }
}
2) REST API – Parámetros dinámicos
URL:

bash
Copiar código
POST /api/params
Body (JSON):

json
Copiar código
{
  "h": 5,
  "r": 3,
  "atr_length": 14,
  "atr_mult": 1.8,
  "rsi_length": 7,
  "ema_length": 55
}
Respuesta:

json
Copiar código
{
  "success": true,
  "new_params": {
    "h": 5,
    "r": 3,
    "atr_length": 14,
    "atr_mult": 1.8,
    "rsi_length": 7,
    "ema_length": 55
  }
}
3) Socket.IO – Eventos
🔹 Suscribirse a actualizaciones:

ts
Copiar código
socket.emit("subscribe_realtime", { symbol: "BTCUSDT", interval: "5m" });
🔹 Recibir actualizaciones periódicas:

ts
Copiar código
socket.on("realtime_update", (data) => {
  console.log("📡 update:", data.signal, data.candles.at(-1));
});
Ejemplo de payload recibido:

json
Copiar código
{
  "symbol": "BTCUSDT",
  "interval": "5m",
  "candles": [...],
  "nadaraya_raw": [...],
  "heikin_raw": [...],
  "signal": "SHORT",
  "timestamp": 1736012450
}
🧩 Integración Next.js
REST:

ts
Copiar código
const res = await fetch("http://localhost:5000/api/realtime/BTCUSDT?interval=5m");
const j = await res.json();
console.log(j.data.signal, j.data.candles);
Socket.IO:

ts
Copiar código
import { io } from "socket.io-client";
const socket = io("http://localhost:5000");

socket.emit("subscribe_realtime", { symbol: "BTCUSDT", interval: "5m" });

socket.on("realtime_update", (data) => {
  console.log("Signal:", data.signal);
});
⚙️ Configuración
Símbolos soportados:

python
Copiar código
SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT"]
Intervalos soportados:
Los definidos en MerinoConfig.TIMEFRAMES y MerinoConfig.UPDATE_INTERVALS.

📍 Ubicación
bash
Copiar código
TradingLatino-main/services/integrations/next_bridge.py
yaml
Copiar código

