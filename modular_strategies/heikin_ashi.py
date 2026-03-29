from .base import BaseStrategy, Requirement, Trend, Signal, Flag

class HeikinAshiStrategy(BaseStrategy):
    def __init__(self, params=None):
        default_params = {
            "required_green_candles": 3
        }
        if params: default_params.update(params)
        
        super().__init__(
            name="HA_FANTASMA",
            display_name="👻 TENDENCIA HEIKIN-ASHI",
            description="Filtro anti-ruido que opera inercia perfecta usando bloques Heikin-Ashi sin mechas inferiores.",
            params=default_params
        )

    def check(self, analysis):
        inds = analysis.get('indicators', {})
        ha = inds.get('heikin_ashi', {})
        
        c1 = ha.get('color', 0) == 1
        c2 = ha.get('prev_color', 0) == 1
        c3 = ha.get('prev2_color', 0) == 1
        three_green = c1 and c2 and c3
        
        ha_open = ha.get('open', 0)
        ha_low  = ha.get('low', 0)
        price   = analysis.get('current_price', 1)
        no_lower_wick = (ha_open - ha_low) < (price * 0.002)
        
        daily_bias = analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')
        
        self.requirements = [
            Requirement("Racha 3 Verdes Mín", three_green, Flag.YES if three_green else Flag.NO, Flag.YES,
                desc="Tres velas Heikin-Ashi verdes consecutivas = inercia alcista establecida y sostenida. ✅ 3 verdes seguidas. ⚠️ Menos de 3: inercia no confirmada, posible ruido."),
            Requirement("Sin Sombra de Rechazo", no_lower_wick, Flag.YES if no_lower_wick else Flag.NO, Flag.YES,
                desc="Vela HA sin mecha inferior = los compradores dominan sin ningún rechazo. Si hay mecha, indica presión vendedora. ✅ sombra < 0.2% del precio. ⚠️ Mecha grande: hay rechazo activo."),
            Requirement("Macro Bias 1D", daily_bias == Trend.BULLISH, daily_bias, Trend.BULLISH,
                desc="El sesgo del gráfico diario confirma la dirección alcista de largo plazo. ✅ 1D = BULLISH: operamos con la macro. ⚠️ Neutral o bajista: operamos contra la tendencia de fondo.")
        ]

        is_triggered = all(r.status for r in self.requirements)
        self.last_check_status = is_triggered
        return is_triggered, self.name if is_triggered else None

    def get_ui_report(self, analysis, snapshot=None):
        perf = self.evaluate_performance(snapshot, analysis)
        inds = analysis.get('indicators', {})
        ha = inds.get('heikin_ashi', {})
        color_str = "VERDE" if ha.get('color', 0) == 1 else "ROJO"
        
        return {
            "judges": [r.to_dict() for r in self.requirements],
            "triggered": self.last_check_status,
            "health_score": perf['health_score'],
            "recommendation": perf['recommendation'],
            "health_judges": perf.get('judges', []),
            "ha_color": color_str,
            "time_info": perf.get('time_judge', {}).get('val', 'Simulado')
        }

    def evaluate_performance(self, snapshot, current_analysis):
        """Auditoría de Salud: ¿Siguen encadenadas las velas HA verdes sin mechas?"""
        from .base import Requirement
        
        base_eval = super().evaluate_performance(snapshot, current_analysis)
        time_judge_data = base_eval["time_judge"]
        time_judge = Requirement(time_judge_data['name'], time_judge_data['ok'], time_judge_data['val'], time_judge_data['target'])

        inds = current_analysis.get('indicators', {})
        ha = inds.get('heikin_ashi', {})
        rsi = inds.get('rsi', {}).get('value', 50)
        adx = inds.get('adx', {}).get('value', 0)
        price = current_analysis.get('current_price', 1)
        
        still_green = ha.get('color', 0) == 1
        still_no_wick = (ha.get('open', 0) - ha.get('low', 0)) < (price * 0.004)  # umbral más holgado en salud
        daily_bias = current_analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')

        audit_juries = [
            (time_judge, 20),
            (Requirement("Vela HA Actual Verde", still_green, Flag.YES if still_green else Flag.NO, Flag.YES,
                desc="La inercia Heikin-Ashi debe permanecer alcista.\n✅ color = VERDE: tendencia saludable.\n⚠️ color = ROJO: cambio de inercia detectado."), 50),
            (Requirement("Sombra Inferior Controlada", still_no_wick, Flag.YES if still_no_wick else Flag.NO, Flag.YES,
                desc="La falta de mecha inferior confirma la fuerza del movimiento.\n✅ sin mecha: presión de compra total.\n⚠️ con mecha: aparece duda o rechazo en la subida."), 20),
            (Requirement("Macro 1D Alcista", daily_bias == Trend.BULLISH, daily_bias, Trend.BULLISH,
                desc="El contexto diario debe respaldar la operación de tendencia.\n✅ 1D BULLISH: a favor de la marea.\n⚠️ 1D Neutral/Bear: riesgo de contratendencia macro."), 10),
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
