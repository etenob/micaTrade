# 📘 Módulo: Estocástico

## 🎯 Objetivo

Detectar condiciones de sobrecompra/sobreventa, ideal para entradas precisas o confirmaciones visuales.

---

## ⚙️ Fórmula

- %K = 100 × (Cierre - Mín. Low) / (Máx. High - Mín. Low)
- %D = Media móvil de %K

Default:  
- Período %K: 14  
- Suavizado %D: 3  

---

## 📦 Función principal

```python
k, d = calcular_estocastico(cierre, alto, bajo)
📈 Visualización
%K (azul) y %D (naranja)

Niveles sugeridos: 80 (sobrecompra) y 20 (sobreventa)

🧠 Notas
El cruce de %K por encima de %D puede interpretarse como señal de entrada.

Muy útil en combinación con el AO o RSI para confirmar dirección.

🧪 Demo incluida
El archivo stoch_oscillator.py genera una gráfica con los dos trazos para pruebas.

yaml
Copiar
Editar
