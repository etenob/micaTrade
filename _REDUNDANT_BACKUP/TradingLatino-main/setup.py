#!/usr/bin/env python3
"""
Script de configuración e instalación para Trading Analysis App
"""
import os
import sys
import subprocess
from pathlib import Path

def create_directory_structure():
    """Crea la estructura de directorios necesaria"""
    directories = [
        'models',
        'services', 
        'utils',
        'websocket',
        'templates',
        'static/css',
        'static/js',
        'static/images',
        'logs',
        'tests'
    ]
    
    print("📁 Creando estructura de directorios...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")
        
        # Crear archivos __init__.py donde sea necesario
        if directory in ['models', 'services', 'utils', 'websocket']:
            init_file = Path(directory) / '__init__.py'
            if not init_file.exists():
                init_file.touch()

def create_env_file():
    """Crea archivo .env con configuración por defecto"""
    env_content = """# Configuración de la aplicación Trading Analysis
# Metodología Jaime Merino

# Configuración del servidor
DEBUG=True
HOST=0.0.0.0
PORT=5000
SECRET_KEY=jaime_merino_trading_2025_secret_key

# Configuración de Binance API (opcional para datos públicos)
BINANCE_API_KEY=
BINANCE_SECRET_KEY=

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=trading_app.log

# Configuración de análisis
UPDATE_INTERVAL=60

# Ambiente de desarrollo
FLASK_ENV=development
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        print("🔧 Creando archivo .env...")
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("   ✅ .env creado")
    else:
        print("   ℹ️ .env ya existe")

def install_dependencies():
    """Instala las dependencias de Python"""
    print("📦 Instalando dependencias...")
    
    try:
        # Verificar si pip está disponible
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      check=True, capture_output=True)
        
        # Instalar dependencias
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        
        print("   ✅ Dependencias instaladas correctamente")
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error instalando dependencias: {e}")
        print("   💡 Intenta instalar manualmente: pip install -r requirements.txt")
        return False
    except FileNotFoundError:
        print("   ❌ pip no encontrado")
        print("   💡 Instala Python y pip primero")
        return False
        
    return True

def create_run_script():
    """Crea script para ejecutar la aplicación"""
    
    # Script para Windows
    windows_script = """@echo off
echo 🚀 Iniciando Trading Analysis - Metodología Jaime Merino
echo.
python app.py
pause
"""
    
    # Script para Unix/Linux/Mac
    unix_script = """#!/bin/bash
echo "🚀 Iniciando Trading Analysis - Metodología Jaime Merino"
echo
python3 app.py
"""
    
    print("📝 Creando scripts de ejecución...")
    
    # Windows batch file
    with open('run.bat', 'w') as f:
        f.write(windows_script)
    print("   ✅ run.bat creado")
    
    # Unix shell script
    with open('run.sh', 'w') as f:
        f.write(unix_script)
    
    # Hacer ejecutable en Unix
    try:
        os.chmod('run.sh', 0o755)
        print("   ✅ run.sh creado")
    except:
        print("   ✅ run.sh creado (sin permisos de ejecución)")

def create_gitignore():
    """Crea archivo .gitignore"""
    gitignore_content = """# Trading Analysis App - .gitignore

# Archivos de entorno
.env
.env.local
.env.production

# Logs
logs/
*.log

# Cache de Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribución / packaging
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
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

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

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Sistema operativo
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Datos temporales
temp/
tmp/
"""
    
    gitignore_file = Path('.gitignore')
    if not gitignore_file.exists():
        print("📝 Creando .gitignore...")
        with open(gitignore_file, 'w') as f:
            f.write(gitignore_content)
        print("   ✅ .gitignore creado")
    else:
        print("   ℹ️ .gitignore ya existe")

def create_readme():
    """Crea archivo README.md"""
    readme_content = """# 🚀 Trading Analysis App
## Metodología Jaime Merino - Análisis Técnico Avanzado

### 📋 Descripción
Aplicación web de análisis técnico en tiempo real para trading de criptomonedas, implementando la metodología de Jaime Merino con indicadores técnicos avanzados.

### ✨ Características
- 📊 Análisis técnico en tiempo real
- 🎯 Señales de trading automatizadas  
- 📈 Indicadores: EMA, ADX, RSI, MACD, Bollinger Bands
- 🔄 Actualizaciones automáticas vía WebSocket
- 📱 Interfaz responsive y moderna
- 🛡️ Gestión de riesgo integrada

### 🔧 Instalación

#### Opción 1: Instalación automática
```bash
python setup.py
```

#### Opción 2: Instalación manual
```bash
# 1. Clonar o descargar el proyecto
git clone <tu-repositorio>

# 2. Instalar dependencias  
pip install -r requirements.txt

# 3. Configurar variables de entorno (opcional)
cp .env.example .env
# Editar .env con tus credenciales de Binance

# 4. Ejecutar aplicación
python app.py
```

### 🚀 Uso

#### Iniciar servidor
```bash
# Windows
run.bat

# Linux/Mac
./run.sh

# O directamente
python app.py
```

#### Acceder a la aplicación
- **Dashboard**: http://localhost:5000
- **Health Check**: http://localhost:5000/health  
- **API**: http://localhost:5000/api/symbols

### 📊 API Endpoints

- `GET /` - Dashboard principal
- `GET /health` - Estado del servidor
- `GET /api/symbols` - Símbolos soportados
- `GET /api/analysis/<symbol>` - Análisis de símbolo específico

### 🔌 WebSocket Events

#### Cliente → Servidor
- `request_analysis` - Solicitar análisis de símbolo
- `request_all_symbols` - Análisis de todos los símbolos
- `ping` - Ping de conexión

#### Servidor → Cliente  
- `analysis_update` - Actualización de análisis
- `analysis_error` - Error en análisis
- `status` - Estado del servidor
- `pong` - Respuesta a ping

### 📁 Estructura del Proyecto
```
trading_project/
├── app.py                     # Aplicación principal
├── config.py                  # Configuración
├── requirements.txt           # Dependencias
├── models/                    # Modelos de datos
│   └── trading_analysis.py    
├── services/                  # Servicios de negocio
│   ├── binance_service.py     
│   ├── analysis_service.py    
│   └── indicators.py          
├── utils/                     # Utilidades
│   ├── logger.py              
│   └── json_utils.py          
├── websocket/                 # WebSocket handlers
│   └── socket_handlers.py     
├── templates/                 # Templates HTML
│   └── index.html             
└── logs/                      # Archivos de log
```

### 🔑 Variables de entorno (.env)
```env
# Servidor
DEBUG=True
HOST=0.0.0.0  
PORT=5000

# Binance API (opcional)
BINANCE_API_KEY=tu_api_key
BINANCE_SECRET_KEY=tu_secret_key

# Configuración
UPDATE_INTERVAL=60
LOG_LEVEL=INFO
```

### 📈 Símbolos Soportados
- BTCUSDT, ETHUSDT, ADAUSDT, BNBUSDT
- SOLUSDT, XRPUSDT, DOTUSDT, LINKUSDT

### 🛠️ Desarrollo

#### Ejecutar en modo desarrollo
```bash
export FLASK_ENV=development
python app.py
```

#### Ejecutar tests (cuando estén disponibles)
```bash
python -m pytest tests/
```

### 📊 Metodología de Análisis

#### Indicadores Utilizados
- **EMA 11/55**: Medias móviles exponenciales para tendencia
- **ADX**: Fuerza de la tendencia  
- **RSI**: Momentum y sobrecompra/sobreventa
- **MACD**: Convergencia/divergencia de medias
- **Bollinger Bands**: Volatilidad y niveles

#### Señales de Trading
- **LONG**: EMA11 > EMA55 + confirmaciones técnicas
- **SHORT**: EMA11 < EMA55 + confirmaciones técnicas  
- **WAIT**: Condiciones indecisas
- **NO_SIGNAL**: Sin configuración clara

### ⚠️ Disclaimer
Esta aplicación es solo para fines educativos y de análisis. No constituye asesoría financiera. El trading conlleva riesgos significativos.

### 📞 Soporte
Para soporte técnico, consulta los logs en la carpeta `logs/` o revisa el health check del servidor.

### 📄 Licencia
Proyecto educativo - Metodología Jaime Merino
"""
    
    readme_file = Path('README.md')
    if not readme_file.exists():
        print("📝 Creando README.md...")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("   ✅ README.md creado")
    else:
        print("   ℹ️ README.md ya existe")

def main():
    """Función principal del setup"""
    print("🚀 Trading Analysis App - Setup")
    print("📈 Metodología Jaime Merino")
    print("=" * 50)
    
    try:
        # Crear estructura
        create_directory_structure()
        print()
        
        # Crear archivos de configuración
        create_env_file()
        create_gitignore()
        create_readme()
        print()
        
        # Crear scripts
        create_run_script()
        print()
        
        # Instalar dependencias
        if Path('requirements.txt').exists():
            install_dependencies()
        else:
            print("⚠️ requirements.txt no encontrado, saltando instalación de dependencias")
        
        print()
        print("✅ Setup completado exitosamente!")
        print()
        print("🎯 Próximos pasos:")
        print("   1. Edita .env con tus credenciales de Binance (opcional)")
        print("   2. Coloca tu template HTML en templates/index.html")
        print("   3. Ejecuta: python app.py")
        print("   4. Abre: http://localhost:5000")
        print()
        print("💡 Para desarrollo rápido:")
        print("   - Windows: run.bat") 
        print("   - Linux/Mac: ./run.sh")
        
    except Exception as e:
        print(f"❌ Error durante setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()