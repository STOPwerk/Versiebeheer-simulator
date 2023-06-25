_**Deze functionaliteit is nog in ontwikkeling**_

De simulator kan het creatieproces bij een bevoegd gezag simuleren, inclusief de rol van adviesbureaus daarbij. Bij het naspelen van een scenario toont de simulator wat er in de software van het bevoegd gezag zou kunnen gebeuren. daarnaast stelt de simulator de inhoud van de [ConsolidatieInformatie](@@@STOP_Documentatie_Url@@@data_xsd_Element_data_ConsolidatieInformatie.html) modules samen voor de aanlevering aan LVBB, die met een beschrijving van het scenario als invoer dient voor de [simulatie van de LVBB](Simulatie-van-de-lvbb).

STOP schrijft niet voor hoe de software van het bevoegd gezag moet werken, maar vereist wel dat de consolidatie-informatie [afleidbaar](@@@STOP_Documentatie_Url@@@consolideren_bg_versiebeheer.html) een reflectie is van het BG-interne versiebeheer. Voor deze simulator is een van de vele mogelijke uitvoeringen gekozen voor het intern versiebeheer, en daaruit is inderdaad de consolidatie-informatie af te leiden. De [procesbegeleiding](@@@STOP_Documentatie_Url@@@consolideren_bg_procesbegeleiding.html) komt tot uitdrukking in de activiteiten die gespecificeerd kunnen worden, en waarvan gecontroleerd wordt dat ze uit te voeren zijn.

Net als de STOP documentatie beoogt de simulator geen verwachtingen te wekken hoe de software van het bevoegd gezag daadwerkelijk gaat werken. Het is bedoeld om te laten zien dat de technische details grotendeels automatiseerbaar zijn. Of/in hoeverre dat moet en hoe dat het beste kan is een zaak voor de leveranciers van de software van het bevoegd gezag.

## Opbouw van een scenario
Via de simulator kan handmatig een volledig scenario samengesteld worden met daarin de activiteiten die het bevoegd gezag (en eventuele adviesbureaus) ontplooit. De simulator bewaart het scenario in de vorm van een specificatie die gedownload kan worden. De specificatie kan op een later moment gebruikt worden om het scenario nogmaals te bekijken, of om het te wijzigen of uit te breiden.

De aanname is dat een bevoegd gezag een proces heeft waarbij een besluit in een project wordt voorbereid, waarbij er op elk moment meerdere projecten (kunnen) lopen. Aan het begin van het project wordt een beschikbare versie van de regelgeving als uitgangspunt genomen. Daarop worden wijzigingen aangebracht, totdat het moment is aangebroken om het besluit (of een ontwerp daarvan) op te stellen. Op zo'n moment worden de wijzigingen in de regelgeving overgenomen in het project die sinds de start van het project zijn doorgevoerd. Ook op latere momenten kan het nodig zijn de versie uit het project bij te werken met wijzigingen die in een van de projecten zijn ontstaan. Daarnaast zijn er gebeurtenissen waarop het bevoegd gezag moet reageren met het aanpassen van eerder bekendgemaakte besluiten. Bijvoorbeeld als niet de juiste versie van een besluit bekendgemaakt is (rectificatie) of als een rechter een besluit (gedeeltelijk) heeft vernietigd. Ook deze activiteiten worden geplaatst in het kader van het project waarvoor het besluit is gemaakt.

Tot slot kan de simulator laten zien hoe het STOP versiebeheer eruit ziet als de start van een project door een adviesbureau gedaan wordt op basis van een download uit de LVBB. De simulator houdt bij welke activiteiten door het adviesbureau en door het bevoegd gezag uitgevoerd worden, maar biedt geen afzonderlijke presentatie van de resultaten vanuit het gezichtspunt van een adviesbureau of van het bevoegd gezag.

Binnen een project kan aan meerdere versies van hetzelfde instrument gewerkt worden die op andere momenten of onder andere condities in werking treden. In STOP termen: er kan aan versies voor meerdere doelen/branches gewerkt worden, met voor elk instrument één versie per doel/branch.

## Specificatie van het scenario
Een scenario wordt gespecificeerd als een JSON object:
```
{
    "BevoegdGezag": "Gemeente" | "Rijk",
    "BGCode": "gm9999",
    "Beschrijving": "... beschrijving (html) ...",
    "Startdatum": "2024-01-01",
    "Uitgangssituatie" : <Momentopname>,
    "Projecten": {
        "<naam>" : [
            { 
                "SoortActiviteit": "<soort activiteit>",
                "Beschrijving": "<Optionele beschrijving van de activiteit>",
                "Tijdstip": <tijdstip van de activiteit>,
                ...
            },
            { 
                "SoortActiviteit": "<soort activiteit>",
                "Beschrijving": "<Optionele beschrijving van de activiteit>",
                "Tijdstip": <tijdstip van de activiteit>,
                ...
            },
            ...
        ],
        ...
    }
}
```
waarbij:
* `Bevoegd gezag` is verplicht en kan `Gemeente` of `Rijk` zijn.
* `BGCode` is optioneel en is de code die voor het bevoegd gezag gebruikt moet worden. Indien geen waarde gegeven is, san wordt _gm9999_ gebruikt voor een gemeente en _mnre9999_ voor de rijksoverheid. Andere voorbeelden zijn _pv99_ voor een provincie of _ws9999_ voor een waterschap.
* `Beschrijving` is een optionele beschrijving van het scenario, te gebruiken bij de presentatie van de resultaten van de twee simulators.
* `Startdatum` is optioneel en geeft de startdatum van het scenario.
* `Uitgangssituatie` is optioneel en beschrijft welke regeling- en informatieobjectversies in werking zijn bij de start van het scenario. In de Momentopname mogen geen tijdstempels voorkomen. De versies worden in een branch met code _start_ ondergebracht, met inwerkingtreding op tijdstip 0 (dat daarna niet meer als tijdstip gebruikt kan worden).
* `Projecten` bevat de activiteiten die voor een project uitgevoerd worden, met per project:
    * `naam` is een code of zeer korte naam van het project, bijvoorbeeld _P1_.
    * Een lijst met activiteiten voor een project, met voor elke activiteit tenminste:
        * `SoortActiviteit` geeft het type activiteit.
        * `Beschrijving` is een optionele beschrijving van de activiteit, te gebruiken bij de presentatie van de resultaten van deze simulator.
        * `UitgevoerdOp` is het tijdstip waarop de activiteit wordt uitgevoerd. Elk _UitgevoerdOp_ tijdstip moet uniek zijn in het scenario

De tijdstippen en datums worden niet als absolute datum maar als een getal gespecificeerd. Het gehele deel van het getal is het aantal dagen sinds de startdatum, het aantal centi-eenheden het tijdstip op de dag. In het bovenstaande voorbeeld:

* _UitgevoerdOp_ = 10 dus het tijdstip is 2024-01-11T00:00:00Z
* _UitgevoerdOp_ = 31.09 dus het tijdstip is 2024-02-01T09:00:00Z

De specificatie van `Uitgangssituatie` en van activiteiten die tevens tot een wijziging van regeling-/informatieobjectversies of tijdstempels kunnen leiden zijn van het type `<Momentopname>`. Dit bestaat uit een opgave van de actuele versies van regelingen, GIO's en PDF-IO's met bijbehorende annotaties (voor zover ze ondersteund worden door de simulator):
```
<Momentopname> = {
        "reg_<nummer of code>" : null | true | false | <uuid> | {
            "Metadata_Citeertitel": "<citeertitel>",
            "Toelichtingrelaties": true | false,
            "Non-STOP": {
                "<code>" : true | false,
                ...
            },
            "uuid": <integer>
        },
        ...,
        "gio_<nummer of code>" : null | true | false | <uuid> | {
            "Metadata_Citeertitel": "<citeertitel>",
            "Symbolisatie": true | false,
            "uuid": <integer>
        },
        ...
        "pdf_<nummer of code>" : null | true | false | <uuid> | {
            "Metadata_Citeertitel": "<citeertitel>",
            "uuid": <integer>
        },
        ...
        "JuridischWerkendVanaf": false | <datum (getal)>,
        "GeldigVanaf": false | <datum (getal)>
    }
```
Hierbij staat:

* `reg_<...>` is de work-aanduiding van een regeling. 
* `gio_<...>` is de work-aanduiding van een GIO (een consolideerbaar informatieobject). 
* `pdf_<...>` is de work-aanduiding van een PDF als consolideerbaar informatieobject. 
* voor elk work kan de versie worden opgegeven als:
    * `null`: het work wijzigt niet op de branch, dit resulteert in STOP-versiebeheer in een terugtrekking
    * `false`: het work wordt ingetrokken
    * `true`: er ontstaat een nieuwe versie van het work die niet uitgewerkt wordt; in STOP-versiebeheer is dit een onbekende versie. Het ligt niet voor de hand dat deze waarde in een specificatie van een scenario voorkomt. Waar dat nodig is zal de simulator een onbekende versie invullen. De waarde wordt in het scenario wel toegestaan om experimenteren met het fenomeen onbekende versie mogelijk te maken.
    * `<uuid>`: een integer die verwijst naar een versie (van hetzelfde instrument) die in een andere momentopname is gespecificeerd.
    * `{ ... }`: er ontstaat een nieuwe versie van het work. Als de annotaties niet wijzigen, dan kan met {} volstaan worden.
* Voor elke versie van een work kunnen annotaties opgegeven worden:
    * `uuid` (optioneel) is een integer die gebruikt kan worden om in een andere momentopname naar deze versie te verwijzen. De waarde wordt alleen voor interne verwijzingen gebruikt en wordt niet in de weergave van de resultaten van de simulatie getoond. De waarde moet uniek zijn binnen het scenario.
    * `Metadata_Citeertitel` is een alternatieve, leesbare titel voor het work.
    * `Toelichtingrelaties` (regeling) en `Symbolisatie` (GIO) zijn STOP annotaties. De simulator kent de inhoud ervan niet. Geef met `true` aan dat er een nieuwe versie van de annotatie wordt doorgegeven, en met `false` dat de annotatie wordt verwijderd.
* Een regeling kan ook `Non-STOP`-annotaties zijn. Dit wordt als een verzameling objecten gemodelleerd, elk geïdentificeerd met een `code`, waarvoor bij elke versie een nieuwe instantie kan worden meegeleverd (met waarde `true`). Als de waarde `false` is, dan wordt het object uit de collectie verwijderd.

## Beperkingen van de simulator

De simulator is niet gemaakt om te demonstreren hoe het interne versiebeheer bij een adviesbureau of bevoegd gezag er precies uit moet zien.De simulator voert een rudimentair versiebeheer uit waarbij de versies van alle bekende regelingen en informatieobjecten tegelijk in één branch beheerd wordt. Als in een scenario meerdere regelingen worden beschreven, dan is niet mogelijk een project te beginnen voor slechts een van de regelingen. 

Een bevoegd gezag of adviesbureau kan in de simulator alleen een beperkt aantal soorten activiteiten uitvoeren. Dit zijn de activiteiten die in de praktijk het meest zullen voorkomen. Bepaalde activiteiten zijn bewust niet opgenomen omdat ze een correctie zijn voor iets dat beter procedureel opgelost kan worden. Bijvoorbeeld als de ontwerpbesluit voor het ene project is geschreven met de aanname dat het project na een ander project in werking treedt, maar uiteindelijk de volgorde van inwerkingtreding omgedraaid blijkt te zijn. Er is een activiteit nodig die niet alleen de wijzigingen van het andere project uit de versie van het ene project haalt (ontvlechting in STOP), maar ook de uitgangssituatie van het project wijzigt. Dit kan voorkomen worden door de geen aannames te doen over de onderlinge volgorde van inwerkingtreding totdat de besluiten voor beide projecten definitief vastgesteld zijn, en daarna de (wel door de simulator ondersteunde) activiteiten voor het overnemen van wijzigingen te gebruiken.

Soms zijn de activiteiten beperkter dan wat in de praktijk mogelijk zal zijn. Het mogelijk maken van meer opties zou de simulator complexer maken terwijl het geen extra inzicht biedt in de (on)mogelijkheden van het STOP versiebeheer.

De simulator gaat uit van instantaan-publiceren. Als een activiteit een publicatie inhoudt of een uitwisseling met de landelijke voorzieningen, dan is de aanname dat de publicatie en verwerking direct uitgevoerd wordt. Het bijhouden van een publicatie-wachtrij is erg complex en voegt weinig toe aan het inzicht dat de simulator probeert te geven in het afleiden van STOP-versiebeheerinformatie uit het interne versiebeheer.

Bij het gebruik van de downloadservice gaat de simulator ervan uit dat de geconsolideerde geldende regelgeving in de landelijke voorziening bij het bevoegd gezag op dat moment gelijk is, dat het bevoegd gezag geen consolidatieachterstand heeft voor de geldende regelgeving.

Bij het samenstellen van een scenario in de simulator of het wijzigen van een eerder ingevoerd scenario zijn niet alle onderdelen van het scenario te wijzigen. Het scenario bestaat in essentie uit een reeks activiteiten die in een bepaalde (tijds-)volgorde worden uitgevoerd. Als de resultaten van de ene activiteit gebruikt worden bij het uitvoeren van de andere activiteit, dan is de eerste activiteit niet meer te wijzigen.

## Activiteiten

De activiteiten die in een project kunnen voorkomen:

| Activiteit | Beschrijving |
| ----- | ------------ |
| [Maak project](#activiteit-maak-project) | Richt een nieuw project in (door bevoegd gezag) |
| [Download](#activiteit-download) | Download de (nu of in de toekomst) geldende instrumentversies uit de LVBB (door een adviesbureau) |
| [Maak branch](#activiteit-maak-branch) | Voeg een extra branch toe binnen een project waarin gewerkt wordt aan instrumentversies voor een nieuw doel |
| [Wijziging](#activiteit-wijziging) | Aanpassing van instrumentversies binnen een project, en/of het maken van een nieuw doel/branch binnen het project. |
| [Uitwisseling](#activiteit-uitwisseling) | Uitwisseling (van adviesbureau naar bevoegd gezag of omgekeerd) van bijgewerkte instrumentversies, die het bevoegd gezag (na eventuele aanpassing) zal opnemen in een besluit |
| [Bijwerken uitgangssituatie](#activiteit-bijwerken-uitgangssituatie) | Verwerken van wijzigingen die (afhankelijk van het soort branch) in de geldende regelgeving of de voorgaande branch zijn aangebracht. |
| [Ontwerpbesluit](#activiteit-ontwerpbesluit) | De publicatie van een ontwerpbesluit dat alle wijzigingen bevat die in het project zijn aangebracht. |
| [Conceptbesluit](#activiteit-concept-vaststellingsbesluit) | Het opstellen van een concept-vaststellingsbesluit dat alle wijzigingen bevat die in het project zijn aangebracht, te gebruiken in de vaststellingsprocedure. |
| [Vaststellingsbesluit](#activiteit-vaststellingsbesluit) | De publicatie van een vaststellingsbesluit (en later eventueel een inwerkingtredingsbesluit) dat alle wijzigingen bevat die in het project zijn aangebracht. |

De lijst met activiteiten moet rekening houden met de beperkingen van de simulator:

* De eerste activiteit voor een project is `Maak project` (uitgevoerd door het bevoegd gezag) of `Download` (uitgevoerd door een adviesbureau).
* Naast `Download` en `Uitwisseling` mag een adviesbureau alleen de activiteit `Wijziging` uitvoeren.
* Bij elke activiteit `Uitwisseling` wisselt ook de uitvoerder. Als een adviesbureau de activiteit `Uitwisseling` uitvoert, dan worden de activiteiten daarna door het bevoegd gezag uitgevoerd. Als een bevoegd gezag `Uitwisseling` uitvoert, dan worden de activiteiten daarna door het adviesbureau uitgevoerd.
* De activiteit `Uitwisseling` mag alleen voorkomen in projecten met één branch.
* De activiteit `Bijwerken uitgangssituatie` mag niet meer uitgevoerd worden voor een branch nadat de branch onderdeel is van een `Vaststellingsbesluit`.
* De simulator valideert niet of het juridisch correct is wat een bevoegd gezag doet. Bij de specificatie van het project moet erop gelet worden dat de activiteiten juridisch mogelijk zijn.

Elke activiteit heeft tenminste de eigenschappen:
```
        { 
            "SoortActiviteit": "Maak branch",
            "Beschrijving": "<Optionele beschrijving van de activiteit>",
            "Tijdstip": <tijdstip van de activiteit>,
            ...
        }
```
waarbij:
* `SoortActiviteit` geeft aan om welke activiteit het gaat;
* `Tijdstip` geeft aan wanneer de activiteit uitgevoerd is/wordt;
* `Beschrijving` is een toelichting op het waarom van de activiteit, de rol die de activiteit speelt in het scenario.


### Activiteit: Maak branch
Maak een of meer nieuwe branches in het versiebeheer aan.
```
        { 
            "SoortActiviteit": "Maak branch",
            "Beschrijving": "<Optionele beschrijving van de activiteit>",
            "Tijdstip": <tijdstip van de activiteit>,
            "<code>": <Momentopname> {
                "Soort": "Regulier",
                ...
            },
            "<code>": <Momentopname> {
                "Soort": "VolgendOp",
                "Branch": "<code>",
                ...
            },
            "<code>": <Momentopname> {
                "Soort": "TegelijkMet",
                "Branches": ["<code>", "<code>", ...]
                ...
            }
            ...
        }
```
waarbij:
* `<code>`: korte unieke naam voor de nieuwe branch.
* `Soort` geeft aan wat de uitgangssituatie voor de branch is:
    * `Regulier`: een besluit in het project zal de wijzigingen ten opzichte van de geldende regelgeving beschrijven. De eerste versies in de branch zijn de op dat moment geldende versies van de bekende works. Als de consolidatie van de geldende regelgeving onverhoopt niet beschikbaar is, dan wordt de voorgaande versie gebruikt.
    * `VolgendOp`: een besluit in het project zal de wijzigingen ten opzichte van de regelgeving beschrijven die volgt uit (en later in werking treedt dan) een andere branch, die via `Branch` is opgegeven (en die bij een ander project kan horen). De eerste versies in de branch zijn de op dat moment beschikbare versies in de andere branch.
    * `TegelijkMet`: een besluit in het project zal de regelgeving beschrijven die in werking treedt als de laatste van twee of meer andere branches in werking is getreden. De andere branches staan in `Branches`, waarbij de eerst opgegeven branch onderdeel moet zijn van het project. Wijzigingen worden ten opzichte van die branch beschreven. Een branch van dit type wordt gebruikt om pro-actief samenloop op te lossen waarvoor een nieuw besluit vereist is.
* De overige inhoud is die van een _Momentopname_ per branch, waarbij tijdstempels nog niet zijn toegestaan.

### Activiteit: Download
Haal de op een bepaald moment geldige regeling/informatieobjecten op uit de LVBB.
```
        { 
            "SoortActiviteit": "Download",
            "Beschrijving": "<Optionele beschrijving van de activiteit>",
            "Tijdstip": <tijdstip van de activiteit>,
            "Branch": "<code>"
        }
```
waarbij:
* `<code>`: korte unieke naam voor de nieuwe branch

Het adviesbureau krijgt de beschikking over alle geldende versies van de regelgeving. Het is in de simulator niet mogelijk aan te geven dat
het adviesbureau slechts één regeling met bijbehorende informatieobjecten downloadt.

### Activiteit: Wijziging
Geef aan dat er nieuwe versies zijn gemaakt van de instrumenten, en/of dat er (gewijzigde) informatie over de geldigheid is.
```
        { 
            "SoortActiviteit": "Maak branch",
            "Beschrijving": "<Optionele beschrijving van de activiteit>",
            "Tijdstip": <tijdstip van de activiteit>,
            "<code>": <Momentopname>,
            "<code>": <Momentopname>,
            ...
        }
```
waarbij:
* `<code>`: korte unieke naam voor de branch waarvan de inhoud wordt gewijzigd
* De overige inhoud is die van een _Momentopname_ per branch, waarbij tijdstempels nog niet zijn toegestaan.

### Activiteit: Uitwisseling 
Stuurt de inhoud van de branch naar het bevoegd gezag (als de activiteit wordt uitgevoerd door een adviesbureau)
of naar een adviesbureau (als de activiteit wordt uitgevoerd door het bevoegd gezag).
```
        { 
            "SoortActiviteit": "Uitwisseling",
            "Beschrijving": "<Optionele beschrijving van de activiteit>",
            "Tijdstip": <tijdstip van de activiteit>
        }
```

### Activiteit: Bijwerken uitgangssituatie
Werkt de uitgangssituatie voor elke branch in het project bij door de branch (afhankelijk van de soort branch) te baseren op de op dat moment geldende regelgeving of inhoud van een andere branch waar de project-branch op volgt. Daarbij worden de wijzigingen die tussen de oude en nieuwe uitgangssituatie zijn aangebracht overgenomen in de project-branch.
```
        { 
            "SoortActiviteit": "Bijwerken uitgangssituatie",
            "Beschrijving": "<Optionele beschrijving van de activiteit>",
            "Tijdstip": <tijdstip van de activiteit>,
            "<code>": <Momentopname>,
            "<code>": <Momentopname>,
            ...
        }
```
Voor elke branch en voor elk work waar de wijzigingen in de uitgangssituatie conflicteren met de wijzigingen in de branch moet via een _Momentopname_ de resulterende versie worden aangegeven. Tijdstempels nog niet zijn toegestaan.

### Activiteit: Ontwerpbesluit
```
        { 
            "SoortActiviteit": "Ontwerpbesluit",
            "Beschrijving": "<Optionele beschrijving van de activiteit>",
            "Tijdstip": <tijdstip van de activiteit>,
            "<code>": <Momentopname>,
            ...
        }
```
waarbij de (optionele) _Momentopname_ als een laatste correctie voorafgaand aan de publicatie opgevat wordt. Tijdstempels nog niet zijn toegestaan.

### Activiteit: Concept-vaststellingsbesluit
```
        { 
            "SoortActiviteit": "Concept-vaststellingsbesluit",
            "Beschrijving": "<Optionele beschrijving van de activiteit>",
            "Tijdstip": <tijdstip van de activiteit>,
            "<code>": <Momentopname>,
            ...
        }
```
waarbij de _Momentopname_ tenminste de tijdstempels moet bevatten voor elke branch. Eventuele aanvullende wijzigingen worden als een laatste correctie voorafgaand aan de verspreiding van het besluit opgevat. Het concept-vaststellingsbesluit wordt niet gepubliceerd.

### Activiteit: Vaststellingsbesluit
```
        { 
            "SoortActiviteit": "Vaststellingsbesluit",
            "Beschrijving": "<Optionele beschrijving van de activiteit>",
            "Tijdstip": <tijdstip van de activiteit>,
            "<code>": <Momentopname>,
            ...
        }
```
waarbij de _Momentopname_ tenminste de tijdstempels moet bevatten voor elke branch. Eventuele aanvullende wijzigingen worden als een laatste correctie voorafgaand aan de publicatie opgevat.

