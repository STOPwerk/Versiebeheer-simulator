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

import json
import os.path
import xml.etree.ElementTree as ET

from applicatie_meldingen import Meldingen
from applicatie_procesopties import ProcesOpties, BenoemdeUitwisseling
from data_bg_project import Project, ProjectActie, ProjectActie_Publicatie, ProjectActie_Uitwisseling
from data_bg_versiebeheer import Versiebeheer
from data_lv_annotatie import Annotatie
from data_lv_consolidatie import GeconsolideerdInstrument
from data_lv_versiebeheerinformatie import Versiebeheerinformatie
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
        # Ingelezen annotaties
        # Lijst met instanties van Annotatie
        self.Annotaties = []
        # Ingelezen consolidatie-informatie modules
        # Lijst met instanties van ConsolidatieInformatieBron, gesorteerd op gemaaktOp
        self.ConsolidatieInformatie = []
        # Ingelezen projecten
        # Lijst met instanties van Project
        self.Projecten = []
        # Geeft aan of de bestanden in het pad samen de invoer voor een scenario vormen
        self.IsScenario = False
        # Geeft aan of de invoer voor het scenario valide is
        self.IsValide = True
        #--------------------------------------------------------------
        # Simulatie bevoegd gezag systemen
        #--------------------------------------------------------------
        # Het interne datamodel met versiebeheerinformatie
        self.Versiebeheer = Versiebeheer ()
        #--------------------------------------------------------------
        # Simulatie ontvangende systemen
        #--------------------------------------------------------------
        # Het interne datamodel met versiebeheerinformatie
        self.Versiebeheerinformatie = Versiebeheerinformatie ()
        # Informatie over de consolidatie van de instrumenten
        # key = workId van niet-geconsolideerd instrument, value = instantie van GeconsolideerdInstrument
        self.GeconsolideerdeInstrumenten = {}
        # Data benodigd voor de weergave die gedurende het proces verzameld wordt
        # Instantie van WeergaveData
        self.WeergaveData = None
        # Volgnummer voor de geconsolideerde instrumenten
        self._InstrumentVolgnummer = 1
        # Toestanden van alle geconsolideerde instrumenten; volgorde is niet van belang.
        # Dit wordt niet per instrument bijgehouden om een unieke ID over alle elementen te verkrijgen voor de weergave
        # Lijst van instanties van ToestandIdentificatie
        self._ToestandIdentificatie = []

    #------------------------------------------------------------------
    # Bron van de consolidatie-informatie
    #------------------------------------------------------------------
    class ConsolidatieInformatieBron:

        def __init__(self, module : ConsolidatieInformatie, actie : ProjectActie):
            """Maak de bron voor consolidatie-informatie aan.
            
            Argumenten:

            module ConsolidatieInformatie  De consolidatie-informatie is afkomstig uit een XML bestand
            actie ProjectActie  De consolidatie-informatie is afgeleid uit een projectactie
            """
            self.Module = module
            self.Actie = actie

        def GemaaktOp (self):
            """Geef het tijdstip van de uitwisseling van de consolidatie-informatie
            """
            return self.Actie.GemaaktOp if self.Module is None else self.Module.GemaaktOp

        def ConsolidatieInformatie (self):
            """Geef de speficicatie van de consolidatie-informatie
            """
            return self.Actie.ConsolidatieInformatie if self.Module is None else self.Module


#======================================================================
#
# Inlezen van de scenario bestanden
#
#======================================================================
    def _VoorScenario (self):
        """Onderzoek of een directory een scenario bevat"""
        self.ApplicatieLog.Detail ("Onderzoek de aanwezigheid van een scenario in '" + self.Pad + "'")

        def _IsScenario ():
            if not self.IsScenario:
                self.ApplicatieLog.Informatie ("Scenario gevonden in '" + self.Pad + "'")
                self.IsScenario = True

        annotatiesPerWorkId = {} # key = workId, value = {} met key = naam, value = instantie van Annotatie 
        projectenPerCode = {} # key = project code, value = instantie van Project
        instrumenten = set() # Instrumenten (work-identificaties) in consolidatie-informatie
        bronPerGemaaktOp = {} # key = gemaaktOp, value = ConsolidatieInformatieBron
        for root, dirs, files in os.walk (self.Pad):
            for file in files:
                # Probeer elk xml/json bestand in te lezen
                pad = os.path.join (root, file)
                fileType = os.path.splitext (pad)[1]
                if fileType == '.xml':
                    # Dit moet een ConsolidatieInformatie module zijn
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
                        if consolidatieInformatie.GemaaktOp in bronPerGemaaktOp:
                            self.Log.Fout ("Deze applicatie kan alleen ConsolidatieInformatie modules met verschillende gemaaktOp verwerken; " + consolidatieInformatie.GemaaktOp + " komt meerdere keren voor")
                            self.IsValide = False
                        else:
                            bronPerGemaaktOp[consolidatieInformatie.GemaaktOp] = Scenario.ConsolidatieInformatieBron(consolidatieInformatie, None)
                            for beoogdeVersie in consolidatieInformatie.BeoogdeVersies:
                                instrumenten.add (beoogdeVersie.WorkId)
                    else:
                        self.IsValide = False

                elif fileType == '.json':
                    # Lees eerst de json in
                    try:
                        with open (pad, "r", encoding = "utf-8") as jsonBestand:
                            data = json.load (jsonBestand)
                    except Exception as e:
                        self.ApplicatieLog.Fout ("Bestand '" + pad + "' bevat geen valide JSON/utf-8: " + str(e))
                        continue

                    if isinstance(data, dict):
                        # Kijk eerst of het een annotatie is
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

                        # Kijk dan of het een project is
                        project = Project.LeesJson (self.ApplicatieLog, pad, data)
                        if project:
                            _IsScenario ()
                            if project._IsValide:
                                if project.Code in projectenPerCode:
                                    self.Log.Fout ("Meerdere specificaties voor een project gevonden met dezelfde code '" + project.Code + "'")
                                    self.IsValide = False
                                else:
                                    projectenPerCode[project.Code] = project
                            else:
                                self.IsValide = False
                            continue

                        # Kijk als laatste of het opties zijn
                        opties = ProcesOpties.LeesJson (self.ApplicatieLog, pad, data)
                        if opties:
                            _IsScenario ()
                            if opties.IsValide:
                                if self.Opties is None:
                                    self.Opties = opties
                                else:
                                    self.Log.Fout ("Meerdere bestanden met procesopties gevonden")
                                    self.IsValide = False
                            else:
                                self.IsValide = False
                            continue

            if not self.IsScenario:
                self.ApplicatieLog.Detail ("Geen scenario gevonden in '" + self.Pad + "'")
                return None, True

        # Default opties
        if self.Opties is None:
            self.Opties = ProcesOpties (None if self.IsValide else False)

        self.Opties.Versiebeheer = False
        if len (projectenPerCode):
            self.Projecten = [projectenPerCode[p] for p in sorted (projectenPerCode.keys ())]
            if self.IsValide and not self.Opties.ActueleToestanden:
                self.Log.Waarschuwing ("Bepaling van actuele toestanden wordt altijd uitgevoerd als er projecten zijn gespecificeerd")
                self.Opties.ActueleToestanden = True
            self.Opties.Versiebeheer = True
            self.Versiebeheer = Versiebeheer ()

            for project in self.Projecten:
                for actie in project.Acties:
                    if actie.UitgevoerdOp in bronPerGemaaktOp:
                        self.Log.Fout ("Deze applicatie kan alleen ConsolidatieInformatie modules en projectacties met verschillende gemaaktOp verwerken; " + actie.UitgevoerdOp + " komt meerdere keren voor")
                        self.IsValide = False
                    else:
                        bronPerGemaaktOp[actie.UitgevoerdOp] = Scenario.ConsolidatieInformatieBron (None, actie)
                    isRevisie = True
                    if isinstance (actie, ProjectActie_Publicatie):
                        isRevisie = actie.SoortPublicatie == ProjectActie_Publicatie._SoortPublicatie_Revisie
                    elif not isinstance (actie, ProjectActie_Uitwisseling):
                        # Alleen publicaties en uitwisselingen worden opgenomen in de lijst met uitwisselingen
                        continue

                    # Gebruik de actie als beschrijving indien aanwezig
                    uwHeeftBeschrijving = False
                    for uw in self.Opties.Uitwisselingen:
                        if uw.GemaaktOp == actie.UitgevoerdOp:
                            uwHeeftBeschrijving = True
                            uw.IsRevisie = isRevisie
                    if not uwHeeftBeschrijving:
                        benoemd = BenoemdeUitwisseling ()
                        benoemd.GemaaktOp = actie.UitgevoerdOp 
                        benoemd.Naam = actie._Project.Code + ': ' + actie.SoortActie
                        benoemd.Beschrijving = actie.Beschrijving
                        benoemd.IsRevisie = isRevisie
                        self.Opties.Uitwisselingen.append (benoemd)

            # Voor weergave: alle niet-actie-gerelateerde modules komen in project "overig"
            projectOverig = None
            for bron in bronPerGemaaktOp.values ():
                if bron.Actie is None:
                    if projectOverig is None:
                        projectOverig = Project ()
                        projectOverig.Code = 'Overig'
                        projectOverig.Beschrijving = 'Alle uitwisselingen die gedaan worden in andere projecten.'
                        self.Projecten.append (projectOverig)
                    bron.Actie = ProjectActie (projectOverig)
                    bron.Actie.SoortActie = 'Publicatie'
                    bron.Actie.Beschrijving = 'Zie de STOP ConsolidatieInformatie module voor details.'
                    bron.Actie.UitgevoerdOp = bron.Module.GemaaktOp
                    bron.Actie._IsUitwisseling = True

        # Sorteer de consolidatie-informatie op volgorde van uitwisseling
        self.ConsolidatieInformatie = [bronPerGemaaktOp[gm] for gm in sorted (bronPerGemaaktOp.keys ())]

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
