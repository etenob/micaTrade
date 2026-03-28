from .base import BaseStrategy, Requirement, Trend, Signal, Action
from datetime import datetime

class AlienStrategy(BaseStrategy):
    """Implementación OOP de la estrategia ALIEN 90."""
    
    def __init__(self, params=None):
        default_params = {
            "strength_min": 90,
            "adx_min": 25,
            "daily_bias_req": Trend.BULLISH,
            "max_patience_min": 480 # 8 horas de paciencia
        }
        if params: default_params.update(params)
        
        super().__init__(
            name="ALIEN",
            display_name="👽 ALIEN 90",
            description="Estrategia institucional estricta basada en ballenas y fuerza extrema.",
            params=default_params
        )

    def check(self, analysis):
        from .base import Requirement
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        daily_bias = analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')

        # Definimos los Jueces de Alien
        self.requirements = [
            Requirement("Dirección LONG", sig['signal'] == Signal.LONG, sig['signal'], Signal.LONG),
            Requirement("Confianza", sig['signal_strength'] >= self.params["strength_min"], sig['signal_strength'], self.params["strength_min"]),
            Requirement("Ballena Institucional", Trend.BULL in sig.get('whale_alert', ''), Trend.BULL if Trend.BULL in sig.get('whale_alert', '') else "None", Trend.BULL),
            Requirement("Fuerza ADX", adx > self.params["adx_min"], round(adx,1), self.params["adx_min"]),
            Requirement("Macro Bias 1D", daily_bias == self.params["daily_bias_req"], daily_bias, self.params["daily_bias_req"]),
            Requirement("Área de Valor VPoC", sig['volume_profile']['in_value_area'], f"{sig['volume_profile']['distance_pct']}%", "< 5%"),
            Requirement("Precio sobre EMA 55", price > ema['ema_55'], "SI" if price > ema['ema_55'] else "NO", "SI")
        ]

        is_triggered = all(r.status for r in self.requirements)
        
        self.last_check_status = is_triggered
        self.last_check_time = datetime.now().isoformat()
        return is_triggered, self.name if is_triggered else None

    def get_ui_report(self, analysis, snapshot=None):
        """Reporte inteligente para la UI con Salud Proyectada."""
        # Calculamos salud usando el método correcto auditado
        perf = self.evaluate_performance(snapshot, analysis)
        health = perf['health_score']
        recommendation = perf['recommendation']
        final_judges = perf['judges']
        
        time_str = perf.get("time_info", "Simulado")
        
        # Obtenemos indicadores básicos de la señal
        indicators = analysis.get('indicators', {})
        ema = indicators.get('ema', {})
        adx = indicators.get('adx', {}).get('value', 0)
        rsi = indicators.get('rsi', {}).get('value', 0)

        return {
            "judges": [r.to_dict() for r in self.requirements],
            "triggered": self.last_check_status,
            "health_score": health,
            "recommendation": recommendation,
            "rsi_15m": round(rsi, 1),
            "adx": round(adx, 1),
            "ema_55": round(ema.get('ema_55', 0), 2),
            "time_info": time_str
        }

    def evaluate_performance(self, snapshot, current_analysis):
        """Auditoría de Salud de Alien basada en el Tribunal de Jueces."""
        from .base import Requirement
        
        # 1. Obtener Juez de Tiempo de la base
        base_eval = super().evaluate_performance(snapshot, current_analysis)
        time_judge_data = base_eval["time_judge"]
        time_judge = Requirement(time_judge_data['name'], time_judge_data['ok'], time_judge_data['val'], time_judge_data['target'])

        price = current_analysis['current_price']
        ema = current_analysis['indicators']['ema']
        adx = current_analysis['indicators']['adx']['value']
        sig = current_analysis['signal']
        
        # 2. Definir los Jueces Auditores de Salud (con su penalización si fallan)
        # Formato: (Requirement, Penalización si falla)
        audit_juries = [
            (time_judge, 30),
            (Requirement("Soporte Macro (EMA 55)", price > ema['ema_55'] * 0.995, "SI" if price > ema['ema_55'] * 0.995 else "NO", "SI"), 70),
            (Requirement("Presencia Ballena", Trend.BULL in sig.get('whale_alert', ''), "SI" if Trend.BULL in sig.get('whale_alert', '') else "NO", "SI"), 40),
            (Requirement("Inercia Trend (ADX)", adx > 20, round(adx,1), ">20"), 30)
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
        if health < 40:
            recommendation = Action.EXIT_NOW
        elif health < 80:
            recommendation = Action.TIGHTEN_SL
        
        return {
            "health_score": health,
            "recommendation": recommendation,
            "reasons": reasons,
            "judges": final_judges,
            "time_info": f"{self._get_minutes_elapsed(snapshot)}m" if snapshot else "Simulado"
        }
