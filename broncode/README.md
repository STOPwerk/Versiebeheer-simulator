# Ontwikkeling van Versiebeheer-simulator

## Indeling
Dit is de root directory voor de ontwikkeling van de STOPwerk Versiebeheer-simulator. Hierin staat de Python code en alle testen.

De ondersteunende scripts (en deze readme) gaan ervan uit dat er twee lokale klonen zijn:

* `root-directory/Versiebeheer-simulator` is een kloon van de public repository [Versiebeheer-simulator](https://github.com/STOPwerk/Versiebeheer-simulator) met de code voor de simulator.

* `root-directory/Versiebeheer-simulator-STOP-voorbeelden` is een kloon van [STOP ontwikkeling](https://gitlab.com/koop/STOP/ontwikkeling), de private repository voor de ontwikkeling van STOP. STOP gebruikt de Versiebeheer-simulator voor een reeks voorbeelden. Die voorbeelden worden als testscenario overgenomen naar Versiebeheer-simulator-ontwikkeling als een vorm van acceptatietest.


## Werkwijze

* Gebruik dit deel van de repository om de Versiebeheer-simulator door te ontwikkelen of te onderhouden. Doe dat op de _development_ branch (of een feature branch).

* Zorg dat zowel alle code-unit tests als alle testscenario's correct uitgevoerd worden. De testscenario's zijn uit te voeren door `voer_alle_unit_tests_uit.bat` of `voer_alle_unit_tests_uit.sh` in [tests/scenarios](tests/scenarios) uit te voeren. Voor het maken van testscenario's en het uitvoeren van de applicatie: zie de [documentatie](../../../wiki).

* Als er nieuwe STOP voorbeelden zijn, ga naar `root-directory/Versiebeheer-simulator-STOP-voorbeelden` en haal met de git tooling de laatste versie op. Voer dan `kopieer_STOP_voorbeelden.bat` uit in [tests/scenarios](tests/scenarios) om de voorbeelden over te nemen als testscenario. Voer de tests uit (via `voer_alle_unit_tests_uit.bat` of `voer_alle_unit_tests_uit.sh`). Als de resultaten voor een nieuw voorbeeld correct zijn, hernoem de `*_actual.json` bestanden in de voorbeeldmap naar `*_verwacht.json`.

* Als er voor de Versiebeheer-simulator een nieuw voorbeeld is, voer dan `kopieer_voorbeelden.bat` uit in [tests/scenarios](tests/scenarios) om de voorbeelden over te nemen als testscenario. Verder gelijk aan een nieuw STOP voorbeeld.

^ Om codewijzigingen uit te leveren: ga naar [uitleveren](uitleveren) en volg de instructies in de README.md..

## Ontwikkelomgeving
De code is ontwikkeld met Python 3.9 en Visual Studio 2022 met extensies `Markdown Editor v2` en `Smart Command Line Arguments for 2022`. De .bat scripts zijn getest met Python 3.8.10, de .sh scripts met Windows 10 WSL/Ubuntu 20.04 en de meegeleverde python3.

Voor het uitvoeren van de scripts moet git en python in het PATH staan. Als dat niet zo is voor Windows, zet dan de environment variabelen:

* `STOP_PYTHON` : directory waar python.exe te vinden is

Hernoemen van grote aantallen bestanden gaat goed met [PowerRename](https://learn.microsoft.com/en-us/windows/powertoys/powerrename).
