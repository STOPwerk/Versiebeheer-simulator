# Code van de applicatie

_**Verouderd, moet nog bijgewerkt worden**_

## Waarvoor dient de code?

De Python code in deze map is een implementatie van de geautomatiseerde consolidatie die in STOP beschreven is. STOP beschrijft de invoer van het proces, wat het resultaat moet zijn, en geeft aanwijzingen hoe het een in het ander om te zetten is. STOP schrijft niet voor hoe dat precies moet. Deze code is een voorbeeld hoe de implementatie eruit kan zien.

## Hoe werkt de applicatie?

De applicatie scant (afhankelijk van de opties) één of meer directories. Als in een directory een XML bestand staat met als inhoud een STOP ConsolidatieInformatie module (uit imop-data.xsd), dan wordt de inhoud van de directory (en subdirectories daarvan) gezien als een scenario waarop de geautomatiseerde consolidatie losgelaten moet worden.

Het proces van geautomatiseerde consolidatie doorloopt de stappen:
* Lees de ConsolidatieInformatie (.xml bestanden) en annotaties (.json bestanden) in
* Reconstrueer de versiebeheerinformatie die geleid heeft tot de uitwisseling van de ConsolidatieInformatie/annotaties. Hierbij zijn de STOP annotaties onderdeel van het versiebeheer. De non-STOP annotaties worden daarbuiten gehouden als een verzameling van uitgewisselde informatie.
* Maak Proefversies voor de uitwisselingen. De non-STOP annotaties worden erbij gezocht aan de hand van de informatie uit de proefversies.
* Maak ActueleToestanden voor elke regeling en informatieobject. De non-STOP annotaties worden erbij gezocht aan de hand van de InstrumentversieHistorie.
* Maak complete toestanden geschikt voor tijdreizen, en zoek de non-STOP annotaties erbij.
* Maak de juridische verantwoording en bepaal voor de toestanden waarvoor geen instrumentversie bekend is een alternatieve manier om de inhoud van de toestand te tonen.
* Maak een webpagina waarin alle resultaten van de consolidatie zijn opgenomen.

Het proces kan ook gebruikt worden voor testscenario's. Dan voert de applicatie aanvullend uit:
* Schrijf een aantal in-memory data structuren naar een JSON bestand
* Als er voor dat bestand een verwachte uitkomst is opgegeven, vergelijk de actuele JSON met de verwachte en rapporteer als de versies afwijken.

Via een json bestand met opties kunnen bepaalde stappen in het proces overgeslagen worden.

## Hoe zit de code in elkaar?

### Rol van de codebestanden

| Patroon | Rol |
| ------- | ----- |
| `applicatie_*.py` | Code die specifiek is voor deze applicatie, zoals de aansturing van het bevoegd gezag- en consolidatieproces en de interactie met de gebruiker van de Python code. Startpunt van de (offline) applicatie is `applicatie.py`. | 
| `index.py` | Startpunt voor de online versie van de applicatie. |
| `proces_simulatie.py` | Startpunt van het proces dat de specificaties van het scenario verwerkt is `proces_simulatie.py`. |
| `proces_bg_*.py` | Implementatie van het proces zoals dat bij het bevoegd gezag en adviesbureaus kan plaatsvinden. Als dit onderdeel is van het scenario, zal de invoer voor de landelijke voorzieningen door deze simulatie gemaakt worden. |
| `proces_lv_*.py` | Implementatie van de geautomatiseerde consolidatie, vanaf het inlezen van de `ConsolidatieInformatie` XML tot en met het vullen van het interne datamodel via het verwerken van de modules. Deze processtappen zullen ook in  STOP-gebruikende systemen voorkomen als die (een deel van) de consolidatie implementeren. |
| `stop_*.py` | Data structuren voor STOP modules. De data structuren volgen zo dicht mogelijk het STOP model, ook al is er voor de verwerking additionele informatie nodig. Voor de `ConsolidatieInformatie` module is ook code aanwezig om de XML modules te lezen en om te zetten naar de in-memory data structuren. |
| `data_bg_*.py` | Data structuren die door de applicatie gebruikt worden om het proces bij het bevoegd gezag te ondersteunen en de resultaten daarvan vast te leggen. |
| `data_lv_*.py` | Data structuren die door de applicatie gebruikt worden om het consolidatieproces uit te voeren. Deze werken samen met of zijn uitbreidingen op de STOP modules. Instanties van de data structuren vormen een in-memory data-opslag die dezelfde rol heeft als het interne datamodel dat een STOP-gebruikend systeem nodig heeft om de STOP (uitwissel)modules te kunnen lezen en produceren. |
| `weergave_*.py` | De overige `weergave_*` bestanden bevatten code om een enkele webpagina samen te stellen waarin de resultaten van de consolidatie zijn beschreven. In de `weergave_*` bestanden is geen consolidatielogica opgenomen, het betreft alleen het presenteren van de eerder bepaalde informatie. Startpunt voor het samenstellen van de pagina is `weergave_resultaat.py`. |
| `weergave_data_*.py` | Data structuren die een aanvulling zijn op de data structuren uit `stop_*` en `data_*`. Deze applicatie houdt veel meer informatie bij over de uitvoering van de geautomatiseerde consolidatie dan strikt noodzakelijk. De extra informatie wordt gebruikt om de resultaten toe te lichten en inzage te geven in de stappen die daadwerkelijk voor de consolidatie zijn uitgevoerd. Deze informatie zal niet (of niet op deze manier) in een STOP-gebruikend systeem aanwezig zijn. |

Naast de Python modules zijn er `*.html`, `*.css` en `*.js` bestanden die fragmenten van de resulterende webpagina bevatten. Ze worden door de bijbehorende Python module ingelezen en (aangevuld) toegevoegd aan de resultaatpagina.

### Datamodel

De Python applicatie maakt gebruik van een intern datamodel dat waar mogelijk gebruik maakt van STOP modules. Deze data structuren zijn gecodeerd in aparte Python bestanden waarvan de namen die met data_* of *stop_* beginnen.

[[Datamodel.png|Datamodel]]

### Van invoer naar resultaten

Een deel van de code kan het ene deel van het datamodel afleiden uit het andere. De code daarvoor staat in Python bestanden waarvan de naam begint met *proces_*. Elk bestand bevat een klasse die de afleiding kan uitvoeren.

[[Dataflow.png|Procesmodel]]

