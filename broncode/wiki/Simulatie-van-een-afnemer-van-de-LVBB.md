STOP kent drie manieren waarop een systeem dat de geconsolideerde regelgeving van LVBB betrekt eigen annotaties kan synchroniseren met de tijdreisinformatie uit de LVBB. Het gaat daarbij om informatie die niet in STOP is gedefinieerd, die net als STOP annotaties de regelgeving duiden of additionele informatie over de regelgeving bevatten en waarvan de inhoud uitsluitend afhangt van de inhoud van de regeling/informatieobject.

De drie manieren zijn:

* **[Proefversie](@@@STOP_Documentatie_Url@@@cons_xsd_Element_cons_Proefversie.html)**: de non-STOP-annotatie wordt uitgewisseld samen met de regelingversie/informatieobjectversie. Om de annotatieversie te vinden voor een regelingversie/informatieobjectversie waarbij geen annotatieversie uitgewisseld wordt, wordt de informatie uit de [proefversie](@@@STOP_Documentatie_Url@@@cons_xsd_Element_cons_Proefversie.html) gebruikt.
* **Toestand**: bij de annotatie worden de [inwerkingtredingsdoelen](@@@STOP_Documentatie_Url@@@cons_xsd_Element_cons_inwerkingtredingsdoel.html) van de toestand van de regeling/informatieobject gespecificeerd waar de annotatie voor opgesteld is. Als voor een toestand geen annotatieversie is opgegeven, dan is de annotatieversie van de voorgaande toestand nog van toepassing.
* **Doel** of wijzigingsproject: voor de annotatie wordt een enkel doel gespecificeerd dat in de [inwerkingtredingsdoelen](@@@STOP_Documentatie_Url@@@cons_xsd_Element_cons_inwerkingtredingsdoel.html) moet voorkomen van de toestand waarvoor de annotatieversie is bedoeld. Als voor een toestand geen annotatieversie is opgegeven, dan is de annotatieversie van de voorgaande toestand nog van toepassing.

Bij de synchronisatie moet ook bedacht worden of en hoe consolidatieproblemen invloed hebben op de selectie van een annotatieversie. Als de inhoud van een toestand onbekend is, dus er is geen regeling-/informatieobjectversie voor de toestand aan te wijzen, dan kan dat betekenen dat de annotatieversie ook nog niet correct is. De simulator houdt daar geen rekening mee; een annotatieversie wordt geselecteerd ongeacht de inhoud van de toestand.

De simulator voert de synchronisatie uit en laat de resultaten zien in:

Als het scenario specificaties van annotaties bevat die via proefversies gesynchroniseerd moeten worden:
* **Proefversies en annotaties**: van elke versie van de regeling/informatieobject wordt een [proefversie](@@@STOP_Documentatie_Url@@@cons_xsd_Element_cons_Proefversie.html) gemaakt waarin staat aangegeven hoe de bijbehorende versie van de annotatie gevonden kan worden. De simulator past die informatie toe om de versie van de annotatie te vinden indien dat mogelijk is.

Als het scenario annotaties bevat die op basis van inwerkingtredingsdoelen worden gesynchroniseerd::
* **Actuele toestanden en annotaties**: de informatie over actuele toestanden en annotaties wordt gecombineerd om een tijdlijn voor de annotatieversies te maken.

## Inhoud van het scenario
Het scenario moet invoerbestanden hebben om de geconsolideerde regelgeving mee op te stellen. Die worden aangevuld met één .json-bestand per annotatie.

Een non-STOP-annotatie die via proefversies gesynchroniseerd wordt, moet op dezelfde manier gespecificeerd worden als een [STOP annotatie](Simulatie-van-de-lvbb#specificatie-van-een-annotatie).

Een non-STOP-annotatie die via de inwerkingtredingsdoelen wordt gesynchroniseerd staat in een .json bestand dat een object bevat:
```
{
    "Annotatie": "<naam>",
    "Synchronisatie": "Toestand" / "Doel",
    "Instrument": "<workId van het instrument waar de annotatie bij hoort>"
    "Uitwisselingen": [
        { "UitgewisseldOp": "<tijdstip van uitwisseling>", "Doelen": ["<identificatie van doel>"], "Beschrijving": "..." },
        { "UitgewisseldOp": "<tijdstip van uitwisseling>", "Doelen": ["<identificatie van doel>", ...], "Beschrijving": "..." },
        ...
    ]
}
```
met:
* `Annotatie` is een korte naam voor de annotatie die gebruikt wordt om in de resultaatpagina de annotatie aan te duiden.
* `Synchronisatie` geeft aan op welke manier de synchronisatie uitgevoerd moet worden: door een match op de `Toestand` of op een enkel `Doel`.
* `Instrument` is het work-ID van de regeling of informatieobject waar de annotatie bij hoort. Het instrument moet terugkomen in de consolidatie-informatie modules van het scenario.
* `Uitwisselingen` is een array met uitwisselingen waarin een versie van de annotatie is meegeleverd:
    * `UitgewisseldOp` is het tijdstip van de uitwisseling.
    * `Doelen` zijn de doelen (bij `Toestand`) of het enkele doel (bij `Doel`) die gelijk moeten zijn (bij `Toestand`) of voor moet komen (bij `Doel`) in de inwerkingtredingsdoelen van de toestand waar de annotatieversie voor is opgesteld.
    * `Beschrijving` is een korte beschrijving van de inhoud van de annotatieversie of van de reden waarom de annotatieversie is uitgewisseld.

