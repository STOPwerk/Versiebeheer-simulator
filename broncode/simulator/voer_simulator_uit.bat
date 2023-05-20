@echo off

if exist "%~dp0venv\Scripts\activate.bat" goto StartVenv

if "A%STOP_PYTHON%" == "A" goto Check_Path
if not exist "%STOP_PYTHON%\python.exe" goto Check_Path
set PATH=%STOP_PYTHON%;%PATH%
goto Installatie

:Check_Path
where /q python.exe
if errorlevel 1 goto Not_Found
goto Installatie

:Not_Found
echo.
echo Kan python.exe niet vinden!
echo.
echo Zorg dat python.exe op het PATH staat
echo of zet de map waarin python.exe staat in de environment variabele STOP_PYTHON
echo.
goto Pause

:Installatie
python.exe -m venv "%~dp0venv"
call "%~dp0venv\Scripts\activate.bat"
python.exe -m pip install --upgrade pip
python.exe -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto Pauze
goto Start

:StartVenv
call "%~dp0venv\Scripts\activate.bat"

:Start
python.exe "%~dp0applicatie.py" %1 %2 %3 %4 %5 %6 %7 %8 %9
if errorlevel 1 goto Pause
if errorlevel 0 goto End

:Pause
pause
:End
