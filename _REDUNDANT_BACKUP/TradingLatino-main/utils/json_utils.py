"""
Utilidades para manejo de JSON y serialización
Soluciona el problema de "Object of type bool is not JSON serializable"
"""
import json
import numpy as np
from datetime import datetime
from decimal import Decimal
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Union
from utils.logger import app_logger

logger = app_logger

def make_json_serializable(obj: Any) -> Any:
    """
    Convierte recursivamente un objeto a formato JSON serializable
    
    Args:
        obj: Objeto a convertir
        
    Returns:
        Objeto JSON serializable
    """
    if obj is None:
        return None
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, bool):
        return obj  # Los bool de Python SÍ son JSON serializables
    elif isinstance(obj, (np.bool_, np.bool8)):
        return bool(obj)  # Convertir numpy bool a Python bool
    elif isinstance(obj, (np.integer, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        if np.isnan(obj) or np.isinf(obj):
            logger.warning(f"Convirtiendo NaN/Inf a None: {obj}")
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif is_dataclass(obj):
        return make_json_serializable(asdict(obj))
    elif hasattr(obj, '__dict__'):
        return make_json_serializable(obj.__dict__)
    elif hasattr(obj, 'item'):  # Numpy scalars
        return make_json_serializable(obj.item())
    else:
        # Intentar convertir a string como último recurso
        try:
            return str(obj)
        except Exception as e:
            logger.error(f"No se pudo serializar objeto {type(obj)}: {obj} - Error: {e}")
            return None

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Serializa un objeto a JSON de forma segura
    
    Args:
        obj: Objeto a serializar
        **kwargs: Argumentos adicionales para json.dumps
        
    Returns:
        String JSON o string de error
    """
    try:
        clean_obj = make_json_serializable(obj)
        return json.dumps(clean_obj, ensure_ascii=False, **kwargs)
    except Exception as e:
        logger.error(f"Error en serialización JSON: {e}")
        return json.dumps({"error": "Serialization failed", "details": str(e)})

def validate_json_serializable(obj: Any, path: str = "root") -> List[str]:
    """
    Valida que un objeto sea JSON serializable y retorna errores encontrados
    
    Args:
        obj: Objeto a validar
        path: Ruta del objeto (para debugging)
        
    Returns:
        Lista de errores encontrados
    """
    errors = []
    
    try:
        json.dumps(obj)
        return errors  # Si funciona, no hay errores
    except (TypeError, ValueError) as e:
        pass  # Continuamos con la validación detallada
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            try:
                json.dumps(value)
            except (TypeError, ValueError):
                error_msg = f"Error en {path}.{key}: {type(value).__name__} = {value}"
                errors.append(error_msg)
                
                # Recursión para objetos complejos
                if isinstance(value, (dict, list)):
                    sub_errors = validate_json_serializable(value, f"{path}.{key}")
                    errors.extend(sub_errors)
                    
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            try:
                json.dumps(value)
            except (TypeError, ValueError):
                error_msg = f"Error en {path}[{i}]: {type(value).__name__} = {value}"
                errors.append(error_msg)
                
                if isinstance(value, (dict, list)):
                    sub_errors = validate_json_serializable(value, f"{path}[{i}]")
                    errors.extend(sub_errors)
    else:
        error_msg = f"Error en {path}: {type(obj).__name__} = {obj}"
        errors.append(error_msg)
    
    return errors

def debug_json_serialization(obj: Any, name: str = "objeto") -> bool:
    """
    Debug completo de serialización JSON
    
    Args:
        obj: Objeto a debuggear
        name: Nombre del objeto para logs
        
    Returns:
        True si es serializable, False si no
    """
    logger.debug(f"🔍 Debugging serialización de {name}")
    
    # Validar errores
    errors = validate_json_serializable(obj)
    
    if errors:
        logger.error(f"❌ Errores de serialización en {name}:")
        for error in errors:
            logger.error(f"  • {error}")
        return False
    else:
        logger.debug(f"✅ {name} es JSON serializable")
        return True

def clean_analysis_dict(analysis_dict: Dict) -> Dict:
    """
    Limpia específicamente un diccionario de análisis de trading
    
    Args:
        analysis_dict: Diccionario con datos de análisis
        
    Returns:
        Diccionario limpio y serializable
    """
    logger.debug("🧹 Limpiando diccionario de análisis")
    
    cleaned = {}
    
    for key, value in analysis_dict.items():
        try:
            # Casos específicos para análisis de trading
            if key in ['price', 'change_percent', 'adx', 'ema_11', 'ema_55']:
                if isinstance(value, (np.floating, np.float32, np.float64)):
                    if np.isnan(value) or np.isinf(value):
                        logger.warning(f"Valor inválido para {key}: {value}, usando 0.0")
                        cleaned[key] = 0.0
                    else:
                        cleaned[key] = float(value)
                else:
                    cleaned[key] = float(value) if value is not None else 0.0
                    
            elif key == 'signal_strength':
                if isinstance(value, (np.integer, np.int32, np.int64)):
                    cleaned[key] = int(value)
                else:
                    cleaned[key] = int(value) if value is not None else 0
                    
            elif key in ['symbol', 'signal', 'trend_bias', 'analysis_text', 'recommendation', 'timestamp']:
                cleaned[key] = str(value) if value is not None else ""
                
            else:
                # Para otros campos, usar la función general
                cleaned[key] = make_json_serializable(value)
                
        except Exception as e:
            logger.error(f"Error limpiando campo {key}: {e}")
            cleaned[key] = None
    
    # Validar el resultado final
    if not debug_json_serialization(cleaned, f"análisis limpio"):
        logger.error("❌ El análisis limpio aún tiene errores de serialización")
    
    return cleaned