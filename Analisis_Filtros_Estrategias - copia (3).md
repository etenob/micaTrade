# 🔍 Análisis Estructural de Estrategias: Visual vs Código vs Teoría

Este documento desglosa cada estrategia del bot en tres capas fundamentales:
1. **ANALIZADOR:** Lo que se muestra visualmente y cómo interactúa el usuario.
2. **STRATEGIES.PY:** El código duro y frío; la matemática que ejecuta el bot.
3. **REALIDAD (Teoría):** El concepto de trading subyacente y lo que la estrategia *debería* lograr en el mercado real.

---

## 👽 1. ALIEN 90 (Estrategia Institucional)

### 🖥️ ANALIZADOR
**¿Qué muestra y qué hace?**
Muestra una interfaz estricta con 6 indicadores en pantalla. Se encienden luces verdes solo si la Confianza de Señal supera el 90%, las Ballenas marcan compras (BULL), el precio está seguro por encima de la media de 55 periodos, la macroeconomía diaria es alcista, y hay fuerza de mercado (ADX > 25). Bloquea visualmente cualquier intento de entrada si falla uno solo de esos 6 pilares.

### ⚙️ STRATEGIES.PY
**¿Qué hace realmente?**
Ejecuta la función `check_alien_90()`. Valida matemáticamente cruces estrictos:
- `sig['signal'] == 'LONG' and sig['signal_strength'] >= 90`
- `price > ema['ema_55']` y `adx > 25`
- Busca la palabra clave `'BULL'` en el string de ballenas y `'BULLISH'` en el bias del dataframe diario (1D).
Si absolutamente todas las condiciones son `True`, la función retorna `True` autorizando la orden a mercado en Binance.

### 🧠 REALIDAD
**¿Qué debería de hacer teóricamente?**
Es la estrategia más purista del método de Jaime Merino combinada con el indicador de ballenas. *Teóricamente*, busca el "Trade Perfecto": el momento exacto en que la tendencia de fondo a largo plazo favorece la subida, la inercia a corto plazo tiene fuerza innegable, y los grandes capitales (instituciones) deciden inyectar liquidez al mismo tiempo. Es de muy baja frecuencia (pocas operaciones), pero de altísima probabilidad de éxito.

---

## 🔫 2. GATILLO 11 (Estrategia de Continuidad)

### 🖥️ ANALIZADOR
**¿Qué muestra y qué hace?**
Muestra el estado del momentum y medias móviles. Enseña si el precio está cruzando hacia arriba la pequeña media móvil exponencial (EMA 11) pero alerta y bloquea en rojo si el precio "ya se fue" (está a más del 1% de distancia). También muestra el estado del RSI para asegurar que no estamos comprando en el techo.

### ⚙️ STRATEGIES.PY
**¿Qué hace realmente?**
En `check_gatillo_11()`, relaja la confianza exigida al 75% pero incorpora un control milimétrico del precio frente a la media móvil:
- Limita la entrada: `ema['ema_11'] < price <= (ema['ema_11'] * 1.01)`.
- Revisa el momentum: `h1_sqz_trend == 'UP'` (El oscilador pinta valle verde).
- Válvula de seguridad: `rsi < 65` (Frena la compra si el activo ya está sobrecomprado).

### 🧠 REALIDAD
**¿Qué debería de hacer teóricamente?**
Conocido como el "gatillo de entrada por confirmación". *Teóricamente*, asume que el mercado ya está en una tendencia alcista, hace una pequeña pausa o retroceso natural (tocando la EMA 11), y retoma su impulso. El bot entra exactamente en el milisegundo en que la moneda rebota en la media móvil para seguir subiendo. Es la estrategia de "surfear la ola".

---

## 💥 3. REBOTE SUELO (Estrategia Agresiva de Suelo)

### 🖥️ ANALIZADOR
**¿Qué muestra y qué hace?**
Dibuja el precio actual frente a la "Banda Inferior de Nadaraya". Prende la luz verde si el precio está impactando o hundido en ese suelo. Muestra el nivel de pánico de los vendedores (RSI muy bajo). Además, muestra un indicador de "Peligro 1H" que actúa como interruptor automático de emergencia si el desplome es muy violento.

### ⚙️ STRATEGIES.PY
**¿Qué hace realmente?**
En `check_rebote_suelo()`, calcula distancias en curvas envolventes:
- Establece el impacto: `lower_floor * 0.990 <= price <= lower_floor * 1.002` (permite penetrar el suelo hasta un 1% o anticiparse un 0.2%).
- Exige sobreventa extrema: `rsi < 35`.
- **Freno de emergencia:** Retorna `False` forzosamente si `h1_adx > 40` y `h1_bias == 'BEARISH'`.

### 🧠 REALIDAD
**¿Qué debería de hacer teóricamente?**
Es una estrategia de reversión a la media, altamente matemática. *Teóricamente*, los algoritmos envolventes como Nadaraya estiman las "bandas elásticas" del precio. Cuando el precio estira demasiado la banda hacia abajo, estadísticamente debe rebotar hacia el centro violentamente. **El principal riesgo teórico** es atrapar un "cuchillo cayendo" (comprar algo que se va a cero por una mala noticia). El freno de ADX de 1H evita exactamente esto, bloqueando el trade si huele pánico fundado.

---

## 🧱 4. BLOCK PINGPONG (Estrategia Geométrica - SMC)

### 🖥️ ANALIZADOR
**¿Qué muestra y qué hace?**
Revisa el libro de órdenes. Muestra cuál es el precio exacto del muro histórico de compras institucionales (Bullish Order Block). Calcula la distancia porcentual del precio en vivo respecto a ese muro, y autoriza si estamos casi colisionando contra él. Revisa que el panorama de 4 horas apoye el rebote.

### ⚙️ STRATEGIES.PY
**¿Qué hace realmente?**
En `check_order_block_pingpong()`, extrae el `bullish_ob_price` del motor geométrico:
- Zona de cacería: `bull_ob * 0.990 <= price <= bull_ob * 1.005` (impacto en la zona cero del bloque).
- Protege con estructura macro: `signal == 'LONG'` y `bias == 'BULLISH'`.
- Impide entrar si el mercado ya está caliente en el rebote (`rsi < 45`).

### 🧠 REALIDAD
**¿Qué debería de hacer teóricamente?**

---

## 🦅 5. TENDENCIA CIEGA (Estrategia de Inercia con Escudos)

### 🖥️ ANALIZADOR
**¿Qué muestra y qué hace?**
Es una versión "liberada" de Alien. Quita el requisito de ver ballenas (Koncorde) para permitir trades basados en inercia técnica pura. Muestra 3 "Escudos Matemáticos" en tiempo real que actúan como luz roja si el precio está muy inflado:
- **Escudo 1 (Banda EMA):** Valida que no estemos comprando "lejos del piso".
- **Escudo 2 (Aire Limpio):** Calcula si queda espacio de subida antes de chocar con el techo de Nadaraya.
- **Escudo 3 (Antifundición):** Revisa el RSI para evitar entrar en la euforia final de los pequeños minoristas.

### ⚙️ STRATEGIES.PY
**¿Qué hace realmente?**
En `check_tendencia_ciega()`, el bot se vuelve un "francotirador de inercia":
- Umbral de confianza: Se relaja a `>= 75%` (porque no busca la perfección institucional de Alien).
- Filtro ADX: Exige `> 20` para asegurar que el precio se mueva con decisión.
- **Triple Blindaje:** 
  1. `0 < dist_ema55 <= 3.0%` (Evita comprar un impulso ya agotado).
  2. `dist_techo >= 2.0%` (Garantiza un ratio beneficio/riesgo mínimo).
  3. `rsi < 60` (Filtra el "FOMO" de retailers).

### 🧠 REALIDAD
**¿Qué debería de hacer teóricamente?**
Es una estrategia de seguimiento de tendencia (Trend Following). *Teóricamente*, reconoce que muchas veces el mercado sube por puro impulso técnico o noticias, sin que las ballenas dejen huella inmediata. Para no quedarse fuera de esos movimientos, el bot entra "al ciego" de ballenas pero con "ojos de lince" en la sobreextensión. **Su misión principal** es evitar que el usuario compre el final de un impulso menor impulsado por minoristas atrapados en la euforia.
