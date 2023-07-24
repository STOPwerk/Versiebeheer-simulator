De Simulator @LVBB kan de werking van de LVBB simuleren. De invoer bestaat dan uit STOP modules die de LVBB ontvangt als onderdeel van de aanlevering van een publicatie van een besluit, rectificatie of mededeling, of van een revisie. Elke aanlevering aan de LVBB bestaat uit:

* Een enkele [ConsolidatieInformatie](@@@STOP_Documentatie_Url@@@data_xsd_Element_data_ConsolidatieInformatie.html) module. Deze is onderdeel van het scenario.
* Een besluit of revisie met daarin de tekst of mutatie van een of meer regelingen. Deze informatie wordt niet gebruikt door de simulator.
* Een of meer versies of mutaties van informatieobjecten. Deze informatie wordt niet gebruikt door de simulator.
* Annotaties, dus extra (service-)informatie over de regelingen en informatieobjecten. Bijvoorbeeld metadata van een regeling of symbolisatie van een geo-informatieobject. In de simulator hoeft een annotatie alleen aangeleverd te worden als de inhoud ervan wijzigt.

De simulator gebruikt de invoer voor de bepaling van:
* **Bekendmaken en beschikbaarstellen**: een overzicht van de publicaties die het gevolg zijn avn de uitwisselingen, en van de uitgewisselde consolidatie-informatie.

* **Verwerking van de publicatiebronnen**: Reconstructie van het versiebeheer zoals dat bij het bevoegd gezag heeft plaatsgevonden en de validatie van deze informatie.

Als het scenario informatie over de inwerkingtreding van besluiten bevat:
* [Actuele toestanden](@@@STOP_Documentatie_Url@@@cons_xsd_Element_cons_ActueleToestanden.html): het overzicht van de nu en in de toekomst geldende versies van de geconsolideerde regeling/informatieobject. In dit overzicht is ook aangegeven voor welke toestanden de consolidatie (door het bevoegd gezag) nog niet is afgerond.
* [Complete toestanden](@@@STOP_Documentatie_Url@@@cons_xsd_Element_cons_CompleteToestanden.html): het overzicht van alle versies van de geconsolideerde regeling/informatieobject, geschikt voor [tijdreizen](@@@STOP_Documentatie_Url@@@regelgeving_in_de_tijd.html) over meerdere tijdassen. De tijdassen kunnen via een **tijdreisfilter** in de resultaatpagina geselecteerd worden.
* Een visuele weergave van **tijdreizen** in bi-temporele diagrammen, op een manier die vaak door consolidatie-experts gebruikt wordt.

Als het scenario specificaties van annotaties bevat:
* **Proefversies en annotaties**: van elke versie van de regeling/informatieobject wordt een [proefversie](@@@STOP_Documentatie_Url@@@cons_xsd_Element_cons_Proefversie.html) gemaakt waarin staat aangegeven hoe de bijbehorende versie van de annotatie gevonden kan worden. De simulator past die informatie toe om de versie van de annotatie te vinden indien dat mogelijk is.

Als het scenario naast annotaties ook informatie over de inwerkingtreding van besluiten bevat:
* **Actuele toestanden en annotaties**: de informatie over actuele toestanden en annotaties wordt gecombineerd om een tijdlijn voor de annotatieversies te maken. Hiermee kunnen annotaties worden opgezocht voor een tijdreis, in plaats van een tijdreis voor de regeling/informatieobject uit te voeren en dan de annotatie (via versiebeheer/proefversies) erbij te zoeken. Er is geen manier in STOP om deze informatie te ontsluiten, het is alleen ter informatie opgenomen in het simulator resultaat.

## Inhoud van het scenario
Het scenario bestaat uit een map met invoerbestanden:

* Minimaal één bestand met een [STOP ConsolidatieInformatie](@@@STOP_Documentatie_Url@@@data_xsd_Element_data_ConsolidatieInformatie.html) module
* Optioneel: een [beschrijving](#beschrijving-van-het-scenario) van het scenario.
* Optioneel: bestanden met een [specificatie](#specificatie-van-een-annotatie) van een annotatie bij een regeling of een informatieobject.

## Beschrijving van het scenario
De beschrijving van het scenario wordt alleen gebruikt voor de weergave van de resultaten. Het maakt de resultaatpagina beter te begrijpen. Het is een .json bestand dat een object bevat:
```
{
    "Titel": "... titel ...",
    "Beschrijving": "... beschrijving (html) ...",
    "Uitwisselingen": [
        { "naam": "... naam ...", "gemaaktOp": "...", "beschrijving": "...", "revisie": true },
        ...
    ],
    "Tijdreizen": {
        "instrument": [
            { "ontvangenOp": "...", "bekendOp": "...", "juridischWerkendOp": "...", "geldigOp": "...", "beschrijving": "..." },
            ...
        ],
    }
}
```
Elk van de attributen is optioneel, maar er moet tenminste één aanwezig zijn:
* `Titel` is een tekst die opgenomen wordt in de titel en in de HTML van de pagina.
* `Beschrijving` is HTML die opgenomen wordt in  de webpagina met het resultaat.
* `Uitwisselingen` is een lijst met benoemde uitwisselingen. De uitwisselingen worden in `Applicatie_Resultaat.html` gebruikt om het versiebeheer na de uitwisseling te tonen. De eerstgenoemde uitwisseling wordt geselecteerd voor de weergave op de resultaatpagina. Elke uitwisseling heeft:
    * `naam`: een korte naam voor de uitwisseling, wordt gebruikt in de uitwisselingselector.
    * `gemaaktOp` is het tijdstip van de uitwisseling; deze moet overeenkomen met het tijdstip in een van de modules met consolidatie-informatie.
    * `beschrijving` is optioneel. Deze wordt onder andere in de uitwisselingselector getoond.
    * `revisie` is optioneel en is `false` als het weggelaten wordt. Geeft aan dat de uitwisseling geen publicatie maar een revisie betreft. Versies die via een revisie worden uitgewisseld komen niet terug in de juridische verantwoording en worden in versiebeheerdiagrammen met geel in plaats van blauw aangeduid.
* `Tijdreizen` is een lijst met tijdreizen per instrument (work-ID van het instrument). Elke tijdreis heeft:
    * `beschrijving` wordt gebruikt als toelichting bij de uitkomst van de tijdreis (= regel uit het overzicht van complete toestanden)
    * Een datum voor elke tijdreisparameter ter identificatie.

## Specificatie van een annotatie
De simulator identificeert een versie van een annotatie aan de hand van de uitwisseling waar de annotatieversie deel van uitmaakt. De simulator maakt geen gebruik van de inhoud van een annotatie. De simulator gaat ervan uit dat een versie van de annotatie alleen wordt uitgewisseld als de inhoud van de annotatie wijzigt of als uit het versiebeheer niet duidelijk blijkt welke versie van de annotatie gebruikt moet worden.

Als invoer wordt een beschijving van de uitwisselmomenten gebruikt. Dit is een .json bestand dat een object bevat:
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
met:
* `Annotatie` is een korte naam voor de annotatie die gebruikt wordt om in de resultaatpagina de annotatie aan te duiden.
* `Instrument` is het work-ID van de regeling of informatieobject waar de annotatie bijhoort. Het instrument moet terugkomen in de consolidatie-informatie modules van het scenario.
* `Uitwisselingen` is een array met uitwisselingen waarin een versie van de annotatie is meegeleverd:
    * `GemaaktOp` is het tijdstip van de uitwisseling; deze moet overeenkomen met het tijdstip in een van de modules met consolidatie-informatie.
    * `Doelen` zijn de doelen waarvoor de annotatieversie is opgesteld; dit moet gelijk zijn aan de doelen van de [BeoogdeRegeling](@@@STOP_Documentatie_Url@@@data_xsd_Element_data_BeoogdeRegeling.html)/[BeoogdInformatieobject](@@@STOP_Documentatie_Url@@@data_xsd_Element_data_BeoogdInformatieobject.html) voor de instrumentversie waar de annotatieversie bij hoort.
    * `Beschrijving` is een korte beschrijving van de inhoud van de annotatieversie of van de reden waarom de annotatieversie is uitgewisseld.

