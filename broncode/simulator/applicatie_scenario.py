#======================================================================
#
# Invoer voor een simulatie-scenario
#
#----------------------------------------------------------------------
#
# Intern datamodel voor de invoer van een simulatie-scenario.
# De invoer bestaat uit een aantal STOP ConsolidatieInformatie
# modules en eventueel json bestanden met gegevens over annotaties
# en/of projecten, en een json bestand met opties voor het 
# simulatieproces.
#
#======================================================================

from cmath import log
from typing import Dict, List
import json
import os.path
import xml.etree.ElementTree as ET

from applicatie_meldingen import Meldingen
from applicatie_procesopties import ProcesOpties, BenoemdeUitwisseling
from data_bg_procesverloop import Procesvoortgang
from data_bg_versiebeheer import Versiebeheerinformatie as BGVersiebeheerinformatie
from data_lv_annotatie import Annotatie
from data_lv_consolidatie import GeconsolideerdInstrument
from data_lv_versiebeheerinformatie import Versiebeheerinformatie
from proces_bg_activiteit import Activiteit
from proces_bg_proces import BGProces
from stop_consolidatieinformatie import ConsolidatieInformatie
from weergave_data_toestanden import Toestandidentificatie

#======================================================================
#
# Itereren van locaties van scenario's
#
#----------------------------------------------------------------------
# Basisklasse
#======================================================================
class ScenarioIterator:

    def __init__ (self):
        """Initialiseer de iterator"""
        super ().__init__ ()
        # Aantal scenario's dat gevonden is
        self.AantalScenarios = 0
        # Aantal scenario's dat met succes is uitgevoerd
        self.AantalSucces = 0
        # Geeft aan dat de meldingen voor een scenario apart gehouden moeten wordn 
        # van de meldingen voor de hele applicatie
        self.MeldingenApart = True

    def VindElkScenario (self, lees_scenario):
        """Vind elk scenario en roep lees_scenario aan met de iterator als argument als een potentieel scenario gevonden is

        Argumenten:

        lees_scenario lambda(pad) Methode die voor elk potentieel scenario wordt aangeroepen.
                                  Geeft terug of er een scenario in de map staat.
        """
        raise 'VindScenarios is niet geïmplementeerd'

    def LeesBestanden (self, lees_json, lees_xml):
        """Lees alle JSON bestanden voor het potentiële scenario.

        Argumenten:

        lees_json lambda(pad,json) Methode die voor elk json bestand wordt aangeroepen.
                                   Argumenten zijn pad en inhoud van het bestand als tekst.
        lees_xml lambda(pad,xml) Methode die voor elk json bestand wordt aangeroepen.
                                 Argumenten zijn pad en inhoud van het bestand als tekst.
        """
        raise 'LeesBestanden is niet geïmplementeerd'

#----------------------------------------------------------------------
#
# Implementatie voor het doorlopen van directories
#
#----------------------------------------------------------------------
class ScenarioMappenIterator (ScenarioIterator):

    def __init__(self, log, directory_paden, recursief):
        """Maak een iterator aan voor het doorlopen van een boom met mappen
        
        Argumenten:
        log Meldingen  Verzameling van meldingen over het lokaliseren en uitvoeren van scenario's
        directory_pad string[]  lijst met directories waarin de applicatie begint met zoeken naar scenario's
        recursief boolean  Geeft aan dat er ook in subdirectories gezocht moet worden.
        """
        super ().__init__()
        self._Log = log
        self._DirectoryPaden = directory_paden
        self._Recursief = recursief
        # Map waarin een potentieel scenario staat
        self._DirectoryPad = None
        # Geeft aan of submappen van deze map nog onderzocht moeten worden
        self._DirectoryPadRecursief = None
        # Scenario dat ingelezen wordt
        self.Scenario : Scenario = None

    def VindElkScenario (self, lees_scenario):
        """Vind elk scenario en roep lees_scenario aan met de iterator als argument als een potentieel scenario gevonden is

        Argumenten:

        lees_scenario lambda(pad) Methode die voor elk potentieel scenario wordt aangeroepen.
                                  Geeft terug of er een scenario in de map staat.
        """
        for directory_pad in self._DirectoryPaden:
            self._VindElkScenario (directory_pad, lees_scenario)
    def _VindElkScenario (self, directory_pad, lees_scenario):
        if os.path.isdir (directory_pad):
            self._DirectoryPad = directory_pad
            self._DirectoryPadRecursief = False
            if not lees_scenario (self._DirectoryPad):
                if self._DirectoryPadRecursief:
                    for root, dirs, _ in os.walk (directory_pad):
                        for dir in dirs:
                            self._VindElkScenario (os.path.join (root, dir), lees_scenario)
                        break

    def LeesBestanden (self, lees_json, lees_xml):
        """Lees alle JSON bestanden voor het potentiële scenario.

        Argumenten:

        lees_json lambda(pad,json) Methode die voor elk json bestand wordt aangeroepen.
                                   Argumenten zijn pad en inhoud van het bestand als tekst.
        lees_xml lambda(pad,xml) Methode die voor elk json bestand wordt aangeroepen.
                                 Argumenten zijn pad en inhoud van het bestand als tekst.
        """
        self._Log.Detail ("Onderzoek de aanwezigheid van een scenario in '" + self._DirectoryPad + "'")
        meldScenario = True
        heeftBestanden = False
        for root, _, files in os.walk (self._DirectoryPad):

            for file in files:
                # Probeer elk json bestand in te lezen
                fileType = os.path.splitext (file)[1]
                if fileType == '.json':
                    heeftBestanden = True
                    pad = os.path.join (root, file)
                    data = None
                    try:
                        with open (pad, "r", encoding = "utf-8") as bestand:
                            data = bestand.read ()
                    except Exception as e:
                        self._Log.Fout ("Bestand '" + pad + "' bevat geen valide utf-8: " + str(e))
                    if not data is None:
                        lees_json (pad, data)

                        if not self.Scenario.Opties is None and self.Scenario.Opties.SimulatorScenario == False:
                            break
                        if meldScenario and self.Scenario.IsScenario:
                            meldScenario = False
                            self._Log.Detail ("Scenario gevonden in '" + self.Scenario.Pad + "'")

            for file in files:
                # Probeer elk xml bestand in te lezen
                pad = os.path.join (root, file)
                fileType = os.path.splitext (pad)[1]
                if fileType == '.xml':
                    heeftBestanden = True
                    pad = os.path.join (root, file)
                    data = None
                    try:
                        with open (pad, "r", encoding = "utf-8") as bestand:
                            data = bestand.read ()
                    except Exception as e:
                        self._Log.Fout ("Bestand '" + pad + "' bevat geen valide utf-8: " + str(e))
                    if not data is None:
                        lees_xml (pad, data)
                        if meldScenario and self.Scenario.IsScenario:
                            meldScenario = False
                            self._Log.Detail ("Scenario gevonden in '" + self.Scenario.Pad + "'")

            if not self.Scenario.IsScenario:
                self._DirectoryPadRecursief = self._Recursief
                break

        if not self.Scenario.IsScenario:
            if heeftBestanden:
                self._Log.Informatie ("Bestanden in '" + self.Scenario.Pad + "' zijn geen invoer voor een scenario")
            else:
                self._Log.Detail ("Geen scenario gevonden in '" + self.Scenario.Pad + "'")

#======================================================================
#
# Ontdekken en inlezen van scenario's
#
#======================================================================
class Scenario:
    
    @staticmethod
    def VoorElkScenario (log : Meldingen, iterator: ScenarioIterator, voer_uit):
        """Voer het proces uit voor elk gevonden scenario
        
        Argumenten:
        log Meldingen  Verzameling van meldingen over het lokaliseren en uitvoeren van scenario's
        directory_pad string[]  lijst met directories waarin de applicatie begint met zoeken naar scenario's
        recursief boolean  Geeft aan dat er ook in subdirectories gezocht moet worden.
        voer_uit lambda(Scenario)  Methode die voor elk gevonden scenario uitgevoerd moet worden,
                                               en die True/False teruggeeft om succesvolle uitvoering aan te geven.
        """
        iterator.AantalScenarios = 0
        iterator.AantalSucces = 0

        def __LeesScenario (pad):
            iterator.Scenario = scenario = Scenario (log, pad, iterator.MeldingenApart)
            scenario._VoorScenario (iterator)
            if scenario.IsScenario:
                iterator.AantalScenarios += 1
                if scenario.IsValide:
                    log.Informatie ("Voer applicatie uit voor het scenario in '" + scenario.Pad + "'")
                    succes = voer_uit (scenario)
                    log.Informatie ("Uitvoering afgerond voor het scenario in '" + scenario.Pad + "'")
                else:
                    if iterator.MeldingenApart:
                        log.Meldingen.extend (scenario.Log.Meldingen)
                    log.Fout ("Niet-valide invoer voor scenario in '" + scenario.Pad + "'")
                    succes = voer_uit (scenario)
                if succes:
                    iterator.AantalSucces += 1
            return scenario.IsScenario

        iterator.VindElkScenario (__LeesScenario)

#----------------------------------------------------------------------
# Aanmaken geconsolideerde instrumenten en toekenning identificatie 
# na eerste inwerkingtreding
#----------------------------------------------------------------------
    def GeconsolideerdeInstrument (self, workId) -> GeconsolideerdInstrument:
        """Geef de informatie over de consolidatie van het niet-geconsolideerde instrument.
        Maak het aan als het nog niet bestaat.
        
        Argumenten:
        workId string  Work identificatie van het niet-geonsolideerde instrument
        """
        geconsolideerd = self.GeconsolideerdeInstrumenten.get (workId)
        if geconsolideerd is None:
            instrument = self.Versiebeheerinformatie.Instrumenten.get (workId)
            if not instrument is None:
                self.GeconsolideerdeInstrumenten[workId] = geconsolideerd = GeconsolideerdInstrument (self, instrument)
        return geconsolideerd

#======================================================================
#
# Datamodel voor de scenario input en output
#
#======================================================================
    def __init__ (self, log, pad, meldingenApart):
        """Maak een nieuwe instantie voor het proces
        
        Argumenten:
        log Meldingen  Verzameling van meldingen over het lokaliseren en uitvoeren van scenario's
        pad string  Pad naar de directory met de invoer voor het proces
        meldingenApart bool Geeft aan dat de meldingen voor het scenario in een eigen log gezet moeten worden
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
        # Titel van het scenario
        self.Titel = os.path.basename (os.path.dirname (self.ResultaatPad))
        # Verzameling van meldingen specifiek voor dit proces
        self.Log = Meldingen (False) if meldingenApart else log
        # Ingelezen annotaties
        self.Annotaties : List[Annotatie] = []
        # Mix van BG activiteiten en ingelezen consolidatie-informatie modules
        # Lijst gesorteerd op gemaaktOp
        self.Gebeurtenissen : List[Scenario.Gebeurtenis] = []
        # Het proces zoals dat bij BG verloopt
        self.BGProces : BGProces = None
        # Geeft aan of de bestanden in het pad samen de invoer voor een scenario vormen
        self.IsScenario = None
        # Geeft aan of de invoer voor het scenario valide is
        self.IsValide = True
        #--------------------------------------------------------------
        # Simulatie bevoegd gezag systemen
        #--------------------------------------------------------------
        # Het BG-interne datamodel met informatie over de uitvoering van
        # activiteiten van het bevoegd gezag. Als alleen de ontvangende
        # systemen gesimuleerd worden, dan bevat de procesvoortgang alleen
        # de informatie over de uitwisselingen.
        self.Procesvoortgang = Procesvoortgang ()
        # Het BG-interne datamodel met versiebeheerinformatie
        self.BGVersiebeheerinformatie : BGVersiebeheerinformatie = None
        #--------------------------------------------------------------
        # Simulatie ontvangende systemen (zoals landelijke voorzieningen)
        #--------------------------------------------------------------
        # Het interne datamodel met versiebeheerinformatie
        self.Versiebeheerinformatie = Versiebeheerinformatie ()
        # Informatie over de consolidatie van de instrumenten
        # key = workId van niet-geconsolideerd instrument
        self.GeconsolideerdeInstrumenten : Dict[str,GeconsolideerdInstrument] = {}
        #--------------------------------------------------------------
        # Data benodigd voor de weergave die gedurende het proces verzameld wordt
        #--------------------------------------------------------------
        # Instantie van WeergaveData
        self.WeergaveData = None
        # Volgnummer voor de geconsolideerde instrumenten
        self._InstrumentVolgnummer = 1
        # Toestanden van alle geconsolideerde instrumenten; volgorde is niet van belang.
        # Dit wordt niet per instrument bijgehouden om een unieke ID over alle elementen te verkrijgen voor de weergave
        self._ToestandIdentificatie : List[Toestandidentificatie] = []

    #------------------------------------------------------------------
    # Bron van de consolidatie-informatie
    #------------------------------------------------------------------
    class Gebeurtenis:

        def __init__(self, consolidatieInformatie : ConsolidatieInformatie, activiteit : Activiteit):
            """Maak de gebeurtenis aan.
            
            Argumenten:

            consolidatieInformatie ConsolidatieInformatie  De gebeurtenis betreft de uitwisseling van informatie, waaronder een XML-module met consolidatie-informatie
            activiteit Activiteit  De gebeurtenis betreft een activiteit van BG
            """
            self.ConsolidatieInformatie = consolidatieInformatie
            self.Activiteit = activiteit

        def GemaaktOp (self):
            """Geef het tijdstip waarop de gebeurtenis plaatsvindt
            """
            if not self.ConsolidatieInformatie is None:
                return self.ConsolidatieInformatie.GemaaktOp
            return self.Activiteit.GemaaktOp

        def ConsolidatieInformatie (self):
            """Geef de specificatie van de consolidatie-informatie
            """
            if not self.ConsolidatieInformatie is None:
                return self.ConsolidatieInformatie
            return self.Activiteit.ConsolidatieInformatie


#======================================================================
#
# Inlezen van de scenario bestanden
#
#======================================================================
    def _VoorScenario (self, iterator: ScenarioIterator):
        """Onderzoek of de locatie waar de iterator nu is een scenario bevat"""
        def _IsScenario (inderdaad):
            if self.IsScenario is None or self.IsScenario != inderdaad:
                self.IsScenario = inderdaad

        annotatiesPerWorkId = {} # key = workId, value = {} met key = naam, value = instantie van Annotatie 
        instrumenten = set() # Instrumenten (work-identificaties) in consolidatie-informatie
        gebeurtenisPerGemaaktOp = {} # key = gemaaktOp, value = ConsolidatieInformatieBron

        def __LeesJsonBestand (pad : str, data : str):
            try:
                data = json.loads (data)
            except Exception as e:
                self.ApplicatieLog.Fout ("Bestand '" + pad + "' bevat geen valide JSON/utf-8: " + str(e))
                return

            if isinstance(data, dict):
                # Kijk eerst of het een annotatie is
                annotatie = Annotatie.LeesJson (self.ApplicatieLog, pad, data)
                if annotatie:
                    _IsScenario (True)
                    if annotatie._IsValide:
                        apw = annotatiesPerWorkId.get (annotatie.WorkId)
                        if apw is None:
                            annotatiesPerWorkId[annotatie.WorkId] = apw = {}
                        if annotatie.Naam in apw:
                            self.Log.Fout ("Meerdere specificaties voor een annotatie van " + annotatie.WorkId + " gevonden met dezelfde naam '" + annotatie.Naam + "'")
                            self.IsValide = False
                        else:
                            apw[annotatie.Naam] = annotatie
                            self.Log.Detail ("Bestand '" + pad + "' bevat een valide annotatiespecificatie")
                    else:
                        self.IsValide = False
                    return

                # Kijk dan of het een specificatie van BG activiteiten is
                bgproces = BGProces.LeesJson (self.ApplicatieLog, pad, data)
                if bgproces:
                    _IsScenario (True)
                    if bgproces._IsValide:
                        if self.BGProces is None:
                            self.BGProces = bgproces
                            self.Log.Detail ("Bestand '" + pad + "' bevat valide BG activiteitspecificaties")
                        else:
                            self.Log.Fout ("Meerdere specificaties voor een BG proces gevonden")
                            self.IsValide = False
                    else:
                        self.IsValide = False
                    return

                # Kijk als laatste of het opties zijn
                opties = ProcesOpties.LeesJson (self.ApplicatieLog, pad, data)
                if opties:
                    _IsScenario (opties.SimulatorScenario)
                    if opties.IsValide:
                        if self.Opties is None:
                            self.Opties = opties
                            self.Log.Detail ("Bestand '" + pad + "' bevat valide procesopties")
                        else:
                            self.Log.Fout ("Meerdere bestanden met procesopties gevonden")
                            self.IsValide = False
                    else:
                        self.IsValide = False
                    return

        def __LeesXmlBestand (pad : str, data : str):
            # Dit moet een ConsolidatieInformatie module zijn
            try:
                xml = ET.fromstring (data)
            except Exception as e:
                self.ApplicatieLog.Fout ("Bestand '" + pad + "' bevat geen valide XML: " + str(e))
                return
            if not ConsolidatieInformatie.IsConsolidatieInformatieBestand (xml):
                self.ApplicatieLog.Detail ("Bestand '" + pad + "' bevat geen ConsolidatieInformatie maar " + xml.tag)
                return

            _IsScenario (True)
            consolidatieInformatie = ConsolidatieInformatie.LeesXml (self.Log, pad, xml)
            if consolidatieInformatie and consolidatieInformatie.IsValide:
                if consolidatieInformatie.GemaaktOp in gebeurtenisPerGemaaktOp:
                    self.Log.Fout ("Deze applicatie kan alleen ConsolidatieInformatie modules met verschillende gemaaktOp verwerken; " + consolidatieInformatie.GemaaktOp + " komt meerdere keren voor")
                    self.IsValide = False
                else:
                    gebeurtenisPerGemaaktOp[consolidatieInformatie.GemaaktOp] = Scenario.Gebeurtenis(consolidatieInformatie, None)
                    for beoogdeVersie in consolidatieInformatie.BeoogdeVersies:
                        instrumenten.add (beoogdeVersie.WorkId)
            else:
                self.IsValide = False

        iterator.LeesBestanden (__LeesJsonBestand, __LeesXmlBestand)

        if not self.IsScenario:
            return None, True

        # Default opties
        if self.Opties is None:
            self.Opties = ProcesOpties (None if self.IsValide else False)

        self.Opties.BGProces = False
        if not self.BGProces is None:
            if self.IsValide and not self.Opties.ActueleToestanden:
                self.Log.Waarschuwing ("Bepaling van actuele toestanden wordt altijd uitgevoerd als BG activiteiten zijn gespecificeerd")
                self.Opties.ActueleToestanden = True
            self.Opties.BGProces = True
            if self.Opties.Beschrijving is None:
                self.Opties.Beschrijving = self.BGProces.Beschrijving
            self.BGVersiebeheerinformatie = BGVersiebeheerinformatie ()

            for activiteit in self.BGProces.Activiteiten:
                if activiteit.UitgevoerdOp in gebeurtenisPerGemaaktOp:
                    self.Log.Fout ("Deze applicatie kan alleen ConsolidatieInformatie modules en BG activiteiten met verschillende gemaaktOp verwerken; " + activiteit.UitgevoerdOp + " komt meerdere keren voor")
                    self.IsValide = False
                else:
                    gebeurtenisPerGemaaktOp[activiteit.UitgevoerdOp] = Scenario.Gebeurtenis (None, activiteit)

        # Sorteer de consolidatie-informatie op volgorde van uitwisseling
        self.Gebeurtenissen = [gebeurtenisPerGemaaktOp[gm] for gm in sorted (gebeurtenisPerGemaaktOp.keys ())]

        # Verifieer de WorkId van de annotaties en ken nummer (per work) toe
        self.Opties.Proefversies = False
        for workId, annotaties in annotatiesPerWorkId.items ():
            if not workId in instrumenten:
                self.Log.Fout ("De annotatie(s) '" + "', '".join (a.Naam for a in annotaties) + "' hoort/horen bij een onbekend instrument " + workId)
                self.IsValide = False
            else:
                for idx, a in enumerate (sorted (annotaties.values(), key = lambda a: a.Naam)):
                    a._Nummer = idx + 1
                    self.Annotaties.append (a)
                    if a.Synchronisatie == Annotatie._Synchronisatie_Versiebeheer:
                        self.Opties.Proefversies = True
