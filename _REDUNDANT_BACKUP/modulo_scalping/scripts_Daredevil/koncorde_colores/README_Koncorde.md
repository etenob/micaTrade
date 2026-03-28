# 📘 Módulo: Koncorde (Curvas Visuales)

## 🎯 Objetivo

Recrear el fondo visual del indicador Koncorde:

- Verde: compradores minoristas
- Marrón: masa del mercado
- Azul: manos fuertes (institucionales)

---

## ⚙️ Componentes calculados

- **PVI / NVI:** Positive / Negative Volume Index
- **OscP:** Diferencia porcentual PVI vs su media
- **RSI + MFI + BollOsc + Estocástico:** combinación visual que forma la línea marrón
- **Verde:** Marrón + OscP
- **Azul:** Derivado del NVI

---

## 📦 Función principal

```python
verde, marron, azul = calcular_koncorde_colores(cierre, alto, bajo, volumen)
📈 Visualización
Verde: presión compradora minorista

Marrón: comportamiento promedio del mercado

Azul: actividad institucional (manos fuertes)

Línea cero: equilibrio

🧠 Notas
Ideal para usar junto al módulo koncorde_diamond.py

Puede agregarse como fondo visual a tus gráficos principales

🧪 Demo incluida
El archivo genera una gráfica con las tres curvas para análisis visual inmediato.

yaml
Copiar
Editar
