from .base import BaseStrategy, Requirement, Trend, Signal, Squeeze, Action
from datetime import datetime

class GatilloStrategy(BaseStrategy):
    """Modularización de GATILLO 11."""
    
    def __init__(self, params=None):
        default_params = {"strength_min": 65, "ema_dist_max": 1.0, "rsi_max": 65, "adx_min": 20, "max_patience_min": 120}
        if params: default_params.update(params)
        super().__init__("GATILLO_11", "⚡ GATILLO 11", "Persecución de tendencia EMA 11.", default_params)

    def check(self, analysis):
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        rsi = analysis['indicators']['rsi']['value']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        h1 = analysis.get('multi_tf', {}).get('1h', {})
        h1_sqz = h1.get('squeeze_trend', 'NEUTRAL')

        dist_ema11 = ((price / ema['ema_11']) - 1) * 100 if ema['ema_11'] > 0 else 99
        
        # El Tribunal de Jueces de Gatillo
        self.requirements = [
            Requirement("Dirección LONG", sig['signal'] == Signal.LONG, sig['signal'], Signal.LONG,
                desc="Motor Merino emite señal LONG activa. ✅ LONG. ⚠️ WAIT o SHORT: no operar."),
            Requirement("Confianza", sig['signal_strength'] >= self.params["strength_min"], sig['signal_strength'], self.params["strength_min"],
                desc=f"Puntos Merino mínimos para operación. ✅ ≥ {self.params['strength_min']}. ⚠️ Debajo: señal débil."),
            Requirement("Soporte EMA 11", 0 < dist_ema11 <= self.params["ema_dist_max"], f"{dist_ema11:.2f}%", f"<= {self.params['ema_dist_max']}%",
                desc=f"Precio tocando la EMA de corto plazo — entrada de precisión. ✅ dist 0%-{self.params['ema_dist_max']}% sobre EMA 11. ⚠️ Lejos o por debajo: entrada tardía o rota."),
            Requirement("Room RSI", rsi < self.params["rsi_max"], round(rsi,1), f"< {self.params['rsi_max']}",
                desc=f"RSI con espacio de recorrido al alza disponible. ✅ RSI < {self.params['rsi_max']}. ⚠️ Sobrecomprado: sin recorrido."),
            Requirement("Fuerza Trend (ADX)", adx > self.params["adx_min"], round(adx,1), self.params["adx_min"],
                desc=f"Momentum cuantificado activo en el mercado. ✅ ADX > {self.params['adx_min']}. ⚠️ Debajo: tendencia sin energía."),
            Requirement("Squeeze 1H", h1_sqz == 'UP', h1_sqz, "UP",
                desc="El squeeze LazyBear en 1H está liberando energía hacia arriba. ✅ squeeze_trend = UP. ⚠️ Neutral o DOWN: la energía está contenida o bajando.")
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
            "health_judges": perf.get("judges", []),
            "rsi_15m": perf.get("rsi_15m", 0),
            "adx": perf.get("adx", 0),
            "ema_55": perf.get("ema_55", 0),
            "time_info": perf.get("time_info", "Simulado")
        }

    def evaluate_performance(self, snapshot, current_analysis):
        """Auditoría de Salud de Gatillo basada en el Tribunal de Jueces."""
        
        # 1. Obtener Juez de Tiempo de la base
        base_eval = super().evaluate_performance(snapshot, current_analysis)
        time_judge_data = base_eval["time_judge"]
        time_judge = Requirement(time_judge_data['name'], time_judge_data['ok'], time_judge_data['val'], time_judge_data['target'])

        price = current_analysis['current_price']
        ema = current_analysis['indicators']['ema']
        h1 = current_analysis.get('multi_tf', {}).get('1h', {})
        h1_sqz = h1.get('squeeze_trend', 'NEUTRAL')
        rsi = current_analysis['indicators']['rsi']['value']
        adx = current_analysis['indicators']['adx']['value']
        
        # 2. Definir los Jueces Auditores de Salud (Persecución)
        audit_juries = [
            (time_judge, 30),
            (Requirement("Soporte EMA 11", price > ema['ema_11'] * 0.998, "SI" if price > ema['ema_11'] * 0.998 else "NO", "SI",
                desc="El precio debe mantenerse por encima de la EMA 11 (base del trade).\n✅ precio sobre EMA 11 (-0.2%): soporte de corto plazo vigente.\n⚠️ Rompe EMA 11: el trade perdió su base, ajustar SL."), 60),
            (Requirement("Momentum Squeeze 1H", h1_sqz == Squeeze.UP, h1_sqz, Squeeze.UP,
                desc="El squeeze en 1H debe seguir liberando energía alcista.\n✅ squeeze_trend = UP: momentum activo y direccional.\n⚠️ Neutral o DOWN: la energía se agotó o invirtió."), 50),
            (Requirement("Capa RSI (Sobrecra)", rsi < 75, round(rsi,1), "<75",
                desc="RSI sin sobrecompra extrema durante el trade.\n✅ RSI < 75: hay recorrido disponible.\n⚠️ RSI > 75: sobrecomprado, riesgo de corrección inminente."), 10)
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
