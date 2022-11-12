# Versiebeheer-simulator
De Versiebeheer-simulator laat zien hoe het [STOP](@@@STOP_Documentatie_Url@@@)-versiebeheer gebruikt kan worden in de keten van adviesbureaus, bevoegd gezagen, landelijke voorzieningen en hun afnemers.

De simulator is een Python script dat toegepast wordt op een set invoerbestanden. Het resultaat is een interactieve webpagina waarin getoond wordt hoe de keten met de informatie uit de bestanden om kan gaan. De simulator laat de mogelijkheden uit het STOP versiebeheer zien. Bij het implementeren van STOP kunnen de verschillende systemen voor een andere aanpak kiezen of aanvullende eisen stellen.

De huidige versie is: `@@@VERSIE@@@`.

## Versiebeheer-simulator online

Er is een [online](@@@Simulator_Online_Url@@@) versie van de Versiebeheer-simulator waar invoerbestanden geüpload of online ingetypt kunnen worden.

## Offline / eigen computer

De simulator is beschikbaar via de [repository](../). Daar staan ook de instructies om de simulator te installeren.

Bij het uitpakken van het [download.zip](../blob/master/download.zip) bestand wordt een map `mijn voorbeelden` gemaakt.

Maak in `mijn voorbeelden` een nieuw map aan (bijvoorbeeld `eerste_scenario`) en plaats daarin de invoerbestanden voor het scenario. Voor een beschrijving van de invoerbestanden zie:
- Simulatie van [bevoegd gezag software](Simulatie-van-bevoegd-gezag-software)
- Simulatie van de [LVBB](Simulatie-van-de-lvbb)
- Simulatie van een [afnemer van de LVBB](Simulatie-van-een-afnemer-van-de-lvbb)

Voer daarna de simulator uit:
- Windows:
    - Start `voer_simulator_uit_voor_mijn_voorbeelden.bat`
- MacOS/Unix:
    - Open de Terminal applicatie in de directory
    - Ga naar de directory waarin `mijn voorbeelden` staat
    - Voer `sh voer_simulator_uit_voor_mijn_voorbeelden.bat.sh` uit

Het Windows script kan ook gebruikt worden om de simulator voor een enkel voorbeeld te draaien, bijvoorbeeld::
- Open een Command Prompt
- Ga naar de directory waarin `mijn voorbeelden` staat
- Voer `voer_simulator_uit_voor_mijn_voorbeelden.bat 'mijn voorbeelden\eerste_scenario'` uit

In [Simulator uitvoeren](Simulator-uitvoeren) is beschreven hoe de simulator direct (zonder dit script) gebruikt kan worden.

Na het uitvoeren van de simulator wordt een webpagina geopend met een verslag van de simulatie(s). Daarin staan links naar de uitkomst van elke simulatie, de `Simulator_Resultaat.html` bestanden.

## Doorgronden
De uitkomst van de simulator wordt voor elke simulatie in het bestand `Simulator_Resultaat.html` in de map met invoerbestanden vastgelegd. Het is een op zichzelf staande interactieve webpagina; er zijn geen andere bestanden nodig om het resultaat te bekijken. In de pagina worden niet alleen de uitkomsten getoond, maar wordt ook uitgelegd hoe de uitkomsten berekend zijn. Tevens is er informatie over de bediening van de pagina opgenomen.

Wie de uitleg in `Simulator_Resultaat.html` niet ver genoeg gaat en in detail wil weten hoe het werkt, kan de [uitleg](Code-overzicht) van de code en de [code](../blob/master/broncode/simulator) zelf raadplegen.

