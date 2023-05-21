_**Deze functionaliteit is nog in ontwikkeling**_

De simulator kan uitgaan van de acties die een bevoegd gezag uitvoert. De simulator berekent dan de inhoud van de [ConsolidatieInformatie](@@@STOP_Documentatie_Url@@@data_xsd_Element_data_ConsolidatieInformatie.html) module voor de aanlevering aan LVBB.

STOP schrijft niet voor hoe de software van het bevoegd gezag moet werken, maar stelt wel dat de consolidatie-informatie [afleidbaar](@@@STOP_Documentatie_Url@@@consolideren_bg_versiebeheer.html) is van het intern versiebeheer als dat goed is ingericht. Voor deze simulator is een van de vele mogelijke uitvoeringen gekozen voor het intern versiebeheer, en daaruit is inderdaad de consolidatie-informatie af te leiden. De [procesbegeleiding](@@@STOP_Documentatie_Url@@@consolideren_bg_procesbegeleiding.html) komt tot uitdrukking in de acties die gespecificeerd kunnen worden, en waarvan gecontroleerd wordt dat ze ook daadwerkelijk uit te voeren zijn.

In aanvulling op de resultaten die beschreven zijn voor de [simulatie van de LVBB](Simulatie-van-de-lvbb).bevat de resultaatpagina ook:

* **Opstellen en consolideren**: een overzicht van de activiteiten in de projecten die als invoer dienen voor de simulatie.

## Werkwijze van het bevoegd gezag
De aanname is dat een bevoegd gezag een proces heeft waarbij een besluit in een project wordt voorbereid, waarbij er op elk moment meerdere projecten (kunnen) lopen. Aan het begin van het project wordt een bevroren versie van de regelgeving als uitgangspunt genomen. Daarop worden wijzigingen aangebracht, totdat het moment is aangebroken om het besluit (of een ontwerp daarvan) op te stellen. Op zo'n moment worden de wijzigingen in de regelgeving overgenomen in het project die sinds de start van het project zijn doorgevoerd. Ook op latere momenten kan het nodig zijn de versie uit het project bij te werken met wijzigingen die in een van de projecten zijn ontstaan.

Daarnaast zijn er gebeurtenissen waarop het bevoegd gezag moet reageren met het aanpassen van eerder bekendgemaakte besluiten. Bijvoorbeeld als niet de juiste versie van een besluit bekendgemaakt is (rectificatie) of als een rechter een besluit (gedeeltelijk) heeft vernietigd.

Tot slot kan de simulator laten zien hoe het STOP versiebeheer eruit ziet als de start van een project door een adviesbureau gedaan wordt op basis van een download uit de LVBB.

Binnen een project kan aan meerdere versies van hetzelfde instrument gewerkt worden die op andere momenten of onder andere condities in werking treden. In STOP termen: er kan aan versies voor meerdere doelen/branches gewerkt worden, met voor elk instrument één versie per doel/brnch.

De acties die in een project kunnen voorkomen:

| Actie | Beschrijving |
| ----- | ------------ |
| [Nieuw doel](#actie-nieuw-doel) | Richt het project zo in dat binnen een project gewerkt wordt aan instrumentversies voor een nieuw doel |
| [Download](#actie-download) | Download de (nu of in de toekomst) geldende instrumentversies uit de LVBB (door een adviesbureau) |
| [Wijziging](#actie-wijziging) | Aanpassing van instrumentversies binnen een project, en/of het maken van een nieuw doel/branch binnen het project. |
| [Uitwisseling](#actie-uitwisseling) | Uitwisseling (van adviesbureau naar bevoegd gezag of omgekeerd) van bijgewerkte instrumentversies, die het bevoegd gezag (na eventuele aanpassing) zal opnemen in een besluit |
| [Overnemen gewijzigde regelgeving](#actie-bijwerken-uitgangssituatie) | Verwerken van wijzigingen in de (nu of in de toekomst) geldende regelgeving in de (bevroren) instrumentversies in een project. De simulator gebruikt daarvoor de bekendgemaakte regelgeving; overnemen van nog niet gepubliceerde instrumentversies wordt niet ondersteund. |
| [Overnemen aanpassingen](#actie-bijwerken-uitgangssituatie) | Overnemen van wijzigingen van een andere branch, ongeacht of de instrumentversies voor die branch al uitgewisseld zijn met andere systemen. De simulator gebruikt daarvoor de intern bekende instrumentversies.  |
| [Publicatie](#actie-publicatie) | De publicatie van een besluit, mededeling of revisie via de LVBB en/of de publicatie van instrumentversies via andere systemen. |

## Beperkingen van de simulator

De simulator is niet gemaakt om te demonstreren dat versiebeheer op slechts een deel van de regelgeving mogelijk is. De simulator voert versiebeheer uit op alle bekende regelingen en informatieobjecten. Als in een scenario meerdere regelingen worden beschreven, dan is niet mogelijk een project te beginnen voor slechts een van de regelingen. 

De simulator kan alleen een beperkt stel acties uitvoeren. Dit zijn de acties die in de praktijk het meest zullen voorkomen. Bepaalde acties zijn bewust niet opgenomen omdat ze een correctie zijn voor iets dat beter procedureel opgelost kan worden. Bijvoorbeeld als de ontwerpbesluit voor het ene project is geschreven met de aanname dat het project na een ander project in werking treedt, maar uiteindelijk de volgorde van inwerkingtreding omgedraaid blijkt te zijn. Er is een actie nodig om de wijzigingen van het andere project uit de versie van het ene project te halen (ontvlechting in STOP). Dit kan voorkomen worden door de geen aannames te doen over de onderlinge volgorde van inwerkingtreding totdat de besluiten voor beide projecten definitief vastgesteld zijn, en daarna de (wel door de simulator ondersteunde) acties voor het overnemen van wijzigingen te gebruiken.

Het is mogelijk om een niet beschikbare actie toch uit te voeren door zelf de consolidatie-informatie voor een _Publicatie_-actie te specificeren. Dit wordt door de simulator verwerkt als ware het de uitkomst van een beschikbare actie. Het omdraaien van de inwerkingtreding is op die manier te simuleren.

De consolidatie-informatie voor het STOP versiebeheer verwijst naar eerdere uitwisselingen/_Publicatie_-acties. Maar als de software van het bevegd gezag (en dus ook deze simulator) bij het uitvoeren van de acties intern verwijst naar andere momentopnamen, dan is bijvoorbeeld het `gemaaktOp`-tijdstip nog niet bekend. Bij andere acties, zoals het overnemen van de geldende regelgeving, heeft het bevoegd gezag de keuze om uit te gaan van wat de publiek bekende geldende regelgeving is, of wat de versie is die intern al klaarstaat maar nog niet is gepubliceerd. Afhankelijk van de werkwijze van het bevoegd gezag kan het nodig zijn onderscheid te maken tussen interne, publieke en voor-publicatie-klaargezet-maar-nog-niet-uitgewisselde versieinformatie.

De simulator kent alleen het onderscheid tussen interne en publieke versieinformatie. Het bijhouden van een publicatie-wachtrij is erg complex en voegt weinig toe aan het inzicht dat de simulator probeert te geven in het afleiden van STOP-versiebeheerinformatie uit het interne versiebeheer. De simulator heeft daarom als beperking dat de acties die bij de voorbereiding van een publicatie horen (zoals _overnemen gewijzigde regelgeving_ en _Overnemen aanpassingen_) meteen gevolgd moeten worden door de _Publicatie_-actie. De simulator ondersteunt niet (althans niet in alle gevallen) het eerst klaarmaken voor publicatie van besluiten, mededelingen en revisies uit meerdere projecten, en daarna pas publiceren ervan. De simulator ondersteunt wel het opeenvolgend klaarmaken voor publicatie en publiceren per project, zelfs als de verschillende projecten dezelfde datum inwerkingtreding hebben.

## Inhoud van het scenario
Het scenario bestaat uit een map met invoerbestanden:

* Eén of meer bestanden met een specificatie van een [project](#Specificatie-van-een-project).
* Optioneel een [beschrijving](#beschrijving-van-het-scenario) van het scenario.
* Optioneel een of meer bestanden met een [STOP ConsolidatieInformatie](@@@STOP_Documentatie_Url@@@data_xsd_Element_data_ConsolidatieInformatie.html)

De modules met consolidatie-informatie worden gezien als informatie die uit projecten komt die voor het scenario niet relevant zijn en daarom niet expliciet als project opgezet zijn. Bijvoorbeeld om eenvoudig een eerste reeks toestanden van een geconsolideerde regeling op te zetten die de projecten als uitgangspunt kunnen nemen. 

## Beschrijving van het scenario
De beschrijving van het scenario wordt alleen gebruikt voor de weergave van de resultaten. Het maakt de resultaatpagina beter te begrijpen. De inhoud van het bestand heeft dezelfde indeling als de [beschrijving](Simulatie-van-de-lvbb#beschrijving-van-het-scenario) van een scenario voor de LVBB simulatie, maar slechts een beperkt aantal attributen zijn van belang voor de simulatie van het bevoegd gezag software:
```
{
    "Beschrijving": "... beschrijving (html) ..."
}
```
* `Beschrijving` is HTML die opgenomen wordt in  de webpagina met het resultaat.

## Specificatie van het bevoegd gezag proces
Een project wordt gespecificeerd door een .json bestand (meestal `bg_proces.json`) dat een object bevat:
```
{
    "BevoegdGezag": "Gemeente" | "Rijk",
    "Beschrijving": "... beschrijving (html) ...",
    "Uitgangssituatie" : {
        "doel-code": <Momentopname>,
        ...
    },
    "Projecten": {
        "<code>" : {
            "Beschrijving": "<beschrijving van het project>",
            "Acties": [
                { 
                    "SoortActie": "<soort actie>",
                    "Beschrijving": "<beschrijving van de actie>",
                    "UitgevoerdOp": "<begintijdstip van de actie/uitwisseling>",
                    ...
                },
                { 
                    "SoortActie": "<soort actie>",
                    "Beschrijving": "<beschrijving van de actie>",
                    "UitgevoerdOp": "<begintijdstip van de actie/uitwisseling>",
                    ...
                },
                ...
            ]
        },
        ...
    },
    "Overig" : [
        { 
            "SoortActie": "<soort actie>",
            "Beschrijving": "<beschrijving van de niet-projectgebonden actie>",
            "UitgevoerdOp": "<begintijdstip van de actie/uitwisseling>",
            ...
        },
        { 
            "SoortActie": "<soort actie>",
            "Beschrijving": "<beschrijving van de niet-projectgebonden actie>",
            "UitgevoerdOp": "<begintijdstip van de actie/uitwisseling>",
            ...
        },
        ...
    ]
}
```
waarbij:
* `Beschrijving` is HTML die opgenomen wordt in  de webpagina met het resultaat, indien er geen [beschrijving](#beschrijving-van-het-scenario) van het scenario aanwezig is. Is dat wel het geval, dan wordt de beschrijving genegeerd.
* `Project` is een code of zeer korte naam van het project, bijvoorbeeld _P1_.
* `Beschrijving` van het project is optioneel
* `Acties` is een lijst met acties die in het project plaatsvinden. De specificatie van de actie hangt af van het type actie maar bevat in ieder geval:
    * `SoortActie` geeft het type actie.
    * `Beschrijving` is verplicht en beschrijft wat het bevoegd gezag (of het adviesbureau) precies doet of waarom de actie uitgevoerd wordt.
    * `UitgevoerdOp` is het (begin)tijdstip waarop de actie uitgevoerd wordt. Het tijdstip moet opgegeven worden als: yyyy-MM-ddThh:mm:ssZ, net als `gemaaktOp` van het STOP versiebeheer. Als de actie een uitwisseling betreft, dan is dit tijdstip gelijk aan de `gemaaktOp` uit het versiebeheer. Voor andere acties wordt het tijdstip alleen gebruikt om de acties in de juiste volgorde te kunnen simuleren.

Op sommige plaatsen komt `... Momentopname ...`. Dit bestaat uit een opgave van de actuele versies van regelingen, GIO's en PDF-IO's met bijbehorende annotaties (voor zover ze ondersteund worden door de simulator):
```
<Momentopname> = {
        "gemaaktOp": "<begintijdstip van uitwisselen>",
        "Regelingen" : {
            "<regeling-work-code>": {
                "Versie": "<versie-code>",
                "Metadata_Citeertitel": "<citeertitel>",
                "Toelichtingrelaties": "<versie-code van laatste toekenning Toelichtingrelaties>",
                "NonSTOP": {
                    "<code>" : "<versie-code van laatste toekenning>",
                    ...
                }
            },
            ...
        },
        "GIO" : {
            "<GIO-work-code>": {
                "Versie": "<versie-code>",
                "Metadata_Citeertitel": "<citeertitel>",
                "Symbolisatie": "<versie-code van laatste toekenning symbolisatie>"
            },
            ...
        },
        "PDF" : {
            "<IO-work-code>": {
                "Versie": "<versie-code>",
                "Metadata_Citeertitel": "<citeertitel>"
            },
            ...
        }
    }
```
De lijst met acties moet rekening houden met de beperkingen van de simulator:

* De eerste actie is `Nieuw doel` of `Download`
* De actie `Download` mag alleen als eerste actie voorkomen; `Nieuw doel` mag meermalen in een project voorkomen.
* De actie `Nieuw doel` en de opvolgende acties worden uitgevoerd door het bevoegd gezag.
* De actie `Download` en de opvolgende acties worden uitgevoerd door een adviesbureau.
* Bij elke actie `Uitwisseling` wisselt ook de uitvoerder. Als een adviesbureau de actie `Uitwisseling` uitvoert, dan worden de acties daarna door het bevoegd gezag uitgevoerd. Als een bevoegd gezag `Uitwisseling` uitvoert, dan worden de acties daarna door het adviesbureau uitgevoerd.
* Naast `Download` en `Uitwisseling` mag een adviesbureau alleen de actie `Wijziging` uitvoeren.
* Na `Download` en `Nieuw doel` moet tenminste één `Wijziging` actie voor het betreffende doel/branch volgen.
* Tussen de uitvoering van `Overnemen gewijzigde regelgeving`/`Overnemen aanpassingen` en de `Publicatie` van het resultaat mag geen wijziging worden doorgevoerd voor de projecten/doelen waarvan de wijzigen/aanpassingen overgenomen worden.
* De simulator valideert niet of het juridisch correct is wat een bevoegd gezag doet. Bij de specificatie van het project moet erop gelet worden dat de acties juridisch mogelijk zijn.

### Actie: Nieuw doel
Maak een nieuw doel aan, d.w.z.  een nieuwe branch in het versiebeheer.
```
        { 
            "SoortActie": "Nieuw doel",
            "Beschrijving": "<beschrijving van de actie>",
            "UitgevoerdOp": "<begintijdstip van de actie>",
            "Doel": "<identificatie van het doel>",
            "Uitgangssituatie": "<datum van geldige regelgeving>" of "<identificatie van een doel>"
        }
```
waarbij:
* `Doel`: de identificatie van het nieuwe doel.
* `GebaseerdOp` geeft aan welke instrumentversies als basis voor het nieuwe doel (branch) gebruikt worden, dus op welke versie van de instrumenten doorgewerkt wordt:
    * Als de waarde een datum is, dan is de basis de regelgeving die op die datum geldig is.
    * Als het de identificatie van een doel is, dan is de basis de meerst recente versie voor dat doel (voor alle instrumenten).
* `Instrumenten`: de work-identificaties van elk instrument dat in de branch nodig is/bijgewerkt wordt. Er moet minimaal één instrument vermeld worden.

`GebaseerdOp` is verplicht tenzij het project tot een nieuwe regeling leidt.

### Actie: Download
Haal de op een bepaald moment geldige regeling/informatieobjecten op uit de LVBB.
```
        { 
            "SoortActie": "Download",
            "Beschrijving": "<beschrijving van de actie>",
            "UitgevoerdOp": "<begintijdstip van de actie>",
            "Doel": "<identificatie van het doel>",
            "GeldigOp": "<datum van geldige regelgeving>",
            "Instrumenten": [
                "<work-identificatie>",
                "<work-identificatie>",
                ...
            ]
        }
```
waarbij:
* `Doel`: de identificatie van het doel/branch dat het adviesbureau gebruikt om de wijzigingen aan te brengen.
* `GeldigOp` is de datum waarop de regelgeving geldig is waarvan de instrumentversies gedownload moet worden. De datum moet groter of gelijk zijn aan de datum uit `UitgevoerdOp`
* `Instrumenten`: de work-identificaties van elk instrument dat in de branch nodig is/bijgewerkt wordt. Er moet minimaal één instrument vermeld worden.

### Actie: Wijziging
Geef aan dat er nieuwe versies zijn gemaakt van de instrumenten, en/of dat er (gewijzigde) informatie over de geldigheid is.
```
        { 
            "SoortActie": "Wijziging",
            "Beschrijving": "<beschrijving van de actie>",
            "UitgevoerdOp": "<begintijdstip van de actie>",
            "Doel": "<identificatie van het doel/branch>",
            "Instrumentversies": [
                { "Instrumentversie": "<expression-identificatie>" },
                { "JuridischUitgewerkt": "work-identificatie" },
                { "OnbekendeVersie": "work-identificatie" },
                { "BestaatNiet": "work-identificatie" },
                ...
            ],
            "JuridischWerkendVanaf": "<datum>",
            "GeldigVanaf": "<datum>"
        }
```
waarbij:
* `Doel`: de identificatie van het doel/branch waarvoor de wijzigingen zijn aangebracht.
* `GeldigOp` is de datum waarop de regelgeving geldig is waarvan de instrumentversies gedownload moet worden. De datum moet groter of gelijk zijn aan de datum uit `UitgevoerdOp`.
* `Instrumentversies` (optioneel): voor elk instrument dat in de branch van het project bijgewerkt wordt: de status van dat instrument. Een instrument dat niet in deze actie gewijzigd wordt hoeft niet vermeld te worden. Er zijn drie mogelijke statussen:
    * `Instrumentversie`: de versie van het instrument.
    * `JuridischUitgewerkt`: het instrument is juridisch uitgewerkt/ingetrokken.
    * `OnbekendeVersie`: er is een nieuwe versie van het instrument, maar het is niet bekend hoe die er precies uitziet.
    * `BestaatNiet`: er is geen versie van het instrument meer voor deze branch. Dat kan alleen als er ook voor de branches die eerder in werking treden (of zijn getreden) geen versie voor het instrument bestaat. Anders moet het instrument als juridisch uitgewerkt gemarkeerd worden.
* `JuridischWerkendVanaf` (optioneel): de datum waarop de wijzigingen voor het doel in werking treden. Laat dit weg als de datum niet gewijzigd is. Geef '-' of '?' als datum als de datum eerder wel bekend was maar ni niet meer.
* `GeldigVanaf` (optioneel): de datum waarop de wijzigingen voor het doel geldig worden. Laat dit weg als de datum (nog) niet bekend is of als `JuridischWerkendVanaf` niet bekend is. Geef '-' of '?' als datum als de datum eerder wel bekend was maar ni niet meer.

Alleen het bevoegd gezag (dus niet een adviesbureau) mag `JuridischWerkendVanaf` en `GeldigVanaf` wijzigen. `GeldigVanaf` kan alleen een datum hebben als `JuridischWerkendVanaf` dat ook heeft.

### Actie: Uitwisseling 
```
        { 
            "SoortActie": "Uitwisseling",
            "Beschrijving": "<beschrijving van de actie>",
            "UitgevoerdOp": "<begintijdstip van de actie>",
            "Doel": "<identificatie van het doel>"
        }
```
waarbij:
* `Doel`: de identificatie van het doel/branch waarvan de instrumentversies uitgewisseld worden.

### Actie: Bijwerken uitgangssituatie
```
        { 
            "SoortActie": "Bijwerken uitgangssituatie",
            "Beschrijving": "<beschrijving van de actie>",
            "UitgevoerdOp": "<begintijdstip van de actie>",
            "Doel": "<identificatie van het doel>",
            "GeldigOp": "<datum van geldige regelgeving>",
            "Instrumentversies": [
                { "Instrumentversie": "<expression-identificatie>" },
                { "JuridischUitgewerkt": "work-identificatie" },
                ...
            ]
        }
```
waarbij:
* `Doel`: de identificatie van het doel/branch waarvan de instrumentversies bijgewerkt worden.
* `GeldigOp` is de datum waarop de regelgeving geldig is waarvan de instrumentversies gedownload moet worden. De datum moet groter of gelijk zijn aan de datum uit `UitgevoerdOp`. `GeldigOp` moet weggelaten worden voor doelen die als uitgangssiutatie een ander doel hebben.
* `Instrumentversies`: voor elk instrument dat in de branch van het project nodig is/bijgewerkt wordt: de status van dat instrument nadat de gewijzigde regelgeving is overgenomen. Elk instrument moet steeds genoemd worden, ook al is de status gelijk aan de status na de vorige actie. Er zijn twee mogelijke statussen:
    * `Instrumentversie`: de versie van het instrument.
    * `JuridischUitgewerkt`: het instrument is juridisch uitgewerkt/ingetrokken.

### Actie: Publicatie
```
        { 
            "SoortActie": "Publicatie",
            "Beschrijving": "<beschrijving van de actie>",
            "UitgevoerdOp": "<begintijdstip van de actie>",
            "Doelen": ["<identificatie van het doel>", "<identificatie van het doel>", ...],
            "SoortPublicatie": "<soort publicatie>"
        }
```
waarbij:
* `Doelen`: de identificatie(s) van het doel/branch uit het project waarvan de instrumentversies in de publicatie zijn opgenomen.
* `SoortPublicatie` geeft aan om welk soort publicatie het gaat. Keuze uit een van de waarden:
    * `Consultatie` - publicatie van een concept-besluit en/of instrumentversies die niet via STOP versiebeheer verloopt
    * `Voorontwerp` - publicatie van een concept-ontwerpbesluit en/of instrumentversies die niet via STOP versiebeheer verloopt
    * `Ontwerpbesluit` - publicatie van een ontwerpbesluit (via de LVBB)
    * `Besluit` - publicatie van een definitief/vastgesteld besluit (via de LVBB)
    * `Rectificatie` - publicatie van een rectificatie van het eerder gepubliceerde (ontwerp)besluit (via de LVBB)
    * `Mededeling uitspraak rechter` - publicatie van een mededeling van een uitspraak van de rechter (via de LVBB)
    * `Revisie` - publicatie van een revisie: een niet-juridische wijziging van de geconsolideerde regelgeving met als doel consolidatieproblemen op te lossen.

Bij publicatie via STOP versiebeheer bepaalt de simulator welke consolidatie-informatie uitgewisseld moet worden. Het is mogelijk om andere consolidatie-informatie in de simulatie te gebruiken door een XML-bestand met de STOP-module ConsolidatieInformatie in de map van het scenario te zetten. Het `gemaaktOp` tijdstip van die module moet overeenkomen met het `UitgevoerdOp` tijdstip van de actie. De informatie uit de STOP module wordt door de simulator gebruikt voor de geautomatiseerde consolidatie, en wordt ook verwerkt in de simulatie van het versiebeheer van het bevoegd gezag.

Deze mogelijkheid dient ertoe om (als dat nodig is) een fout resultaat van de simulator te corrigeren. Het kan ook gebruikt worden om te zien wat het effect is de software van het beveogd gezag in speciale gevallen de consolidatie-informatie op een andere manier samenstelt dan de simulator dat doet.

