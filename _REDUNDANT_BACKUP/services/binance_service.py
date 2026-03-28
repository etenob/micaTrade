"""
Servicio para interactuar con la API de Binance
----------------------------------------------
Este módulo crea un servicio centralizado para pedir datos de Binance:
- Precios en tiempo real
- Velas (klines) para análisis técnico
- Información de mercado
- Estado del servidor

Usa cache, control de límites de peticiones y manejo de errores.
"""

import time
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException
from models.trading_analysis import MarketData
from utils.logger import binance_logger

# Usamos el logger central
logger = binance_logger


# ============================================================
# 🔹 Clase Principal: BinanceService
# ============================================================
class BinanceService:
    """
    Servicio mejorado para interactuar con la API de Binance.
    Se encarga de todas las peticiones de precios, velas y datos.
    """

    def __init__(self, api_key: str = None, secret_key: str = None):
        """
        Inicializa el servicio de Binance.

        Args:
            api_key: API key de Binance (opcional para datos públicos).
            secret_key: Secret key de Binance (opcional para datos públicos).
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.client = None
        self.base_url = "https://api.binance.com"
        self.session = self._create_session()
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms entre requests (para evitar límites)

        # Cache de precios para no abusar de la API
        self._price_cache = {}
        self._cache_timeout = 30  # 30 segundos

        # Si tenemos credenciales, intentamos iniciar cliente autenticado
        if api_key and secret_key:
            try:
                self.client = Client(api_key, secret_key)
                self.client.get_account()  # Test inicial
                logger.info("✅ Cliente Binance inicializado con credenciales")
            except Exception as e:
                logger.error(f"❌ Error inicializando cliente Binance: {e}")
                self.client = None
        else:
            logger.info("📊 Usando API pública de Binance (sin credenciales)")

        # Test conexión inicial
        if self.test_connection():
            logger.info("🌐 Conexión con Binance establecida exitosamente")
        else:
            logger.warning("⚠️ Problemas de conexión con Binance")

    # ============================================================
    # 🔹 Métodos auxiliares (internos)
    # ============================================================
    def _create_session(self) -> requests.Session:
        """Crea una sesión HTTP optimizada (con headers y reintentos)."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'JaimeMerino-TradingBot/1.0',
            'Content-Type': 'application/json'
        })
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('https://', adapter)
        return session

    def _rate_limit_check(self):
        """Controla los tiempos entre requests para no pasarnos del límite."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        self._last_request_time = time.time()

    def _is_cache_valid(self, symbol: str) -> bool:
        """Verifica si el cache aún es válido para un símbolo."""
        if symbol not in self._price_cache:
            return False
        cache_time = self._price_cache[symbol].get('timestamp', 0)
        return (time.time() - cache_time) < self._cache_timeout

    def _update_cache(self, symbol: str, price: float):
        """Actualiza el cache con el último precio."""
        self._price_cache[symbol] = {
            'price': price,
            'timestamp': time.time()
        }

    # ============================================================
    # 🔹 Métodos principales
    # ============================================================
    def get_current_price(self, symbol: str, use_cache: bool = True) -> Optional[float]:
        """
        Obtiene el precio actual de un símbolo.

        Args:
            symbol: par de trading (ej: 'BTCUSDT').
            use_cache: usar cache para evitar demasiadas peticiones.

        Returns:
            Precio como float, o None si hay error.
        """
        if use_cache and self._is_cache_valid(symbol):
            return self._price_cache[symbol]['price']

        self._rate_limit_check()

        try:
            if self.client:
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
            else:
                url = f"{self.base_url}/api/v3/ticker/price"
                response = self.session.get(url, params={'symbol': symbol}, timeout=10)
                response.raise_for_status()
                data = response.json()
                price = float(data['price'])

            self._update_cache(symbol, price)
            return price
        except Exception as e:
            logger.error(f"❌ Error obteniendo precio de {symbol}: {e}")
            return None

    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Obtiene velas (klines) de un símbolo.

        Args:
            symbol: par de trading (ej: 'BTCUSDT').
            interval: intervalo ('1m', '5m', '1h', '1d', etc.).
            limit: cantidad de velas (máx 1000).

        Returns:
            DataFrame con las velas o None si hay error.
        """
        self._rate_limit_check()

        try:
            if self.client:
                klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            else:
                url = f"{self.base_url}/api/v3/klines"
                params = {'symbol': symbol, 'interval': interval, 'limit': limit}
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                klines = response.json()

            # Convertimos a DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            return df

        except Exception as e:
            logger.error(f"❌ Error obteniendo klines de {symbol}: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test básico de conexión con Binance.
        """
        try:
            url = f"{self.base_url}/api/v3/ping"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"❌ Error de conexión con Binance: {e}")
            return False


# ============================================================
# 🔹 Instancia Global (se importa en toda la app)
# ============================================================
try:
    from enhanced_config import MerinoConfig
    binance_service = BinanceService(
        api_key=MerinoConfig.BINANCE_API_KEY,
        secret_key=MerinoConfig.BINANCE_SECRET_KEY
    )
    logger.info("🚀 BinanceService global inicializado con config")
except ImportError:
    binance_service = BinanceService()
    logger.warning("⚠️ BinanceService inicializado sin configuración (solo datos públicos)")

