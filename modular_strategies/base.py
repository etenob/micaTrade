import logging
from datetime import datetime

log = logging.getLogger(__name__)

class Trend:
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    # Alias para ballenas
    BULL = "BULL"
    BEAR = "BEAR"
    NO_WHALE = "NO"

class Signal:
    LONG = "LONG"
    SHORT = "SHORT"
    WAIT = "WAIT"

class Squeeze:
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"

class Action:
    HOLD = "HOLD"
    EXIT_NOW = "EXIT_NOW"
    TIGHTEN_SL = "TIGHTEN_SL"
    WAIT = "WAIT"

class Requirement:
    """Representa un 'Juez' o condición técnica que debe cumplirse."""
    def __init__(self, name, status, current=None, target=None):
        self.name = name
        self.status = status     # True/False
        self.current = current   # Valor medido
        self.target = target     # Valor objetivo
    
    def to_dict(self):
        return {
            "name": self.name,
            "ok": self.status,
            "val": str(self.current),
            "target": str(self.target)
        }

class BaseStrategy:
    """Clase base para el motor de estrategias de trading."""
    
    def __init__(self, name, display_name, description, params=None):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.params = params or {}
        # Estado interno
        self.last_check_status = False
        self.last_check_time = None
        self.requirements = [] # Lista de objetos Requirement

    def check(self, analysis):
        """Método de validación. Debe sobrescribirse."""
        raise NotImplementedError("Implementar check()")

    def get_ui_report(self, analysis):
        """Reporte para el Analizador HTML. Debe sobrescribirse."""
        raise NotImplementedError("Implementar get_ui_report()")

    def _get_minutes_elapsed(self, snapshot):
        """Utilidad interna para calcular cuánto tiempo lleva el trade abierto."""
        entry_time_str = snapshot.get('entry_time')
        if not entry_time_str: return 0
        try:
            entry_time = datetime.fromisoformat(entry_time_str)
            elapsed = (datetime.now() - entry_time).total_seconds() / 60
            return round(elapsed, 1)
        except Exception:
            return 0

    def evaluate_performance(self, snapshot, current_analysis):
        """
        Compara la 'foto' de entrada con el estado actual.
        Devuelve un dict con health_score y recomendación.
        Este método base ahora calcula el Tiempo de Vida.
        """
        # Si no hay snapshot, es una Simulación del Laboratorio (Análisis de mercado)
        if snapshot is None:
            return {
                "health_score": 100,
                "recommendation": "SIMULADO",
                "time_judge": Requirement("Tiempo de Vida", True, "0m", "Simulado").to_dict(),
                "judges": [Requirement("Tiempo de Vida", True, "0m", "Simulado").to_dict()]
            }

        elapsed = self._get_minutes_elapsed(snapshot)
        max_time = self.params.get("max_patience_min", 360) # Default 6h
        
        # El Juez del Cronómetro (Común para todos)
        time_judge = Requirement("Tiempo de Vida", elapsed <= max_time, f"{elapsed}m", f"<{max_time}m")
        
        return {
            "health_score": 100 if time_judge.status else 70,
            "recommendation": "HOLD" if time_judge.status else "TIGHTEN_SL",
            "time_judge": time_judge.to_dict()
        }
