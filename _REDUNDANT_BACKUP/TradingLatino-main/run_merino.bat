@echo off
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
