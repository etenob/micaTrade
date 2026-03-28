# 💣 Módulo Squeeze Momentum

Este módulo evalúa la presión del mercado con el indicador **Squeeze Momentum** (SMI), basado en la relación entre **Bollinger Bands (BB)** y **Keltner Channels (KC)**:

---

## 📊 Lógica del indicador

* **Squeeze ON**: El mercado está en compresión (BB dentro de KC) → se espera un movimiento fuerte.
* **Squeeze OFF**: El mercado salió del estado de compresión (BB fuera de KC) → posible inicio de tendencia.

Además, usa el histograma de momentum para ver la dirección:

* Verde oscuro: momentum creciente (compra)
* Verde claro: momentum decreciente en zona positiva (sobrecompra)
* Rojo oscuro: momentum decreciente (venta)
* Bordó: momentum creciente en zona negativa (sobreventa)

---

## ⚙️ Funciones principales

```python
calcular_squeeze_momentum(close: Series, length: int = 20) -> dict
```

---

## 📥 Entrada requerida

* `close`: Serie de precios de cierre
* `length`: Período para cálculo de BB y KC (default: 20)

---

## 📤 Salida esperada (diccionario)

```python
{
  'squeeze_on': Series[bool],
  'squeeze_off': Series[bool],
  'momentum': Series[float],
  'color': Series[str]  # 'verde_oscuro', 'verde_claro', 'rojo_oscuro', 'bordo'
}
```

---

## ✅ Ejemplo de uso

```python
from squeeze_momentum import calcular_squeeze_momentum

sm = calcular_squeeze_momentum(close)
if sm['squeeze_on'][-1]:
    print("💣 Squeeze activado, posible breakout")
if sm['color'][-1] == 'verde_oscuro':
    print("✅ Momentum fuerte alcista")
```

---

## 📦 Parte del sistema

`/Scripts_Daredevil/Scripts/squeeze_momentum/`
