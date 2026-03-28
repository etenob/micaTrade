@echo off
title Mico Station - STOCK SCANNER
echo 🏛️ Iniciando Escaner de Bolsa (Merino Methodology)...
echo.
cd /d "%~dp0"
:start
python bot_stock_scanner.py
echo.
echo ⚠️ El bot se detuvo. Reiniciando en 5 segundos...
timeout /t 5
goto start
