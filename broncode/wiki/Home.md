# Versiebeheer-simulator
De Versiebeheer-simulator laat zien hoe het [STOP](@@@STOP_Documentatie_Url@@@)-versiebeheer gebruikt kan worden in de keten van adviesbureaus, bevoegd gezagen, landelijke voorzieningen en hun afnemers.

De simulator bestaat uit twee delen:

* Een simulator van de software die het bevoegd gezag (of een adviesbureau) gebruikt om nieuwe versies van regelgeving te maken, die via besluiten juridische betekenis te geven en het proces rondom de besluiten te begeleiden.
* Een simulator van de LVBB en eventuele andere (landelijke) voorzieningen die op basis van publicaties en revisies in staat zijn de geldende regelgeving te (re)construeren en informatie over het proces rondom besluiten kan presenteren.

Het eerste deel is een webpagina (single page javascript applicatie) die de STOP XML modules kan maken die het bevoegd gezag aan de LVBB moet leveren. Deze modules (met eventueel aanvullende beschrijving van het scenario) vormt de invoer voor het tweede deel, een Python script dat toegepast wordt op de set invoerbestanden. Het resultaat daarvan is een interactieve webpagina waarin getoond wordt hoe de landelijke voorzieningen met de informatie uit de bestanden om kan gaan.

De simulator demonstreert de mogelijkheden die het STOP versiebeheer biedt. Het laat zien dat het STOP versiebeheer vooral een technisch mechanisme is dat vooral door (de ontwikkelaars van) de software begrepen moet worden. Eindgebruikers kunnen onwetend gehouden worden van de technische details, in de zin dat alle benodigde functionaliteit te automatiseren is. De simulator is niet bedoeld om te laten zien hoe de software van bevoegd gezagen en de landelijke voorzieningen daadwerkelijk gaat functioneren. Bij het implementeren van STOP in de software kunnen leveranciers en eindgebruikers voor een geheel andere aanpak kiezen.

De huidige versie is: `@@@VERSIE@@@`.

## Versiebeheer-simulator online

Er is een [online](@@@Simulator_Online_Url@@@) versie van de Versiebeheer-simulator waar invoerbestanden geüpload of online samengesteld kunnen worden.

## Offline / eigen computer

De simulator is beschikbaar via de [repository](../). Daar staan ook de instructies om de simulator te installeren. Een van de opties is om op de eigen computer dezelfde website te draaien die online staat. Dit is de meest eenvoudige manier om de simulator te draaien.

### Bevoegd gezag simulator
De bevoegd gezag simulator is alleen online beschikbaar of als pagina in de simulator website die lokaal gedraaid wordt. In plaats van elk scenario via de webpagina in te voeren kan ook gebruik gemaakt worden van een invoerbestand:

- Simulatie van [bevoegd gezag software](Simulatie-van-bevoegd-gezag-software)

Als een scenario via de webpagina gespecificeerd is, kan het bijbehorende invoerbestand gedownload worden voor hergebruik. Ook de invoerbestanden voor de LVBB-simulator kunnen gedownload worden.

### LVBB simulator
Bij het uitpakken van het [download.zip](../blob/master/download.zip) bestand wordt een map `mijn voorbeelden` gemaakt.

Maak in `mijn voorbeelden` een nieuw map aan (bijvoorbeeld `eerste_scenario`) en plaats daarin de invoerbestanden voor het scenario. Voor een beschrijving van de invoerbestanden zie:
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

De uitkomst van de simulator wordt voor elke simulatie in het bestand `Simulator_Resultaat.html` in de map met invoerbestanden vastgelegd. Het is een op zichzelf staande interactieve webpagina; er zijn geen andere bestanden nodig om het resultaat te bekijken. In de pagina worden niet alleen de uitkomsten getoond, maar wordt ook uitgelegd hoe de uitkomsten berekend zijn. Tevens is er informatie over de bediening van de pagina opgenomen.

Wie de uitleg in `Simulator_Resultaat.html` niet ver genoeg gaat en in detail wil weten hoe het werkt, kan de [uitleg](Code-overzicht) van de code en de [code](../blob/master/broncode/simulator) zelf raadplegen.

