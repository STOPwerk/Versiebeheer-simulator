# Uitleveren

## Voorbereiding

- Werk de bestanden in [download](download) bij indien nodig. Gebruik geen subdirectories. Bij de release worden deze bestanden samen met een lege `mijn voorbeelden` directory en de simulator in [download.zip](../../download.zip) gezet.

- Werk [configuratie.json](configuratie.json) bij indien nodig. Dit is een dictionary die gebruikt wordt om parameters in de broncode van de simulator en in de documentatie ervan te vervangen. Hier wordt later de parameter VERSIE toegevoegd met het versienummer van de uitlevering. De parameters moeten binnen een paar `@@@` voorkomen. Dus worden vervangen:
    - `@@@VERSIE@@@` door de versie van de release
    - `@@@Simulator_Online_Url@@@` door de URL van de online simulator
    - `@@@STOP_Documentatie_Url@@@` door de URL van de STOP documentatie van de juiste versie van STOP
    - `@@@STOP_Voorbeelden_Url@@@` door de URL van de STOP voorbeelden van de juiste versie van STOP

- Commit alle wijzigingen naar de _development_ branch. Als dit niet gedaan wordt, dan worden alle nog niet gecommitte wijzigingen meegenomen in de commit van de release.

- Selecteer de _development_ branch als de huidige branch.

## Uitvoering

- Start `publiceer.bat`
- Nadat alle git commando's zijn uitgevoerd wordt gevraagd of `git push` gedaan moet worden. Als dat niet gedaan wordt, dan moet de push later handmatig uitgevoerd worden. Het gaat om zowel een push naar de _main_ branch van de simulator als naar de wiki repository

Wat het `publiceer.bat` script doet:

- Haalt de laatste versie van de wiki (documentatie) op en zet die in de `wiki` directory. Clone als de `wiki` map nog niet bestaat, pull als die er wel is.
- Past bestanden op de huidige (_development_) branch aan:
    - Werkt de VERSIE in [configuratie.json](configuratie.json) bij met het versienummer van de release.
    - Vervangt de parameters in [publiceer_git.bat](publiceer_git.bat).
    - Overschrijft het [download.zip](../../download.zip) bestand
    - Kopieert de inhoud van de [wiki](../wiki) documentatiebron en van [wiki_extra](wiki_extra) naar de `wiki` map en vervangt de parameters
- Commit de wijzigingen voor de wiki
- Commit de wijzigingen naar de huidige branch
- Switcht naar de _main_ branch en voert een pull uit
- Merget de inhoud van de _development_ branch in _main_
- Verwijdert de inhoud van de [wiki](../wiki) documentatiebron
- Commit de wijzigingen naar _main_ onder het `STOPwerk` account
- Switcht naar de _development_ branch
- Vraagt of alles gepusht mag worden, en doet dat bij een positief antwoord
