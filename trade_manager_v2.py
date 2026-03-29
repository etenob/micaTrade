import json
import os
from datetime import datetime

class TradeManager:
    @staticmethod
    def add_active_trade(symbol, strategy, quantity, usdt_value, entry_price, targets, stop_loss):
        """Método de conveniencia para añadir un trade con todos sus parámetros."""
        trade_data = {
            'strategy': strategy,
            'quantity': quantity,
            'usdt_value': usdt_value,
            'entry_price': entry_price,
            'targets': targets,
            'stop_loss': stop_loss,
            'last_stop': stop_loss
        }
        TradeManager.save_active_trade(symbol, trade_data)

    @staticmethod
    def _read_json(path):
        if not os.path.exists(path): return []
        try:
            with open(path, 'r') as f: return json.load(f)
        except: return []

    @staticmethod
    def _write_json(path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def save_active_trade(symbol, entry_data):
        """Guarda un trade activo (Aislamiento V2)."""
        trades = TradeManager._read_json('active_trades_v2.json')
        # Evitar duplicados
        trades = [t for t in trades if t['symbol'] != symbol]
        entry_data['symbol'] = symbol
        entry_data['detected_at'] = datetime.now().isoformat()
        trades.append(entry_data)
        TradeManager._write_json('active_trades_v2.json', trades)

    @staticmethod
    def get_active_trade(symbol):
        trades = TradeManager._read_json('active_trades_v2.json')
        for t in trades:
            if t['symbol'] == symbol: return t
        return None

    @staticmethod
    def close_trade(symbol, exit_price, reason="Exit"):
        """Cierra un trade, calcula PnL y lo mueve al historial (V2)."""
        active = TradeManager._read_json('active_trades_v2.json')
        trade_to_close = next((t for t in active if t['symbol'] == symbol), None)
        
        if trade_to_close:
            # Eliminar de activos
            new_active = [t for t in active if t['symbol'] != symbol]
            TradeManager._write_json('active_trades_v2.json', new_active)
            
            # Calcular PnL
            qty = trade_to_close['quantity']
            entry_price = trade_to_close['entry_price']
            pnl_sucio = (exit_price - entry_price) * qty
            # Comisión aprox (0.1% buy + 0.1% sell)
            comision = (entry_price * qty * 0.001) + (exit_price * qty * 0.001)
            pnl_neto = pnl_sucio - comision
            pnl_pct = (pnl_neto / (entry_price * qty)) * 100
            
            # Guardar en historial (V2)
            history = TradeManager._read_json('trade_history_v2.json')
            trade_to_close['exit_price'] = exit_price
            trade_to_close['pnl_neto'] = round(pnl_neto, 4)
            trade_to_close['pnl_pct'] = round(pnl_pct, 2)
            trade_to_close['reason'] = reason
            trade_to_close['exit_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            history.append(trade_to_close)
            TradeManager._write_json('trade_history_v2.json', history)
            return True
        return False

    @staticmethod
    def get_history():
        return TradeManager._read_json('trade_history_v2.json')

    @staticmethod
    def get_all_active():
        return TradeManager._read_json('active_trades_v2.json')

    @staticmethod
    def get_total_exposure():
        """Calcula el valor total expuesto en USDT de los trades activos."""
        trades = TradeManager.get_all_active()
        return sum(float(t.get('usdt_value', 0)) for t in trades)
