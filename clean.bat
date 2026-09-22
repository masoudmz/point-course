@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Point — Clean LaTeX aux files

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