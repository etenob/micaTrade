# 📈 Guía de Optimización: Cómo "Abrir el Grifo" del Bot
Este documento detalla qué variables podemos tocar en el código y la configuración para que el bot sea menos exigente y entre en más operaciones, especialmente en mercados laterales o ligeramente bajistas.

---

## 🛡️ 1. El Switch Maestro: El Filtro 1D (Macro)
Actualmente, casi todas las estrategias (Alien, Ciega, Gatillo) consultan el gráfico **Diario (1D)**. Si el Diario es `BEARISH`, el bot se cruza de brazos. 

**Cómo ampliar el mercado:**
*   **Opción A (Moderada):** Permitir operar si el 1D es `NEUTRAL`.
*   **Opción B (Agresiva):** Eliminar por completo el check de 1D en estrategias de "rebote" (como Rebote Suelo o PingPong), asumiendo que el rebote ocurre igual aunque la tendencia mayor sea caer.
*   **Impacto:** Es el cambio que más dispararía la frecuencia de trades de inmediato.

---

## 👽 2. Estrategia: ALIEN 90
Es la más tacaña del bot. Está configurada para la perfección.

**Perillas a girar:**
1.  **Confianza (90% → 75%):** Bajar el umbral de `signal_strength`. Como el bot usa escalones (50-75-90), bajarlo a 75% permitiría que Alien entre con la misma exigencia técnica que las otras estrategias, pero manteniendo su requisito de Ballenas.
2.  **ADX (25 → 18):** El ADX de 25 exige mucha fuerza. Si lo bajamos a 18-20, el bot detectará "inicios" de tendencia en lugar de esperar a que la tendencia ya esté madura.
3.  **Whale Alert (Opcional):** Actualmente exige ver ballenas. Podríamos hacer que si la confianza es muy alta (ej. 95%), entre aunque no haya ballenas detectadas en ese segundo exacto.

---

## 🦅 3. Estrategia: TENDENCIA CIEGA
Ya es más relajada que Alien, pero sus "escudos" son los que suelen bloquearla.

**Perillas a girar:**
1.  **Escudo 1 (Distancia EMA 3% → 5%):** Esto permite comprar monedas que ya han subido un poco más. Amplía la ventana de entrada.
2.  **Escudo 2 (Aire Limpio 2% → 1%):** Permite entrar aunque el techo de Nadaraya esté cerca. Es más arriesgado porque el "techo" de ganancia es menor, pero daría más trades.
3.  **Escudo 3 (RSI 60 → 70):** Permite comprar cuando el mercado está más "caliente". 60 es muy conservador; 70 es el estándar de sobrecompra real.

---

## 🔫 4. Estrategia: GATILLO 11
Es la estrategia de "perseguir" el precio.

**Perillas a girar:**
1.  **Distancia de Persecución (1% → 2.5%):** Actualmente, si el precio se aleja más de un 1% de la media de 11 periodos, el bot aborta. Subir esto a 2.5% permitiría capturar esos movimientos explosivos que "se escapan" rápido.
2.  **Squeeze Direction (UP → ANY):** Actualmente exige que el momentum esté subiendo. Podríamos permitir que entre si el momentum es alto, aunque esté empezando a curvarse.

---

## 💥 5. Estrategia: REBOTE SUELO
Es la mejor para cuando el mercado está "medio bajando" como ahora.

**Perillas a girar:**
1.  **Umbral de Pánico (RSI 35 → 45):** Actualmente solo compra si el RSI es bajísimo (pánico extremo). Si lo subimos a 45, comprará en retrocesos normales de precio, no solo en cracks.
2.  **Freno de ADX (40 → 50):** El bot deja de comprar si el precio cae con demasiada fuerza (ADX 40). Subir este límite lo hace más valiente ante caídas verticales.

---

## 🧱 6. Estrategia: BLOCK PINGPONG
Depende totalmente de que el precio toque los muros institucionales (OB).

**Perillas a girar:**
1.  **Margen de zona (1% → 2%):** Ampliar el área de "cacería" alrededor del Order Block. Si el precio se queda cerca pero no llega a tocar el bloque por un pelo, hoy no entra. Ampliar esto asegura la ejecución.

---

## 📊 Tabla de Resumen de Impacto

| Variable | Frecuencia | Riesgo | Comentario |
| :--- | :--- | :--- | :--- |
| **Bajar Confianza** | Alta 📈 | Medio ⚠️ | Entrará en señales más dudosas. |
| **Quitar Filtro 1D** | Máxima 🚀 | Alto 🔥 | Operarás contra la tendencia mayor. |
| **Bajar ADX** | Media 📊 | Bajo ✅ | Entrarás en mercados más lentos o laterales. |
| **Subir Tolerancia %** | Media 📊 | Medio ⚠️ | Comprarás un poco más caro/tarde. |
| **Flexibilizar RSI** | Media 📊 | Medio ⚠️ | Comprarás en zonas de mayor euforia. |

---
> [!TIP]
> **Recomendación Personal:** Si quieres ver acción sin volverte loco, yo empezaría por **bajar el ADX a 20** en todas las estrategias y permitir que el **1D sea NEUTRAL** (no solo Bullish). Eso mantendría la seguridad pero abriría mucho más la puerta a nuevas monedas.
