@echo off
setlocal

set "VENV_DIR=O:\HACKING\MY_PROJECTS\oesk\venv"
set "MAIN_SCRIPT=O:\HACKING\MY_PROJECTS\oesk\gissonline_csv.py"

set PYTHONPATH=O:\HACKING\MY_PROJECTS\oesk\backend
REM $env:PYTHONPATH += ";O:\HACKING\MY_PROJECTS\oesk\backend"
REM Abrindo o arquivo CSV no Bloco de Notas
echo Edite o arquivo caso necessario, salve e feche para continuar...
notepad "%PYTHONPATH%\pgdas_fiscal_oesk\data_clients_files\gissonline_csv.csv"

REM Executa script
echo Executa script GISS ONLINE
call "%VENV_DIR%\Scripts\activate"    REM Ative o ambiente virtual
python "%MAIN_SCRIPT%"                REM Execute o arquivo main.py
pause
endlocal
