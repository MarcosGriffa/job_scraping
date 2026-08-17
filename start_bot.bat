@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
cd /d C:\projects\job_scraping
echo [startup] Esperando red (20s)... >> data\bot.log
timeout /t 20 /nobreak > nul
echo [startup] Arrancando bot... >> data\bot.log
venv\Scripts\python.exe -u bot_listener.py >> data\bot.log 2>&1
