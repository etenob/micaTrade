#!/bin/bash
# ==========================================================
# run_app_streamlit.sh
# Levanta la app Streamlit usando el entorno virtual
# ==========================================================

# Ruta al proyecto
PROJECT_DIR="$HOME/TradingLatino-main"

# Activar entorno virtual
source "$PROJECT_DIR/venv/bin/activate"

# Exportar variables de entorno (.env)
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' $PROJECT_DIR/.env | xargs)
fi

# Correr Streamlit
streamlit run "$PROJECT_DIR/tests/app_scalping_streamlit.py"

