🧠 Indicador: MACD Básico
Archivo: macd_basic.py
Ubicación sugerida: /Scripts/macd_basic/

📈 ¿Qué hace?
Este módulo calcula el indicador MACD:

Línea MACD y línea Signal

Histograma de diferencia entre ambas

Color del histograma según su forma y zona:

🟩 Verde oscuro: subiendo en zona positiva

🟨 Verde claro: bajando en zona positiva

🟥 Rojo claro: subiendo en zona negativa

🟪 Bordó: bajando en zona negativa

Cruces detectados entre MACD y Signal:

🔼 Cruce alcista

🔽 Cruce bajista

⚙️ Función principal
python
Copiar
Editar
macd, signal, hist, color, cruce = calcular_macd(cierre)
cierre: Serie de precios (Pandas Series)

color: Lista de etiquetas de color por barra

cruce: Lista con los eventos de cruce detectados

🧪 Estado
✅ Implementado y funcional
📦 Sin alertas aún
🎯 Puede usarse como filtro o complemento

