#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║                 🚀 JAIME MERINO TRADING BOT 🚀                   ║
║              📈 Metodología Trading Latino Avanzada 📈           ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${PURPLE}💡 Filosofía: "El arte de tomar dinero de otros legalmente"${NC}"
echo -e "${YELLOW}🎯 Disciplina: "Es mejor perder una oportunidad que perder dinero"${NC}"
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
