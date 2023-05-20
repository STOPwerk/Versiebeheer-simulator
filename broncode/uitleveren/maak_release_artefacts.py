
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

# Lees configuratie en update het versienummer
configuratiePad = os.path.join (uitleverbestanden_map, 'configuratie.json')
try:
    with open (configuratiePad, 'r', encoding='utf-8') as json_file:
        configuratie = json.load(json_file)
except Exception as e:
    print ('Kan bestand "' + configuratiePad + '" niet lezen: ' + str(e))
    sys.exit(2)
configuratie["VERSIE"] = datetime.now().strftime ("%Y-%m-%d %H:%M:%S")
try:
    with open (configuratiePad, 'w', encoding='utf-8') as json_file:
        json.dump (configuratie, json_file, indent=4)
except Exception as e:
    print ('Kan bestand "' + configuratiePad + '" niet schrijven: ' + str(e))
    sys.exit(2)


# Vervang het versienummer in publiceer_git.bat
publiceer_git_Pad = os.path.join (uitleverbestanden_map, 'publiceer_git_template.bat')
try:
    with open (publiceer_git_Pad, 'r', encoding='utf-8') as batFile:
        script = batFile.read ()
except Exception as e:
    print ('Kan bestand "' + publiceer_git_Pad + '" niet lezen: ' + str(e))
    sys.exit(2)
for term, waarde in configuratie.items ():
    script = script.replace ('@@@' + term + '@@@', waarde)
publiceer_git_Pad = os.path.join (uitleverbestanden_map, 'publiceer_git.bat')
try:
    with open (publiceer_git_Pad, 'w', encoding='utf-8') as batFile:
        batFile.write (script)
except Exception as e:
    print ('Kan bestand "' + publiceer_git_Pad + '" niet schrijven: ' + str(e))
    sys.exit(2)

# Vervang de wiki documentatie
wiki_doel_pad = os.path.join (uitleverbestanden_map, 'wiki')
for root, dirs, files in os.walk (wiki_doel_pad):
    for file in files:
        try:
            os.remove (os.path.join (root, file))
        except Exception as e:
            print ('Kan bestaand wiki bestand "' + file + '" niet weggooien: ' + str(e))
            sys.exit(2)
    for dir in dirs:
        if dir == '.git':
            continue
        try:
            shutil.rmtree (os.path.join (root, dir))
        except Exception as e:
            print ('Kan bestaand wiki map "' + dir + '" niet weggooien: ' + str(e))
            sys.exit(2)
    break
try:
    shutil.copytree (os.path.join (uitleverbestanden_map, 'wiki_extra'), wiki_doel_pad, dirs_exist_ok=True)
except Exception as e:
    print ('Kan map wiki-extra niet kopieren naar de wiki repository: ' + str(e))
    sys.exit(2)
try:
    shutil.copytree (os.path.join (repo_root_map, 'broncode', 'wiki'), wiki_doel_pad, dirs_exist_ok=True)
except Exception as e:
    print ('Kan map broncode/wiki niet kopieren naar de wiki repository: ' + str(e))
    sys.exit(2)


# Maak een zip bestand om te downloaden
downloadPad = os.path.join (repo_root_map, 'download.zip')
with zipfile.ZipFile (downloadPad, 'w') as zip:
    for root, dirs, files in os.walk (os.path.join (repo_root_map, 'broncode', 'simulator')):
        for file in files:
            if file.startswith ('Versiebeheer.Simulator'):
                # Visual Studio bestanden
                pass
            elif file == 'vercel.json':
                # Web deployment bestanden
                pass
            else:
                try:
                    with open (os.path.join (root, file), 'r') as tekstfile:
                        tekst = tekstfile.read ()
                except Exception as e:
                    print ('Kan bestand "' + file + '" niet lezen: ' + str(e))
                    sys.exit(2)
                for term, waarde in configuratie.items ():
                    tekst = tekst.replace ('@@@' + term + '@@@', waarde)
                zip.writestr ('simulator/' + file, tekst)
        break

    zip.writestr (zipfile.ZipInfo("mijn voorbeelden/"), "") 
    for root, dirs, files in os.walk (os.path.join (uitleverbestanden_map, 'download')):
        for file in files:
            zip.write (os.path.join (root, file), file)
        break
