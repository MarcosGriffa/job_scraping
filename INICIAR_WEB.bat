@echo off
chcp 65001 > nul
title EmpatIA NextStep - Arranque

REM ============================================================
REM  INICIAR_WEB.bat - arranca TODO con doble clic.
REM
REM  Levanta las dos piezas que necesita la web:
REM    1) El motor (Python/FastAPI) en el puerto 8000
REM    2) La web (Next.js) en el puerto 3000
REM  y abre el navegador solo.
REM
REM  Cada pieza abre su propia ventana negra. Para APAGAR todo,
REM  cerra esas dos ventanas (o aprieta Ctrl+C en cada una).
REM
REM  OJO: este archivo se genera con tools/generar_bat.py y tiene que
REM  quedar en ASCII puro y con finales de linea CRLF. Ver ahi.
REM ============================================================

REM Trabajar siempre desde la carpeta donde esta este archivo,
REM sin importar desde donde se lo ejecute ni si se mueve el proyecto.
cd /d "%~dp0"

REM UTF-8 para Python: sin esto, los mensajes con flechas del motor
REM rompen la busqueda en Windows. (Bug real, ya nos paso.)
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo.
echo ============================================
echo   EmpatIA ^| NextStep - arrancando...
echo ============================================
echo.

REM ---------- Chequeos previos, con mensajes claros ----------
where python >nul 2>&1
if errorlevel 1 goto NO_PYTHON

where npm >nul 2>&1
if errorlevel 1 goto NO_NODE

if not exist ".env" goto NO_ENV

REM Dependencias de la web: la primera vez tarda unos minutos.
if not exist "web\node_modules" (
    echo [1/3] Primera vez: instalando dependencias de la web...
    echo       Esto tarda unos minutos, es normal. No cierres la ventana.
    echo.
    call npm --prefix web install
    if errorlevel 1 goto FALLO_NPM
)

REM ---------- Arranque ----------
REM Las ventanas nuevas heredan la carpeta actual y las variables de
REM entorno de arriba. OJO: no anidar comillas dentro del "cmd /k ..."
REM porque cierran la cadena y rompen el comando.
echo [2/3] Arrancando el motor de busqueda...
start "EmpatIA - MOTOR (no cerrar)" cmd /k chcp 65001 ^>nul ^&^& python -m uvicorn api.main:app --port 8000

echo [3/3] Arrancando la web...
start "EmpatIA - WEB (no cerrar)" cmd /k npm --prefix web run dev

REM Esperar a que la web responda antes de abrir el navegador, para no
REM mostrarle al usuario un error de "no se puede conectar".
echo.
echo Esperando a que este lista...
set INTENTOS=0

:ESPERAR
set /a INTENTOS=%INTENTOS%+1
timeout /t 2 /nobreak > nul
curl -s -o nul -m 2 http://localhost:3000
if not errorlevel 1 goto LISTO
if %INTENTOS% GEQ 45 goto TARDA_MUCHO
goto ESPERAR

:LISTO
echo.
echo ============================================
echo   Listo. Abriendo el navegador...
echo ============================================
start http://localhost:3000
echo.
echo Para APAGAR todo: cerra las dos ventanas negras
echo llamadas "EmpatIA - MOTOR" y "EmpatIA - WEB".
echo.
timeout /t 8 /nobreak > nul
exit /b 0

:NO_PYTHON
echo.
echo [ERROR] No encuentro Python instalado.
echo         Instalalo desde python.org y volve a intentar.
echo.
pause
exit /b 1

:NO_NODE
echo.
echo [ERROR] No encuentro Node.js instalado.
echo         Instalalo desde nodejs.org y volve a intentar.
echo.
pause
exit /b 1

:NO_ENV
echo.
echo [ERROR] Falta el archivo .env con las claves.
echo         Copia .env.example como .env y completalo.
echo.
pause
exit /b 1

:FALLO_NPM
echo.
echo [ERROR] Fallo la instalacion de dependencias de la web.
echo.
pause
exit /b 1

:TARDA_MUCHO
echo.
echo [AVISO] La web esta tardando mas de lo normal en arrancar.
echo         Fijate si alguna de las dos ventanas negras muestra un error.
echo         Si arranca, entra a mano a: http://localhost:3000
echo.
pause
exit /b 1
