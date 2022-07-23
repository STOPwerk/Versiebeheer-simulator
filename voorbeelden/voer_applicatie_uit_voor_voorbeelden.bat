@echo off

if "A%STOP_PYTHON%" == "A" goto Check_Path
if not exist "%STOP_PYTHON%\python.exe" goto Check_Path
set PATH=%STOP_PYTHON%;%PATH%
goto Start

:Check_Path
where /q python.exe
if errorlevel 1 goto Not_Found
goto Start

:Not_Found
echo.
echo Kan python.exe niet vinden!
echo.
echo Zorg dat python.exe op het PATH staat
echo of zet de map waarin python.exe staat in de environment variabele STOP_PYTHON
echo.
goto Pause

:Start
python.exe ..\simulator\applicatie.py --meldingen logs --alle .
if errorlevel 1 goto Pause
if errorlevel 0 goto End

:Pause
pause

:End