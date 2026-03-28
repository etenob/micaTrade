@echo off
title 🤖 Bot Merino - Estacion Institucional
color 0A
cd /d "%~dp0"

echo.
echo  ============================================
echo   BOT MERINO - Estacion de Trading Pro
echo  ============================================
echo   Dashboard: http://127.0.0.1:5000
echo   Log:       bot_merino.log
echo  ============================================
echo.

:start
echo [%date% %time%] Iniciando bot...
python bot_merino.py

echo.
echo [%date% %time%] El bot se cerro inesperadamente.
echo Reiniciando en 10 segundos... (Ctrl+C para cancelar)
timeout /t 10
goto start
