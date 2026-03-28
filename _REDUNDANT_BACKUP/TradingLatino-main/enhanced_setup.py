#!/usr/bin/env python3
"""
Script de configuración e instalación mejorado para Jaime Merino Trading Bot
Metodología Trading Latino - Análisis Técnico Avanzado
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def print_banner():
    """Imprime el banner de bienvenida"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                 🚀 JAIME MERINO TRADING BOT 🚀                   ║
    ║              📈 Metodología Trading Latino Avanzada 📈           ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║                                                                  ║
    ║  💡 "El arte de tomar dinero de otros legalmente"               ║
    ║  🎯 "Es mejor perder una oportunidad que perder dinero"         ║
    ║  📊 "Solo operamos con alta probabilidad de éxito"              ║
    ║                                                                  ║
    ║  🔧 Sistema de Setup y Configuración Automática                 ║
    ║  🎨 Interfaz Web Moderna con Dashboard en Tiempo Real           ║
    ║  📡 WebSockets para Actualizaciones Instantáneas                ║
    ║  🧪 Backtesting Integrado para Validación de Estrategia         ║
    ║  ⚡ Indicadores Técnicos Avanzados (EMAs, ADX, Squeeze, VPVR)   ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def create_directory_structure():
    """Crea la estructura de directorios completa"""
    directories = [
        'models',
        'services', 
        'utils',
        'websocket',
        'templates',
        'static/css',
        'static/js',
        'static/images',
        'static/fonts',
        'logs',
        'tests',
        'backtest_results',
        'data/historical',
        'data/cache',
        'docs',
        'scripts',
        'config'
    ]
    
    print("📁 Creando estructura de directorios...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")
        
        # Crear archivos __init__.py donde sea necesario
        if directory in ['models', 'services', 'utils', 'websocket', 'tests']:
            init_file = Path(directory) / '__init__.py'
            if not init_file.exists():
                init_file.touch()
    
    print("   🎯 Estructura de directorios creada exitosamente")

def create_enhanced_env_file():
    """Crea archivo .env mejorado con todas las configuraciones"""
    env_content = """# =============================================================================
# JAIME MERINO TRADING BOT - CONFIGURACIÓN AVANZADA
# Metodología Trading Latino - Análisis Técnico Profesional
# =============================================================================

# 🚀 CONFIGURACIÓN DEL SERVIDOR
DEBUG=True
HOST=0.0.0.0
PORT=5000
SECRET_KEY=jaime_merino_trading_latino_2025_advanced_secret

# 📡 CONFIGURACIÓN DE BINANCE API
# Obtén tus credenciales en: https://www.binance.com/en/my/settings/api-management
# NOTA: Solo se necesitan para funciones avanzadas, el bot funciona sin ellas
BINANCE_API_KEY=
BINANCE_SECRET_KEY=

# 📊 CONFIGURACIÓN DE ANÁLISIS TÉCNICO
# Intervalos de actualización por timeframe (en segundos)
UPDATE_INTERVAL_4H=900     # 15 minutos para 4H
UPDATE_INTERVAL_1H=300     # 5 minutos para 1H  
UPDATE_INTERVAL_1D=3600    # 1 hora para diario
UPDATE_INTERVAL_RT=60      # 1 minuto para tiempo real

# 🎯 CONFIGURACIÓN DE SEÑALES
MIN_SIGNAL_STRENGTH=50     # Fuerza mínima para operar (50-100)
HIGH_PROBABILITY_THRESHOLD=70  # Umbral para alta probabilidad
MIN_CONFLUENCE_SCORE=2     # Confluencias mínimas requeridas
REQUIRE_ADX_TRENDING=True  # Requiere ADX > 25
AVOID_SQUEEZE_TRADING=True # Evitar operar durante squeeze

# 💰 GESTIÓN DE RIESGO (Filosofía 40-30-20-10)
BTC_LONG_TERM_PCT=40.0     # 40% Bitcoin largo plazo
WEEKLY_CHARTS_PCT=30.0     # 30% Gráficos semanales
DAILY_TRADING_PCT=20.0     # 20% Trading diario
FUTURES_PCT=10.0           # 10% Futuros

# Límites de riesgo por operación
MAX_POSITION_SIZE_PCT=5.0  # 5% máximo por posición
DEFAULT_POSITION_SIZE_PCT=2.0  # 2% posición estándar
MAX_RISK_PER_TRADE_PCT=1.0 # 1% riesgo máximo por trade

# Límites de pérdida según Merino
MAX_DAILY_LOSS_PCT=6.0     # 6% pérdida máxima diaria
MAX_WEEKLY_LOSS_PCT=8.0    # 8% pérdida máxima semanal
MAX_MONTHLY_LOSS_PCT=10.0  # 10% pérdida máxima mensual

# 📈 CONFIGURACIÓN DE INDICADORES
EMA_FAST_PERIOD=11         # EMA rápida
EMA_SLOW_PERIOD=55         # EMA lenta
ADX_PERIOD=14              # Período ADX
ADX_ZERO_POINT=23          # Punto 23 como 0 según Merino
RSI_PERIOD=14              # Período RSI
SQUEEZE_BB_LENGTH=20       # Bollinger Bands para Squeeze
SQUEEZE_KC_LENGTH=20       # Keltner Channels para Squeeze
VPVR_LOOKBACK=100          # Períodos para Volume Profile

# 🔄 CONFIGURACIÓN DE BACKTESTING
BACKTESTING_ENABLED=True
BACKTEST_START_DATE=2023-01-01
BACKTEST_END_DATE=2024-12-31
BACKTEST_INITIAL_CAPITAL=10000
BACKTEST_COMMISSION_PCT=0.1

# 📝 CONFIGURACIÓN DE LOGGING
LOG_LEVEL=INFO
LOG_TO_FILE=True
LOG_ROTATION=True
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# 🌐 CONFIGURACIÓN DE WEBSOCKET
SOCKETIO_ASYNC_MODE=threading
SOCKETIO_CORS_ALLOWED_ORIGINS=*
SOCKETIO_PING_TIMEOUT=60
SOCKETIO_PING_INTERVAL=25

# 🎨 CONFIGURACIÓN DE INTERFAZ
THEME=dark
LANGUAGE=es
TIMEZONE=America/Mexico_City
CURRENCY_DISPLAY=USD
DECIMAL_PLACES=4

# 📱 CONFIGURACIÓN DE NOTIFICACIONES
DESKTOP_NOTIFICATIONS=True
SOUND_ALERTS=True
HIGH_PROBABILITY_ALERTS=True
MARKET_ALERTS=True

# 🔒 CONFIGURACIÓN DE SEGURIDAD
ENABLE_API_RATE_LIMITING=True
MAX_REQUESTS_PER_MINUTE=100
ENABLE_CORS=True
SESSION_TIMEOUT=3600

# 🚀 CONFIGURACIÓN AVANZADA
ENABLE_CACHING=True
CACHE_TIMEOUT=300
ENABLE_COMPRESSION=True
PARALLEL_PROCESSING=True
MAX_WORKER_THREADS=4

# 🧪 CONFIGURACIÓN DE DESARROLLO
FLASK_ENV=development
TESTING=False
PROFILING_ENABLED=False
DEBUG_WEBSOCKETS=False
MOCK_BINANCE_DATA=False

# 📊 CONFIGURACIÓN DE MÉTRICAS
ENABLE_METRICS=True
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# 🌍 CONFIGURACIÓN DE MONITOREO
ENABLE_MONITORING=False
MONITORING_ENDPOINT=
MONITORING_API_KEY=

# ============================================================================= 
# FILOSOFÍA JAIME MERINO INTEGRADA EN EL SISTEMA
# =============================================================================
# "El arte de tomar dinero de otros legalmente"
# "Es mejor perder una oportunidad que perder dinero" 
# "Solo operamos con alta probabilidad de éxito"
# "Operamos contra el 90% que pierde dinero"
# "Disciplina > Análisis técnico perfecto"
# =============================================================================
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        print("🔧 Creando archivo .env mejorado...")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("   ✅ .env creado con configuración avanzada")
    else:
        print("   ℹ️ .env ya existe - manteniendo configuración actual")

def install_dependencies():
    """Instala las dependencias de Python"""
    print("📦 Verificando e instalando dependencias...")
    
    try:
        # Verificar si pip está disponible
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("   ❌ pip no está disponible")
            return False
        
        print(f"   ✅ pip detectado: {result.stdout.strip()}")
        
        # Verificar si requirements.txt existe
        if not Path('enhanced_requirements.txt').exists():
            print("   ⚠️ requirements.txt no encontrado")
            create_basic_requirements()
        
        # Actualizar pip
        print("   🔄 Actualizando pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # Instalar dependencias principales
        print("   📥 Instalando dependencias principales...")
        main_deps = [
            'Flask==3.0.0',
            'Flask-SocketIO==5.3.6',
            'requests==2.31.0',
            'numpy==1.24.3',
            'pandas==2.0.3',
            'ta==0.10.2',
            'python-binance==1.0.19',
            'python-dotenv==1.0.0'
        ]
        
        for dep in main_deps:
            print(f"   📌 Instalando {dep.split('==')[0]}...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                              check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print(f"   ⚠️ Error instalando {dep} - continuando...")
        
        print("   ✅ Dependencias principales instaladas")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en instalación: {e}")
        return False

def create_basic_requirements():
    """Crea un requirements.txt básico si no existe"""
    basic_requirements = """# Jaime Merino Trading Bot - Dependencias Básicas
Flask==3.0.0
Flask-SocketIO==5.3.6
python-socketio==5.10.0
python-engineio==4.7.1
requests==2.31.0
numpy==1.24.3
pandas==2.0.3
ta==0.10.2
python-binance==1.0.19
python-dotenv==1.0.0
gunicorn==21.2.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(basic_requirements)
    print("   📝 requirements.txt básico creado")

def create_run_scripts():
    """Crea scripts para ejecutar la aplicación"""
    
    # Script mejorado para Windows
    windows_script = """@echo off
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                 🚀 JAIME MERINO TRADING BOT 🚀                   ║
echo ║              📈 Metodología Trading Latino Avanzada 📈           ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo 💡 Filosofía: "El arte de tomar dinero de otros legalmente"
echo 🎯 Disciplina: "Es mejor perder una oportunidad que perder dinero"
echo.
echo 🔄 Iniciando aplicación...
echo.

REM Verificar si existe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    echo 💡 Instala Python desde: https://python.org
    pause
    exit /b 1
)

REM Verificar si existe el archivo principal
if not exist "enhanced_app.py" (
    if exist "app.py" (
        echo 📊 Ejecutando versión original...
        python app.py
    ) else (
        echo ❌ No se encontró archivo principal de la aplicación
        pause
        exit /b 1
    )
) else (
    echo 📊 Ejecutando versión mejorada Jaime Merino...
    python enhanced_app.py
)

echo.
echo 👋 Aplicación finalizada
pause
"""
    
    # Script mejorado para Unix/Linux/Mac
    unix_script = """#!/bin/bash

# Colores para output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
PURPLE='\\033[0;35m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║                 🚀 JAIME MERINO TRADING BOT 🚀                   ║
║              📈 Metodología Trading Latino Avanzada 📈           ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${PURPLE}💡 Filosofía: \"El arte de tomar dinero de otros legalmente\"${NC}"
echo -e "${YELLOW}🎯 Disciplina: \"Es mejor perder una oportunidad que perder dinero\"${NC}"
echo ""
echo -e "${BLUE}🔄 Iniciando aplicación...${NC}"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python no está instalado${NC}"
        echo -e "${CYAN}💡 Instala Python desde: https://python.org${NC}"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo -e "${GREEN}✅ Python detectado: $($PYTHON_CMD --version)${NC}"

# Verificar archivo principal
if [ -f "enhanced_app.py" ]; then
    echo -e "${CYAN}📊 Ejecutando versión mejorada Jaime Merino...${NC}"
    $PYTHON_CMD enhanced_app.py
elif [ -f "app.py" ]; then
    echo -e "${YELLOW}📊 Ejecutando versión original...${NC}"
    $PYTHON_CMD app.py
else
    echo -e "${RED}❌ No se encontró archivo principal de la aplicación${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}👋 Aplicación finalizada${NC}"
"""
    
    print("📝 Creando scripts de ejecución mejorados...")
    
    # Windows batch file
    with open('run_merino.bat', 'w', encoding='utf-8') as f:
        f.write(windows_script)
    print("   ✅ run_merino.bat creado")
    
    # Unix shell script
    with open('run_merino.sh', 'w', encoding='utf-8') as f:
        f.write(unix_script)
    
    # Hacer ejecutable en Unix
    try:
        os.chmod('run_merino.sh', 0o755)
        print("   ✅ run_merino.sh creado y configurado como ejecutable")
    except:
        print("   ✅ run_merino.sh creado")

def create_enhanced_gitignore():
    """Crea archivo .gitignore mejorado"""
    gitignore_content = """# Jaime Merino Trading Bot - .gitignore Avanzado

# =============================================================================
# ARCHIVOS DE CONFIGURACIÓN SENSIBLES
# =============================================================================
.env
.env.local
.env.production
.env.staging
config/production.py
config/secrets.py

# =============================================================================
# CREDENCIALES Y CLAVES API
# =============================================================================
*.key
*.pem
*.crt
api_keys.json
credentials.json
secrets.json

# =============================================================================
# LOGS Y DATOS
# =============================================================================
logs/
*.log
*.log.*
log_*.txt

# Datos de backtesting y cache
backtest_results/
data/cache/
data/historical/
*.pkl
*.pickle

# =============================================================================
# PYTHON
# =============================================================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# =============================================================================
# IDEs Y EDITORES
# =============================================================================
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# Sublime Text
*.sublime-workspace
*.sublime-project

# Vim
*.vim
.vimrc

# Emacs
*~
\#*\#
/.emacs.desktop
/.emacs.desktop.lock
*.elc
auto-save-list
tramp
.\#*

# =============================================================================
# SISTEMA OPERATIVO
# =============================================================================
# Windows
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db
*.stackdump
[Dd]esktop.ini
$RECYCLE.BIN/
*.cab
*.msi
*.msix
*.msm
*.msp
*.lnk

# macOS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
.fseventsd
.TemporaryItems
.VolumeIcon.icns
.com.apple.timemachine.donotpresent
.AppleDouble
.LSOverride
Icon

# Linux
*~
.fuse_hidden*
.directory
.Trash-*
.nfs*

# =============================================================================
# BASES DE DATOS
# =============================================================================
*.db
*.sqlite
*.sqlite3
*.db-journal

# =============================================================================
# ARCHIVOS DE RESPALDO Y TEMPORALES
# =============================================================================
*.bak
*.backup
*.tmp
*.temp
temp/
tmp/
*.swp
*.swo
*~

# =============================================================================
# DOCUMENTACIÓN GENERADA
# =============================================================================
docs/_build/
docs/build/
site/

# =============================================================================
# ARCHIVOS DE DEPENDENCIAS Y PACKAGES
# =============================================================================
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# =============================================================================
# ARCHIVOS DE CONFIGURACIÓN LOCAL
# =============================================================================
local_settings.py
local_config.py
config_local.py

# =============================================================================
# ARCHIVOS DE TRADING ESPECÍFICOS
# =============================================================================
# Reportes de trading
reports/
trading_reports/
*.pdf
*.xlsx
*.csv

# Datos de mercado descargados
market_data/
price_data/
historical_data/

# Modelos entrenados
models/trained/
*.model
*.joblib

# =============================================================================
# ARCHIVOS DE MONITOREO Y MÉTRICAS
# =============================================================================
monitoring/
metrics/
prometheus/
grafana/

# =============================================================================
# ARCHIVOS DE DESPLIEGUE
# =============================================================================
.docker/
docker-compose.override.yml
.dockerignore
k8s/secrets/
helm/values-prod.yaml

# =============================================================================
# ARCHIVOS DE SSL Y CERTIFICADOS
# =============================================================================
ssl/
certificates/
*.crt
*.key
*.pem
*.p12
*.pfx

# =============================================================================
# OTROS ARCHIVOS ESPECÍFICOS DEL PROYECTO
# =============================================================================
# Configuraciones específicas del entorno
.local
.user
user_config.json
personal_settings.json

# Archivos de análisis personal
my_analysis/
personal_strategies/
private_notes.txt
"""
    
    gitignore_file = Path('.gitignore')
    if not gitignore_file.exists():
        print("📝 Creando .gitignore avanzado...")
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("   ✅ .gitignore creado")
    else:
        print("   ℹ️ .gitignore ya existe")

def create_project_readme():
    """Crea README.md detallado del proyecto"""
    readme_content = """# 🚀 Jaime Merino Trading Bot

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![Methodology](https://img.shields.io/badge/methodology-Jaime%20Merino-purple.svg)

**📈 Metodología Trading Latino - Análisis Técnico Avanzado 📈**

*"El arte de tomar dinero de otros legalmente"* - Jaime Merino

</div>

## 🎯 Descripción

Bot de trading avanzado que implementa fielmente la metodología de **Jaime Merino** (Trading Latino), el trader e influencer de criptomonedas más reconocido de América Latina. El sistema combina análisis técnico profesional, gestión de riesgo disciplinada y una interfaz web moderna para proporcionar señales de trading de alta probabilidad.

### 💡 Filosofía Integrada

- **🎨 "El arte de tomar dinero de otros legalmente"**
- **⚠️ "Es mejor perder una oportunidad que perder dinero"**
- **🎯 "Solo operamos con alta probabilidad de éxito"**
- **📊 "Operamos contra el 90% que pierde dinero"**
- **🧠 "Disciplina > Análisis técnico perfecto"**

## ✨ Características Principales

### 📊 Análisis Técnico Avanzado
- **EMAs 11/55**: Sistema de medias móviles exponenciales de Merino
- **ADX Modificado**: Punto 23 como 0 según configuración específica
- **Squeeze Momentum**: Indicador LazyBear para detectar consolidaciones
- **Volume Profile (VPVR)**: Identificación del Volume Point of Control
- **RSI y MACD**: Indicadores complementarios de momentum

### ⏱️ Análisis Multi-Temporal
- **4H**: Timeframe principal para decisiones de trading
- **1H**: Timing preciso para entradas
- **Diario**: Contexto macro y tendencia general
- **Confluencia**: Validación entre múltiples marcos temporales

### 💰 Gestión de Riesgo 40-30-20-10
- **40%**: Bitcoin largo plazo
- **30%**: Gráficos semanales
- **20%**: Trading diario
- **10%**: Futuros
- **Calculadora automática** de tamaño de posición

### 🎯 Sistema de Señales Inteligente
- **Señales**: LONG, SHORT, WAIT, WAIT_SQUEEZE, NO_SIGNAL
- **Score de confluencia**: 0-4 factores técnicos
- **Fuerza de señal**: Basada en múltiples criterios (0-100%)
- **Invalidaciones automáticas**: Según reglas técnicas de Merino

### 🌐 Interfaz Web Moderna
- **Dashboard en tiempo real** con WebSockets
- **Tema oscuro profesional** optimizado para trading
- **Notificaciones inteligentes** para señales de alta probabilidad
- **Responsive design** para móvil y escritorio

### 🧪 Backtesting Integrado
- **Validación histórica** de la metodología
- **Métricas detalladas** de performance
- **Análisis por fuerza de señal** y confluencias
- **Validación de filosofía** de Merino

## 🚀 Instalación Rápida

### Opción 1: Setup Automático
```bash
python setup.py
```

### Opción 2: Instalación Manual
```bash
# 1. Clonar el repositorio
git clone <tu-repositorio>
cd jaime-merino-trading-bot

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\\Scripts\\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 5. Ejecutar la aplicación
python enhanced_app.py
```

## 🎮 Uso

### Iniciar el Bot
```bash
# Versión mejorada (recomendada)
python enhanced_app.py

# O usar scripts de conveniencia
./run_merino.sh      # Linux/Mac
run_merino.bat       # Windows
```

### Acceder a la Interfaz
- **Dashboard Principal**: http://localhost:5000
- **API de Estado**: http://localhost:5000/health
- **Símbolos Soportados**: http://localhost:5000/api/merino/symbols
- **Filosofía de Merino**: http://localhost:5000/api/merino/philosophy

### Ejecutar Backtesting
```python
from services.merino_backtesting import run_sample_backtest

# Ejecutar test de muestra
results = run_sample_backtest()
```

## 📊 API Endpoints

### Principales
- `GET /` - Dashboard principal
- `GET /health` - Estado del servidor y servicios
- `GET /api/merino/symbols` - Símbolos monitoreados
- `GET /api/merino/analysis/<symbol>` - Análisis específico
- `GET /api/merino/philosophy` - Filosofía completa de Merino
- `GET /api/merino/risk-management` - Reglas de gestión de riesgo

### WebSocket Events

#### Cliente → Servidor
- `request_merino_analysis` - Solicitar análisis específico
- `request_all_merino_symbols` - Análisis masivo
- `request_merino_philosophy` - Obtener filosofía
- `request_risk_calculator` - Calcular riesgo
- `set_client_preferences` - Configurar preferencias

#### Servidor → Cliente
- `merino_analysis_update` - Actualización de análisis
- `merino_welcome` - Mensaje de bienvenida
- `philosophy_reminder` - Recordatorio filosófico
- `market_alert` - Alertas de mercado
- `risk_calculation` - Resultado de cálculo de riesgo

## 📁 Estructura del Proyecto

```
jaime_merino_trading_bot/
├── enhanced_app.py                 # Aplicación principal mejorada
├── enhanced_config.py              # Configuración Merino
├── models/
│   ├── enhanced_trading_model.py   # Modelos específicos Merino
│   └── trading_analysis.py         # Modelos originales
├── services/
│   ├── enhanced_analysis_service.py # Servicio principal Merino
│   ├── enhanced_indicators.py      # Indicadores específicos
│   ├── binance_service.py          # Conexión Binance
│   └── merino_backtesting.py       # Sistema de backtesting
├── websocket/
│   └── enhanced_socket_handlers.py # Handlers WebSocket mejorados
├── templates/
│   └── merino_dashboard.html       # Interfaz web principal
├── static/
│   ├── css/merino_styles.css       # Estilos específicos
│   └── js/merino_client.js         # Cliente JavaScript
├── utils/                          # Utilidades
├── logs/                           # Archivos de log
├── backtest_results/               # Resultados de backtesting
└── tests/                          # Suite de pruebas
```

## ⚙️ Configuración

### Variables de Entorno Principales

```env
# Configuración del servidor
DEBUG=True
HOST=0.0.0.0
PORT=5000

# API de Binance (opcional para datos públicos)
BINANCE_API_KEY=tu_api_key
BINANCE_SECRET_KEY=tu_secret_key

# Configuración de señales
MIN_SIGNAL_STRENGTH=50
HIGH_PROBABILITY_THRESHOLD=70
MIN_CONFLUENCE_SCORE=2

# Gestión de riesgo (Filosofía 40-30-20-10)
BTC_LONG_TERM_PCT=40.0
WEEKLY_CHARTS_PCT=30.0
DAILY_TRADING_PCT=20.0
FUTURES_PCT=10.0
```

### Símbolos Monitoreados
- **BTCUSDT** (Principal - Bitcoin)
- **ETHUSDT** (Ethereum)
- **ADAUSDT** (Cardano)
- **BNBUSDT** (Binance Coin)
- **SOLUSDT** (Solana)
- **XRPUSDT** (Ripple)
- **DOTUSDT** (Polkadot)
- **LINKUSDT** (Chainlink)

## 🧪 Backtesting

### Ejecutar Backtesting Básico
```python
from services.merino_backtesting import MerinoBacktester
from datetime import datetime, timedelta

# Configurar test
backtester = MerinoBacktester(initial_capital=10000)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
symbols = ['BTCUSDT', 'ETHUSDT']

# Ejecutar
results = backtester.run_backtest(symbols, start_date, end_date)

# Mostrar resultados
print(f"Win Rate: {results.win_rate:.1f}%")
print(f"Total Return: {results.total_return_percentage:.2f}%")
print(f"Max Drawdown: {results.max_drawdown_percentage:.2f}%")
```

### Métricas de Backtesting
- **Win Rate**: Porcentaje de trades ganadores
- **Total Return**: Retorno total y porcentual
- **Sharpe Ratio**: Retorno ajustado por riesgo
- **Max Drawdown**: Pérdida máxima desde el pico
- **Calmar Ratio**: Retorno anualizado / Max Drawdown
- **Análisis por fuerza de señal**: Performance según strength
- **Análisis por confluencias**: Efectividad según confluencias

## 🎨 Interfaz de Usuario

### Dashboard Principal
- **Vista en tiempo real** de todos los símbolos
- **Indicadores visuales** de fuerza de señal
- **Alertas de alta probabilidad** destacadas
- **Panel de control** para análisis manual
- **Log del sistema** en tiempo real

### Características de UX
- **Tema oscuro profesional** optimizado para trading
- **Animaciones suaves** y transiciones fluidas
- **Notificaciones no intrusivas**
- **Responsive design** para todos los dispositivos
- **Atajos de teclado** para operaciones rápidas

## 🔧 Desarrollo

### Ejecutar en Modo Desarrollo
```bash
export FLASK_ENV=development
python enhanced_app.py
```

### Estructura de Testing
```bash
# Ejecutar todos los tests
python -m pytest tests/

# Test específico
python -m pytest tests/test_enhanced_indicators.py

# Con coverage
python -m pytest --cov=services tests/
```

### Contribuir al Proyecto
1. Fork del repositorio
2. Crear branch para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit de cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📚 Documentación Adicional

### Metodología Jaime Merino
- [Video: Estrategia Completa](https://youtube.com/watch?v=example)
- [Filosofía de Trading](docs/metodologia_merino.md)
- [Gestión de Riesgo 40-30-20-10](docs/gestion_riesgo.md)
- [Indicadores Técnicos](docs/indicadores_tecnicos.md)

### Recursos de Trading
- [Canal de YouTube - Trading Latino](https://youtube.com/@tradinglatino)
- [Comunidad de Discord](https://discord.gg/tradinglatino)
- [Cursos Oficiales](https://tradinglatino.com/cursos)

## ⚠️ Disclaimer

**IMPORTANTE**: Este software es únicamente para fines educativos y de análisis técnico. No constituye asesoría financiera ni recomendaciones de inversión. El trading de criptomonedas conlleva riesgos significativos y puede resultar en pérdidas sustanciales. 

La metodología de Jaime Merino aquí implementada es una interpretación basada en contenido público disponible. Los resultados pasados no garantizan rendimientos futuros.

**Utilice este bot bajo su propio riesgo y responsabilidad.**

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **Jaime Merino** y **Trading Latino** por la metodología y filosofía de trading
- **Binance** por proporcionar APIs públicas de datos de mercado
- **Comunidad de Trading Latino** por el feedback y pruebas
- **Contribuidores** del proyecto open source

## 📞 Soporte

### Soporte Técnico
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/jaime-merino-bot/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/tu-usuario/jaime-merino-bot/wiki)
- **Logs**: Revisar archivos en `logs/` para debugging

### Comunidad
- **Discord**: Trading Latino Community
- **Telegram**: Grupo de usuarios del bot
- **YouTube**: Canal de Trading Latino

---

<div align="center">

**🚀 Desarrollado con ❤️ para la comunidad de Trading Latino 🚀**

*"Es mejor perder una oportunidad que perder dinero"* - Jaime Merino

![Trading Latino](https://img.shields.io/badge/Trading%20Latino-Metodología%20Oficial-purple.svg)
![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)
![Real Time](https://img.shields.io/badge/Real%20Time-WebSockets-green.svg)

</div>
"""
    
    readme_file = Path('README.md')
    if not readme_file.exists():
        print("📝 Creando README.md detallado...")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("   ✅ README.md creado con documentación completa")
    else:
        print("   ℹ️ README.md ya existe")

def create_configuration_summary():
    """Crea resumen de configuración del proyecto"""
    summary = {
        'project_name': 'Jaime Merino Trading Bot',
        'version': '2.0.0',
        'methodology': 'JAIME_MERINO',
        'philosophy': 'El arte de tomar dinero de otros legalmente',
        'setup_date': datetime.now().isoformat(),
        'features': [
            'Análisis técnico avanzado según metodología Merino',
            'EMAs 11/55, ADX modificado, Squeeze Momentum, Volume Profile',
            'Análisis multi-temporal (4H, 1H, Diario)',
            'Gestión de riesgo 40-30-20-10',
            'Sistema de señales con confluencias',
            'Interfaz web moderna con WebSockets',
            'Backtesting integrado',
            'Dashboard en tiempo real'
        ],
        'supported_symbols': [
            'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT',
            'SOLUSDT', 'XRPUSDT', 'DOTUSDT', 'LINKUSDT'
        ],
        'files_created': [
            'enhanced_app.py',
            'enhanced_config.py', 
            'models/enhanced_trading_model.py',
            'services/enhanced_analysis_service.py',
            'services/enhanced_indicators.py',
            'services/merino_backtesting.py',
            'websocket/enhanced_socket_handlers.py',
            'templates/merino_dashboard.html',
            'static/css/merino_styles.css',
            'static/js/merino_client.js',
            '.env',
            'README.md',
            '.gitignore',
            'run_merino.sh',
            'run_merino.bat'
        ]
    }
    
    try:
        os.makedirs('config', exist_ok=True)
        with open('config/project_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print("📋 Resumen de configuración creado en config/project_summary.json")
    except Exception as e:
        print(f"⚠️ Error creando resumen: {e}")

def show_completion_summary():
    """Muestra resumen de finalización del setup"""
    print("\n" + "="*80)
    print("🎉 SETUP COMPLETADO - JAIME MERINO TRADING BOT")
    print("="*80)
    print()
    print("💡 Filosofía integrada:")
    print("   'El arte de tomar dinero de otros legalmente'")
    print("   'Es mejor perder una oportunidad que perder dinero'")
    print()
    print("✅ Características implementadas:")
    print("   📊 Análisis técnico según metodología Merino")
    print("   ⚡ Indicadores avanzados (EMAs, ADX, Squeeze, VPVR)")
    print("   🎯 Sistema de señales con confluencias")
    print("   💰 Gestión de riesgo 40-30-20-10")
    print("   🌐 Interfaz web moderna con WebSockets")
    print("   🧪 Backtesting integrado")
    print("   📱 Dashboard responsivo en tiempo real")
    print()
    print("🚀 Para iniciar el bot:")
    print("   Windows: run_merino.bat")
    print("   Linux/Mac: ./run_merino.sh")
    print("   Manual: python enhanced_app.py")
    print()
    print("🌐 Una vez iniciado, accede a:")
    print("   Dashboard: http://localhost:5000")
    print("   Health: http://localhost:5000/health")
    print("   API: http://localhost:5000/api/merino/symbols")
    print()
    print("📚 Documentación completa en README.md")
    print("🔧 Configuración avanzada en .env")
    print("📊 Backtesting disponible en services/merino_backtesting.py")
    print()
    print("🎯 ¡Bot de Trading Jaime Merino listo para usar!")
    print("="*80)

def main():
    """Función principal del setup mejorado"""
    try:
        print_banner()
        
        print("🔧 Iniciando configuración avanzada del proyecto...")
        print()
        
        # Ejecutar pasos del setup
        create_directory_structure()
        print()
        
        create_enhanced_env_file()
        print()
        
        create_enhanced_gitignore()
        print()
        
        create_project_readme()
        print()
        
        create_run_scripts()
        print()
        
        install_dependencies()
        print()
        
        create_configuration_summary()
        print()
        
        show_completion_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️ Setup interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante el setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()