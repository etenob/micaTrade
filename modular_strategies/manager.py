from .alien import AlienStrategy
from .ciega import CiegaStrategy
from .rebote import ReboteStrategy
from .gatillo import GatilloStrategy
from .pingpong import PingPongStrategy
from .sweep_hunter import SweepHunterStrategy
from .heikin_ashi import HeikinAshiStrategy
from .divergence import DivergenceStrategy
from .audit import AuditManager

class StrategyManager:
    """Clase para gestionar el conjunto de todas las estrategias modulares."""

    def __init__(self, custom_params=None):
        """
        Inicializa todas las estrategias y el gestor de auditoría. 
        """
        cp = custom_params or {}
        self.audit = AuditManager() # Caja Negra
        
        # Guardamos como dict para búsqueda rápida por nombre
        s_list = [
            AlienStrategy(params=cp.get('ALIEN')),
            CiegaStrategy(params=cp.get('TENDENCIA_CIEGA')),
            ReboteStrategy(params=cp.get('REBOTE_SUELO')),
            GatilloStrategy(params=cp.get('GATILLO_11')),
            PingPongStrategy(params=cp.get('BLOCK_PINGPONG')),
            SweepHunterStrategy(params=cp.get('SWEEP_HUNTER')),
            HeikinAshiStrategy(params=cp.get('HA_FANTASMA')),
            DivergenceStrategy(params=cp.get('DIVERGENCIA_3D'))
        ]
        self.strategies = {s.name: s for s in s_list}

    def record_trade_snapshot(self, strategy_name, analysis, symbol, metadata=None):
        """Busca el objeto estrategia por nombre y guarda su Snapshot."""
        strat = self.strategies.get(strategy_name)
        if strat:
            return self.audit.save_verdict_snapshot(strat, analysis, symbol, metadata)
        return None

    def get_active_strategies_for_coin(self, analysis_data):
        """
        Analiza un activo con todas las estrategias y devuelve 
        una lista de los nombres de las que están 'disparadas'.
        """
        active = []
        for name, strategy in self.strategies.items():
            try:
                is_triggered, _ = strategy.check(analysis_data)
                if is_triggered:
                    active.append(name)
            except Exception:
                continue
        return active

    def get_strategy_report(self, analysis_data, snapshot=None):
        """Genera el reporte para la UI seleccionando la estrategia adecuada."""
        strat_name = analysis_data.get('strategy_name', 'alien')
        # Buscamos en el dict, fallback a 'alien'
        strategy = self.strategies.get(strat_name, self.strategies.get('alien'))
        if strategy:
            return strategy.get_ui_report(analysis_data, snapshot=snapshot)
        return {}

    def get_radar_report(self, analysis):
        """
        Genera un reporte simplificado para el Radar con conteos de confluencia.
        Retorna: { 'alien': {'triggered': False, 'ok': 2, 'total': 5}, ... }
        """
        report = {}
        for name, strat in self.strategies.items():
            try:
                # Ejecutamos el check para actualizar requisitos internos
                is_triggered, _ = strat.check(analysis)
                
                # Contamos cuántos requisitos están en status=True
                ok_count = sum(1 for r in strat.requirements if r.status)
                total_count = len(strat.requirements)
                
                # Normalizamos el nombre para el frontend (ej: ALIEN -> alien)
                clean_name = name.lower().replace("_", "")
                
                report[clean_name] = {
                    'triggered': is_triggered,
                    'ok': ok_count,
                    'total': total_count,
                    'pct': int((ok_count / total_count) * 100) if total_count > 0 else 0
                }
            except Exception:
                continue
        return report

    def get_strategy_report_all(self, analysis):
        """Genera el reporte unificado con TODOS los jueces para el Analizador HTML."""
        report = {}
        for name, strat in self.strategies.items():
            # Ejecutamos el diagnóstico para actualizar los jueces internos
            strat.check(analysis)
            
            # Usamos el nombre original como clave para que se vea bien en la UI
            report[name] = strat.get_ui_report(analysis)
            report[name]['triggered'] = strat.last_check_status
        return report
