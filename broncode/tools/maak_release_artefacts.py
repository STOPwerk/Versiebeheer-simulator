
#======================================================================
#
# Hulpmiddel: maak alle bestanden aan die voor een release van de
# simulator nodig zijn.
#
#======================================================================

from datetime import datetime
import json
import os
import shutil
import sys
import zipfile

helptekst = '''
maak_release_artefacts.py pad_naar_uitleverbestanden pad_naar_repo_root_map 

pad_naar_uitleverbestanden  Pad naar de directory waarin de extra bestanden voor de uitlevering staan
pad_naar_repo_root_map      Pad naar de root directory van de repo, waar de download.zip moet komen te staan.
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

repo_root_map = sys.argv[2]
if not os.path.isdir (repo_root_map):
    print ('FOUT: map bestaat niet: ' + repo_root_map)
    print (helptekst)
    sys.exit(2)
repo_root_map = os.path.realpath (repo_root_map)

# Lees configuratie
configuratiePad = os.path.join (uitleverbestanden_map, 'configuratie.json')
try:
    with open (configuratiePad, 'r') as json_file:
        configuratie = json.load(json_file)
except Exception as e:
    print ('Kan bestand "' + configuratiePad + '" niet lezen: ' + str(e))
    sys.exit(2)
configuratie["VERSIE"] = datetime.now().strftime ("%Y-%m-%d %H:%M:%S")

# Kopieer templates naar de root van de repo
templatesPad = os.path.join (uitleverbestanden_map, 'templates')
if os.path.isdir (templatesPad):
    for root, dirs, files in os.walk (templatesPad):
        for file in files:
            bronPad = os.path.join (root, file)
            doelPad = os.path.join (repo_root_map, bronPad[len(templatesPad)+1:])

            try:
                with open (bronPad, 'r', encoding='utf-8') as tekstfile:
                    tekst = tekstfile.read ()
                for term, waarde in configuratie.items ():
                    tekst = tekst.replace ('@@@' + term + '@@@', waarde)
                with open (doelPad, 'w', encoding='utf-8') as tekstfile:
                    tekstfile.write (tekst)
            except Exception as e:
                print ('Kan bestand "' + bronPad + '" niet kopiëren naar "' + doelPad + '": ' + str(e))
                sys.exit(2)

# Maak het bestand met de applicatie configuratie
appConfigPad = os.path.join (uitleverbestanden_map, 'applicatie_configuratie.py')
with open (appConfigPad, "w") as codeFile:
    codeFile.write ('''#======================================================================
#
# Configuratie van de applicatie
#
#======================================================================

Applicatie_versie = "versie d.d. ''' + configuratie["VERSIE"] + '''"

STOP_Documentatie_Url = "''' + configuratie["STOP_Documentatie_Url"] + '''"
STOP_Repository_Url = "''' + configuratie["STOP_Repository_Url"] + '''"
''')

# Maak een zip bestand om te downloaden
downloadPad = os.path.join (repo_root_map, 'download.zip')
with zipfile.ZipFile (downloadPad, 'w') as zip:
    for root, dirs, files in os.walk (os.path.join (repo_root_map, 'broncode', 'simulator')):
        for file in files:
            if file == 'applicatie_configuratie.py':
                zip.write (appConfigPad, 'simulator/' + file)
            elif file.startswith ('Versiebeheer.Simulator'):
                # Visual Studio bestanden
                pass
            elif file.startswith ('applicatie_web') or file == 'requirements.txt' or file == 'vercel.json':
                # Web bestanden
                pass
            else:
                zip.write (os.path.join (root, file), 'simulator/' + file)
        break

    zip.writestr (zipfile.ZipInfo("mijn voorbeelden/"), "") 
    for root, dirs, files in os.walk (os.path.join (uitleverbestanden_map, 'download')):
        for file in files:
            zip.write (os.path.join (root, file), file)
        break
