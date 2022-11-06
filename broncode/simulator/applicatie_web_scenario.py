#======================================================================
#
# Invoer voor een simulatie-scenario dat als web request wordt
# doorgegeven
#
#======================================================================

from typing import Dict
import os.path

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
        self._Log = log
        self._Data = []
        fileData = []
        if not files is None and 'files[]' in files:
            files = files.getlist('files[]')
            for file in files:
                fileType = os.path.splitext (file.filename)[1]
                try:
                    data = file.stream.read ().decode("utf-8")
                    if fileType == '.json' or fileType == '.xml':
                        fileData.append ((file.filename, data.strip ()))
                    elif file.filename != '':
                        self._Log.Waarschuwing ("Bestand '" + file.filename + "' genegeerd; is geen .xml of .json bestand")
                except Exception as e:
                    self._Log.Fout ("Bestand '" + file.filename + "' bevat geen valide utf-8: " + str(e))
        if not onlineInvoer is None:
            fileData.extend ([(d, t.strip ()) for d, t in onlineInvoer.items () if d.startswith ('onlineInvoer')])
        for naam, data in fileData:
            if len(data) == 0:
                self._Log.Waarschuwing ("Leeg bestand '" + naam + "' genegeerd")
            else:
                self._Data.append ((naam, data))

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
