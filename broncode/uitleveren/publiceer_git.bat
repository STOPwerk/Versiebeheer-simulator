@echo off
rem Origineel is: templates\broncode\uitleveren\publiceer_git.bat

if "A%1" == "ARelease" goto Start
echo.
echo Dit script wordt gedraaid vanuit publiceer.bat
echo.
goto Pause

:Start
echo geen git
exit /b 1
git commit -m "Release 2022-10-15 13:03:32"
git push
if errorlevel 1 goto Pause

git config user.mail "frank.robijn@koop.overheid.nl"
if errorlevel 1 goto Pause
git config user.name "STOPwerk"

git switch main
if errorlevel 1 goto Pause
git pull
if errorlevel 1 goto Pause
git merge --squash -m "Release 2022-10-15 13:03:32" development
if errorlevel 1 goto Pause
git commit -m "Release 2022-10-15 13:03:32"
if errorlevel 1 goto Pause
git push
if errorlevel 1 goto Pause

git config --unset user.mail
git config --unset user.name
git switch development

if errorlevel 0 goto End
:Pause
exit 1

:End
