@echo off
setlocal

set "VENV_DIR=O:\HACKING\MY_PROJECTS\oesk\venv"
set "MAIN_SCRIPT=O:\HACKING\MY_PROJECTS\oesk\main.py"

call "%VENV_DIR%\Scripts\activate"    REM Ative o ambiente virtual
call pip install .                    REM instala dependencias
python "%MAIN_SCRIPT%"                REM Execute o arquivo main.py
pause
endlocal
