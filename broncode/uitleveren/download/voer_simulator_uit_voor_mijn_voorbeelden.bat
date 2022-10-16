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
if "A%1" == "A" goto MijnVoorbeelden
python.exe simulator\applicatie.py --meldingen logs --alle %1 %2 %3 %4 %5 %6 %7 %8 %9
goto Check_Error
:MijnVoorbeelden
python.exe simulator\applicatie.py --meldingen logs --alle "mijn voorbeelden"

:Check_Error
if errorlevel 1 goto Pause
if errorlevel 0 goto End

:Pause
pause

:End
