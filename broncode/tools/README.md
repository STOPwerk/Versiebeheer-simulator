# Tools

Deze map bevat enkele op zichzelf staande Python tools die gebruikt worden voor ontwikkeling en onderhoud.

## maak_release_artefacts

Een script dat een selectie van bestanden uit deze repository in een download.zip bestand zet,
en andere voorbereidingen treft voor het publiceren van een versie. Aangeroepen vanuit [publiceer.bat](..\uitleveren\publiceer.bat).

## pas_configuratie_toe

Een script dat voor een selectie van bestanden uit deze repository parameters vervangt door concrete waarden, als onderdeel van het publiceren van een versie. Aangeroepen vanuit [publiceer.bat](..\uitleveren\publiceer.bat).

## voorbeelden_naar_unittests

Een script dat scenario's vanuit een map met voorbeelden kopieert naar een map met testscenario's. De invoerbestanden worden overschreven, extra bestanden worden niet weggehaald. Het invoerbestand met de beschrijving van het scneario wordt deels overgenomen en gecombineerd met de bestaande beschrijving in de map met het testscenario.
