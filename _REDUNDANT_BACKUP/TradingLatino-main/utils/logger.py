"""
Configuración de logging para la aplicación
"""
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler 
from pathlib import Path

def setup_logger(name: str, log_file: str = None, level: str = 'INFO') -> logging.Logger:
    """
    Configura y retorna un logger personalizado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger
    
    # Nivel de logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Formato personalizado
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola con colores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        # Crear directorio de logs si no existe
        log_path = Path('logs')
        log_path.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_path / log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

class ColoredFormatter(logging.Formatter):
    """Formatter con colores para la consola"""
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',    # Cian
        'INFO': '\033[32m',     # Verde
        'WARNING': '\033[33m',  # Amarillo
        'ERROR': '\033[31m',    # Rojo
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Agregar color según el nivel
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Formato con color
        record.levelname = f"{level_color}{record.levelname}{reset_color}"
        
        # Agregar emojis según el nivel
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': '📊',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        
        original_msg = record.getMessage()
        if not any(emoji in original_msg for emoji in ['🔍', '📊', '⚠️', '❌', '🚨']):
            emoji = emoji_map.get(record.levelname.replace(level_color, '').replace(reset_color, ''), '')
            record.msg = f"{emoji} {original_msg}"
        
        return super().format(record)

# Logger principal de la aplicación
app_logger = setup_logger('trading_app', 'trading_app.log')
analysis_logger = setup_logger('analysis', 'analysis.log')
websocket_logger = setup_logger('websocket', 'websocket.log')
binance_logger = setup_logger('binance', 'binance.log')