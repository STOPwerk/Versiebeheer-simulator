# Uitleveren

## Voorbereiding

- Werk de bestanden in [download](download) bij indien nodig. Gebruik geen subdirectories. Bij de release worden deze bestanden samen met een lege `mijn voorbeelden` directory en de simulator in [download.zip](../../download.zip) gezet.

- Werk de bestanden in [templates](templates) bij indien nodig. Deze worden naar de [root](../../) van de repository gekopieerd. Hierin worden vervangen:
    - @@@VERSIE@@@ door de versie van de release
    - @@@STOP_Documentatie_Url@@@ door de URL van de STOP documentatie van de juiste versie van STOP
    - @@@STOP_Voorbeelden_Url@@@ door de URL van de STOP voorbeelden van de juiste versie van STOP

- Werk [configuratie.json](configuratie.json) bij indien nodig.

- Commit alle wijzigingen naar de _development_ branch. Als dit niet gedaan wordt, dan worden alle nog niet gecommitte wijzigingen meegenomen in de commit van de release.

- Selecteer de _development_ branch als de huidige branch.

## Uitvoering

- Start `publiceer.bat`
- Nadat alle git commando's zijn uitgevoerd wordt gevraagd of `git push` gedaan moet worden. Als dat niet gedaan wordt, dan moet de push later handmatig uitgevoerd worden.

Wat het `publiceer.bat` script doet:

- Past bestanden op de huidige (_development_) branch aan:
    - Gebruikt de [templates](templates) om bestanden in deze branch aan te passen
    - Maakt een versie van [applicatie_configuratie.py](../simulator/applicatie_configuratie.py) met gegevens uit de [configuratie.json](configuratie.json) en het versienummer van de release.
    - Overschrijft het [download.zip](../../download.zip) bestand
- Commit de wijzigingen naar de huidige branch
- Switcht naar de _main_ branch en voert een pull uit
- Merget de inhoud van de _development_ branch in _main_
- Commit de wijzigingen naar _main_ onder het `STOPwerk` account
- Switcht naar de _development_ branch
- Vraagt of alles gepusht mag worden, en doet dat bij een positief antwoord
