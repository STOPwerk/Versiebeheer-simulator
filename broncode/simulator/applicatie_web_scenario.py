#======================================================================
#
# Invoer voor een simulatie-scenario dat als web request wordt
# doorgegeven
#
#======================================================================

from typing import Dict
from io import BytesIO
import os.path
from zipfile import ZipFile

from applicatie_scenario import ScenarioIterator

#======================================================================
#
# Implenentatie van de scenario iterator voor data in het web request
#
#======================================================================
class ScenarioPostedDataIterator (ScenarioIterator):

    def __init__(self, log, onlineInvoer, files):
        """Maak een iterator aan voor het doorlopen van een boom met mappen
        
        Argumenten:
        log Meldingen  Verzameling van meldingen over het lokaliseren en uitvoeren van scenario's
        onlineInvoer {} Form data, dus de tekst in de tekstvakken
        files {} Meegestuurde bestanden
        """
        super ().__init__()
        self.MeldingenApart = False
        self._Log = log
        self._Data = []
        if not files is None and 'files[]' in files:
            files = files.getlist('files[]')
            for file in files:
                fileType = os.path.splitext (file.filename)[1]
                if fileType == '.zip':
                    try:
                        with ZipFile(BytesIO(file.stream.read ()), 'r') as zipData:
                            for zipFile in zipData.infolist ():
                                fileType = os.path.splitext (zipFile.filename)[1]
                                if fileType == '.json' or fileType == '.xml':
                                    try:
                                        data = zipData.read(zipFile.filename).strip ()
                                    except Exception as e:
                                        self._Log.Fout ("Kan bestand '" + zipFile.filename + "' in '" + file.filename + "' niet lezen: " + str(e))
                                        continue
                                    if len(data) == 0:
                                        self._Log.Waarschuwing ("Leeg bestand '" + zipFile.filename + "' in '" + file.filename + "' genegeerd")
                                    else:
                                        self._Data.append ((zipFile.filename, data))
                                elif zipFile.filename != '':
                                    self._Log.Waarschuwing ("Bestand '" + zipFile.filename + "' in '" + file.filename + "' genegeerd; is geen .xml of .json bestand")
                    except Exception as e:
                        self._Log.Fout ("Bestand '" + file.filename + "' is geen valide zip bestand: " + str(e))
                else:
                    try:
                        data = file.stream.read ().decode("utf-8").strip ()
                        if fileType == '.json' or fileType == '.xml':
                            if len(data) == 0:
                                self._Log.Waarschuwing ("Leeg bestand '" + file.filename + "' genegeerd")
                            else:
                                self._Data.append ((file.filename, data))
                        elif file.filename != '':
                            self._Log.Waarschuwing ("Bestand '" + file.filename + "' genegeerd; is geen .xml of .json bestand")
                    except Exception as e:
                        self._Log.Fout ("Bestand '" + file.filename + "' bevat geen valide utf-8: " + str(e))
        if not onlineInvoer is None:
            fileData = [(d, t.strip ()) for d, t in onlineInvoer.items () if d.startswith ('onlineInvoer')]
            self._Data.extend ((d,t) for d,t in fileData if len(t) > 0)

    def VindElkScenario (self, lees_scenario):
        """Vind elk scenario en roep lees_scenario aan met de iterator als argument als een potentieel scenario gevonden is

        Argumenten:

        lees_scenario lambda(pad) Methode die voor elk potentieel scenario wordt aangeroepen.
                                  Geeft terug of er een scenario in de map staat.
        """
        if len (self._Data) > 0:
            lees_scenario ("(data in request)")
        else:
            self._Log.Waarschuwing ("Geen invoerbestanden opgestuurd")

    def LeesBestanden (self, lees_json, lees_xml):
        """Lees alle JSON bestanden voor het potentiële scenario.

        Argumenten:

        lees_json lambda(pad,json) Methode die voor elk json bestand wordt aangeroepen.
                                   Argumenten zijn pad en inhoud van het bestand als tekst.
        lees_xml lambda(pad,xml) Methode die voor elk json bestand wordt aangeroepen.
                                 Argumenten zijn pad en inhoud van het bestand als tekst.
        """
        self.Scenario.Titel = "Versiebeheer-simulator resultaat"
        self.Scenario.ResultaatPad = None
        for naam, data in self._Data:
            filetype = os.path.splitext (naam)[1]
            if filetype == '':
                if data[0] == '<':
                    filetype = '.xml'
                else:
                    filetype = '.json'
            if filetype == '.xml':
                lees_xml (naam, data)
            elif filetype == '.json':
                lees_json (naam, data)
