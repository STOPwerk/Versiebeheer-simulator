
#======================================================================
#
# Hulpmiddel: kopieer alle uit te leveren bestanden naar een kloon van
# de publieke repository.
#
#======================================================================

from codecs import ignore_errors    
from datetime import datetime
import json
import os
import shutil
import sys
import zipfile

helptekst = '''
maak_download_zip.py pad_naar_uitleverbestanden pad_naar_repo_root_map 

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

# Maak het bestand met de applicatie versie
versiePad = os.path.join (uitleverbestanden_map, 'applicatie_versie.py')
with open (versiePad, "w") as codeFile:
    codeFile.write ('''#======================================================================
#
# Versie van de applicatie
#
#======================================================================
Applicatie_versie = "versie d.d. ''' + datetime.now().strftime ("%Y-%m-%d %H:%M:%S") + '"')

# Maak een zip bestand om te downloaden
downloadPad = os.path.join (repo_root_map, 'download.zip')
downloadTemplatePad = os.path.join (uitleverbestanden_map, 'download.zip')
zipfileMode = 'w'
if os.path.isfile (downloadTemplatePad):
    try:
        shutil.copy (downloadTemplatePad, downloadPad)
    except Exception as e:
        print ('Kan bestand "' + downloadTemplatePad + '" niet kopiëren naar "' + downloadPad + '": ' + str(e))
        sys.exit(2)
    zipfileMode = 'a'

with zipfile.ZipFile (downloadPad, zipfileMode) as zip:
    for root, dirs, files in os.walk (os.path.join (repo_root_map, 'broncode', 'simulator')):
        for file in files:
            if file == 'applicatie_versie.py':
                zip.write (versiePad, 'simulator/' + file)
            else:
                zip.write (os.path.join (root, file), 'simulator/' + file)
        break
