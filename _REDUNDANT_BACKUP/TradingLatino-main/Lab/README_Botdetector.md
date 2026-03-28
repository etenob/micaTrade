# 🧪 /Lab – Detector de Bots de Mercado

## 📌 Objetivo
Este módulo experimental busca **detectar la actividad de bots en los orderbooks** de exchanges (ejemplo: Binance).  
La idea no es competir contra ellos, sino **usar sus huellas a favor** – “cabalgar” los millones de bots que ya dominan el mercado.

## ⚙️ Archivo principal
- `orderbook_botdetector.py`:  
  Script que descarga el orderbook y trades recientes, calcula métricas clave y guarda los resultados en CSV.

## 🔍 Métricas extraídas
- **imbalance** → desequilibrio entre volumen de bids y asks.  
- **spread** → diferencia relativa entre mejor bid y mejor ask.  
- **taker_imbalance** → flujo neto de órdenes agresivas (compras vs ventas).  
- **top_bid / top_ask** → cotizaciones en la punta del libro.

Estas señales suelen revelar:
- Bots de colocación de liquidez (market makers).  
- Algoritmos de spoofing (colocan y cancelan órdenes rápido).  
- Flujos de presión agresiva (taker bots).  

## 🚀 Uso rápido
1. Instalar dependencias:
   ```bash
   pip install ccxt pandas numpy
Ejecutar:

bash
Copiar código
python orderbook_botdetector.py
El script:

Baja datos cada WINDOW_SEC segundos (por defecto 30).

Imprime métricas en consola.

Guarda un histórico en botdetector_features.csv.

📊 Próximos pasos
Conectar el CSV/stream a un dashboard en Next.js.

Visualizar imbalance y taker_imbalance en tiempo real.

Integrar con lógica de trading para que actúe como filtro de bots.
