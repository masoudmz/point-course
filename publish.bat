@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Point — Publish and Clean

if "%~1"=="" (
    set /p SID="Session id (e.g., S2): "
) else (
    set "SID=%~1"
)

echo.
echo === Publishing session %SID% ===
python tools/publish_lecture.py %SID%
if errorlevel 1 (
    echo.
    echo [!] Publish failed. Auxiliary files NOT cleaned.
    pause
    exit /b 1
)

echo.
echo === Cleaning auxiliary LaTeX files in lectures\ ===
set count=0
for %%E in (aux log out toc lof lot synctex.gz fls fdb_latexmk bbl blg nav snm vrb idx ilg ind) do (
    if exist "lectures\*.%%E" (
        del /q "lectures\*.%%E"
        echo   - removed *.%%E
        set /a count+=1
    )
)
echo.
echo Done. %count% extension type(s) cleaned.
pause