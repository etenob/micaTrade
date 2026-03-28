# services/integrations/README_NEXT.md

# 📡 Next Bridge – Jaime Merino Bot

Módulo de integración **Next.js ↔ Flask (Merino Bot)**.  
Permite acceder en tiempo real a **velas + indicadores (Nadaraya + Heikin)** y modificar parámetros dinámicos desde el frontend.

---

## 🚀 Endpoints disponibles

### 1) REST API – Realtime

**URL**

```
GET /api/realtime/<symbol>?interval=<timeframe>
```

**Parámetros**

- `symbol`: `BTCUSDT` o `ETHUSDT`  
- `interval`: opcional (por defecto usa `MerinoConfig.SCALPING['timeframe']`, ej. `5m`)  

**Ejemplo**

```bash
curl "http://localhost:5000/api/realtime/BTCUSDT?interval=5m"
```

**Respuesta**

```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSDT",
    "interval": "5m",
    "candles": [
      { "time": 1736012340, "open": 38000, "high": 38200, "low": 37900, "close": 38100, "volume": 120.3 }
    ],
    "nadaraya_raw": [...],
    "heikin_raw": [...],
    "signal": "LONG",
    "timestamp": 1736012345
  }
}
```

---

### 2) REST API – Parámetros dinámicos

**URL**

```
POST /api/params
```

**Body (JSON)**

```json
{
  "h": 4.0,
  "r": 4.0,
  "atr_length": 14,
  "atr_mult": 1.5,
  "rsi_length": 5,
  "ema_length": 55
}
```

**Respuesta**

```json
{
  "success": true,
  "new_params": {
    "h": 4.0,
    "r": 4.0,
    "lag": 2,
    "atr_length": 14,
    "atr_mult": 1.5,
    "rsi_length": 5,
    "ema_length": 55
  }
}
```

---

### 3) Socket.IO

**Eventos disponibles**

🔹 Suscribirse a actualizaciones:

```ts
socket.emit("subscribe_realtime", { symbol: "BTCUSDT", interval: "5m" });
```

🔹 Recibir actualizaciones periódicas:

```ts
socket.on("realtime_update", (data) => {
  console.log("📡 update:", data.signal, data.candles.at(-1));
});
```

**Ejemplo de payload recibido**

```json
{
  "symbol": "BTCUSDT",
  "interval": "5m",
  "candles": [...],
  "nadaraya_raw": [...],
  "heikin_raw": [...],
  "signal": "SHORT",
  "timestamp": 1736012450
}
```

---

## ⚙️ Configuración

- **Símbolos soportados**  
  ```py
  SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT"]
  ```

- **Intervalos soportados**  
  Los definidos en `MerinoConfig.TIMEFRAMES` y `MerinoConfig.UPDATE_INTERVALS`.

- **Cálculo de señales**  
  - Estrategia Nadaraya (ATR + RSI)  
  - Confirmación Heikin-Ashi (EMA/TMA cruzada)

---

## 🧩 Integración Next.js

### REST

```ts
const res = await fetch("http://localhost:5000/api/realtime/BTCUSDT?interval=5m");
const j = await res.json();
console.log(j.data.signal, j.data.candles);
```

### Socket.IO

```ts
import { io } from "socket.io-client";
const socket = io("http://localhost:5000");

socket.emit("subscribe_realtime", { symbol: "BTCUSDT", interval: "5m" });

socket.on("realtime_update", (data) => {
  console.log("Signal:", data.signal);
});
```

### Parámetros dinámicos desde panel

```ts
await fetch("http://localhost:5000/api/params", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(params),
});
```

---

## 📍 Ubicación de módulos

- **Estrategia** → `modulo_scalping/nadaraya_strategy.py`  
- **Confirmación** → `modulo_scalping/heikin_confirm.py`  
- **Módulo ejecución** → `modulo_scalping/scalping_module.py`  
- **Puente interno** → `modulo_scalping/scalping_bridge.py`  
- **Puente externo (Flask)** → `services/integrations/next_bridge.py`  
- **Frontend (Next.js)** → `src/components/RealtimeChart.tsx`

