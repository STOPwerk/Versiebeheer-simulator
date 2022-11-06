@echo off
rem Origineel is: templates\broncode\uitleveren\publiceer_git.bat

if not "A%1" == "A" goto Start
echo.
echo Dit script moet gedraaid worden vanuit publiceer.bat
echo.
goto Pause

:Start
echo on
git commit -a -m "Release @@@VERSIE@@@"
@if errorlevel 1 goto Pause
git config user.mail "frank.robijn@koop.overheid.nl"
@if errorlevel 1 goto Pause
git config user.name "STOPwerk"
git switch main
@if errorlevel 1 goto Pause
git pull
@if errorlevel 1 goto Pause
git merge --strategy-option theirs --squash -m "Release @@@VERSIE@@@" development
@if errorlevel 1 goto Pause
copy /b/v/y applicatie_configuratie.py %1applicatie_configuratie.py
@if errorlevel 1 goto Pause
git add -u applicatie_configuratie.py
@if errorlevel 1 goto Pause
pause
git commit -a -m "Release @@@VERSIE@@@"
@if errorlevel 1 goto Pause
git config --unset user.mail
git config --unset user.name
git switch development
@echo off
echo.
echo Alles staat klaar voor de release.
set /P gitpush=Push naar github (J/[N])?
if /I "%gitpush%" NEQ "J" goto End
git push --all
@if errorlevel 1 goto Pause

if errorlevel 0 goto End
:Pause
@echo off
exit /b 1

:End
