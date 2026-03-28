from .base import BaseStrategy, Requirement, Trend, Signal, Action
from datetime import datetime

class PingPongStrategy(BaseStrategy):
    """Modularización de BLOCK PINGPONG."""
    
    def __init__(self, params=None):
        default_params = {"rsi_max": 45, "dist_max": 0.5, "dist_min": -1.0, "max_patience_min": 240}
        if params: default_params.update(params)
        super().__init__("BLOCK_PINGPONG", "🧱 ORDER BLOCK", "Rebote en Order Blocks.", default_params)

    def check(self, analysis):
        from .base import Requirement
        price = analysis['current_price']
        ob = analysis['trading_levels']['order_blocks']
        bull_ob = ob['bullish_ob_price']
        rsi = analysis['indicators']['rsi']['value']
        sig = analysis['signal']

        dist_ob = ((price / bull_ob) - 1) * 100 if bull_ob > 0 else -99
        
        # El Tribunal de Jueces de PingPong
        self.requirements = [
            Requirement("Existencia de OB", bull_ob > 0, "SI" if bull_ob > 0 else "NO", "SI"),
            Requirement("Zona de Rebote OB", (self.params["dist_min"] <= dist_ob <= self.params["dist_max"]), f"{dist_ob:.2f}%", f"[{self.params['dist_min']}%, {self.params['dist_max']}%]"),
            Requirement("RSI favorable", rsi < self.params["rsi_max"], round(rsi,1), f"< {self.params['rsi_max']}"),
            Requirement("Confluencia LONG", (sig['signal'] == Signal.LONG and sig['bias'] == Trend.BULLISH), f"{sig['signal']}/{sig['bias']}", "LONG/BULLISH"),
            Requirement("Área de Valor VPoC", sig.get('volume_profile', {}).get('in_value_area', False), f"{sig.get('volume_profile', {}).get('distance_pct', 0)}%", "< 5%")
        ]

        is_triggered = all(r.status for r in self.requirements)
        self.last_check_status = is_triggered
        return is_triggered, self.name if is_triggered else None

    def get_ui_report(self, analysis, snapshot=None):
        """Reporte inteligente para la UI con Salud Proyectada."""
        perf = self.evaluate_performance(snapshot, analysis)
        
        return {
            "judges": [r.to_dict() for r in self.requirements],
            "triggered": self.last_check_status,
            "health_score": perf["health_score"],
            "recommendation": perf["recommendation"],
            "rsi_15m": perf.get("rsi_15m", 0),
            "adx": perf.get("adx", 0),
            "ema_55": perf.get("ema_55", 0),
            "time_info": perf.get("time_info", "Simulado")
        }

    def evaluate_performance(self, snapshot, current_analysis):
        """Auditoría de Salud de PingPong basada en el Tribunal de Jueces."""
        from .base import Requirement
        
        # 1. Obtener Juez de Tiempo de la base
        base_eval = super().evaluate_performance(snapshot, current_analysis)
        time_judge_data = base_eval["time_judge"]
        time_judge = Requirement(time_judge_data['name'], time_judge_data['ok'], time_judge_data['val'], time_judge_data['target'])

        price = current_analysis['current_price']
        ob = current_analysis['trading_levels']['order_blocks']
        bull_ob = ob['bullish_ob_price']
        rsi = current_analysis['indicators']['rsi']['value']
        adx = current_analysis['indicators']['adx']['value']
        ema = current_analysis['indicators']['ema']
        
        # 2. Definir los Jueces Auditores de Salud (Niveles OB)
        dist_ob = ((price / bull_ob) - 1) * 100 if bull_ob > 0 else -99
        
        audit_juries = [
            (time_judge, 20),
            (Requirement("Soporte Institucional (OB)", bull_ob > 0, "SI" if bull_ob > 0 else "NO", "SI"), 80),
            (Requirement("Zona de Seguridad OB", dist_ob > -1.5, f"{dist_ob:.2f}%", ">-1.5%"), 70)
        ]

        # 3. Calcular Salud Dinámica
        health = 100
        reasons = []
        final_judges = []

        for judge, penalty in audit_juries:
            final_judges.append(judge.to_dict())
            if not judge.status:
                health -= penalty
                reasons.append(f"Fallo en {judge.name}: {judge.current}")

        health = max(0, health)
        
        # 4. Determinación de Recomendación con Constantes Pro
        recommendation = Action.HOLD
        if health < 50:
            recommendation = Action.EXIT_NOW
        elif health < 90:
            recommendation = Action.TIGHTEN_SL
            
        return {
            "health_score": health,
            "recommendation": recommendation,
            "reasons": reasons,
            "judges": final_judges,
            "rsi_15m": round(rsi, 1),
            "adx": round(adx, 1),
            "ema_55": round(ema.get('ema_55', 0), 2),
            "time_info": f"{self._get_minutes_elapsed(snapshot)}m" if snapshot else "Simulado"
        }
