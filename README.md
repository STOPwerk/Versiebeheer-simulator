# Versiebeheer-simulator

Huidige versie: `2023-07-24 19:57:20`.

## Wat is het?
Simulator die laat zien hoe het [STOP](https://koop.gitlab.io/STOP/voorinzage/standaard-preview-b/)-versiebeheer gebruikt kan worden in de keten van adviesbureaus, bevoegd gezagen, landelijke voorzieningen en hun afnemers.

De simulator is een Python script dat toegepast wordt op een set invoerbestanden. Het resultaat is een interactieve webpagina waarin getoond wordt hoe de keten met de informatie uit de bestanden om kan gaan. De simulator laat de mogelijkheden uit het STOP versiebeheer zien. Bij het implementeren van STOP kunnen de verschillende systemen voor een andere aanpak kiezen of aanvullende eisen stellen.

## Hoe gebruik ik het?

### Online

- Ga naar de [Versiebeheer-simulator online](https://versiebeheer-simulator.vercel.app/)

### Offline / eigen computer
- Zorg dat Python geïnstalleerd is. Dat is op Unix en MacOS meestal het geval. Voor Windows kan de laatste versie van Python [hier](https://www.python.org/downloads/) gedownload worden.

- [Download](download.zip) de simulator en pak het zip bestand uit.

Nu is er de keuze hoe verder te gaan. Om de [online versie](https://versiebeheer-simulator.vercel.app/) lokaal te draaien:

- Voer `start_webserver` uit om de webserver te starten. De online versie is daarna beschikbaar via [http://localhost:5555/](http://localhost:5555/).

De script kunnen ook op voorbeeldbestanden toegepast worden:

- Lees de [documentatie](../../wiki) waarin staat hoe de invoerbestanden gemaakt moeten worden.

- Maak eigen voorbeelden in de `mijn voorbeelden` map en voer `voer_simulator_uit_voor_mijn_voorbeelden` uit om de resultaat-webpagina te maken.

- Bekijk de [voorbeelden](broncode/simulator/voorbeelden) om inspiratie op te doen. De simulator is ook gebruikt voor een deel van de [STOP voorbeelden](https://gitlab.com/koop/STOP/voorinzage/standaard-preview-b/-/tree/master/voorbeelden).

