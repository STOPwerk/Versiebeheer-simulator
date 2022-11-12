@echo off
rem Origineel is: templates\broncode\uitleveren\publiceer_git.bat

if not "A%1" == "A" goto Start
echo.
echo Dit script moet gedraaid worden vanuit publiceer.bat
echo.
goto Pause

:Start
echo on
@echo Commit naar development
git commit -a -m "Release @@@VERSIE@@@"
@if errorlevel 1 goto Pause

@echo Update wiki
python.exe ..\tools\pas_configuratie_toe.py . wiki
@if errorlevel 1 goto Pause
@cd wiki
git config user.mail "@@@STOPwerk_Github_email@@@"
@if errorlevel 1 goto Pause
git config user.name "@@@STOPwerk_Github_user@@@"
git commit -a -m "Release @@@VERSIE@@@"
@if errorlevel 1 goto Pause
@cd ..

@echo Switch naar main en update repository
git config user.mail "@@@STOPwerk_Github_email@@@"
@if errorlevel 1 goto Pause
git config user.name "@@@STOPwerk_Github_user@@@"
git switch main
@if errorlevel 1 goto Pause
git pull
@if errorlevel 1 goto Pause
git merge --strategy-option theirs --squash -m "Release @@@VERSIE@@@" development
@if errorlevel 0 goto GaVerder
Los de merge conflicten op en ga verder
pause
:GaVerder
python.exe ..\tools\pas_configuratie_toe.py . ..\..
@if errorlevel 1 goto Pause
python.exe ..\tools\pas_configuratie_toe.py . ..\broncode
@if errorlevel 1 goto Pause
rd /s /q ..\wiki
git add -A
@if errorlevel 1 goto Pause
pause
git commit -a -m "Release @@@VERSIE@@@"
@if errorlevel 1 goto Pause
git config --unset user.mail
git config --unset user.name

@echo Switch naar development
git switch development
@echo off
echo.
echo Alles staat klaar voor de release.
set /P gitpush=Push naar github (J/[N])?
if /I "%gitpush%" NEQ "J" goto End
@echo Push naar deze repo en naar wiki-repo
git push --all
@if errorlevel 1 goto Pause
@cd wiki
git push --all
@if errorlevel 1 goto Pause
@cd ..

if errorlevel 0 goto End
:Pause
@echo off
exit /b 1

:End
