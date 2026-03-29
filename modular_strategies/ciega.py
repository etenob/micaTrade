from .base import BaseStrategy, Requirement, Trend, Signal, Action
from datetime import datetime

class CiegaStrategy(BaseStrategy):
    """Implementación modular de TENDENCIA CIEGA."""
    
    def __init__(self, params=None):
        default_params = {
            "strength_min": 65, "adx_min": 20, "max_ema_dist": 3.0, 
            "min_techo_dist": 2.0, "max_rsi": 60, "max_patience_min": 720
        }
        if params: default_params.update(params)

        super().__init__(
            name="TENDENCIA_CIEGA",
            display_name="🦅 TENDENCIA CIEGA",
            description="Momentum técnico sin ballenas, protegida por escudos anti-FOMO.",
            params=default_params
        )

    def check(self, analysis):
        from .base import Requirement
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        nad = analysis['indicators']['nadaraya']
        rsi = analysis['indicators']['rsi']['value']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        daily_bias = analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')

        dist_ema55 = ((price / ema['ema_55']) - 1) * 100 if ema['ema_55'] > 0 else 99
        dist_techo = ((nad['upper'] / price) - 1) * 100 if price > 0 else 0

        # El Tribunal de Jueces de Ciega
        self.requirements = [
            Requirement("Dirección LONG", sig['signal'] == Signal.LONG, sig['signal'], Signal.LONG,
                desc="Motor Merino debe emitir señal LONG. ✅ signal = LONG. ⚠️ WAIT o SHORT: no operar."),
            Requirement("Confianza Técnica", sig['signal_strength'] >= self.params["strength_min"], sig['signal_strength'], self.params["strength_min"],
                desc=f"Señal Merino con fuerza técnica sin necesitar ballena. ✅ ≥ {self.params['strength_min']} pts. ⚠️ Debajo: señal insuficiente."),
            Requirement("Fuerza Momentum (ADX)", adx > self.params["adx_min"], round(adx,1), self.params["adx_min"],
                desc=f"Energía cuantificada de la tendencia. ✅ ADX > {self.params['adx_min']}. ⚠️ Debajo: tendencia lateral o débil."),
            Requirement("Tendencia Macro 1D", daily_bias == Trend.BULLISH, daily_bias, Trend.BULLISH,
                desc="El gráfico diario debe ser alcista. ✅ 1D = BULLISH: operamos con el viento. ⚠️ Neutral o bajista: contra tendencia macro."),
            Requirement("Cerca de VPoC (Vol)", sig['volume_profile']['in_value_area'], f"{sig['volume_profile']['distance_pct']}%", "< 5%",
                desc="Precio en zona de mayor interés institucional. ✅ Dentro del 5% del VPoC. ⚠️ Fuera: sin soporte volumétrico."),
            Requirement("Escudo EMA (Cerca Base)", 0 < dist_ema55 <= self.params["max_ema_dist"], f"{dist_ema55:.1f}%", f"<= {self.params['max_ema_dist']}%",
                desc=f"Anti-FOMO: no entramos muy lejos de la EMA 55. ✅ dist < {self.params['max_ema_dist']}%. ⚠️ Más lejos: entrada tardía, ratio R:R malo."),
            Requirement("Escudo Nad (Espacio Techo)", dist_techo >= self.params["min_techo_dist"], f"{dist_techo:.1f}%", f">= {self.params['min_techo_dist']}%",
                desc=f"Debe haber espacio libre hasta el techo Nadaraya (ratio R:R). ✅ dist techo > {self.params['min_techo_dist']}%. ⚠️ Sin espacio: no hay recorrido potencial."),
            Requirement("Escudo RSI (No FOMO)", rsi < self.params["max_rsi"], round(rsi,1), f"< {self.params['max_rsi']}",
                desc=f"RSI sin sobrecompra para evitar comprar bombeado. ✅ RSI < {self.params['max_rsi']}. ⚠️ Sobrecomprado: riesgo de comprar en techo.")
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
        """Auditoría de Salud de Ciega basada en el Tribunal de Jueces."""
        from .base import Requirement
        
        # 1. Obtener Juez de Tiempo de la base
        base_eval = super().evaluate_performance(snapshot, current_analysis)
        time_judge_data = base_eval["time_judge"]
        time_judge = Requirement(time_judge_data['name'], time_judge_data['ok'], time_judge_data['val'], time_judge_data['target'])

        price = current_analysis['current_price']
        ema = current_analysis['indicators']['ema']
        adx = current_analysis['indicators']['adx']['value']
        rsi = current_analysis['indicators']['rsi']['value']
        
        # 2. Definir los Jueces Auditores de Salud (🦅🦅)
        audit_juries = [
            (time_judge, 20),
            (Requirement("Momentum Trail (ADX)", adx > 18, round(adx,1), ">18",
                desc="La tendencia sigue activa y con energía suficiente para continuar.\n✅ ADX > 18: trending válido.\n⚠️ ADX < 18: mercado lateral, la tendencia se está muriendo."), 40),
            (Requirement("Base Macro (EMA 55)", price > ema['ema_55'] * 0.997, "SI" if price > ema['ema_55'] * 0.997 else "NO", "SI",
                desc="El precio debe mantenerse sobre la EMA de largo plazo (soporte macro).\n✅ precio sobre EMA 55: tendencia de fondo intacta.\n⚠️ Rompe EMA 55: salida urgente, la tendencia terminó."), 60),
            (Requirement("Escudo RSI", rsi < 80, round(rsi,1), "<80",
                desc="RSI no sobrecomprado durante el trade de tendencia.\n✅ RSI < 80: recorrido disponible al alza.\n⚠️ RSI > 80: zona de sobrecompra extrema, ajustar SL."), 10)
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
        
        # 4. Determinación de Recomendación
        recommendation = Action.HOLD
        if health < 40:
            recommendation = Action.EXIT_NOW
        elif health < 80 or rsi > 75 or not time_judge.status:
            recommendation = Action.TIGHTEN_SL
            
        return {
            "health_score": health,
            "recommendation": recommendation,
            "reasons": reasons,
            "judges": final_judges,
            "rsi_15m": round(rsi, 1),
            "adx": round(adx, 1),
            "ema_55": round(ema['ema_55'], 2),
            "time_info": f"{self._get_minutes_elapsed(snapshot)}m" if snapshot else "Simulado"
        }
