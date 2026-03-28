// test-socket.js
import { io } from "socket.io-client";

const socket = io("http://localhost:5000");

socket.on("connect", () => {
  console.log("✅ Conectado al Merino server con ID:", socket.id);

  // Suscribirse a BTCUSDT 5m
  socket.emit("subscribe_realtime", { symbol: "BTCUSDT", interval: "5m" });
});

socket.on("realtime_update", (data) => {
  console.log("📡 Update recibido:", data);
});

socket.on("disconnect", () => {
  console.log("❌ Desconectado");
});

