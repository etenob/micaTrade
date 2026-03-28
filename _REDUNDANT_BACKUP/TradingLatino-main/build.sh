#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "🚀 JAIME MERINO ENHANCED TRADING BOT - BUILD SCRIPT"
echo "📈 Metodología Trading Latino Avanzada"
echo "════════════════════════════════════════════════════════════════"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Iniciando build para Render...${NC}"

# Verificar Python
echo -e "${YELLOW}🐍 Verificando Python...${NC}"
python --version
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error: Python no encontrado${NC}"
    exit 1
fi

# Actualizar pip y herramientas fundamentales
echo -e "${YELLOW}📦 Actualizando herramientas fundamentales...${NC}"
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

# Verificar que setuptools esté disponible (CRÍTICO para el error que tenías)
echo -e "${YELLOW}🔍 Verificando setuptools...${NC}"
python -c "import setuptools; print(f'✅ setuptools {setuptools.__version__} disponible')"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error: setuptools no disponible${NC}"
    exit 1
fi

# Verificar requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt no encontrado${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Contenido de requirements.txt:${NC}"
head -10 requirements.txt

# Instalar dependencias
echo -e "${YELLOW}📥 Instalando dependencias...${NC}"
python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error instalando dependencias${NC}"
    exit 1
fi

# Verificar dependencias críticas
echo -e "${YELLOW}✅ Verificando dependencias críticas...${NC}"
python -c "
try:
    import flask
    import flask_socketio
    import requests
    import numpy
    import pandas
    import ta
    print('✅ Todas las dependencias críticas instaladas correctamente')
except ImportError as e:
    print(f'❌ Error importando dependencia: {e}')
    exit(1)
"

# Crear directorios necesarios
echo -e "${YELLOW}📁 Creando estructura de directorios...${NC}"
mkdir -p templates
mkdir -p static
mkdir -p logs
mkdir -p data

# Verificar archivo principal
if [ -f "enhanced_app.py" ]; then
    echo -e "${GREEN}✅ enhanced_app.py encontrado${NC}"
else
    echo -e "${RED}❌ Error: enhanced_app.py no encontrado${NC}"
    exit 1
fi

# Test básico de sintaxis
echo -e "${YELLOW}🔍 Verificando sintaxis de enhanced_app.py...${NC}"
python -m py_compile enhanced_app.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Sintaxis correcta${NC}"
else
    echo -e "${RED}❌ Error de sintaxis en enhanced_app.py${NC}"
    exit 1
fi

# Mostrar información del sistema
echo -e "${BLUE}ℹ️ Información del sistema:${NC}"
echo "Python: $(python --version)"
echo "Pip: $(pip --version)"
echo "Directorio actual: $(pwd)"
echo "Archivos disponibles: $(ls -la | grep -E '\.(py|txt|yaml)$')"

echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ BUILD COMPLETADO EXITOSAMENTE${NC}"
echo -e "${GREEN}🎯 Listo para ejecutar: python enhanced_app.py${NC}"
echo -e "${GREEN}💡 Filosofía: 'El arte de tomar dinero de otros legalmente'${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"