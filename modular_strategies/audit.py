import os
import json
import logging
from datetime import datetime

log = logging.getLogger(__name__)

class AuditManager:
    """Gestiona la Caja Negra: Snapshots de Veredicto para auditoría."""
    
    def __init__(self, history_dir="trade_history"):
        self.history_dir = history_dir
        self.snapshots_dir = os.path.join(self.history_dir, "snapshots")
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Crea las carpetas de historial si no existen."""
        if not os.path.exists(self.snapshots_dir):
            os.makedirs(self.snapshots_dir)
            log.info(f"Carpeta de historial creada: {self.snapshots_dir}")

    def save_verdict_snapshot(self, strategy, analysis, symbol, metadata=None):
        """
        Guarda una 'foto' completa del motivo de compra.
        strategy: La instancia de la estrategia que disparó.
        analysis: El dict completo de indicadores y precios.
        symbol: El par de trading (ej: BTCUSDT).
        """
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        
        # Formato del nombre: 2026-03-28_BTCUSDT_ALIEN.json
        filename = f"{now.strftime('%Y-%m-%d')}_{symbol}_{strategy.name}.json"
        
        # Si el archivo ya existe (mismo día/par/strat), le agregamos el timestamp para no pisar
        filepath = os.path.join(self.snapshots_dir, filename)
        if os.path.exists(filepath):
            filename = f"{timestamp}_{symbol}_{strategy.name}.json"
            filepath = os.path.join(self.snapshots_dir, filename)

        # Empaquetamos todo
        snapshot = {
            "metadata": {
                "timestamp": timestamp,
                "strategy": strategy.name,
                "display_name": strategy.display_name,
                "symbol": symbol,
                "extra": metadata or {}
            },
            "verdict": strategy.get_ui_report(analysis),
            "market_data": {
                "price": analysis.get('current_price'),
                "signal": analysis.get('signal'),
                "indicators": analysis.get('indicators'),
                "levels": analysis.get('trading_levels'),
                "macro_context": analysis.get('multi_tf')
            }
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=4, ensure_ascii=False)
            log.info(f"Caja Negra: Snapshot guardado en {filepath}")
            return filepath
        except Exception as e:
            log.error(f"Error guardando Snapshot: {e}")
            return None
