@echo off
title 🤖 Bot Multi-Estrategia PRO
color 0B
cd /d "%~dp0"

echo.
echo  ============================================
echo   BOT MULTI-ESTRATEGIA - Trading Avanzado
echo  ============================================
echo   1. ALIEN 👽 (Conservador)
echo   2. REBOTE 🟢 (Agresivo)
echo   3. GATILLO ⚡ (Moderado)
echo   4. PING-PONG 🏓 (Bloques)
echo  --------------------------------------------
echo   Dashboard: http://127.0.0.1:5000
echo   Log:       bot_multi.log
echo  ============================================
echo.

:start
echo [%date% %time%] Iniciando multi-bot...
python bot_multi_strategy.py

echo.
echo [%date% %time%] El bot se detuvo. Reiniciando en 10s...
timeout /t 10
goto start
