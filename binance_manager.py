import os
import math
import numpy as np
import requests
import time
import hmac
import hashlib
from binance.client import Client
from binance.enums import *
from config import Config

def floor_step(value, step):
    """Redondea hacia abajo al incremento más cercano (paso)."""
    return math.floor(value / step) * step

class BinanceManager:
    def __init__(self):
        self.api_key = Config.BINANCE_API_KEY
        self.api_secret = Config.BINANCE_SECRET_KEY
        self.client = Client(self.api_key, self.api_secret)
        self._symbol_info_cache = {}

    def get_symbol_info(self, symbol):
        """Obtiene información del símbolo con caché."""
        if symbol not in self._symbol_info_cache:
            self._symbol_info_cache[symbol] = self.client.get_symbol_info(symbol)
        return self._symbol_info_cache[symbol]

    def get_symbol_balance(self, asset):
        """Obtiene el saldo disponible de un activo."""
        try:
            balance = self.client.get_asset_balance(asset=asset.replace("USDT", ""))
            return float(balance['free']) if balance else 0.0
        except Exception as e:
            print(f"❌ Error saldo {asset}: {e}")
            return 0.0

    def format_quantity(self, symbol, quantity):
        """Ajusta la cantidad a la precisión permitida por Binance."""
        info = self.get_symbol_info(symbol)
        step_size = 0.00000001
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                step_size = float(f['stepSize'])
        return floor_step(quantity, step_size)

    def place_market_buy(self, symbol, usdt_amount):
        """Compra a mercado un monto en USDT."""
        try:
            order = self.client.order_market_buy(
                symbol=symbol,
                quoteOrderQty=usdt_amount
            )
            print(f"✅ Compra Mercado Exitosa: {symbol}")
            return order
        except Exception as e:
            print(f"❌ Error Compra {symbol}: {e}")
            return None

    def place_market_sell(self, symbol, quantity):
        """Vende a mercado una cantidad específica del activo."""
        try:
            qty_str = self.format_quantity_str(symbol, quantity)
            order = self.client.order_market_sell(
                symbol=symbol,
                quantity=qty_str
            )
            print(f"✅ Venta Mercado Exitosa: {symbol} ({qty_str})")
            return order
        except Exception as e:
            print(f"❌ Error Venta {symbol}: {e}")
            return None

    def _sign_query(self, query):
        return hmac.new(self.api_secret.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()

    def place_oco_sell(self, symbol, quantity, tp_price, stop_price, limit_price):
        """Coloca una orden OCO de venta usando requests directo (más confiable)."""
        try:
            # 1. Validación de precios y redondeo adaptativo
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            # Ajustar si los precios están "del lado equivocado" del actual
            if tp_price <= current_price: 
                tp_price = current_price * 1.01
            if stop_price >= current_price:
                stop_price = current_price * 0.99
                limit_price = stop_price * 0.998
            
            # 2. Formateo final según reglas de Binance
            q_str = self.format_quantity_str(symbol, quantity)
            tp_str = self.format_price_str(symbol, tp_price)
            sp_str = self.format_price_str(symbol, stop_price)
            lp_str = self.format_price_str(symbol, limit_price)

            print(f"📡 Enviando RAW OCO {symbol}: Q:{q_str} TP:{tp_str} SL:{sp_str} LP:{lp_str}")

            self.cancel_open_orders(symbol)
            
            # 3. Construir Request Manual
            params = {
                "symbol": symbol,
                "side": "SELL",
                "quantity": q_str,
                "price": tp_str,
                "stopPrice": sp_str,
                "stopLimitPrice": lp_str,
                "stopLimitTimeInForce": "GTC",
                "timestamp": int(time.time() * 1000)
            }
            
            query = "&".join([f"{k}={v}" for k, v in params.items()])
            signature = self._sign_query(query)
            url = f"https://api.binance.com/api/v3/order/oco?{query}&signature={signature}"
            
            headers = {"X-MBX-APIKEY": self.api_key}
            response = requests.post(url, headers=headers)
            result = response.json()
            
            if "orderListId" in result:
                print(f"✅ OCO RAW establecida con éxito: ID {result['orderListId']}")
                return result
            else:
                print(f"❌ Error API OCO: {result}")
                return None
        except Exception as e:
            print(f"❌ Error crítico en OCO RAW: {e}")
            return None

    def format_quantity_str(self, symbol, quantity):
        """Formatea la cantidad según el LOT_SIZE del símbolo."""
        info = self.get_symbol_info(symbol)
        step_size = 0.0001
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                step_size = float(f['stepSize'])
        
        precision = int(round(-math.log10(step_size))) if step_size < 1 else 0
        return f"{{:0.{precision}f}}".format(floor_step(quantity, step_size))

    def format_price_str(self, symbol, price):
        """Formatea el precio según el PRICE_FILTER del símbolo."""
        info = self.get_symbol_info(symbol)
        tick_size = 0.01
        for f in info['filters']:
            if f['filterType'] == 'PRICE_FILTER':
                tick_size = float(f['tickSize'])
        
        precision = int(round(-math.log10(tick_size))) if tick_size < 1 else 0
        # Evitar ceros absolutos si el precio es muy bajo
        formatted = f"{{:0.{precision}f}}".format(round(price / tick_size) * tick_size)
        if float(formatted) == 0 and price > 0:
            # Fallback de emergencia: usar más precisión si el redondeo lo mata
            return f"{{:0.{max(precision, 8)}f}}".format(price)
        return formatted


    def cancel_open_orders(self, symbol):
        """Cancela todas las órdenes abiertas de un símbolo."""
        from binance.exceptions import BinanceAPIException
        try:
            orders = self.client.get_open_orders(symbol=symbol)
            for o in orders:
                try:
                    self.client.cancel_order(symbol=symbol, orderId=o['orderId'])
                except BinanceAPIException as e:
                    if e.code != -2011: # Ignorar solo 'Unknown order' (ya cancelada por OCO)
                        print(f"❌ Error cancelando orden {o['orderId']}: {e}")
            return True
        except Exception as e:
            print(f"❌ Error general cancelando órdenes {symbol}: {e}")
            return False

    def get_open_oco_orders(self, symbol):
        """Busca órdenes OCO abiertas."""
        try:
            orders = self.client.get_open_orders(symbol=symbol)
            # Las OCO aparecen como dos órdenes con el mismo orderListId
            return [o for o in orders if 'orderListId' in o and o['orderListId'] != -1]
        except:
            return []
