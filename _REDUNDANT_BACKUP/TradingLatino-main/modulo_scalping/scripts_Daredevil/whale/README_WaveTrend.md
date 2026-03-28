# 📘 WaveTrend - Módulo LPWN

Este módulo implementa el cálculo del indicador **WaveTrend**, tal como aparece en el script original *"Multiple Strategies \[LPWN]"* usado por Daredevil. Forma parte esencial de la lógica de las **señales Whale 👽 y 👹**.

---

## 📐 Fórmula y lógica

El indicador WaveTrend se calcula a partir de la media exponencial suavizada del precio promedio (hlc3) y de una medida de desviación absoluta. Genera dos líneas principales:

* `wt1`: Línea rápida (más sensible)
* `wt2`: Línea lenta (suavizada con media móvil)

De estas se derivan:

* `wtCross`: cruces de wt1 con wt2 (valor +1, -1 o 0)
* `wtCrossUp`: si wt1 cruza por encima de wt2
* `wtCrossDown`: si wt1 cruza por debajo de wt2
* `wtVwap`: diferencia entre `wt1` y `wt2`, usada como oscilador visual

---

## 🧠 Aplicación

El módulo es utilizado en las siguientes condiciones del sistema:

### ✅ Whale 👽 (compra):

* wtCrossUp == True
* Confirmado por condiciones de Diamond y Sommi Flag

### ✅ Whale 👹 (venta):

* wtCrossDown == True
* Confirmado por condiciones de Diamond y Sommi Flag

---

## 🔍 Parámetros por defecto

* `channel_length = 9`
* `average_length = 12`
* `ma_length = 3`

Estos valores pueden ser ajustados desde el archivo principal que orquesta los módulos.

---

## 🔗 Integración

Este módulo es invocado desde `core_signals.py` o cualquier motor de backtest / alerta que quiera evaluar condiciones Whale. Debe recibir un `DataFrame` con columnas `['high', 'low', 'close']`.

---

## 🛠️ Uso básico en Python

```python
from wavetrend import calcular_wavetrend

# df es un DataFrame con columnas high, low, close
resultado = calcular_wavetrend(df)
print(resultado[['wt1', 'wt2', 'wtCross']].tail())
```

---

## 📁 Ubicación

Este archivo forma parte del repositorio:

```
/Scripts_Daredevil/Scripts/wavetrend/
```
