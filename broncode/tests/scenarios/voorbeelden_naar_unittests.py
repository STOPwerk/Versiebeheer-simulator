#======================================================================
#
# Hulpmiddel: kopieer de scenario's vanuit de voorbeelden naar de 
# unit tests.
#
# Er zijn een aantal voorbeelden die voor de STOP documentatie
# interessant zijn en dus in voorbeelden staan, maar die ook zeer
# geschikt zijn als unit test. Maak deze scenario's eerst in de 
# voorbeelden map, en kopieer ze daarna naar de unit tests met
# dit script.
#
# Dit script zorgt ervoor dat de bestanden met verwachte uitkomsten
# bestaan in de unit tests map en dat er een bestand voor procesopties
# bestaat.
#
#======================================================================

import json
import os
import shutil
import sys

helptekst = '''
voorbeelden_naar_unittests.py pad_naar_map_in_voorbeelden pad_naar_map_in_unit_tests 

pad_naar_map_in_voorbeelden  Pad naar een directory waaruit (recursief) gekopieerd 
pad_naar_map_in_unit_tests   Pad waarnaar gekopieerd moet worden
'''

if len (sys.argv) != 3:
    print (helptekst)
    sys.exit(2)

# Maak volledige paden van de argumenten
voorbeelden_map = sys.argv[1]
if not os.path.isdir (voorbeelden_map):
    print ('FOUT: map bestaat niet: ' + voorbeelden_map)
    print (helptekst)
    sys.exit(2)
voorbeelden_map = os.path.realpath (voorbeelden_map)

unittests_map = os.path.realpath (sys.argv[2])

def _SchrijfBestand (root, rel_map, file, inhoud):
    pad = os.path.join (unittests_root, file)
    if not os.path.isfile (pad):
        try:
            with open (pad, "w", encoding="utf-8") as bestand:
                bestand.write (inhoud)
        except Exception as e:
            print ('Kan bestand "' + (os.path.join (rel_map, file) if rel_map else file)  + '" niet schrijven: ' + str(e))

def _SchrijfOpties (root, rel_map, file, procesopties):
    pad = os.path.join (unittests_root, file)
    if os.path.isfile (pad):
        opties = { "Procesopties" : True }
        try:
            with open (pad, "r", encoding="utf-8") as bestand:
                opties = json.load (bestand)
        except Exception as e:
            print ('Kan json bestand "' + (os.path.join (rel_map, file) if rel_map else file)  + '" niet lezen: ' + str(e))
        for key, value in opties.items():
            if not key in procesopties:
                procesopties[key] = value
    else:
        procesopties["Procesopties"] = True
    try:
        with open (pad, "w", encoding="utf-8") as bestand:
            json.dump (procesopties, bestand, indent=4)
    except Exception as e:
        print ('Kan bestand "' + (os.path.join (rel_map, file) if rel_map else file)  + '" niet schrijven: ' + str(e))


# Start kopieeractie
for voorbeelden_root, dirs, files in os.walk (voorbeelden_map):
    
    # Onderzoek doel-map
    rel_map = voorbeelden_root[len (voorbeelden_map)+1:]
    unittests_root = os.path.join (unittests_map, rel_map) if rel_map else unittests_map
    unittests_overbodigeBestanden = set ()
    if os.path.isdir (unittests_root):
        for _, testdirs, testfiles in os.walk (unittests_root):
            # Alle .json en .xml bestanden worden weggehaald als ze niet overschreven worden
            for file in testfiles:
                isSpeciaalBestand = False
                if os.path.splitext(file)[1] == '.json':
                    for start in ['Test_Meldingen', 'Test_Versiebeheerinformatie', 'Test_BranchesCumulatief', 'Test_Proefversies', 'Test_ActueleToestanden', 'Test_CompleteToestanden', 'Test_Annotaties']:
                        if file.startswith (start):
                            isSpeciaalBestand = True
                            break
                if not isSpeciaalBestand:
                    unittests_overbodigeBestanden.add (file)

            for dir in testdirs:
                if not dir in dirs:
                    # Directory komt niet meer voor in de voorbeelden
                    pad = os.path.join (unittests_root, dir)
                    shutil.rmtree (pad, True)
            break
    else:
        # Maak doel-map
        try:
            os.makedirs (unittests_root, exist_ok=True)
        except Exception as e:
            print ('Kan map "' + rel_map + '" niet aanmaken: ' + str(e))
            if not os.path.isdir (unittests_root):
                sys.exit(2)

    # Kopieer de bestanden
    isScenario = False
    procesopties = {}
    for file in files:
        ext = os.path.splitext(file)[1]
        if ext == '.html' or ext == '.bat' or ext == '.sh':
            continue
        pad = os.path.join (voorbeelden_root, file)
        if ext == '.xml':
            try:
                # Lees als tekst, ga niet de XML parsen
                with open (pad, "r") as xmlFile:
                    data = xmlFile.read ()
            except Exception as e:
                print ('Kan xml bestand "' + (os.path.join (rel_map, file) if rel_map else file) + '" niet lezen: ' + str(e))
                continue
            if not '<ConsolidatieInformatie' in data or not 'https://standaarden.overheid.nl/stop/imop/data/' in data:
                # Dit kan geen ConsolidatieInformatie module zijn
                continue
            isScenario = True
        elif ext == '.json':
            try:
                with open (pad, "r") as jsonFile:
                    data = json.load (jsonFile)
            except Exception as e:
                print ('Kan json bestand "' + (os.path.join (rel_map, file) if rel_map else file) + '" niet lezen: ' + str(e))
                continue

            if not "Project" in data:
                isOpties = False
                for optie in ["Procesopties", "ActueleToestanden", "CompleteToestanden", "Proefversies", "Beschrijving", "Tijdreizen"]:
                    if optie in data:
                        isOpties = True
                if isOpties:
                    for optie in ["Beschrijving", "Uitwisselingen", "Tijdreizen"]:
                        if optie in data:
                            procesopties[optie] = data[optie]
                    continue
        else:
            continue

        if file in unittests_overbodigeBestanden:
            unittests_overbodigeBestanden.remove (file)
        try:
            shutil.copyfile (pad, os.path.join (unittests_root, file))
        except Exception as e:
            print ('Kan bestand "' + (os.path.join (rel_map, file) if rel_map else file) + '" niet kopiëren: ' + str(e))

    # Gooi de overbodige bestanden weg
    for file in unittests_overbodigeBestanden:
        try:
            os.remove (os.path.join (unittests_root, file))
        except:
            pass

    if isScenario:
        # Maak procesopties aan
        _SchrijfOpties (unittests_root, rel_map, 'Proces_unit_test.json', procesopties)

        # Maak verwachting-bestanden aan
        _SchrijfBestand (unittests_root, rel_map, 'Test_Meldingen_verwacht.json', '[]')
        _SchrijfBestand (unittests_root, rel_map, 'Test_Versiebeheerinformatie_verwacht.json', '["verwachting hier nog invullen"]')
        _SchrijfBestand (unittests_root, rel_map, 'Test_Proefversies_verwacht.json', '["verwachting hier nog invullen"]')
        _SchrijfBestand (unittests_root, rel_map, 'Test_ActueleToestanden_verwacht.json', '["verwachting hier nog invullen"]')
        _SchrijfBestand (unittests_root, rel_map, 'Test_CompleteToestanden_verwacht.json', '["verwachting hier nog invullen"]')
