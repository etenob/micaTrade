# 📊 Verificación de Ejecución - Scalping Jaime Merino

Este documento permite comprobar que el módulo de **Scalping** se está ejecutando correctamente y que las señales enviadas a **Telegram** son reales y no de prueba.

---

## 🔹 1. Archivos principales

| Archivo | Función |
|---------|---------|
| `run_scalping.py` | Loop principal que ejecuta el módulo de scalping continuamente |
| `modulo_scalping/scalping_module.py` | Estrategia Nadaraya + confirmación Heikin, gestión de alertas |
| `Telegram/alert_manager.py` | Evita duplicados y aplica cooldown |
| `Telegram/telegram_helper.py` | Envía mensajes a Telegram |
| `Telegram/send_test.py` | Envía mensajes de prueba a Telegram |

---

## 🔹 2. Flujo de ejecución

```mermaid
flowchart TD
    A[run_scalping.py\n(loop infinito)] --> B[run_scalping(symbol)]
    B --> C[binance_service.get_klines(symbol)]
    C -->|Retorna velas| D[NadarayaStrategy → señal LONG/SHORT/None]
    D --> E[HeikinConfirm → confirma señal]
    E --> F{Señal confirmada?}
    F -- No --> G[Fin de iteración, espera sleep_seconds]
    F -- Sí --> H[AlertManager.send_alert(symbol, timeframe, signal, telegram_func)]
    H --> I{¿Alerta duplicada reciente?}
    I -- Sí --> G
    I -- No --> J[telegram_func → send_telegram_message]
    J --> K[Mensaje enviado a Telegram]
    K --> G[Fin de iteración, espera sleep_seconds]
🔹 3. Verificación rápida
Inicializar scalping:

bash
Copiar código
python run_scalping.py
Revisar consola:

✅ 📊 ✅ Cliente Binance inicializado con credenciales

✅ 📊 🌐 Conexión con Binance establecida

✅ 🔥 Alerta enviada: ETHUSDT LONG (1h) → indica señal real

Revisar Telegram:

Mensaje con formato:

scss
Copiar código
🔥 [SCALPING] Señal CONFIRMADA LONG en ETHUSDT (1h)
Diferenciar test de real:

Mensajes de send_test.py siempre contienen [TEST].

Mensajes de run_scalping.py solo se envían si la señal es confirmada y no duplicada.

AlertManager evita duplicados según cooldown configurado.

Contadores de señales:

signal_counters_hour → controla máximo por hora.

signal_counters_day → controla máximo por día.

🔹 4. Ajustes de configuración
Archivo: enhanced_config.py → MerinoConfig.SCALPING

Parámetro	Descripción
timeframe	Temporalidad usada para scalping (ej. '1h')
max_signals_per_hour	Máximo de señales enviadas por hora
max_trades_per_day	Máximo de trades por día

Archivo: Telegram/alert_manager.py

Parámetro	Descripción
cooldown_seconds	Intervalo mínimo entre alertas del mismo símbolo y señal

🔹 5. Troubleshooting
⚠️ No llegan mensajes a Telegram:

Revisar TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env.

Probar con python -m Telegram.send_test.

⚠️ No se generan señales:

Revisar que Binance retorne velas correctamente.

Asegurarse que NadarayaStrategy y HeikinConfirm estén funcionando.

⚠️ Señales filtradas por cooldown:

Mensaje en consola: ⏳ Alerta filtrada por cooldown.

Indica que la señal ya fue enviada recientemente.

🔹 6. Recomendación
Ejecutar run_scalping.py en segundo plano o en un servicio.

Revisar logs en consola o configurar logging adicional en modulo_scalping/scalping_module.py.
