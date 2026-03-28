import logging

log = logging.getLogger(__name__)

class StrategyEngine:
    @staticmethod
    def check_alien_90(analysis):
        """Estrategia Institucional: Solo señales 90%+ con Whale Bull y tendencia macro."""
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        
        # Filtros: Fuerza >= 90%, Ballena Alcista, Sobre EMA 55 (Tendencia Macro) y ADX fuerte
        if sig['signal'] == 'LONG' and sig['signal_strength'] >= 90:
            if 'BULL' in sig.get('whale_alert', '') and price > ema['ema_55']:
                # REFINAMIENTO MTF: Confirmación con tendencia diaria
                daily_bias = analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')
                if adx > 25 and daily_bias == 'BULLISH':
                    return True, "ALIEN_90"
        return False, None

    @staticmethod
    def check_tendencia_ciega(analysis):
        """Estrategia de Momentum Puro: Versión de Alien sin ballenas, pero con 3 escudos anti-minoristas FOMO."""
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        nadaraya = analysis['indicators']['nadaraya']
        rsi = analysis['indicators']['rsi']['value']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        
        # Señal de Fondo LONG + 75% confianza técnica (sin requerir ballenas)
        if sig['signal'] == 'LONG' and sig['signal_strength'] >= 75:
            daily_bias = analysis.get('multi_tf', {}).get('1d', {}).get('bias', 'NEUTRAL')
            if daily_bias == 'BULLISH' and adx > 20:
                # Escudos Anti-FOMO Minorista
                dist_ema55 = ((price / ema['ema_55']) - 1) * 100 if ema['ema_55'] > 0 else 99
                dist_techo = ((nadaraya['upper'] / price) - 1) * 100 if price > 0 else 0
                if 0 < dist_ema55 <= 3.0 and dist_techo >= 2.0 and rsi < 60:
                    return True, "TENDENCIA_CIEGA"
        return False, None

    @staticmethod
    def check_rebote_suelo(analysis):
        """Estrategia Agresiva: Precio cerca de la banda inferior de Nadaraya."""
        prices = analysis['current_price']
        nadaraya = analysis['indicators']['nadaraya']
        rsi = analysis['indicators']['rsi']['value']
        lower_floor = nadaraya['lower']
        
        # Si el precio está en la zona de rebote + RSI bajo
        if lower_floor * 0.990 <= prices <= lower_floor * 1.002 and rsi < 35:
            # REFINAMIENTO MTF: Evitar entrar si la caída en 1h tiene demasiada "fuerza" bajista
            h1_data = analysis.get('multi_tf', {}).get('1h', {})
            h1_adx = h1_data.get('adx', 0)
            h1_bias = h1_data.get('bias', 'NEUTRAL')
            
            # Si el ADX en 1h es > 40 y la tendencia es bajista, es un "cuchillo cayendo"
            if h1_adx > 40 and h1_bias == 'BEARISH':
                return False, None
                
            return True, "REBOTE_SUELO"
        return False, None

    @staticmethod
    def check_gatillo_11(analysis):
        """Estrategia Moderada: Cruce de EMA 11 con confianza 75%+ y filtros de seguridad."""
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        price = analysis['current_price']
        rsi = analysis['indicators']['rsi']['value']
        adx = analysis['indicators']['adx']['value']
        
        # Filtros: Fuerza > 75%, Precio sobre EMA 11 pero no estirado (>1%), RSI no agotado (<65) y Tendencia (ADX > 20)
        if sig['signal'] == 'LONG' and sig['signal_strength'] >= 75:
            if ema['ema_11'] < price <= (ema['ema_11'] * 1.01):
                # REFINAMIENTO MTF: Confirmación de momentum en 1h
                h1_sqz_trend = analysis.get('multi_tf', {}).get('1h', {}).get('squeeze_trend', 'NEUTRAL')
                if rsi < 65 and adx > 20 and h1_sqz_trend == 'UP':
                    return True, "GATILLO_11"
        return False, None

    @staticmethod
    def check_order_block_pingpong(analysis):
        """Estrategia Geométrica: Rebote en bloque de órdenes verde."""
        price = analysis['current_price']
        ob = analysis['trading_levels']['order_blocks']
        rsi = analysis['indicators']['rsi']['value']
        bull_ob = ob['bullish_ob_price']
        
        # Si el precio está rebotando en el OB Bullish + RSI moderado
        if bull_ob > 0 and bull_ob * 0.990 <= price <= bull_ob * 1.005 and rsi < 45:
            # REFINAMIENTO: Ahora es obligatorio que la señal sea LONG + tendencia alcista
            if analysis['signal']['signal'] == 'LONG' and analysis['signal']['bias'] == 'BULLISH':
                return True, "BLOCK_PINGPONG"
        return False, None

    @classmethod
    def get_strategy_report(cls, analysis):
        """Genera un reporte detallado de todas las estrategias para el Analizador."""
        sig = analysis['signal']
        ema = analysis['indicators']['ema']
        rsi = analysis['indicators']['rsi']['value']
        adx = analysis['indicators']['adx']['value']
        price = analysis['current_price']
        
        multi_tf = analysis.get('multi_tf', {})
        d1_bias = multi_tf.get('1d', {}).get('bias', 'NEUTRAL')
        h1_data = multi_tf.get('1h', {})
        h1_adx = h1_data.get('adx', 0)
        h1_bias = h1_data.get('bias', 'NEUTRAL')
        h1_sqz_trend = h1_data.get('squeeze_trend', 'NEUTRAL')
        m15_momentum = multi_tf.get('15m', {}).get('momentum', 'N/A')

        # ALIEN 90
        alien_ok = (sig['signal'] == 'LONG' and sig['signal_strength'] >= 90 and 
                    'BULL' in sig.get('whale_alert', '') and price > ema['ema_55'] and
                    adx > 25 and d1_bias == 'BULLISH')
        
        # TENDENCIA CIEGA (ALIEN SIN BALLENAS + ESCUDOS)
        nad = analysis['indicators']['nadaraya']
        tendencia_ciega_ema_dist = ((price / ema['ema_55']) - 1) * 100 if ema['ema_55'] > 0 else 99
        tendencia_ciega_techo_dist = ((nad['upper'] / price) - 1) * 100 if price > 0 else 0
        tendencia_ciega_ok = (sig['signal'] == 'LONG' and sig['signal_strength'] >= 75 and 
                              d1_bias == 'BULLISH' and adx > 20 and
                              0 < tendencia_ciega_ema_dist <= 3.0 and 
                              tendencia_ciega_techo_dist >= 2.0 and 
                              rsi < 60)

        # REBOTE SUELO
        dist_nad = ((price / nad['lower']) - 1) * 100 if nad['lower'] > 0 else -99
        rebote_ok = (nad['lower'] * 0.990 <= price <= nad['lower'] * 1.002 and 
                     rsi < 35 and not (h1_adx > 40 and h1_bias == 'BEARISH'))
        
        # GATILLO 11
        ema11_dist = ((price / ema['ema_11']) - 1) * 100 if ema['ema_11'] > 0 else -99
        gatillo_ok = (sig['signal'] == 'LONG' and sig['signal_strength'] >= 75 and 
                      0 < ema11_dist <= 1.0 and rsi < 65 and adx > 20 and 
                      h1_sqz_trend == 'UP')
        
        # PING PONG
        ob = analysis['trading_levels']['order_blocks']
        bull_ob = ob['bullish_ob_price']
        ob_dist = ((price / bull_ob) - 1) * 100 if bull_ob > 0 else -99
        pingpong_ok = (bull_ob > 0 and -1.0 <= ob_dist <= 0.5 and 
                       rsi < 45 and sig['signal'] == 'LONG' and sig['bias'] == 'BULLISH')

        return {
            'alien': {'triggered': alien_ok},
            'tendencia_ciega': {'triggered': tendencia_ciega_ok},
            'rebote': {'triggered': rebote_ok},
            'gatillo': {
                'triggered': gatillo_ok,
                'warning': (not gatillo_ok and sig['signal'] == 'LONG' and sig['signal_strength'] >= 75 and 
                           0 < ema11_dist <= 1.0 and rsi < 65 and adx > 20 and 'BAJANDO' in m15_momentum)
            },
            'pingpong': {'triggered': pingpong_ok}
        }

    @classmethod
    def get_active_signals(cls, analysis):
        """Revisa todas las estrategias y devuelve las que dispararon."""
        report = cls.get_strategy_report(analysis)
        active = []
        if report['alien']['triggered']: active.append("ALIEN_90")
        if report.get('tendencia_ciega', {}).get('triggered'): active.append("TENDENCIA_CIEGA")
        if report['rebote']['triggered']: active.append("REBOTE_SUELO")
        if report['gatillo']['triggered']: active.append("GATILLO_11")
        if report['pingpong']['triggered']: active.append("BLOCK_PINGPONG")
        return active
