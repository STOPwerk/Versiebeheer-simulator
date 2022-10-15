@echo off
rem Origineel is: templates\broncode\uitleveren\publiceer_git.bat

if "A%1" == "ARelease" goto Start
echo.
echo Dit script wordt gedraaid vanuit publiceer.bat
echo.
goto Pause

:Start
echo on
git commit -a -m "Release @@@VERSIE@@@"
if errorlevel 1 goto Pause

git config user.mail "frank.robijn@koop.overheid.nl"
if errorlevel 1 goto Pause
git config user.name "STOPwerk"

git switch main
if errorlevel 1 goto Pause
git pull
if errorlevel 1 goto Pause
git merge --squash -m "Release @@@VERSIE@@@" development
if errorlevel 1 goto Pause
git commit -a -m "Release @@@VERSIE@@@"
if errorlevel 1 goto Pause
rem git push --all
if errorlevel 1 goto Pause

git config --unset user.mail
git config --unset user.name
git switch development

if errorlevel 0 goto End
:Pause
exit /b 1

:End
