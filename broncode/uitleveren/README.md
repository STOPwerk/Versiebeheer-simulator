# Uitleveren

## Voorbereiding

- Werk de bestanden in [download](download) bij indien nodig. Gebruik geen subdirectories. Bij de release worden deze bestanden samen met een lege `mijn voorbeelden` directory en de simulator in [download.zip](../../download.zip) gezet.

- Werk de bestanden in [templates](templates) bij indien nodig. Deze worden naar de [root](../../) van de repository gekopieerd. Hierin worden vervangen:
    - @@@VERSIE@@@ door de versie van de release
    - @@@STOP_Documentatie_Url@@@ door de URL van de STOP documentatie van de juiste versie van STOP
    - @@@STOP_Voorbeelden_Url@@@ door de URL van de STOP voorbeelden van de juiste versie van STOP

- Werk [configuratie.json](configuratie.json) bij indien nodig.

- Commit en push alle wijzigingen naar de _development_ branch.

## Uitvoering

Deze repository is de ontwikkelrepository voor de versiebeheersimulator. Bij het uitleveren wordt een deel van de bestanden uit deze repository overgezet naar een publieke repository. Dat wordt gedaan met het tools\uitlevering_naar_publieke_repo.py script uit het Python project.

Ter voorbereiding:

- De aanname is dat deze kloon van de ontwikkelrepository in een map staat met als naam *pad*`/`*ontwikkelrepository_map_naam*
- Maak een kloon van de publieke repository (momenteel https://github.com/STOPwerk/Versiebeheer-simulator/) in een map met de naam *pad*`/Versiebeheer-simulator`.

Uitleveren:

- Zorg dat de kloon in *pad*`/Versiebeheer-simulator` up to date is
- Voer `publiceer.bat` uit
- Commit de wijzigingen in *pad*`/Versiebeheer-simulator`, inclusief non-versioned files.

## Uit te leveren bestanden
Het python script weet welke bestanden er voor de simulator uitgeleverd moeten worden. Als de inhoud van een map gekopieerd moet worden, dan maakt het uitleverscript de betreffende map in de publieke repository eerst leeg en kopieert er daarna de bestanden.

Het python script maakt ook een downloadbare versie van de simulator in de vorm van een zip bestand en zet die in de root van de publieke repository. Als een `download.zip` bestand in deze map gevonden wordt, dan wordt dat bestand als basis voor de downloadbare versie van de simulator gebruikt.

Daarnaast worden alle bestanden uit de `bestanden` map en submappen recursief gekopieerd, waarbij de bestanden uit de `bestanden` map in de root van de publieke repository gezet worden. Als een bestand in de publieke repository al bestaat wordt het overschreven. Eerder gekopieerde bestanden die nu niet meer in de `bestanden` map staan worden niet weggehaald.

