```
python applicatie.py [--help|-h] [--alle|-a] [--meldingen|-m meldingen_pad] [--testen|-t] directory_pad [directory_pad ..]
```

Voer de simulator uit voor één of meer scenario's. Een scenario is een map met invoerbestanden. De simulator maakt een bestand `Simulator_Resultaat.html` aan voor elk scenario en plaatst het bestand in de map met invoerbestanden. In dat bestand staan de uitkomsten van de simulatie voor dat scenario. Daarnaast wordt een webpagina getoond met een verslag van de uitvoering van de applicatie. Deze webpagina wordt in de systeem-map voor tijdelijke bestanden geplaatst.

| Command line | Beschrijving |
| ----- | ----- |
| `python` | Het programma om een Python script mee uit te voeren. Op Windows is dat `py.exe` of `python.exe`, op MacOS/Unix `python3`. Voor Windows kan de laatste versie van Python [hier](https://www.python.org/downloads/) gedownload worden. |
| `applicatie.py` | Het pad van het Python script dat uitgevoerd moet worden. Het script is te vinden in de `simulator` map in [download.zip](../blob/master/download.zip). De overige bestanden in de `simulator` map worden bij het uitvoeren van de Python code ingelezen. |
| `directory_pad` | Pad naar een map met een scenario waarvoor de simulator uitgevoerd moet worden |
| `-a` of `--alle` | Kijk ook in subdirectories van `directory_pad` voor scenario's. Met deze optie kan de simulator tegelijk voor een hele collectie van scenario's uitgevoerd worden. |
| `-m meldingen_pad` of `--meldingen meldingen_pad` | Bewaar het verslag van de uitvoering van de applicatie in de `meldingen_pad` map, in plaats van in de systeem-map voor tijdelijke bestanden. |
| `-h` of `--help` | Toon de mogelijke command line opties, dus de informatie die op deze pagina staat. |
| `-t` of `--testen` | Deze optie is bedoeld voor gebruik bij de (door)ontwikkeling van de simulator. De scenario's zijn [testscenario's](../blob/master/broncode/tests/scenarios/). De applicatie slaat berekende resultaten op als json en vergelijkt ze met de verwachte resultaten. |
