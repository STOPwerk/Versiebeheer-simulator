# Consolidatie

## Over deze applicatie

De applicatie voert de geautomatiseerde consolidatie uit van regelingen en/of informatieobjecten op basis van STOP invoerbestanden. Het resultaat wordt in een webpagina getoond.

Deze applicatie is niet bedoeld als productiewaardige software, maar als demonstratie hoe de geautomatiseerde consolidatie in STOP werkt. De Python [code](code) is uitvoerig gedocumenteerd en kan dienen als inspiratie voor STOP-gebruikende software. De applicatie kan ook gebruikt worden om te verifiëren of een eigen implementatie goed werkt.

## Python moet geïnstalleerd zijn

Voor het uitvoeren van de applicatie is Python vereist. Getest is met Python 3.9.

Op Unix/iOS systemen:
- `python3` moet beschikbaar zijn vanaf de command line.
- Gebruik `start.sh` (met argumenten) om de applicatie te starten.

Op Windows systemen:
- `python.exe` moet beschikbaar zijn vanaf de command line, of in plaats daarvan:
- de `STOP_PYTHON` environment variabele de directory bevatten waar `python.exe` staat.
- Gebruik `start.bat` (met argumenten) om de applicatie te starten.

## Uitvoeren van de applicatie

Maken van een consolidatie-scenario:

- Maak een nieuwe directory
- Maak de ConsolidatieInformatie modules voor het scenario, en plaats elke module in een apart XML bestand in de directory
- Draai de applicatie: `start _directory_pad_`
- In de directory staat daarna een bestand `Applicatie_Resultaat.html` met het resultaat.
- Een verlag van het draaien van de applicatie opent in de webbrowser

In [voorbeelden](voorbeelden) staan consolidatie-scenario's en de resultaten die met deze applicatie zijn verkregen.

## Consolidatie-scenario

De invoer voor een consolidatie-scenario bestaat uit:

* Eén of meer .xml bestanden met daarin de STOP module ConsolidatieInformatie uit imop-data.xsd.
* Nul of meer .json bestanden met informatie over annotaties bij de regelingen of informatieobjecten waarvoor de consolidatie-informatie gespecificeerd is.
* Nul of één .json bestand met opties voor het uitvoeren van de geautomatiseerde consolidatie.

Een directory wordt gezien als invoer voor een consolidatie-scenario als een van deze bestanden gevonden wordt. Ook de subdirectories worden gescand op aanvullende invoerbestanden.

### .xml met ConsolidatieInformatie
In de IMOP documentatie is beschreven hoe deze module eruit moet zien. Voor de applicatie gelden de regels:
* Er mag maximaal één .xml bestand zijn per waarde van het `gemaaktOp` tijdstip.
* De datum `ontvangenOp` is gelijk aan de datum uit `gemaaktOp`.
* Als er geen datum voor `bekendOp` gegeven is, dan wordt de datum uit `gemaaktOp` gebruikt.

### .json met annotatie
Een .json bestand dat een object bevat met als een van de attributen `Annotatie` wordt gezien als de specificatie van een annotatie die ofwel door STOP gedefinieerd is, ofwel door een andere standaard of conventie. Hierbij wordt ervan uitgegaan dat de annotatie alleen wordt uitgewisseld als de inhoud van de annotatie wijzigt of als uit het versiebeheer niet duidelijk blijkt welke versie van de annotatie gebruikt moet worden.

De applicatie kan op drie manieren bepalen welke annotatieversie bij een toestand van het geconsolideerd instrument hoort. Een ervan is op basis van versiebeheerinformatie. Een annotatie die meeloopt met het versiebeheer van de juridische informatie heeft als specificatie:
```
{
    "Annotatie": "<naam>",
    "Instrument": "<workId van het isntrument waar de annotatie bijhoort>"
    "Uitwisselingen": [
        { "GemaaktOp": "<tijdstip van uitwisseling>", "Doelen": ["<identificatie van doel>"], "Beschrijving": "..." },
        { "GemaaktOp": "<tijdstip van uitwisseling>", "Doelen": ["<identificatie van doel>", ...], "Beschrijving": "..." },
        ...
    ]
}
```
Alle door STOP gedefinieerde annotaties zijn van dit type. De `GemaaktOp` datum moet overeenkomen met een van de `GemaaktOp` in de consolidatie-informatie modules voor het instrument. Als `naam` kan een willekeurige naam gebruikt worden. Voor elk instrument moeten de namen van alle annotaties uniek zijn.

De andere twee manieren vergelijken de doelen waarvoor de annotatie is opgesteld met de inwerkingtredingsdoelen van de toestanden. Voor annotaties die niet meelopen met het versiebeheer is de specificatie:
```
{
    "Annotatie": "<naam>",
    "Instrument": "<workId van het isntrument waar de annotatie bijhoort>"
    "Uitwisselingen": [
        { "UitgewisseldOp": "<tijdstip van uitwisseling>", "Doelen": ["<identificatie van doel>"], "Beschrijving": "..." },
        { "UitgewisseldOp": "<tijdstip van uitwisseling>", "Doelen": ["<identificatie van doel>", ...], "Beschrijving": "..." },
        ...
    ]
}
```
Het `UitgewisseldOp` tijdstip moet op dezelfde manier opgegeven worden als `GemaaktOp`.

Het is niet mogelijk aan te geven welke methode voor het bepalen van de annotatieversie gebruikt moet worden. De applicatie gebruikt alle methoden die voor een annotatie mogelijk zijn om het verschil tussen de methoden te laten zien.

### Opties voor het consolidatieprocess

Een .json bestand dat een object bevat met als een van de onderstaande attributen wordt gezien als de specificatie van opties voor het uitvoeren van de geautomatiseerde consolidaties:
```
{
    "Beschrijving": "... beschrijving (html) ...",
    "Uitwisselingen": [
        { "naam": "... naam ...", "gemaaktOp": "...", "beschrijving": "..." },
        ...
    ],
	"Tijdreizen": {
		"instrument": [
			{ "ontvangenOp": "...", "bekendOp": "...", "juridischWerkendOp": "...", "geldigOp": "...", "beschrijving": "..." },
			...
		],
	},
    "Procesopties": true | false,
    "Proefversies": true | false,
    "ActueleToestanden": true | false,
    "CompleteToestanden": true | false,
    "Applicatie_Resultaat": true | false
}
```
Elk van de attributen is optioneel, maar er moet tenminste één aanwezig zijn:
* `Beschrijving` is HTML die opgenomen wordt in  de webpagina met het resultaat.
* `Uitwisselingen` is een lijst met benoemde uitwisselingen. Elke uitwisseling heeft een korte naam en de `gemaaktOp` met het tijdstip van de uitwisseling, en optioneel een beschrijving. De uitwisselingen worden in `Applicatie_Resultaat.html` gebruikt om het versiebeheer na de uitwisseling te tonen. De eerstgenoemde tijdreis is de default voor de weergave van het versiebeheer. De uitwissselingen worden alleen gebruikt als `Applicatie_Resultaat` true is.
* `Tijdreizen` is een lijst met tijdreizen per instrument (work-ID van het instrument). Elke tijdreis heeft een beschrijving die in `Applicatie_Resultaat.html` wordt gebruikt, en verder datums voor alle tijdreisparameters ter identificatie. De tijdreizen worden alleen gebruikt als 'CompleteToestanden' en `Applicatie_Resultaat` true zijn.
* `Procesopties` overschrijft de default waarde voor elk van de andere attributen zoals die hieronder gegeven zijn.
* `Proefversies` (default true) geeft aan of de STOP module Proefversies voor elke uitwisseling bepaald wordt. Als voor een toestand geen passende instrumentversie gevonden kan worden, worden de proefversies gebruikt om een alternatieve weergave van de inhoud van de toestand te bepalen.
* 'ActueleToestanden' (default true) geeft aan of de STOP module ActueleToestanden voor elk instrument bepaald wordt.
* 'CompleteToestanden' (default true) geeft aan of de STOP module CompleteToestanden voor elk instrument bepaald wordt.
* 'Applicatie_Resultaat' (default true) geeft aan of de resultaatbeschrijving `Applicatie_Resultaat.html` gemaakt wordt. Deze optie is alleen toegestaan bij het uitvoeren van een test.
