
#======================================================================
#
# Hulpmiddel: vervang parameters in alle bestanden in een directory
# (niet recursief)
#
#======================================================================

from datetime import datetime
import json
import os
import shutil
import sys
import zipfile

helptekst = '''
pas_configuratie_toe.py pad_naar_uitleverbestanden pad_naar_te_configureren_bestanden 

pad_naar_uitleverbestanden         Pad naar de directory waarin de extra bestanden voor de uitlevering staan
pad_naar_te_configureren_bestanden Pad naar de directory met geparametriseerde bestanden
'''

if len (sys.argv) != 3:
    print (helptekst)
    sys.exit(2)

# Maak volledige paden van de argumenten
uitleverbestanden_map = sys.argv[1]
if not os.path.isdir (uitleverbestanden_map):
    print ('FOUT: map bestaat niet: ' + uitleverbestanden_map)
    print (helptekst)
    sys.exit(2)
uitleverbestanden_map = os.path.realpath (uitleverbestanden_map)

bestanden_map = sys.argv[2]
if not os.path.isdir (bestanden_map):
    print ('FOUT: map bestaat niet: ' + bestanden_map)
    print (helptekst)
    sys.exit(2)
bestanden_map = os.path.realpath (bestanden_map)

# Lees configuratie
configuratiePad = os.path.join (uitleverbestanden_map, 'configuratie.json')
try:
    with open (configuratiePad, 'r') as json_file:
        configuratie = json.load(json_file)
except Exception as e:
    print ('Kan bestand "' + configuratiePad + '" niet lezen: ' + str(e))
    sys.exit(2)
configuratie["VERSIE"] = datetime.now().strftime ("%Y-%m-%d %H:%M:%S")

# Onderzoek de bestanden
if os.path.isdir (bestanden_map):
    for root, dirs, files in os.walk (bestanden_map):
        for file in files:
            ext = os.path.splitext(file)[1]
            if not ext is None and ext in ['.py', '.css', '.js', '.htm', '.html', '.txt', '.md', '.bat']:
                bronPad = os.path.join (root, file)
                try:
                    with open (bronPad, 'r') as tekstfile:
                        tekst = tekstfile.read ()
                    vervangen = tekst
                    for term, waarde in configuratie.items ():
                        vervangen = vervangen.replace ('@@@' + term + '@@@', waarde)
                    if vervangen != tekst:
                        with open (bronPad, 'w') as tekstfile:
                            tekstfile.write (vervangen)
                except Exception as e:
                    print ('Kan parameters in bestand "' + bronPad + '" niet vervangen: ' + str(e))
                    sys.exit(2)
        break
