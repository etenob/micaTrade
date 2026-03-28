from .base import BaseStrategy, Requirement, Trend, Signal, Action
from datetime import datetime

class ReboteStrategy(BaseStrategy):
    """Modularización de REBOTE SUELO."""
    
    def __init__(self, params=None):
        default_params = {"rsi_max": 35, "h1_adx_crash": 40, "max_patience_min": 60}
        if params: default_params.update(params)
        super().__init__("REBOTE_SUELO", "🟢 REBOTE SUELO", "Reversión a la media con Nadaraya.", default_params)

    def check(self, analysis):
        from .base import Requirement
        price = analysis['current_price']
        nad = analysis['indicators']['nadaraya']
        rsi = analysis['indicators']['rsi']['value']
        h1 = analysis.get('multi_tf', {}).get('1h', {})
        sig = analysis.get('signal', {})
        
        is_panic = (h1.get('adx', 0) > self.params["h1_adx_crash"] and h1.get('bias','') == Trend.BEARISH)
        r_dist_ok = (nad['lower'] * 0.990 <= price <= nad['lower'] * 1.002)
        dist_nad = ((price / nad['lower']) - 1) * 100 if nad['lower'] > 0 else -99

        # El Tribunal de Jueces de Rebote
        self.requirements = [
            Requirement("Suelo Nadaraya", r_dist_ok, f"{dist_nad:.2f}%", "[-1.0%, +0.2%]"),
            Requirement("Agotamiento RSI", rsi < self.params["rsi_max"], round(rsi,1), f"< {self.params['rsi_max']}"),
            Requirement("Freno Pánico 1H", not is_panic, h1.get('bias','-'), "NON-BEAR-CRASH"),
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
        """Auditoría de Salud de Rebote basada en el Tribunal de Jueces."""
        from .base import Requirement
        
        # 1. Obtener Juez de Tiempo de la base
        base_eval = super().evaluate_performance(snapshot, current_analysis)
        time_judge_data = base_eval["time_judge"]
        time_judge = Requirement(time_judge_data['name'], time_judge_data['ok'], time_judge_data['val'], time_judge_data['target'])

        price = current_analysis['current_price']
        nad = current_analysis['indicators']['nadaraya']
        rsi = current_analysis['indicators']['rsi']['value']
        h1 = current_analysis.get('multi_tf', {}).get('1h', {})
        
        # 2. Definir los Jueces Auditores de Salud (Rehabilitación)
        dist_nad = ((price / nad['lower']) - 1) * 100 if nad['lower'] > 0 else -99
        is_panic = (h1.get('adx', 0) > self.params["h1_adx_crash"] and h1.get('bias','') == Trend.BEARISH)
        
        audit_juries = [
            (time_judge, 20),
            (Requirement("Suelo Intacto", dist_nad > -2.0, f"{dist_nad:.2f}%", ">-2.0%"), 70),
            (Requirement("Filtro Pánico 1H", not is_panic, h1.get('bias','-'), "SAFE"), 40),
            (Requirement("Recuperación RSI", rsi > 40, round(rsi,1), ">40"), 10)
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
        
        # 4. Recomendación con Constantes
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
            "adx": round(h1.get('adx', 0), 1),
            "ema_55": round(current_analysis['indicators'].get('ema', {}).get('ema_55', 0), 2),
            "time_info": f"{self._get_minutes_elapsed(snapshot)}m" if snapshot else "Simulado"
        }
