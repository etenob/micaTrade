# Desglose Técnico: Auditoría de Estrategias y Comparativa Temporal

Este documento detalla la "Tesis" de cada estrategia y cómo el nuevo motor modular juzga la evolución de un trade en tiempo real.

---

## 👽 1. Alien 90 (Fuerza Institucional)
**Tesis:** "Estamos siguiendo a las ballenas en una tendencia macro poderosa".

| Momento de Entrada (Snapshot) | Monitoreo del Presente (Evolución) | Acción si Falla |
| :--- | :--- | :--- |
| **Whale Alert BULL** | ¿Sigue la ballena empujando? | **Health -40%**: Alerta de debilidad. |
| **Precio > EMA 55** | ¿El precio sigue sobre la EMA 55? | **Health -70%**: **EXIT_NOW**. La tendencia macro murió. |
| **ADX > 25** | ¿El ADX se mantiene arriba de 20? | **Health -30%**: El mercado se aplanó. **TIGHTEN_SL**. |

---

## 🦅 2. Tendencia Ciega (Momentum Técnico)
**Tesis:** "El precio tiene inercia y está protegido por escudos de seguridad".

| Momento de Entrada (Snapshot) | Monitoreo del Presente (Evolución) | Acción si Falla |
| :--- | :--- | :--- |
| **ADX > 20** | ¿El ADX cayó abajo de 15? | **Health -40%**: Perdimos el momentum. **EXIT_NOW**. |
| **RSI < 60** | ¿El RSI superó los 75? | **Recommendation: TIGHTEN_SL**. Estamos "estirados", asegurar ganancias. |
| **Daily Bias BULL** | ¿El precio rompió la EMA 55? | **Health -60%**: Cambio de estructura. **EXIT_NOW**. |

---

## 🟢 3. Rebote Suelo (Reversión Proyectada)
**Tesis:** "Estamos en un suelo matemático (Nadaraya) y esperamos un rebote a la media".

| Momento de Entrada (Snapshot) | Monitoreo del Presente (Evolución) | Acción si Falla |
| :--- | :--- | :--- |
| **Precio cerca de Nadaraya Lower** | ¿El precio perforó el suelo > 2%? | **Health -70%**: **EXIT_NOW**. El suelo no aguantó. |
| **1H Bias SAFE** | ¿Se activó pánico (ADX/Bias) en 1H? | **Health -40%**: Nueva amenaza externa. **TIGHTEN_SL**. |
| **RSI en sobreventa** | ¿El RSI ya subió a 45? | **Recommendation: TIGHTEN_SL**. El rebote ya empezó, cubrir el empate. |

---

## ⚡ 4. Gatillo 11 (Persecución EMA)
**Tesis:** "Tendencia rápida apoyada en la EMA 11 y Squeeze alcista".

| Momento de Entrada (Snapshot) | Monitoreo del Presente (Evolución) | Acción si Falla |
| :--- | :--- | :--- |
| **Precio > EMA 11** | ¿El precio cruzó la EMA 11 a la baja? | **Health -60%**: La micro-tendencia se rompió. **EXIT_NOW**. |
| **Squeeze 1H UP** | ¿El Squeeze 1H cambió a DOWN? | **Health -50%**: El impulso se dio vuelta. **EXIT_NOW**. |
| **RSI < 65** | ¿RSI > 75? | **TIGHTEN_SL**: Subir stop al último mínimo. |

---

## 🧱 5. Order Block (PingPong)
**Tesis:** "Rebote en una zona de alta liquidez institucional".

| Momento de Entrada (Snapshot) | Monitoreo del Presente (Evolución) | Acción si Falla |
| :--- | :--- | :--- |
| **Bullish OB detectado** | ¿El precio perforó el OB > 1.5%? | **Health -80%**: El bloque fue invalidado. **EXIT_NOW**. |
| **Signal LONG** | ¿El bloque desapareció del análisis? | **Health -50%**: El nivel ya no es relevante. **TIGHTEN_SL**. |

---

### 🚀 Conclusión
Con este sistema, el Manager de estrategias podrá supervisar cada moneda que tengas activa. En lugar de solo esperar al "Take Profit" o "Stop Loss", el bot ahora puede **entender** si el mercado cambió y actuar preventivamente.

**¿Qué te parece este desglose?** ¿Añadirías alguna otra "señal de alerta" para alguna de ellas?
