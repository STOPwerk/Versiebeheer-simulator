@echo off

rem ===== Python?
if "A%STOP_PYTHON%" == "A" goto Check_Path_python
if not exist "%STOP_PYTHON%\python.exe" goto Check_Path_python
set PATH=%STOP_PYTHON%;%PATH%
goto Check_Path_git

:Check_Path_python
where /q python.exe
if errorlevel 1 goto Not_Found_python
goto Check_Path_git

:Not_Found_python
echo.
echo Kan python.exe niet vinden!
echo.
echo Zorg dat python.exe op het PATH staat
echo of zet de map waarin python.exe staat in de environment variabele STOP_PYTHON
echo.
goto Pause

rem ===== git?
:Check_Path_git
where /q python.exe
if errorlevel 1 goto Not_Found_git
goto Start

:Not_Found_git
echo.
echo Kan git.exe niet vinden!
echo.
echo Zorg dat git.exe op het PATH staat
echo.
goto Pause

@rem ===== Script
:Start
rd /s /q wiki
git clone https://github.com/STOPwerk/Versiebeheer-simulator.wiki.git wiki
if errorlevel 1 goto Pause

python.exe ..\tools\maak_release_artefacts.py . ..\..
if errorlevel 1 goto Pause
call publiceer_git.bat ..\simulator\ || goto Pause

if errorlevel 0 goto End
:Pause
pause

:End
del /q publiceer_git.bat
