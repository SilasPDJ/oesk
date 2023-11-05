@echo off
setlocal

set "VENV_DIR=O:\HACKING\MY_PROJECTS\oesk\venv"
set "MAIN_SCRIPT=O:\HACKING\MY_PROJECTS\oesk\main.py"

set PYTHONPATH=O:\HACKING\MY_PROJECTS\oesk\backend;O:\HACKING\MY_PROJECTS\oesk\backend
REM $env:PYTHONPATH += ";O:\HACKING\MY_PROJECTS\oesk\backend"

call "%VENV_DIR%\Scripts\activate"    REM Ative o ambiente virtual
python "%MAIN_SCRIPT%"                REM Execute o arquivo main.py
pause
endlocal
