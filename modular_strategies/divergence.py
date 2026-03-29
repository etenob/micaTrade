from .base import BaseStrategy, Requirement, Trend, Signal, Flag

class DivergenceStrategy(BaseStrategy):
    def __init__(self, params=None):
        default_params = {
            "require_whale": True
        }
        if params: default_params.update(params)
        
        super().__init__(
            name="DIVERGENCIA_3D",
            display_name="🎭 DIVERGENCIA OCULTA",
            description="Algoritmo geométrico que detecta fallas físicas donde el precio cae pero la fuerza acumula.",
            params=default_params
        )

    def check(self, analysis):
        inds = analysis.get('indicators', {})
        rsi_info = inds.get('rsi', {})
        
        has_divergence = rsi_info.get('bullish_divergence', False)
        
        sig = analysis.get('signal', {})
        whale = sig.get('whale_alert', 'NORMAL')
        has_whale = whale == Trend.BULL
        
        self.requirements = [
            Requirement("Falla Geométrica (Div+)", has_divergence, Flag.YES if has_divergence else Flag.NO, Flag.YES,
                desc="El precio hace un mínimo nuevo pero el RSI no lo acompaña = acumulación oculta. El mercado está mintiendo: la caída exterior esconde compras institucionales internas. ✅ divergence = True. ⚠️ False: no hay falla geométrica."),
            Requirement("Inyección Institucional", has_whale, Trend.BULL if has_whale else Trend.NO_WHALE, Trend.BULL if self.params['require_whale'] else "CUALQUIERA",
                desc="Capital institucional (ballena) comprando mientras el precio cae = confluencia de divergencia con soporte institucional real. ✅ whale = BULL. ⚠️ Sin ballena: la divergencia no tiene respaldo institucional.")
        ]
        
        if not self.params["require_whale"]:
            self.requirements[1] = Requirement("Inyección Institucional", True, "N/A", "NO_REQUERIDA")

        is_triggered = all(r.status for r in self.requirements)
        self.last_check_status = is_triggered
        return is_triggered, self.name if is_triggered else None

    def get_ui_report(self, analysis, snapshot=None):
        perf = self.evaluate_performance(snapshot, analysis)
        inds = analysis.get('indicators', {})
        
        return {
            "judges": [r.to_dict() for r in self.requirements],
            "triggered": self.last_check_status,
            "health_score": perf['health_score'],
            "recommendation": perf['recommendation'],
            "health_judges": perf.get('judges', []),
            "rsi": inds.get('rsi', {}).get('value', 0),
            "time_info": perf.get('time_judge', {}).get('val', 'Simulado')
        }

    def evaluate_performance(self, snapshot, current_analysis):
        """Auditoría de Salud: ¿La divergencia y la ballena siguen activas?"""
        from .base import Requirement
        
        base_eval = super().evaluate_performance(snapshot, current_analysis)
        time_judge_data = base_eval["time_judge"]
        time_judge = Requirement(time_judge_data['name'], time_judge_data['ok'], time_judge_data['val'], time_judge_data['target'])

        inds = current_analysis.get('indicators', {})
        rsi_info = inds.get('rsi', {})
        sig = current_analysis.get('signal', {})
        rsi = rsi_info.get('value', 50)
        adx = inds.get('adx', {}).get('value', 0)
        
        still_diverging = rsi_info.get('bullish_divergence', False)
        whale = sig.get('whale_alert', 'NORMAL')
        still_whale = whale == Trend.BULL
        rsi_recovering = rsi > 35  # Buena señal de que el precio está rebotando

        audit_juries = [
            (time_judge, 20),
            (Requirement("Divergencia Activa", still_diverging, Flag.YES if still_diverging else Flag.NO, Flag.YES,
                desc="La divergencia alcista debe persistir como motor del movimiento.\n✅ activa: el motor de reversión sigue encendido.\n⚠️ apagada: la falla geométrica se ha disuelto."), 40),
            (Requirement("Ballena Confirmada", still_whale, Trend.BULL if still_whale else "SALIÓ", Trend.BULL,
                desc="La ballena debe permanecer en la zona para sostener el precio.\n✅ ballena BULL: soporte institucional firme.\n⚠️ ballena SALIÓ: los grandes se retiraron, alto riesgo."), 30),
            (Requirement("RSI Recuperando >35", rsi_recovering, round(rsi, 1), "> 35",
                desc="El RSI debe salir de la zona de peligro para confirmar el rebote.\n✅ RSI > 35: el precio está ganando fuerza real.\n⚠️ RSI < 35: el precio sigue débil y vulnerable."), 10),
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
            "ema_55": 0,
            "time_info": time_judge_data['val'],
            "time_judge": time_judge_data
        }
