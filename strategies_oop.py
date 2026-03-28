import logging
from datetime import datetime

log = logging.getLogger(__name__)

class BaseStrategy:
    """Clase base para el motor de estrategias de trading."""
    
    def __init__(self, name, display_name, description, params=None):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.params = params or {}
        # Estado interno (pueden usarse para métricas en el futuro)
        self.last_check_status = False
        self.last_check_time = None

    def check(self, analysis):
        """
        Método principal de validación de compra.
        Debe ser sobrescrito por cada subclase.
        """
        raise NotImplementedError("Cada estrategia debe implementar su propia lógica de 'check'")

    def get_ui_report(self, analysis):
        """
        Genera el diccionario detallado para el Analizador HTML.
        Debe retornar un dict con los indicadores y su estado (OK/NOK).
        """
        raise NotImplementedError("Cada estrategia debe implementar su propio 'get_ui_report'")


class AlienStrategy(BaseStrategy):
    """Implementación OOP de la estrategia ALIEN."""
    
    def __init__(self, params=None):
        default_params = {
            "strength_min": 90,
            "adx_min": 25,
            "daily_bias_req": "BULLISH"
        }
        if params: default_params.update(params)
        
        super().__init__(
            name="ALIEN",
            display_name="👽 ALIEN 90",
            description="Estrategia institucional estricta: Ballenas y fuerza extrema.",
            params=default_params
        )

    def check(self, analysis):
        """Lógica pura de ejecución de compra."""
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        daily_bias = analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')

        # Evaluación de condiciones
        cond_signal = (sig['signal'] == 'LONG' and sig['signal_strength'] >= self.params["strength_min"])
        cond_whale = ('BULL' in sig.get('whale_alert', ''))
        cond_trend = (price > ema['ema_55'] and daily_bias == self.params["daily_bias_req"])
        cond_force = (adx > self.params["adx_min"])

        is_triggered = cond_signal and cond_whale and cond_trend and cond_force
        
        self.last_check_status = is_triggered
        self.last_check_time = datetime.now().isoformat()
        
        return is_triggered, self.name if is_triggered else None

    def get_ui_report(self, analysis):
        """Reporte detallado para los badges del Analizador."""
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        daily_bias = analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')

        # Retornamos el estado de cada componente visual
        return {
            "confianza": {
                "val": f"{sig['signal_strength']}%",
                "ok": sig['signal_strength'] >= self.params["strength_min"]
            },
            "ballenas": {
                "val": "BULL" if 'BULL' in sig.get('whale_alert', '') else "NO",
                "ok": 'BULL' in sig.get('whale_alert', '')
            },
            "adx": {
                "val": f"{adx:.1f}",
                "ok": adx > self.params["adx_min"]
            },
            "macro_1d": {
                "val": daily_bias,
                "ok": daily_bias == self.params["daily_bias_req"]
            },
            "triggered": self.last_check_status
        }


class CiegaStrategy(BaseStrategy):
    """Implementación OOP de la estrategia TENDENCIA CIEGA."""
    
    def __init__(self, params=None):
        default_params = {
            "strength_min": 75,
            "adx_min": 20,
            "max_ema_dist": 3.0,
            "min_techo_dist": 2.0,
            "max_rsi": 60
        }
        if params: default_params.update(params)

        super().__init__(
            name="TENDENCIA_CIEGA",
            display_name="🦅 TENDENCIA CIEGA",
            description="Momentum técnico sin ballenas, protegida por escudos anti-FOMO.",
            params=default_params
        )

    def check(self, analysis):
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        nad = analysis['indicators']['nadaraya']
        rsi = analysis['indicators']['rsi']['value']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        daily_bias = analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')

        # Cálculo de distancias (Lógica que hoy está repetida en dos sitios)
        dist_ema55 = ((price / ema['ema_55']) - 1) * 100 if ema['ema_55'] > 0 else 99
        dist_techo = ((nad['upper'] / price) - 1) * 100 if price > 0 else 0

        is_triggered = (
            sig['signal'] == 'LONG' and 
            sig['signal_strength'] >= self.params["strength_min"] and
            daily_bias == "BULLISH" and 
            adx > self.params["adx_min"] and
            0 < dist_ema55 <= self.params["max_ema_dist"] and
            dist_techo >= self.params["min_techo_dist"] and
            rsi < self.params["max_rsi"]
        )

        self.last_check_status = is_triggered
        return is_triggered, self.name if is_triggered else None

    def get_ui_report(self, analysis):
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        nad = analysis['indicators']['nadaraya']
        rsi = analysis['indicators']['rsi']['value']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        daily_bias = analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')

        dist_ema55 = ((price / ema['ema_55']) - 1) * 100 if ema['ema_55'] > 0 else 99
        dist_techo = ((nad['upper'] / price) - 1) * 100 if price > 0 else 0

        return {
            "confianza": {"val": f"{sig['signal_strength']}%", "ok": sig['signal_strength'] >= self.params["strength_min"]},
            "adx": {"val": f"{adx:.1f}", "ok": adx > self.params["adx_min"]},
            "ema_dist": {"val": f"{dist_ema55:.1f}%", "ok": 0 < dist_ema55 <= self.params["max_ema_dist"]},
            "techo_dist": {"val": f"{dist_techo:.1f}%", "ok": dist_techo >= self.params["min_techo_dist"]},
            "rsi": {"val": f"{rsi:.1f}", "ok": rsi < self.params["max_rsi"]},
            "macro_1d": {"val": daily_bias, "ok": daily_bias == "BULLISH"},
            "triggered": self.last_check_status
        }


class ReboteStrategy(BaseStrategy):
    """Estrategia de suelos Nadaraya."""
    def __init__(self, params=None):
        default_params = {"rsi_max": 35, "h1_adx_crash": 40}
        if params: default_params.update(params)
        super().__init__("REBOTE_SUELO", "🟢 REBOTE SUELO", "Reversión a la media en sobreventa extrema.", default_params)

    def check(self, analysis):
        price = analysis['current_price']
        nadaraya = analysis['indicators']['nadaraya']
        rsi = analysis['indicators']['rsi']['value']
        h1 = analysis.get('multi_tf', {}).get('1h', {})
        
        is_panic = (h1.get('adx', 0) > self.params["h1_adx_crash"] and h1.get('bias','') == 'BEARISH')
        r_dist_ok = (nadaraya['lower'] * 0.990 <= price <= nadaraya['lower'] * 1.002)
        
        is_triggered = r_dist_ok and rsi < self.params["rsi_max"] and not is_panic
        self.last_check_status = is_triggered
        return is_triggered, self.name if is_triggered else None


class GatilloStrategy(BaseStrategy):
    """Estrategia de persecución EMA 11."""
    def __init__(self, params=None):
        default_params = {"strength_min": 75, "ema_dist_max": 1.0, "rsi_max": 65, "adx_min": 20}
        if params: default_params.update(params)
        super().__init__("GATILLO_11", "⚡ GATILLO 11", "Persecución de tendencia en timeframe corto.", default_params)

    def check(self, analysis):
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        rsi = analysis['indicators']['rsi']['value']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        h1_sqz = analysis.get('multi_tf', {}).get('1h', {}).get('squeeze_trend', 'NEUTRAL')

        dist_ema11 = ((price / ema['ema_11']) - 1) * 100 if ema['ema_11'] > 0 else 99
        
        is_triggered = (
            sig['signal'] == 'LONG' and sig['signal_strength'] >= self.params["strength_min"] and
            0 < dist_ema11 <= self.params["ema_dist_max"] and
            rsi < self.params["rsi_max"] and adx > self.params["adx_min"] and
            h1_sqz == 'UP'
        )
        self.last_check_status = is_triggered
        return is_triggered, self.name if is_triggered else None


class PingPongStrategy(BaseStrategy):
    """Estrategia de rebote en Order Blocks."""
    def __init__(self, params=None):
        default_params = {"rsi_max": 45, "dist_max": 0.5, "dist_min": -1.0}
        if params: default_params.update(params)
        super().__init__("BLOCK_PINGPONG", "🧱 ORDER BLOCK", "Rebote en niveles institucionales.", default_params)

    def check(self, analysis):
        price = analysis['current_price']
        ob = analysis['trading_levels']['order_blocks']
        bull_ob = ob['bullish_ob_price']
        rsi = analysis['indicators']['rsi']['value']
        sig = analysis['signal']

        if bull_ob <= 0: return False, None
        
        dist_ob = ((price / bull_ob) - 1) * 100
        is_triggered = (
            self.params["dist_min"] <= dist_ob <= self.params["dist_max"] and
            rsi < self.params["rsi_max"] and
            sig['signal'] == 'LONG' and sig['bias'] == 'BULLISH'
        )
        self.last_check_status = is_triggered
        return is_triggered, self.name if is_triggered else None
