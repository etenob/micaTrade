# 📊 El Espectro de Confianza: Del 0% al 100%
Este documento explica cómo el bot interpreta la "fuerza" de una señal. La confianza no es solo un número; es la suma de capas de confirmación (Confluencia).

---

## 🛑 Rango 0% - 40%: El Ruido (Zona de Peligro)
En este nivel, el bot está ciego o el mercado es impredecible.
*   **0% - 10%:** Error de conexión, falta de datos de Binance o moneda recién listada sin historial.
*   **15% - 40%:** Mercado lateral "sucio". El precio sube y baja sin romper medias móviles, el ADX está por debajo de 15 (sin fuerza) y no hay volumen. **Entrar aquí es tirar una moneda al aire.**

---

## ⚠️ Rango 45% - 60%: El "WAIT" (Duda Metódica)
Es el estado por defecto del bot cuando el mercado está respirando.
*   **50%:** El valor estándar institucional. Hay una señal (ej. el Squeeze cambió de color), pero el ADX es bajo o los "hermanos mayores" (1H o 4H) están en contra.
*   **60%:** Inercia leve. El precio intenta romper la EMA 11, pero la EMA 55 todavía está muy lejos. Es un rebote débil que puede fallar pronto.

---

## 📈 Rango 65% - 75%: Inercia Técnica (Entrada Minorista)
Aquí es donde empiezan a disparar las estrategias como **Gatillo 11** o **Tendencia Ciega**.
*   **75% (CONFIRMADO):** 
    *   **Criterio:** Cruce de EMA 11/55 + Squeeze en verde + ADX > 20.
    *   **Significado:** La matemática puramente técnica dice que hay una probabilidad a favor. No hay ballenas confirmadas, pero el "sentimiento" del mercado es positivo.

---

## 👽 Rango 80% - 90%: Confluencia Institucional (Zona Alien)
Este es el territorio de alta probabilidad. Es lo que busca el bot para operaciones serias.
*   **85%:** Todo lo anterior + el gráfico de 1 Hora (1H) apoya el movimiento.
*   **90% (MAXIMA SEGURIDAD):** 
    *   **Criterio:** Cruce técnico perfecto + ADX fuerte (> 25) + **BALLENAS COMPRANDO (Whale Alert)**.
    *   **Significado:** No solo el gráfico se ve bien, sino que hay "dinero real" (instituciones) entrando en la moneda. Es el filtro de Jaime Merino al 100%.

---

## 💎 Rango 95% - 100%: La Confluencia Espejo (El Santo Grial)
Es extremadamente raro ver un 100%, ya que requiere una alineación astral de todas las temporalidades.
*   **95%:** Alineación de 15m, 1h, 4h y 1d en la misma dirección (BULLISH) + Ballenas activas.
*   **100%:** 
    *   **Criterio:** Alineación total Multi-TF + Precio rebotando exactamente en un **Order Block (OB)** histórico + RSI en zona de despegue (no sobrecomprado).
    *   **Significado:** Es una operación donde el riesgo de fallo es estadísticamente mínimo. Prácticamente "dinero gratis" si se respeta el Stop Loss.

---

## 🛠️ Resumen de Acción según Confianza

| Confianza | Acción del Bot | Apalancamiento Sugerido |
| :--- | :--- | :--- |
| **< 50%** | **BLOQUEO TOTAL** | 0x |
| **50% - 74%** | Monitoreo / Alerta | 1x (Spot) |
| **75% - 84%** | **COMPRA (Ciega/Gatillo)** | 2x - 3x |
| **85% - 95%** | **COMPRA (Alien 90)** | 3x - 5x |
| **100%** | **EJECUCIÓN TOTAL** | 5x+ (Bajo discreción) |

---
> [!IMPORTANT]
> **Nota sobre el mercado actual:** Si el bot "no entra", es porque la confianza de la mayoría de las monedas está oscilando en el rango del **50%**. Hay inercia, pero falta el ADX (fuerza) o el apoyo del gráfico Diario (1D) para saltar al 75% o 90%.
