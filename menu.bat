@echo off
REM Script de ayuda rápida para Hashiwokakero

echo ========================================
echo    HASHIWOKAKERO - Menu de Comandos
echo ========================================
echo.
echo Selecciona una opcion:
echo.
echo [1] Ejecutar el juego
echo [2] Ejecutar pruebas unitarias
echo [3] Ejecutar benchmark
echo [4] Generar reporte JSON
echo [5] Ver estructura del proyecto
echo [6] Salir
echo.
set /p opcion="Ingresa el numero de opcion: "

if "%opcion%"=="1" (
    echo.
    echo Ejecutando el juego...
    py main.py
)

if "%opcion%"=="2" (
    echo.
    echo Ejecutando pruebas unitarias...
    py tests\run_all_tests.py
    pause
)

if "%opcion%"=="3" (
    echo.
    echo Ejecutando benchmark...
    py benchmark\benchmark_solvers.py
    pause
)

if "%opcion%"=="4" (
    echo.
    echo Generando reporte JSON...
    py benchmark\generate_report.py
    pause
)

if "%opcion%"=="5" (
    echo.
    echo Estructura del proyecto:
    echo.
    tree /F /A
    pause
)

if "%opcion%"=="6" (
    exit
)

echo.
echo Opcion no valida
pause
