@echo off
chcp 65001 >nul
title Organismo Vivo v4.0 — Panel de Control
color 0A
cls

:MENU
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║     ORGANISMO VIVO v4.0 — Panel de Control      ║
echo  ╠══════════════════════════════════════════════════╣
echo  ║                                                  ║
echo  ║  [1] Inicializar Vault de Obsidian               ║
echo  ║  [2] Ejecutar Pipeline (texto directo)           ║
echo  ║  [3] Iniciar Watcher (monitor de carpeta)        ║
echo  ║  [4] Iniciar Servidor Webhook (para n8n)         ║
echo  ║  [5] Panel de Control Web (interfaz grafica)     ║
echo  ║  [6] Verificar Estado del Sistema                ║
echo  ║  [7] Abrir Vault en Obsidian                     ║
echo  ║  [8] Instalar Dependencias                       ║
echo  ║  [0] Salir                                       ║
echo  ║                                                  ║
echo  ╚══════════════════════════════════════════════════╝
echo.

set /p opcion="  Selecciona una opcion [0-8]: "

if "%opcion%"=="1" goto INIT
if "%opcion%"=="2" goto PIPELINE
if "%opcion%"=="3" goto WATCHER
if "%opcion%"=="4" goto SERVER
if "%opcion%"=="5" goto PANEL_WEB
if "%opcion%"=="6" goto STATUS
if "%opcion%"=="7" goto OBSIDIAN
if "%opcion%"=="8" goto DEPS
if "%opcion%"=="0" goto SALIR
echo  Opcion invalida. Intenta de nuevo.
goto MENU

:INIT
echo.
echo  Inicializando vault de Obsidian...
python main.py init
echo.
pause
goto MENU

:PIPELINE
echo.
set /p texto="  Escribe el texto a procesar: "
python main.py pipeline --input "%texto%"
echo.
pause
goto MENU

:WATCHER
echo.
echo  Iniciando monitor de carpeta...
echo  (Ctrl+C para detener)
python main.py watcher --procesar-existentes
pause
goto MENU

:SERVER
echo.
echo  Iniciando servidor webhook en puerto 5679...
echo  (Ctrl+C para detener)
python main.py server
pause
goto MENU

:PANEL_WEB
echo.
echo  Iniciando Panel de Control Web...
echo  Abriendo en http://localhost:5680
start http://localhost:5680
python panel_control.py
pause
goto MENU

:STATUS
echo.
python main.py status
echo.
pause
goto MENU

:OBSIDIAN
echo.
for /f "delims=" %%i in ('python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('VAULT_PATH', 'C:\\Users\\Public\\Robot\\Zerg'))"') do set VAULT=%%i
echo  Abriendo: %VAULT%
start "" "obsidian://open?path=%VAULT%"
goto MENU

:DEPS
echo.
echo  Instalando dependencias...
pip install flask watchdog python-dotenv numpy
echo.
echo  Dependencias instaladas.
pause
goto MENU

:SALIR
echo.
echo  Saliendo del Panel de Control.
exit /b 0
