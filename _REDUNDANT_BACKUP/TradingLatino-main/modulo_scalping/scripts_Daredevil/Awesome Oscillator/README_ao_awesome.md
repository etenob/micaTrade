# 📘 Módulo: AO (Awesome Oscillator)

## 🎯 Objetivo

Detectar cambios de momentum entre compradores y vendedores, con un histograma simple de barras rojas y verdes.

---

## ⚙️ Cálculo

AO = SMA(5) del punto medio - SMA(34) del punto medio  
Donde punto medio = (High + Low) / 2

---

## 📦 Función principal

```python
ao = calcular_ao(alto, bajo)
📈 Visualización
Histograma con barras verdes si AO > 0 (momentum positivo)

Barras rojas si AO < 0 (momentum negativo)

🧠 Notas
AO no necesita configuración de usuario (es un indicador fijo).

Puede servir para confirmar entradas Whale 👽 o divergencias.

🧪 Demo incluida
El archivo ao_awesome.py genera un gráfico con barras AO para pruebas.
