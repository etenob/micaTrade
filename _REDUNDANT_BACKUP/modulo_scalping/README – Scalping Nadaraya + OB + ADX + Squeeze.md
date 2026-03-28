📄 README – Scalping Nadaraya + OB + ADX + Squeeze
⚙️ Descripción general

Este script combina varias herramientas de confluencia para scalping intradía:

Kernel Nadaraya → genera curvas de regresión y bandas dinámicas.

Order Blocks (OB) → zonas relevantes de liquidez (bullish/bearish).

ADX modificado → mide fuerza de la tendencia, con gatillo en nivel 23.

Squeeze Momentum (versión visual con colores) → identifica compresión/expansión.

RSI (opcional) → como filtro adicional.

Panel de estadísticas (testing) → mide winrate, PnL y retorno.

El objetivo es combinar zonas (OB) con condiciones de fuerza (ADX + squeeze) y validar entradas con Nadaraya.

🧩 Componentes principales
🔹 Kernel Nadaraya

Curvas yhat1 (principal) y yhat2 (lag).

Bandas dinámicas upper/lower calculadas con ATR.

Se usan para identificar posibles rebotes.

🔹 Order Blocks (OB)

Dibujo automático de Bullish OB y Bearish OB.

Marcados con box.new() en el gráfico.

Funcionan como zonas de interés → no siempre implican entrada.

🔹 ADX (Average Directional Index modificado)

Se calcula manualmente (plusDI, minusDI, adx_value).

Nivel clave = 23 → cuando el ADX llega aquí, aumenta la probabilidad de continuación.

Se dibuja línea horizontal en 23 + label con el valor actual.

🔹 Squeeze Momentum

Representado con histogramas de colores:

Verde / Verde oscuro → presión alcista.

Rojo / Bordó → presión bajista.

Se usa junto al ADX para confirmar si la tendencia tiene fuerza real.

🔹 Señales (Entradas y Salidas)

Entradas (LONG/SHORT) → se muestran con plotshape() en el gráfico.

Salidas (EXIT) → automáticas, según ATR o % configurado.

El objetivo es que el cartelito LONG o SHORT sea la entrada efectiva, y EXIT la salida correspondiente.

🔹 Panel de Estadísticas

Muestra en el gráfico:

Total de trades.

Winrate %.

P&L neto.

Retorno %.

Útil para testing rápido de parámetros.

⚙️ Configuración de parámetros

h, r, lag → controlan sensibilidad de Nadaraya.

atrLength, atr_stop_mult, tp_atr_mult → gestión de riesgo por ATR.

adx_len, adx_dilen, adx_level → configuración del ADX.

use_percent_tp, tp_pct, sl_pct → alternativa de gestión por %.

cooldown_bars → barras de espera entre señales.

show_arrows, draw_table → visualización de entradas y panel.

🚦 Lógica de confirmación de entradas

El precio toca un OB → zona de interés.

El ADX está cerca o por encima del nivel 23 → fuerza confirmada.

El Squeeze cambia color o forma "gancho" → muestra pérdida o ganancia de momentum.

Se activa condición de Nadaraya (crossover/crossunder).

Resultado:

LONG si confluye en OB alcista.

SHORT si confluye en OB bajista.

📌 Próximos pasos

Ajustar la visualización de OBs (para que no ensucien demasiado).

Configurar el Squeeze visual en histogramas.

Ampliar panel con métricas específicas de OB (ej: cuántos OBs respetados vs fallidos).

Preparar versión Python + Next.js para control dinámico.

👉 Con esto ya queda documentada la idea base.
Después vamos iterando sobre configuración de OBs, squeeze, visualización y seguimos expandiendo el README
