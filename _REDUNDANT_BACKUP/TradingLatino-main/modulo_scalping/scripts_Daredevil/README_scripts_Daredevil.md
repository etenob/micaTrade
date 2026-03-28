# 🧠 Scripts_Daredevil

Repositorio modular de indicadores desarmados del sistema de TradingView de Daredevil 🦊

Este módulo contiene todos los scripts personalizados derivados de:

- `Multiple Strategies [LUPOWN]`
- `Multiple Indicators + TL Alerts`

---

## 📦 Estructura del repositorio

/Scripts/ ← Indicadores separados por módulo
/scripts_Daredevil
|   checklist de proceso.md ← Proceso de separación de los scrpits
|   README_scripts_Daredevil.md	← Este archivo
|   tree.txt   
+---ADX_status
|       adx.py
|       README_ADX.md       
+---Awesome Oscillator
|       ao_awesome.py
|       README_ao_awesome.md       
+---Ema
|       ema_combo.py
|       README_EMA.md       
+---Ema_cross
|       ema_cross.py
|       README_EMA_Cross.md       
+---ema_trend_color
|       ema_trend_color.py
|       README_EMA_Color.md       
+---Estocßstico
|       README_Estocßstico.md
|       stoch_oscillator.py       
+---koncorde_colores
|       koncorde_colores.py
|       README_Koncorde.md       
+---koncorde_diamond
|       koncorde.py
|       README_Koncorde.md       
+---MACD
|       macd_basic.py
|       README_MACD.md       
+---Momentum
|       estado_momentum.py
|       README_Momentum.md       
+---RSI_Divergencias
|       README_RSI.md
|       rsi_divergencias.py       
+---show_status
|       README_ShowStatus.md
|       show_status.py|       
+---Squeeze_Momentum
|       README_Squeeze_Momentum.md
|       squeeze_momentum.py       
\---whale_lpwn
        Readme.md
        whale_lpwn.py

├── Kernel.md ← Documentación del motor central (Faltante)
├── /Bitacora ← Registro cronológico de decisiones y pruebas (Faltante)

---

## 📌 Objetivo

Descomponer los scripts de TradingView en módulos Python independientes, cada uno con:

- Su propio código funcional
- Un `README.md` explicativo
- Compatibilidad con consola o automatización

---

## ⚙️ Indicadores planeados

- `whale_lpwn` → Señales 👽 / 👹 por patrón Sommi
- `adx_status` → Evaluación de fuerza de tendencia por nivel 23
- `koncorde_diamond` → Cruce marrón/media con diamantes ✅❌
- `squeeze_momentum` → Evaluación de compresión y expansión de volatilidad
- ... y más

---

> ⚠️ Este repositorio es parte del sistema mayor: `Kernel_Daredevil_TradingBot`