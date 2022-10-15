#======================================================================
#
# Startpunt van de applicatie
#
#----------------------------------------------------------------------
#
# De code in deze module voert de regie over de uitvoering van de
# applicatie.
#
#======================================================================

import getopt
import inspect
import os.path
import sys

#======================================================================
# Initialisatie van de applicatie.
#======================================================================
# Voeg het pad toe voor alle applicatie modules
script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append (script_dir)

helptekst = '''
applicatie.py [--help|-h] [--alle|-a] [--testen|-t] [--meldingen|-m meldingen_pad] directory_pad [directory_pad ..]

directory_pad     Pad naar een directory met een scenario waarvoor de applicatie uitgevoerd moet worden
-h of --help      Toon deze tekst
-a of --alle      Kijk ook in subdirectories voor scenario's
-t of --testen    De scenario's zijn unit testen. Sla resultaten op als json en vergelijk ze met de verwachte resultaten.
-m of --meldingen Bewaar de log van de uitvoering van de applicatie in de meldingen_pad directory, niet in de systeem-tempdirectory
'''
# De paden naar de directories
directory_paden = []
# Geeft aan of de scenario's test cases zijn
testen = False
# Geeft aan of de directory recursief doorzocht moet worden.
recursie = False
# Pad waar de meldingen terecht moeten komen; None is tempdir
meldingen_pad = None
try:
    (opts, args) = getopt.getopt(sys.argv[1:], "ahm:t", ["alle", "help", "meldingen=", "testen"])
except getopt.GetoptError:
    print (helptekst)
    sys.exit(2)
for opt, arg in opts:
    if opt in ('-h', '--help'):
        print (helptekst)
        sys.exit()
    elif opt in ('-t', '--testen'):
        testen = True
        recursie = True
    elif opt in ('-a', '--alle'):
        recursie = True
    elif opt in ('-m', '--meldingen'):
        meldingen_pad = arg
for arg in args:
    if not os.path.isdir (arg):
        print ("Geen directory: " + arg)
    else:
        directory_paden.append (arg)

if len(directory_paden) == 0:
    print (helptekst)
    sys.exit(2)

#======================================================================
# Uitvoeren van de applicatie.
#======================================================================
from applicatie_meldingen import Meldingen
from applicatie_scenario import Scenario
import applicatie_configuratie

log = Meldingen (True)
log.Informatie ('<a href="https://github.com/STOPwerk/Versiebeheer-simulator">Versiebeheer-simulator</a> ' + applicatie_configuratie.Applicatie_versie)

if testen:
    log.Informatie ("Voer unit tests uit")
    from applicatie_testen import UnitTests
    aantalScenarios, aantalSucces = Scenario.VoorElkScenario (log, directory_paden, recursie, UnitTests.VoerUit)
    log.Informatie ("Unit tests: " + str (aantalScenarios) + " uitgevoerd, " + str (aantalSucces) + " geslaagd, " + str (aantalScenarios - aantalSucces)+ " gefaald")
else:
    log.Informatie ("Bepaal de consolidatie voor de scenario's")
    from applicatie_uitvoeren import Uitvoering
    aantalScenarios, aantalSucces = Scenario.VoorElkScenario (log, directory_paden, recursie, Uitvoering.VoerUit)
    log.Informatie ("Consolidaties: " + str (aantalSucces) + " uitgevoerd, " + str (aantalScenarios - aantalSucces) + " niet (volledig) uitgevoerd")

log.ToonHtml (meldingen_pad)
