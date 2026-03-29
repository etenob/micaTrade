from .base import BaseStrategy, Requirement, Trend, Signal, Flag

class SweepHunterStrategy(BaseStrategy):
    def __init__(self, params=None):
        default_params = {
            "min_wick_pct": 65.0,  # La mecha inferior debe ser > 65% del total de la vela
            "min_vol_spike": 1.5   # Volumen debe ser 1.5x el promedio
        }
        if params: default_params.update(params)
        
        super().__init__(
            name="SWEEP_HUNTER",
            display_name="🧹 CAZA-LIQUIDACIONES",
            description="Algoritmo de reversión extrema que compra asimetrías de panico absorbiendo Stop Losses.",
            params=default_params
        )

    def check(self, analysis):
        inds = analysis.get('indicators', {})
        spike_info = inds.get('volume_spike', {})
        wick_pct = spike_info.get('lower_wick_pct', 0)
        vol_ratio = spike_info.get('ratio', 0)
        
        ema_55 = inds.get('ema', {}).get('ema_55', 0)
        price = analysis.get('current_price', 0)
        
        self.requirements = [
            Requirement("Absorción Brutal (>65%)", wick_pct >= self.params["min_wick_pct"], f"{wick_pct}%", f">={self.params['min_wick_pct']}%",
                desc=f"Mecha inferior > {self.params['min_wick_pct']}% de la vela total = trampa de pánico real. Los stop-losses fueron cazados y el precio está siendo absorbido. ✅ Mecha grande. ⚠️ Sin mecha: no hay trampa, rebote débil."),
            Requirement("Volumen Institucional", vol_ratio >= self.params["min_vol_spike"], f"{vol_ratio}x", f">={self.params['min_vol_spike']}x",
                desc=f"Volumen {self.params['min_vol_spike']}x el promedio = presencia institucional activa absorbiendo la caída. ✅ ratio ≥ {self.params['min_vol_spike']}x. ⚠️ Bajo: sin capital institucional detrás."),
            Requirement("Dip Confirmado", price < ema_55, Flag.YES if price < ema_55 else Flag.NO, Flag.YES,
                desc="Precio por debajo de EMA 55 = el pánico es real, no es ruido. Confirma que hubo sobreextensión bajista absorbible. ✅ precio < EMA 55. ⚠️ Sobre EMA 55: no hay liquidaciones reales que cazar.")
        ]

        is_triggered = all(r.status for r in self.requirements)
        self.last_check_status = is_triggered
        return is_triggered, self.name if is_triggered else None

    def get_ui_report(self, analysis, snapshot=None):
        perf = self.evaluate_performance(snapshot, analysis)
        inds = analysis.get('indicators', {})
        spike = inds.get('volume_spike', {})
        
        return {
            "judges": [r.to_dict() for r in self.requirements],
            "triggered": self.last_check_status,
            "health_score": perf['health_score'],
            "recommendation": perf['recommendation'],
            "health_judges": perf.get('judges', []),
            "vol_ratio": spike.get('ratio', 0),
            "wick_pct": spike.get('lower_wick_pct', 0),
            "time_info": perf.get('time_judge', {}).get('val', 'Simulado')
        }

    def evaluate_performance(self, snapshot, current_analysis):
        """Auditoría de Salud: ¿Sigue habiendo cuerpo de reversión tras la entrada?"""
        from .base import Requirement
        
        base_eval = super().evaluate_performance(snapshot, current_analysis)
        time_judge_data = base_eval["time_judge"]
        time_judge = Requirement(time_judge_data['name'], time_judge_data['ok'], time_judge_data['val'], time_judge_data['target'])

        inds = current_analysis.get('indicators', {})
        spike = inds.get('volume_spike', {})
        price = current_analysis.get('current_price', 0)
        ema_55 = inds.get('ema', {}).get('ema_55', 1)
        rsi = inds.get('rsi', {}).get('value', 50)
        adx = inds.get('adx', {}).get('value', 0)

        dist_ema = ((price / ema_55) - 1) * 100 if ema_55 > 0 else 0
        vol_ok = spike.get('ratio', 0) >= self.params['min_vol_spike']

        audit_juries = [
            (time_judge, 20),
            (Requirement("Volumen Institucional Activo", vol_ok, f"{spike.get('ratio', 0)}x", f">={self.params['min_vol_spike']}x",
                desc=f"El volumen debe mantenerse alto para confirmar que la absorción sigue vigente.\n✅ ratio ≥ {self.params['min_vol_spike']}x: capital institucional presente.\n⚠️ Bajo: el interés institucional se disipó."), 50),
            (Requirement("Recuperando EMA 55", price >= ema_55 * 0.99, f"{dist_ema:.1f}%", ">= -1%",
                desc="El precio debe buscar reingresar al canal de la EMA 55 tras la cacería.\n✅ cercanía > -1%: recuperación en curso.\n⚠️ dist < -1%: el precio sigue hundiéndose, abortar."), 30),
        ]

        health = 100
        reasons = []
        final_judges = []
        for judge, penalty in audit_juries:
            final_judges.append(judge.to_dict())
            if not judge.status:
                health -= penalty
                reasons.append(f"Fallo en {judge.name}: {judge.current}")

        health = max(0, health)
        from .base import Action
        recommendation = Action.HOLD
        if health < 50: recommendation = Action.EXIT_NOW
        elif health < 80: recommendation = Action.TIGHTEN_SL

        return {
            "health_score": health,
            "recommendation": recommendation,
            "reasons": reasons,
            "judges": final_judges,
            "rsi_15m": round(rsi, 1),
            "adx": round(adx, 1),
            "ema_55": round(ema_55, 4),
            "time_info": time_judge_data['val']
        }
