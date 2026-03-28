# WalletEngine

**Proyecto:** Motor de billeteras auto‑alimentadas (The\_Daredevil) — *WalletEngine*

**Propósito:** implementar un motor modular para gestionar múltiples wallets que reinvierten rendimientos (auto‑compounding), dimensionan posiciones usando la F óptima (Kelly / Kelly fraccional), optimizan frecuencia de harvest frente a fees y protegen el capital con límites y circuit‑breakers.

---

## Tabla de contenido

1. Visión general
2. Objetivos
3. Arquitectura y módulos
4. Estructura del repositorio
5. Instalación rápida
6. Configuración básica
7. Flujo de trabajo (ejemplos)
8. Métricas y reporting
9. Seguridad y operaciones
10. Testing y simulaciones
11. Roadmap y próximos pasos
12. Contribuir
13. Licencia

---

## 1. Visión general

WalletEngine es un conjunto modular (Python + notebooks + scripts) pensado para:

* Recolectar datos on‑chain / off‑chain y estimar parámetros de rendimiento por activo.
* Calcular fracciones de capital vía *F óptima (Kelly)*, con opción de Kelly fraccional.
* Ejecutar harvest / reinversión en la frecuencia óptima considerando fees, slippage y locks.
* Registrar contabilidad por wallet y exponer reportes (CAGR, drawdown, costo en fees, etc.).

Diseñado para ser auditable, extensible y desplegable tanto en servidores como en máquinas locales (Raspberry, NAS, VPS).

---

## 2. Objetivos

* Automatizar la reinversión (compound) de recompensas.
* Minimizar riesgo mediante sizing de posición con Kelly fraccional y límites configurables.
* Optimizar tradeoffs entre frecuencia de reinversión y coste por operación.
* Proveer simulador/backtester para validar configuraciones antes de ejecutar on‑chain.

---

## 3. Arquitectura y módulos

Cada pieza es un módulo intercambiable:

* **data\_oracle/**: ingesta histórica y en tiempo real (CSV, APIs, oráculos). Normaliza precios, APRs, rewards y fees.
* **estimator/**: funciones para estimar $\mu,\sigma$ por activo/estrategia; EWMA, rolling windows y bootstrap para estimar incertidumbre.
* **position\_sizer/**: cálculo de F óptima (Kelly) puro y fraccional, límites min/max, reglas de protección (max\_exposure).
* **harvest\_scheduler/**: lógica para decidir cuándo harvest/reinvest (time-based, threshold-based, cost-benefit). Simulador de frecuencia óptima.
* **executor/**: adaptadores on‑chain/off‑chain (scripts para firmar y enviar txs, batching, retries, gas optimization). Soporte multisig hardware wallets.
* **ledger/**: contabilidad por wallet, registro de transacciones, costes y métricas derivadas.
* **simulator/**: Monte Carlo y backtesting con escenarios de mu/sigma, slippage y fees.
* **ui\_cli/**: utilidades CLI y endpoints (opcional Next/React para consola visual futura).
* **security/**: circuit-breakers, whitelists, rate limits, key-management guidelines.

---

## 4. Estructura del repositorio (sugerida)

```
/WalletEngine
├── README.md
├── pyproject.toml / requirements.txt
├── notebooks/
│   ├── 01_kelly_and_estimators.ipynb
│   └── 02_simulator_harvest_frequency.ipynb
├── wallet_engine/
│   ├── data_oracle/
│   ├── estimator/
│   ├── position_sizer/
│   ├── harvest_scheduler/
│   ├── executor/
│   ├── ledger/
│   └── simulator/
├── scripts/
│   ├── run_simulator.py
│   └── run_executor.py
├── config/
│   └── example_config.yaml
└── docs/
    └── design_decisions.md
```

---

## 5. Instalación rápida

```bash
git clone <tu-repo>/WalletEngine.git
cd WalletEngine
python -m venv .venv
source .venv/bin/activate  # linux/mac
.venv\Scripts\activate     # windows
pip install -r requirements.txt
```

Recomendación: usa Python >= 3.10.

---

## 6. Configuración básica

Ejemplo `config/example_config.yaml`:

```yaml
global:
  base_currency: USD
  account: wallet_1
  max_exposure_per_asset: 0.35
  kelly_fraction: 0.5   # Kelly fraccional, 1.0 = full Kelly

data_oracle:
  price_source: csv
  csv_path: data/prices.csv

executor:
  mode: dry_run
  gas_limit: 200000
  retry_attempts: 3

harvest:
  strategy: cost_benefit
  min_reward_usd: 5.0
  min_reward_to_gas_ratio: 1.2
```

---

## 7. Flujo de trabajo (ejemplos)

1. Preparar datos (CSV o conectar API) y colocar en `data/`.
2. Ejecutar notebook `01_kelly_and_estimators.ipynb` para estimar $\mu,\sigma$ y obtener fracciones iniciales.
3. Correr `run_simulator.py --config config/example_config.yaml` para comparar frecuencias de harvest.
4. Revisar resultados en `ledger/reports/` y ajustar `kelly_fraction` o `max_exposure_per_asset`.
5. Pasar a `executor` en modo `dry_run`, y finalmente `live` cuando estés listo.

---

## 8. Métricas y reporting

Siempre registra y expón:

* Balance histórico por wallet (USD + assets)
* CAGR anualizado
* Drawdown máximo y duración
* Volatilidad anualizada
* Costos acumulados en fees
* Net Harvest Benefit = rewards - (gas + slippage + fees)

Formato de reportes: CSV + JSON + gráficos en notebooks.

---

## 9. Seguridad y operaciones

* **Gestión de claves:** preferir multisig / hardware wallets (Ledger, Trezor) para mover fondos.
* **Circuit-breakers:** umbrales que desactivan ejecuciones automáticas (e.g., caída del mercado > X% en 24h).
* **Approval staging:** pruebas en testnet o redes locales antes de lanzar en mainnet.
* **Auditoría:** logs inmutables en `ledger/` y firma de artefactos críticos.

---

## 10. Testing y simulaciones

* **Unit tests** para cada módulo (pytest recomendado).
* **Simulaciones Monte Carlo** con varying mu/sigma para ver sensibilidad de Kelly.
* **Backtests históricos** que incluyan eventos extremos y cambios en fees.

Comando ejemplo:

```bash
python scripts/run_simulator.py --config config/example_config.yaml --mc-runs 1000
```

---

## 11. Roadmap y próximos pasos (priorizados)

1. 📄 README (hecho)
2. 📓 Notebooks: estimadores (01) + simulador harvest (02)
3. 🧩 Implementar `position_sizer` + `estimator` (funciones básicas)
4. 🛠 `harvest_scheduler` con simulador de coste/beneficio
5. 🔐 `executor` en modo dry\_run con soporte multisig
6. 📊 Dashboard ligero (Next/React) para visualizar wallets y métricas
7. 🔁 Integración on‑chain (Yearn‑like vaults / adapters a protocolos)

---

## 12. Contribuir

* Crear branch por feature: `feature/<modulo>-descripcion`.
* Abrir PR con tests y notebooks de ejemplo.
* Mantener documentación actualizada en `docs/`.

---

## 13. Licencia

MIT (sensible para desarrollo privado; cambiar si querés otra).

---

### Nota final

Este README es el punto de partida. Puedo generar ahora mismo los notebooks `01_kelly_and_estimators.ipynb` y `02_simulator_harvest_frequency.ipynb`, o empezar por el módulo `position_sizer` en código Python. ¿Cuál preferís que arme ahora?

