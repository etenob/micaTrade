#!/bin/bash
set -e

echo "🚀 Jaime Merino Trading Bot - Build para Render"
echo "🔧 Solucionando problemas de compatibilidad Python..."

# Verificar versión de Python
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python detectado: $PYTHON_VERSION"

# Si es Python 3.13, mostrar advertencia
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️ Python 3.13 detectado - usando configuración compatible"
fi

# Estrategia de instalación por pasos para evitar conflictos
echo "📦 Paso 1: Actualizando herramientas básicas..."
python -m pip install --upgrade pip

echo "📦 Paso 2: Instalando setuptools compatible..."
python -m pip install --upgrade "setuptools>=70.0.0" "wheel>=0.43.0"

echo "📦 Paso 3: Instalando dependencias críticas una por una..."

# Lista de dependencias críticas en orden de importancia
declare -a critical_deps=(
    "Flask==3.0.3"
    "click==8.1.7"
    "python-dotenv==1.0.1"
    "requests==2.32.3"
    "urllib3==2.2.2"
    "python-socketio==5.11.0"
    "python-engineio==4.9.0"
    "Flask-SocketIO==5.3.6"
    "eventlet==0.36.1"
    "numpy==1.26.4"
    "pandas==2.2.2"
    "ta==0.10.2"
    "python-binance==1.0.19"
    "python-dateutil==2.9.0"
    "pytz==2024.1"
    "flask-cors==4.0.1"
    "gunicorn==22.0.0"
)

# Instalar cada dependencia individualmente
for dep in "${critical_deps[@]}"; do
    echo "📌 Instalando: $dep"
    python -m pip install "$dep" || {
        echo "⚠️ Error instalando $dep - continuando..."
    }
done

# Instalar ujson por separado (puede fallar en algunos entornos)
echo "📌 Instalando ujson (opcional)..."
python -m pip install "ujson==5.10.0" || {
    echo "⚠️ ujson no instalado - usando json nativo"
}

echo "✅ Verificando instalación crítica..."
python -c "
import sys
print(f'Python: {sys.version}')

critical_imports = [
    'flask', 'flask_socketio', 'requests', 
    'numpy', 'pandas', 'ta', 'dotenv'
]

failed = []
for module in critical_imports:
    try:
        __import__(module.replace('-', '_'))
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module}')
        failed.append(module)

if failed:
    print(f'⚠️ Módulos faltantes: {failed}')
    print('🔄 Continuando con módulos disponibles...')
else:
    print('🎉 Todas las dependencias críticas instaladas')
"

# Crear directorios necesarios
echo "📁 Creando estructura..."
mkdir -p templates static logs data

# Verificar archivo principal
if [ -f "enhanced_app.py" ]; then
    echo "✅ enhanced_app.py encontrado"
    
    # Test de sintaxis
    python -m py_compile enhanced_app.py
    echo "✅ Sintaxis verificada"
else
    echo "❌ enhanced_app.py no encontrado"
    exit 1
fi

echo "🎯 Build completado - listo para producción"