# 🔍 Análisis de Estrategias: Dashboard vs Código Real

Este documento desglosa paso a paso qué condiciones visualiza el **Analizador de Estrategias** (el panel web) y cómo se traducen exactamente en la lógica matemática real del bot (`strategies.py` y `merino_math.py`).

---

## 👽 1. ALIEN 90 (Institucional)
**Objetivo:** La estrategia más conservadora que busca alineación total del mercado (macro, ballenas, fuerza y dirección).

### 🛠 Código Real vs Analizador:
Para que esta estrategia dispare (devuelva `True`), el código exige que se cumplan las siguientes 6 condiciones simultáneamente:

1. **Confianza de Señal:**
   - *Código:* `sig['signal_strength'] >= 90`
   - *Analizador:* Muestra el % de confianza en verde si es mayor o igual a 90.
2. **Señal de Fondo (Dirección):**
   - *Código:* `sig['signal'] == 'LONG'`
   - *Analizador:* Exige que la dirección calculada en 4H sea LONG.
3. **Tendencia MACRO (1D):**
   - *Código:* `analysis.get('multi_tf', {}).get('1d', {}).get('bias') == 'BULLISH'`
   - *Analizador:* Revisa el marco temporal de 1 Día para asegurar que la macroeconomía de la moneda es alcista.
4. **Alerta de Ballenas:**
   - *Código:* `'BULL' in sig.get('whale_alert', '')`
   - *Analizador:* Busca la firma "ALIEN" u "OGRE" de transacciones institucionales alcistas.
5. **Posición Macro (EMA 55):**
   - *Código:* `price > ema['ema_55']`
   - *Analizador:* Verifica que el precio de entrada no esté por debajo de la media móvil de 55 periodos (debe ser soporte).
6. **Filtro de Tendencia (ADX):**
   - *Código:* `adx > 25`
   - *Analizador:* Exige que la inercia tenga fuerza real (no lateralización).

---

## 💥 2. REBOTE SUELO (Agresiva)
**Objetivo:** Atrapar el precio exactamente cuando toca el fondo del canal envolvente de Nadaraya Watson, asegurando que no sea una caída en picado mortal.

### 🛠 Código Real vs Analizador:
El código en `check_rebote_suelo()` es más directo y depende fuertemente de evitar "cuchillos cayendo":

1. **Límite Suelo (Nadaraya Inferior):**
   - *Código:* `lower_floor * 0.990 <= price <= lower_floor * 1.002`
   - *Analizador:* Calcula matemáticamente si el precio actual está penetrando el soporte (máximo -1% por debajo) o rebotando apenas por encima (máximo +0.2%).
2. **RSI (Sobreventa):**
   - *Código:* `rsi < 35`
   - *Analizador:* Confirma que estadísticamente los vendedores están agotados.
3. **Peligro en 1H (Anti-Cuchillo):**
   - *Código:* `if h1_adx > 40 and h1_bias == 'BEARISH': return False`
   - *Analizador:* El bot bloquea sistemáticamente la compra si detecta que la moneda se está desplomando libremente en marcos de tiempo cortos (Peligro de caída libre).

---

## 🔫 3. GATILLO 11 (Moderada)
**Objetivo:** La estrategia clásica de continuidad. Entra justo cuando el precio, tras un pequeño descanso, rompe la EMA de 11 periodos hacia arriba.

### 🛠 Código Real vs Analizador:
El código une los indicadores clásicos de Jaime Merino para asegurar que haya una ruptura limpia:

1. **Señal y Confianza:**
   - *Código:* `sig['signal'] == 'LONG' and sig['signal_strength'] >= 75`
   - *Analizador:* No necesita el 90% de ALIEN, le basta un 75% muy sólido pero obligatorio.
2. **Posición vs EMA 11 (El Gatillo):**
   - *Código:* `ema['ema_11'] < price <= (ema['ema_11'] * 1.01)`
   - *Analizador:* Verifica que el precio acaba de cruzar la EMA 11. **Filtro matemático crucial:** Si el precio subió más de un 1% por encima de la EMA, YA SE FUE (comprar alto es peligroso), por lo que bloquea la entrada por FOMO.
3. **Filtro de ADX y RSI:**
   - *Código:* `adx > 20 and rsi < 65`
   - *Analizador:* El ADX garantiza que hay volumen empujando, y el RSI < 65 garantiza que aún hay margen para que suba antes de llegar al límite.
4. **Tendencia Squeeze en 1H:**
   - *Código:* `h1_sqz_trend == 'UP'`
   - *Analizador:* Exige que los valles del indicador Squeeze (en el marco de tiempo menor de 1 hora) tengan inercia alcista comprobada.

---

## 🧱 4. BLOCK PINGPONG (Geométrica)
**Objetivo:** Estrategia pura de "Smart Money". Compra exactamente en los muros institucionales (Order Blocks) que se dejaron pendientes.

### 🛠 Código Real vs Analizador:
Es la estrategia que depende 100% de la tabla de precios provista por el libro de órdenes:

1. **El Muro de Compra:**
   - *Código:* `bull_ob > 0 and bull_ob * 0.990 <= price <= bull_ob * 1.005`
   - *Analizador:* El bot obtiene el precio exacto del muro alcista (Order Block verde). Exige que la moneda choque contra ese muro (permitiendo un margen de penetración del 1% y un rebote previo del 0.5%).
2. **Seguridad Dimensional (Bias 4H):**
   - *Código:* `sig['signal'] == 'LONG' and sig['bias'] == 'BULLISH'`
   - *Analizador:* No importa qué tan fuerte sea el rebote, si la estructura de mercado general es bajista (`BEARISH`), la orden bloquea para evitar trampas bajistas.
3. **RSI de Margen:**
   - *Código:* `rsi < 45`
   - *Analizador:* Por seguridad adicional, incluso rebotando en el muro, el "momentum" estático de RSI debe ser neutral/bajo para asegurar un buen riesgo/beneficio.

---

### 🔬 Conclusión de Auditoría

Tras la auditoría del código `strategies.py` contra las validaciones de `strategy_analyzer.html`, confirmamos que:
- **No hay desincronización**: El panel web lee **exactamente las mismas variables** y aplica las **mismas matemáticas** simuladas del motor en ejecución.
- Si el Analizador en `localhost:5000` marca todas las bolitas de una estrategia en `VERDE`, es una garantía matemática de que el `bot_multi_strategy.py` ha ejecutado o intentado ejecutar la orden en Binance.
