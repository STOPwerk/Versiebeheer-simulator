# Testscenario's

## Drie soorten scenario's
Deze map bevat specificaties voor scenario's die dienen als testscenario. Er zijn drie soorten scenario's:

1. In `STOP`: scenario's afkomstig uit de STOP voorbeelden.
1. In `Versiebeheer.Simulator`: scenario's afkomstig uit de [voorbeelden](../../voorbeelden) van de simulator.
1. In de andere mappen: scenario's om specifieke onderdelen van de simulator te testen.

In de eerste twee mappen worden kopiën van voorbeelden opgenomen die daarna als acceptatietest kunnen dienen. In principe hoort een wijziging in de code van de simulator geen ander resultaat voor de voorbeelden op te leveren.

## Overnemen van voorbeelden
Voor het overnemen van STOP voorbeelden is de aanname dat de kloon van de Versiebeheer-simulator repository waar dit bestand deel van uitmaakt in een map staat met als naam *pad*`/`*repository_map_naam*
* Maak een kloon van STOP in *pad*`/Versiebeheer-simulator-STOP-voorbeelden`
* Selecteer de juiste branch en haal de laatste wijzigingen op.
* Voer `kopieer_STOP_voorbeelden.bat` uit.
* Voer de simulator uit via het `voer_alle_testen_uit.bat`/`voer_alle_testen_uit.sh` script.
* Controleer dat de uitkomst van de overgenomen testscenario's correct is. Hernoem (indien nodig) de `Test_*_actueel.json` bestanden naar `Test_*_verwacht.json`
* Commit/push de resultaten

Voor het overnemen van voorbeelden voor de simulator:
* Voer `kopieer_voorbeelden.bat` uit.
* Voer de simulator uit via het `voer_alle_testen_uit.bat`/`voer_alle_testen_uit.sh` script.
* Controleer dat de uitkomst van de overgenomen testscenario's correct is. Hernoem (indien nodig) de `Test_*_actueel.json` bestanden naar `Test_*_verwacht.json`
* Commit/push de resultaten

Bij het overnemen van de scenario's wordt [tools/voorbeelden_naar_unittests.py](../../tools/voorbeelden_naar_unittests.py) gebruikt. Dat script kopieert alleen nieuwe en bestaande bestanden, maar verwijdert geen bestanden. Als dat wel nodig is, moet dat met de hand gebeuren.

## Inhoud van een testscenario

Een testscenario bestaat uit dezelfde bestanden als een gewoon scenario, aangevuld met:

* `Test_*_actueel.json` bestanden met een dump van het interne datamodel van de simulator, gemaakt worden door de simulator.
* Optioneel: een `Test_*_verwacht.json` bestand voor iedere `Test_*_actueel.json` met daarin de verwachte inhoud van het interne datamodel van de simulator.
* Optioneel: instructies voor het uitvoeren van de simulatie als onderdeel van de beschrijving van het scenario.

Een test slaagt als de inhoud van alle `Test_*_actueel.json` bestanden overeenkomt met de `Test_*_verwacht.json` bestanden.

De beschrijving van het scenario kan uitgebreid worden met extra opties:
```
{
    "Beschrijving": "... als gewoon scenario ...",
    "Uitwisselingen": [
        ... als gewoon scenario ...
    ],
    "Tijdreizen": {
        ... als gewoon scenario ...
    },
    "Procesopties": true | false,
    "ActueleToestanden": true | false,
    "CompleteToestanden": true | false,
    "Applicatie_Resultaat": true | false
}
```
* `Procesopties` overschrijft de default waarde voor elk van de andere attributen zoals die hieronder gegeven zijn.
* 'ActueleToestanden' (default true) geeft aan of de STOP module ActueleToestanden voor elk instrument bepaald wordt.
* 'CompleteToestanden' (default true) geeft aan of de STOP module CompleteToestanden voor elk instrument bepaald wordt.
* 'Applicatie_Resultaat' (default true) geeft aan of de resultaatbeschrijving `Simulator_Resultaat.html` gemaakt wordt.

## Uitvoeren van de simulator voor testscenario's

De simulator gaat scenario's zien als testscenratio's als het command line argument `--testen` of `-t` meegegeven wordt. De overige argumenten zijn gelijk aan die voor een gewone uitvoering van de simulator.
