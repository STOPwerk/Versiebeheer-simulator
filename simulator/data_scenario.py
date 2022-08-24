#======================================================================
#
# Invoer voor een consolidatie-scenario
#
#----------------------------------------------------------------------
#
# Intern datamodel voor de invoer van een consolidatie-scenario.
# De invoer bestaat uit een aantal STOP ConsolidatieInformatie
# modules en eventueel json bestanden met gegevens over annotaties
# en een json bestand met opties voor het consolidatieproces.
#
#======================================================================

import json
import os.path
import xml.etree.ElementTree as ET

from applicatie_meldingen import Meldingen
from data_annotatie import Annotatie
from data_consolidatie import GeconsolideerdInstrument
from data_procesopties import ProcesOpties
from data_versiebeheerinformatie import Versiebeheerinformatie
from stop_consolidatieinformatie import ConsolidatieInformatie

#======================================================================
#
# Ontdekken en inlezen van scenario's
#
#======================================================================
class Scenario:
    
    @staticmethod
    def VoorElkScenario (log, directory_paden, recursief, voer_uit):
        """Voer het proces uit voor elk gevonden scenario
        
        Argumenten:
        log Meldingen  Verzameling van meldingen over het lokaliseren en uitvoeren van scenario's
        directory_pad string[]  lijst met directories waarin de applicatie begint met zoeken naar scenario's
        recursief boolean  Geeft aan dat er ook in subdirectories gezocht moet worden.
        voer_uit lambda(Scenario)  Methode die voor elk gevonden scenario uitgevoerd moet worden,
                                               en die True/False teruggeeft om succesvolle uitvoering aan te geven.

        Geeft terug: (aantal scenario's, aantal succes)
        """
        aantalScenarios = 0
        aantalSucces = 0
        for directory_pad in directory_paden:
            if os.path.isdir (directory_pad):
                scenario = Scenario (log, directory_pad)
                scenario._VoorScenario ()
                if scenario.IsScenario:
                    aantalScenarios += 1
                    if scenario.IsValide:
                        log.Informatie ("Voer applicatie uit voor het scenario in '" + scenario.Pad + "'")
                        succes = voer_uit (scenario)
                        log.Informatie ("Uitvoering afgerond voor het scenario in '" + scenario.Pad + "'")
                    else:
                        log.Fout ("Niet-valide invoer voor scenario in '" + directory_pad + "'")
                        succes = voer_uit (scenario)
                    if succes:
                        aantalSucces += 1
                elif recursief:
                    for root, dirs, files in os.walk (directory_pad):
                        asc, asu = Scenario.VoorElkScenario (log, [os.path.join (root, dir) for dir in dirs], recursief, voer_uit)
                        aantalScenarios += asc
                        aantalSucces += asu
                        break
        return aantalScenarios, aantalSucces

#----------------------------------------------------------------------
# Aanmaken geconsolideerde instrumenten en toekenning identificatie 
# na eerste inwerkingtreding
#----------------------------------------------------------------------
    def GeconsolideerdeInstrument (self, workId):
        """Geef de informatie over de consolidatie van het niet-geconsolideerde instrument.
        Maak het aan als het nog niet bestaat.
        
        Argumenten:
        workId string  Work identificatie van het niet-geonsolideerde instrument
        """
        geconsolideerd = self.GeconsolideerdeInstrumenten.get (workId)
        if geconsolideerd is None:
            self.GeconsolideerdeInstrumenten[workId] = geconsolideerd = GeconsolideerdInstrument (self, self.Versiebeheerinformatie.Instrumenten[workId])
        return geconsolideerd

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, log, pad):
        """Maak een nieuwe instantie voor het proces
        
        Argumenten:
        log Meldingen  Verzameling van meldingen over het lokaliseren en uitvoeren van scenario's
        pad string  Pad naar de directory met de invoer voor het proces
        """
        #--------------------------------------------------------------
        # Invoer
        #--------------------------------------------------------------
        self.ApplicatieLog = log
        self.Pad = pad
        # Opties voor het (gedeeltelijk) uitvoeren van het consolidatieproces
        # Instantie van ProcesOpties
        self.Opties = None
        # Pad van de webpagina met resultaten van dit proces
        self.ResultaatPad = os.path.join (self.Pad, "Simulator_Resultaat.html")
        # Verzameling van meldingen specifiek voor dit proces
        self.Log = Meldingen (False)
        # Ingelezen consolidatie-informatie modules
        # Lijst met instanties van ConsolidatieInformatie, gesorteerd op gemaaktOp
        self.ConsolidatieInformatie = []
        # Ingelezen annotaties
        # Lijst met instanties van Annotatie
        self.Annotaties = []
        # Geeft aan of de bestanden in het pad samen de invoer voor een scenario vormen
        self.IsScenario = False
        # Geeft aan of de invoer voor het scenario valide is
        self.IsValide = True
        #--------------------------------------------------------------
        # Resultaten
        #--------------------------------------------------------------
        # Het interne datamodel met versiebeheerinformatie
        self.Versiebeheerinformatie = Versiebeheerinformatie ()
        # Informatie over de consolidatie van de instrumenten
        # key = workId van niet-geconsolideerd instrument, value = instantie van GeconsolideerdInstrument
        self.GeconsolideerdeInstrumenten = {}
        # Data benodigd voor de weergave die gedurende het proces verzameld wordt
        # Instantie van WeergaveData
        self.WeergaveData = None
        # Toestanden van alle geconsolideerde instrumenten; volgorde is niet van belang.
        # Dit wordt niet per instrument bijgehouden om een unieke ID over alle elementen te verkrijgen voor de weergave
        # Lijst van instanties van ToestandIdentificatie
        self._ToestandIdentificatie = []

    def _VoorScenario (self):
        """Onderzoek of een directory een scenario bevat"""
        self.ApplicatieLog.Detail ("Onderzoek de aanwezigheid van een scenario in '" + self.Pad + "'")

        def _IsScenario ():
            if not self.IsScenario:
                self.ApplicatieLog.Informatie ("Scenario gevonden in '" + self.Pad + "'")
                self.IsScenario = True

        annotatiesPerWorkId = {}
        instrumenten = set() # Instrumenten (work-identificaties) in consolidatieinformatie
        for root, dirs, files in os.walk (self.Pad):
            # Probeer eerst alle ConsolidatieInformatie modules te lezen
            for file in files:
                pad = os.path.join (root, file)
                fileType = os.path.splitext (pad)[1]
                if fileType == '.xml':
                    try:
                        xml = ET.parse (pad).getroot ()
                    except Exception as e:
                        self.ApplicatieLog.Fout ("Bestand '" + pad + "' bevat geen valide XML: " + str(e))
                        continue
                    if not ConsolidatieInformatie.IsConsolidatieInformatieBestand (xml):
                        self.ApplicatieLog.Detail ("Bestand '" + pad + "' bevat geen ConsolidatieInformatie maar " + xml.tag)
                        continue

                    if not self.IsScenario:
                        self.ApplicatieLog.Informatie ("Scenario gevonden in '" + self.Pad + "'")
                        self.IsScenario = True
                    consolidatieInformatie = ConsolidatieInformatie.LeesXml (self.Log, pad, xml)
                    if consolidatieInformatie and consolidatieInformatie.IsValide:
                        self.ConsolidatieInformatie.append (consolidatieInformatie)
                        for beoogdeVersie in consolidatieInformatie.BeoogdeVersies:
                            instrumenten.add (beoogdeVersie.WorkId)
                    else:
                        self.IsValide = False

                elif fileType == '.json':
                    try:
                        with open (pad, "r", encoding = "utf-8") as jsonBestand:
                            data = json.load (jsonBestand)
                    except Exception as e:
                        self.ApplicatieLog.Fout ("Bestand '" + pad + "' bevat geen valide JSON/utf-8: " + str(e))
                        continue

                    if isinstance(data, dict):
                        annotatie = Annotatie.LeesJson (self.ApplicatieLog, pad, data)
                        if annotatie:
                            _IsScenario ()
                            if annotatie._IsValide:
                                apw = annotatiesPerWorkId.get (annotatie.WorkId)
                                if apw is None:
                                    annotatiesPerWorkId[annotatie.WorkId] = apw = {}
                                if annotatie.Naam in apw:
                                    self.Log.Fout ("Meerdere specificaties voor een annotatie van " + annotatie.WorkId + " gevonden met dezelfde naam '" + annotatie.Naam + "'")
                                    self.IsValide = False
                                else:
                                    apw[annotatie.Naam] = annotatie
                            else:
                                self.IsValide = False
                            continue

                        opties = ProcesOpties.LeesJson (self.ApplicatieLog, pad, data)
                        if opties:
                            _IsScenario ()
                            if opties.IsValide:
                                if self.Opties is None:
                                    self.Opties = opties
                                else:
                                    self.Log.Fout ("Meerdere opties voor de geautomatiseerde consolidatie gevonden")
                                    self.IsValide = False
                            else:
                                self.IsValide = False
                            continue

            if not self.IsScenario:
                self.ApplicatieLog.Detail ("Geen scenario gevonden in '" + self.Pad + "'")
                return None, True

        # Sorteer de consolidatie-informatie op volgorde van uitwisseling
        self.ConsolidatieInformatie.sort (key = lambda ci: ci.GemaaktOp)
        laastGemaaktOp = None
        for ci in self.ConsolidatieInformatie:
            if ci.GemaaktOp == laastGemaaktOp:
                self.Log.Fout ("Deze applicatie kan alleen ConsolidatieInformatie modules met verschillende gemaaktOp verwerken; " + ci.GemaaktOp + " komt meerdere keren voor")
                self.IsValide = False
            laastGemaaktOp = ci.GemaaktOp

        # Default opties
        if self.Opties is None:
            self.Opties = ProcesOpties (None if self.IsValide else False)

        # Verifieer de WorkId van de annotaties en ken nummer (per work) toe
        self.Opties.Proefversies = False
        for workId, annotaties in annotatiesPerWorkId.items ():
            if not workId in instrumenten:
                self.Log.Fout ("De annotatie(s) '" + "', '".join (a.Naam for a in annotatie) + "' hoort/horen bij een onbekend instrument " + workId)
                self.IsValide = False
            else:
                for idx, a in enumerate (sorted (annotaties.values(), key = lambda a: a.Naam)):
                    a._Nummer = idx + 1
                    self.Annotaties.append (a)
                    if a.ViaVersiebeheer:
                        self.Opties.Proefversies = True
