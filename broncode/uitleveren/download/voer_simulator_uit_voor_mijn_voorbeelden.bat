@echo off

if "A%1" == "A" goto MijnVoorbeelden
call %~dp0simulator\voer_simulator_uit.bat --meldingen %~dp0logs %1 %2 %3 %4 %5 %6 %7
goto End
:MijnVoorbeelden
call %~dp0simulator\voer_simulator_uit.bat --meldingen %~dp0logs --alle "mijn voorbeelden"

:End
