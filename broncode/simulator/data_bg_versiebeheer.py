#======================================================================
#
# Versiebeheer bij een bevoegd gezag.
#
#======================================================================
#
# De bevoegd gezag software zal moeten beschikken over een intern 
# versiebeheer dat tenminste een bepaalde hoeveelheid informatie
# bevat (of kan afleiden). Deze module bevat het datamodel voor
# het interne versiebeheer voor deze applicatie. Het datamodel 
# kent geen historie; activiteiten overschrijven oude informatie.
# Waar het versiebeheer in de landelijke voorzieningen per instrument
# uitgevoerd wordt en tot toestanden leidt, is dat hier per branch 
# en per datum (met mogelijk meerdere instrumenten).
#
# Dit interne datamodel beheert per branch/doel de regeling- en
# informatieobjectversies van de gehele regelgeving van het bevoegd
# gezag in deze simulator, en gebruikt het ook om de activiteiten van
# een adviesbureau vast te leggen. Dat is niet erg realistisch maar
# maakt de code eenvoudiger zonder in te leveren op de uitlegbaarheid
# van de interactie tussen BG-intern versiebeheer en STOP versiebeheer.
#
# De simulator kan een branch beheren die gebaseerd is op geldende 
# regelgeving of op een andere branch. Daarbij wordt ervan uitgegaan
# dat bij het overnemen van de inhoud van geldende regelgeving altijd
# voor de nu geldende regelgeving gekozen wordt - in de praktijk zal
# vaak voor de laatstbesloten versie gekozen worden,tenzij die te ver 
# in de toekomst ligt. Bij het volgen van een andere branch wordt geen
# rekening gehouden met versies op de andere branch die nog niet
# gepubliceerd zijn en mogelijk pas na de huidige branch tot een
# publicatie kunnen leiden. Deze beperkingen doen niet af aan de
# systematiek van het versiebeheer, maar maken de user interactie / 
# scenario specificatie voor de simulator veel eenvoudiger.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from copy import copy

from applicatie_meldingen import Meldingen
from data_doel import Doel

from stop_consolidatieinformatie import ConsolidatieInformatie, Momentopname, VoorInstrument, BeoogdeVersie, Intrekking, Terugtrekking, TerugtrekkingIntrekking, TerugtrekkingTijdstempel, Tijdstempel

#======================================================================
#
# Versiebeheerinformatie: minimale informatie die in de bevoegd gezag
#                         software beschikbaar moet zijn.
#
#======================================================================
#region Versiebeheerinformatie
#----------------------------------------------------------------------
#
# Alle versiebeheer informatie die (in de simulator) voor een BG 
# bijgehouden wordt.
#
#----------------------------------------------------------------------
class Versiebeheerinformatie:

    def __init__ (self):
        """Maak een nieuwe instantie van het versiebeheer bij het bevoegd gezag.
        """
        #--------------------------------------------------------------
        # Intern versiebeheer
        #--------------------------------------------------------------
        # Informatie over alle doelen die door bevoegd gezag beheerd worden
        self.Branches : Dict[Doel,Branch] = {}
        # Informatie over alle bekende instrumenten
        # key = workId en naam, value = instrument
        self.Instrumenten : Dict[str,Instrument] = {}
        #--------------------------------------------------------------
        # Ondersteuning consolidatieproces
        #--------------------------------------------------------------
        # De consolidatie kan bij het bevoegd gezag op het niveau van branches
        # worden bijgehouden. Dat wordt vertaald naar informatie per instrument
        # bij het omzetten naar STOP consolidatie-informatie.
        # Lijst is gesorteerd op volgorde van inwerkingtreding/juridischGeldigVanaf
        self.Consolidatie : List[Consolidatie] = {}

    def WerkConsolidatieBij(self, applicatielog : Meldingen, verslag: Meldingen, gemaaktOp : str) -> bool:
        """Werk de consolidatie bij op basis van de huidige stand van het versiebeheer

        Argumenten:

        applicatielog Meldingen  Meldingen voor fouten/waarschuwingen voor het scenario
        verslag Meldingen  Meldingen voor de uitvoering van de consolidatie
        gemaaktOp str Tijdstip waarop de consolidatie uitgevoerd wordt

        Geeft terug of de consolidatie bijgewerkt kon worden
        """
        return Consolidatie._WerkConsolidatieBij (self, applicatielog, verslag, gemaaktOp[0:10])

#----------------------------------------------------------------------
#
# Instrumenten waarvoor versiebeheer uitgevoerd wordt
#
#----------------------------------------------------------------------
class Instrument:

    @staticmethod
    def Bepaal (activiteit, versiebeheer: Versiebeheerinformatie, naam : str):
        """Bepaal aan de hand van de naam van het instrument welk soort instrument het is

        Argumenten:

        activiteit Activiteit  De activiteit die door BG wordt uitgevoerd
        naam str  De naam van het instrument zoals in de specificatie is opgegeven
        """
        instrument = versiebeheer.Instrumenten.get (naam)
        if not instrument is None:
            return instrument
        instrument = Instrument ()
        if naam.startswith ('reg_'):
            instrument._Soort = 'Regeling'
            instrument.Naam = naam
            instrument.WorkId = '/akn/nl/act/' + activiteit._BGProcess.BGCode + '/' + activiteit.UitgevoerdOp[0:4] + '/' + naam
        elif naam.startswith ('gio_'):
            instrument._Soort = 'GIO'
            instrument.Naam = naam
            instrument.WorkId = '/join/id/regdata/' + activiteit._BGProcess.BGCode + '/' + activiteit.UitgevoerdOp[0:4] + '/' + naam
        elif naam.startswith ('pdf_'):
            instrument._Soort = 'PDF'
            instrument.Naam = naam
            instrument.WorkId = '/join/id/regdata/' + activiteit._BGProcess.BGCode + '/' + activiteit.UitgevoerdOp[0:4] + '/' + naam
        elif naam.startswith ('/akn/nl/act/'):
            instrument._Soort = 'Regeling'
            instrument.Naam = naam[naam.rindex('/')+1:]
            instrument.WorkId = naam
        elif naam.startswith ('/join/id/regdata/'):
            instrument.Naam = naam[naam.rindex('/')+1:]
            instrument.WorkId = naam
            if instrument.Naam.startswith ('pdf_'):
                instrument._Soort = 'PDF'
            else:
                instrument._Soort = 'GIO'
        else:
            instrument = None
            return
        versiebeheer.Instrumenten[instrument.Naam] = instrument
        versiebeheer.Instrumenten[instrument.WorkId] = instrument

        return instrument

    def __init__(self):
        # Verkorte identificatie van het instrument
        self.Naam : str = None
        # Identificatie van het instrument
        self.WorkId : str = None
        # Soort instrument
        self._Soort : str = None;

    def MaakExpressionId (self, uitgevoerdOp, branch):
        """Maak een expressionId voor een nieuwe instrumentversie

        Argumenten:

        uitgevoerdOp string  Het tijdstip waarop de activiteit wordt uitgevoerd waar de instrumentversie uit ontstaat.
        branch Branch  De branch waarvoor de instrumentversie wordt aangemaakt
        """
        expressionId = self.WorkId
        if self._Soort == "Regeling":
            expressionId += "/nl"
        expressionId += "@" + uitgevoerdOp[0:10] + ";" + branch._Doel.Naam
        return expressionId

    def HeeftCiteertitel (self):
        """Geeft aan of het instrument een Citeertitel kent"""
        return True

    def STOPAnnotatieModules (self):
        """Geeft de namen van de STOP annotatiemodules waarvan 
        alleen het uitwisselen (en niet de inhoud) wordt vastgelegd
        """
        if self._Soort == "Regeling":
            return ["Toelichtingrelaties"]
        if self._Soort == "GIO":
            return ["Symbolisatie"]
        return []

    def KentNonSTOPAnnotatie (self):
        """Geeft aan of het instrument non-STOP annotaties kent"""
        return self._Soort == "Regeling"

    def KanGewijzigdWorden (self):
        """Geeft aan of het instrument gewijzigd kan worden in plaatst van opnieuw vastgesteld te worden"""
        return self._Soort != "PDF"

    def SorteerKey (self):
        return ('1' if self._Soort == "Regeling" else '2' if self._Soort == "GIO" else '3' if self._Soort == "PDF" else '9') + self.WorkId

#======================================================================
#
# Intern versiebeheer per doel
#
#======================================================================

#----------------------------------------------------------------------
#
# Branch: informatie over alle instrumenten en tijdstempels voor 
#         een enkel doel.
#
#----------------------------------------------------------------------
class Branch:

    def __init__(self, versiebeheer: Versiebeheerinformatie, doel : Doel, ontstaanOp: str):
        """Maak een nieuwe branch aan

        Argumenten:

        doel Doel  Instantie van het doel waar de branch voor aangemaakt is
        versiebeheer Versiebeheerinformatie Versiebeheer waar deze branch onderdeel van is
        ontstaanOp string  Tijdstip waarop de branch is aangemaakt
        """
        self._Versiebeheer = versiebeheer
        self._Doel = doel
        self._OntstaanOp = ontstaanOp
        #--------------------------------------------------------------
        # Relatie met andere branches
        #--------------------------------------------------------------
        # Als de branch een versie van regelgeving beschrijft die als uitgangssituatie
        # de publiek bekende geldende regelgeving heeft, dan is de datum waarop de
        # regelgeving geldig is gegeven als:
        self.Uitgangssituatie_GeldigOp = None
        # Als de branch een versie van regelgeving beschrijft die als uitgangssituatie
        # het resultaat van een ander doel heeft, dan is dat doel opgegeven als:
        self.Uitgangssituatie_Doel : Branch = None
        # Geeft aan ten opzichte van welke commit de wijzigingen in regelgeving in het
        # besluit opgenomen moeten worden. Totdat de regelgeving is vastgesteld moet
        # de wijziging ten opzichte van een van bovenstaande uitgangssituaties beschreven
        # worden, daarna wordt het beschreven ten opzichte van de vastgestelde versie
        # (in rectificaties, vervolgbesluiten etc).
        self.Uitgangssituatie_Renvooi : Commit = None
        # Geeft aan dat de branch in werking treedt als alle opgegeven branches in werking getreden zijn
        # (naast Uitgangssituatie_Doel)
        self.TreedtConditioneelInWerkingMet : Set[Branch] = None
        # Geeft aan dat de regeling- en informatieobjectversies in deze branch hetzelfde zijn als
        # die van de andere branches. Tot de inwerkingtreding zal een wijziging in een instrumentversie van
        # de ene branch tegelijk tot een wijziging in de andere branch leiden. Deze branch is ook 
        # opgenomen in DeeltInstrumentversiesMet
        self.DeeltInstrumentversiesMet : Set[Branch] = None
        #--------------------------------------------------------------
        # Intern versiebeheer
        #--------------------------------------------------------------
        # De actuele (interne, binnen de creatie-keten) stand van de instrumentversies
        # key = work-Id
        self.Instrumentversies : Dict[str,InstrumentInformatie] = {}
        # De actuele (interne, binnen de creatie-keten) waarden van de tijdstempels
        self.Tijdstempels = Tijdstempels ()
        #--------------------------------------------------------------
        # Voortgang van uitwisseling met LVBB
        #--------------------------------------------------------------
        # Datum waarop de inhoud van deze branch publiek bekend is geworden.
        # None als dat pas bij publicatie het geval is; heeft tijdelijk een waarde 
        # bij de uitspraak van de rechter
        self.BekendOp : str = None
        # De waarden van de tijdstempels zoals die voor het laatst zijn uitgewisseld met de LVBB 
        # voor deze branch
        self.UitgewisseldeTijdstempels = Tijdstempels ()
        # Geeft aan of de vastgestelde versie van de regelgeving is (of nu wordt) gepubliceerd.
        # Tot dat moment is het uitgangspunt van de renvooi een andere branch, daarna deze branch
        self._VastgesteldeVersieGepubliceerd : bool = False
        #--------------------------------------------------------------
        # Consolidatie ondersteuning
        #--------------------------------------------------------------
        # Geeft de gemaaktOp datum van de meest recente uitwisseling met de LVBB
        self.LaatsteGemaaktOp : str = None
        # De branches en gemaaktOp die in deze branch verwerkt zijn
        self.VervlochtenMet : Dict[Branch,str] = {}
        #--------------------------------------------------------------
        # Weergave op de resultaatpagina
        #--------------------------------------------------------------
        self.Commits : List[Commit] = []
        
    def IsInWerking (self, tijdstipHeden : str):
        """Geeft aan of de regelgeving beheerd op deze branch op dit moment in werking is.
        Voor het rectificeren/corrigeren/... van regelgeving maakt het een groot verschil
        of het om toekomstige regelgeving gaat of om regelgeving die al in werking is.

        Argumenten:

        tijdstipHeden string  Datum of tijdstip van het "nu"/"heden" in de simulatie
        """
        if self.UitgewisseldeTijdstempels.JuridischWerkendVanaf is None:
            return False
        if self.UitgewisseldeTijdstempels.JuridischWerkendVanaf <= tijdstipHeden[0:10]:
            return True
        return False

    def BaseerOpBranch (self, verslag: Meldingen, commit: 'Commit', branch: 'Branch'):
        """Neem de inhoud van de branch over

        Argumenten

        verslag Meldingen  log om vsat te leggen hoe het versiebeheer is uitgevoerd
        commit Commit  Commit waar de wijziging deel van uitmaakt
        branch Branch  branch waarop de huidige branch is gebaseerd
        """
        verslag.Informatie ("Branch '" + self._Doel.Naam + "' heeft als uitgangspunt branch '" + branch._Doel.Naam + "'")
        commit.Basisversie = commit.Uitgangssituatie_Renvooi = self.Uitgangssituatie_Doel = self.Uitgangssituatie_Renvooi = branch.Commits[-1]
        self.Instrumentversies = { workId: InstrumentInformatie (self, huidigeVersie._Instrument, huidigeVersie.Instrumentversie) for workId, huidigeVersie in branch.Instrumentversies.items () }
        commit.InstrumentversiesBijStart = { workId : copy (info.Instrumentversie) for workId, info in self.Instrumentversies.items () }
        self.VervlochtenMet[branch] = branch.Commits[-1].GemaaktOp

    def NeemVeranderdeBranchVersieOver (self, verslag: Meldingen, commit: 'Commit'):
        """Neem de wijzigingen uit de branch over die het uitgangspunt is voor deze branch

        Argumenten

        verslag Meldingen  log om vsat te leggen hoe het versiebeheer is uitgevoerd
        commit Commit  Commit waar de wijziging deel van uitmaakt

        Geeft een array terug met de workId van de instrumenten die niet zijn bijgewerkt omdat ze op de branch zijn gewijzigd
        """
        if self.Uitgangssituatie_Renvooi._Branch != self:
            commit.Uitgangssituatie_Renvooi = self.Uitgangssituatie_Renvooi = self.Uitgangssituatie_Doel.Commits[-1]
            verslag.Informatie ("De renvooi in branch '" + self._Doel.Naam + "' moet vanaf nu gegeven worden ten opzichte van de inhoud van branch '" + self.Uitgangssituatie_Renvooi._Branch.Naam + "' per " + self.Uitgangssituatie_Renvooi.GemaaktOp)
            self.VervlochtenMet[self.Uitgangssituatie_Doel] = self.Uitgangssituatie_Renvooi.GemaaktOp

        nietBijgewerkt = []
        for workId, nieuweVersie in self.Uitgangssituatie_Doel.Instrumentversies.items ():
            huidigeVersie = self.Instrumentversies.get (workId)
            if huidigeVersie is None or not huidigeVersie.IsGewijzigdInBranch ():
                # Deze versie moet overgenomen worden
                self.Instrumentversies[workId] = InstrumentInformatie (self, self._Versiebeheer.Instrumenten[workId], nieuweVersie.Instrumentversie)
                commit.Instrumentversies[workId] = copy (self.Instrumentversies[workId])
            else:
                nietBijgewerkt.append (workId)
        return nietBijgewerkt


    def BaseerOpGeldendeVersie (self, verslag: Meldingen, commit: 'Commit', consolidatie: 'Consolidatie'):
        """Neem de inhoud van de geldende (geconsolideerde) regelgeving over

        Argumenten

        verslag Meldingen  log om vsat te leggen hoe het versiebeheer is uitgevoerd
        commit Commit  Commit waar de wijziging deel van uitmaakt
        consolidatie Consolidatie geldende regelgeving waarvan de inhoud overgenomen moet worden
        """
        if consolidatie is None:
            verslag.Informatie ("Branch '" + self._Doel.Naam + "' heeft geen geldige regelgeving als uitgangspunt")
        else:
            verslag.Informatie ("Branch '" + self._Doel.Naam + "' heeft als uitgangspunt de regelgeving geldig vanaf " + consolidatie.JuridischGeldigVanaf)
            self.Uitgangssituatie_GeldigOp = consolidatie.JuridischGeldigVanaf
            commit.Basisversie = commit.Uitgangssituatie_Renvooi = self.Uitgangssituatie_Renvooi = consolidatie.Branches[0].Commits[-1] # Elke branch is goed
            verslag.Informatie ("Branch '" + self._Doel.Naam + "' is gebaseerd op de inhoud van branch '" + self.Uitgangssituatie_Renvooi._Branch._Doel.Naam + "'")
            self.Instrumentversies = { workId: InstrumentInformatie (self, self._Versiebeheer.Instrumenten[workId], huidigeVersie) for workId, huidigeVersie in consolidatie.Instrumentversies.items () }
            commit.InstrumentversiesBijStart = { workId : copy (info.Instrumentversie) for workId, info in self.Instrumentversies.items () }
            self.VervlochtenMet[self.Uitgangssituatie_Renvooi._Branch] = self.Uitgangssituatie_Renvooi.GemaaktOp

    def NeemVeranderdeGeldendeVersieOver (self, verslag: Meldingen, commit: 'Commit', consolidatie: 'Consolidatie'):
        """Neem de wijzigingen uit de geldende (geconsolideerde) regelgeving over

        Argumenten

        verslag Meldingen  log om vsat te leggen hoe het versiebeheer is uitgevoerd
        commit Commit  Commit waar de wijziging deel van uitmaakt
        consolidatie Consolidatie geldende regelgeving waarvan de wijzigingen overgenomen moet worden

        Geeft een array terug met de workId van de instrumenten die niet zijn bijgewerkt omdat ze op de branch zijn gewijzigd
        """
        verslag.Informatie ("Branch '" + self._Doel.Naam + "' heeft als uitgangspunt de regelgeving geldig vanaf " + consolidatie.JuridischGeldigVanaf)
        self.Uitgangssituatie_GeldigOp = consolidatie.JuridischGeldigVanaf
        if self.Uitgangssituatie_Renvooi._Branch != self:
            del self.VervlochtenMet[self.Uitgangssituatie_Renvooi._Branch]
            commit.Uitgangssituatie_Renvooi = self.Uitgangssituatie_Renvooi = consolidatie.Branches[0].Commits[-1]
            verslag.Informatie ("De renvooi in branch '" + self._Doel.Naam + "' moet vanaf nu gegeven worden ten opzichte van de inhoud van branch '" + self.Uitgangssituatie_Renvooi._Branch.Naam + "' per " + self.Uitgangssituatie_Renvooi.GemaaktOp)
            self.VervlochtenMet[self.Uitgangssituatie_Renvooi._Branch] = self.Uitgangssituatie_Renvooi.GemaaktOp

        nietBijgewerkt = []
        for workId, nieuweVersie in consolidatie.Instrumentversies.items ():
            huidigeVersie = self.Instrumentversies.get (workId)
            if huidigeVersie is None or not huidigeVersie.IsGewijzigdInBranch ():
                # Deze versie moet overgenomen worden
                self.Instrumentversies[workId] = InstrumentInformatie (self, self._Versiebeheer.Instrumenten[workId], nieuweVersie)
                commit.Instrumentversies[workId] = copy (self.Instrumentversies[workId]) 
            else:
                nietBijgewerkt.append (workId)
        return nietBijgewerkt

    def WijzigTijdstempels (self, commit: 'Commit', juridischWerkendVanaf : str, geldigVanaf : str):
        """Voer een nieuwe tijdstempels op voor deze branch

        Argumenten:

        commit Commit  Commit waar de wijziging deel van uitmaakt
        juridischWerkendVanaf string  Datum voor JuridischWerkendVanaf; None om de datum te scrappen
        geldigVanaf string  Datum voor geldigVanaf; None als die gelijk is aan juridischWerkendVanaf
        """
        if juridischWerkendVanaf is None or juridischWerkendVanaf == geldigVanaf:
            geldigVanaf = None
        self.Tijdstempels = Tijdstempels ()
        self.Tijdstempels.JuridischWerkendVanaf = juridischWerkendVanaf
        self.Tijdstempels.GeldigVanaf = geldigVanaf
        commit.Tijdstempels = self.Tijdstempels

    def VastgesteldeVersieIsGepubliceerd (self, verslag: Meldingen, commit: 'Commit'):
        """Geeft aan dat de publicatie van het vaststellingsbesluit zojuist is gedaan

        Argumenten

        verslag Meldingen  log om vsat te leggen hoe het versiebeheer is uitgevoerd
        commit Commit  Commit waar de wijziging deel van uitmaakt
        """
        commit.Uitgangssituatie_Renvooi = self.Uitgangssituatie_Renvooi = self.Commits[-1]
        verslag.Informatie ("De renvooi in branch '" + self._Doel.Naam + "' moet vanaf nu gegeven worden ten opzichte van de inhoud van dezelfde branch per " + self.Uitgangssituatie_Renvooi.GemaaktOp)

#----------------------------------------------------------------------
#
# Commit: verandering van de informatie op een branch. 
#         Als het resultaat van de commit uitgewisseld wordt in de keten
#         dan komt het overeen met een STOP momentopname.
#         In de simulator wordt het bijgehouden om in de resultaatpagina 
#         het in het versiebeheer te kunnen tonen. De informatie die nodig 
#         is om de uitwisseling met de LVBB te faciliteren staat in de 
#         branch zelf en is de optelsom van alle wijzigingen.
#
#----------------------------------------------------------------------
class Commit:

    def __init__(self, collectie : List['Commit'], branch : Branch, gemaaktOp : str):
        """Informatie over een commit / bijwerken van de inhoud van een branch. 

        Argumenten:

        collectie []  Lijst van commits (voor een activiteitverloop) waar dit er een van wordt
        branch Branch  Branch waarvoor de commit aangemaakt is
        gemaaktOp string  Tijdstip van wijziging van de branch
        """
        self._Branch = branch
        branch.Commits.append (self)
        collectie.append (self)
        self.GemaaktOp = gemaaktOp
        # Sommige activiteiten leiden tot meerdere opeenvolgende aanpassingen
        # in het versiebeheer. In productiewaardige software zouden de aanpassingen
        # elk een opvolgend gemaaktOp tijdstip hebben. In de simulator wordt de volgorde
        # via een volgnummer vastgelegd. Dit is alleen nodig voor de weergave op de 
        # resultaatpagina.
        self.Volgnummer = len (collectie)
        #--------------------------------------------------------------
        # Informatie beheerd op de branch
        #--------------------------------------------------------------
        # De instrumentversies voorafgaand aan de commit
        self.InstrumentversiesBijStart = { w: copy (i.Instrumentversie) for w, i in branch.Instrumentversies.items () }
        # De gewijzigde (interne, binnen de creatie-keten) instrumentversies
        # key = work-Id
        self.Instrumentversies : Dict[str,Instrumentversie] = {}
        # De (interne, binnen de creatie-keten) waarden van de tijdstempels bij de start van de commit
        self.TijdstempelsBijStart = branch.Tijdstempels
        # De bijgewerkte (interne, binnen de creatie-keten) waarden van de tijdstempels
        self.Tijdstempels : Tijdstempels = None
        # Geeft aan ten opzichte waarvan de tekst- of geo-renvooi gemaakt moet worden.
        self.Uitgangssituatie_Renvooi_BijStart : Commit = branch.Uitgangssituatie_Renvooi
        self.Uitgangssituatie_Renvooi : Commit = None
        #--------------------------------------------------------------
        # Relatie met andere branches
        #--------------------------------------------------------------
        # De commit van een andere branch die nu als basisversie gebruikt wordt
        self.Basisversie : Commit = None
        # De commits van andere branches waarmee deze branch vervlochten is bij deze wijziging
        self.VervlochtenVersie : List[Commit] = []
        # De commits van andere branches waarmee deze branch ontvlochten is bij deze wijziging
        self.OntvlochtenVersie : List[Commit] = []
        #--------------------------------------------------------------
        # Uitwisseling binnen keten
        #--------------------------------------------------------------
        # Soort uitwisseling waar deze commit deel van uitmaakt; een van de _Uitwisseling_ waarden
        self.SoortUitwisseling : str = None

    _Uitwisseling_LVBB_Naar_Adviesbureau = "LVBB -> Adviesbureau"
    _Uitwisseling_BG_Naar_Adviesbureau = "BG -> Adviesbureau"
    _Uitwisseling_Adviesbureau_Naar_BG = "Adviesbureau -> BG"
    _Uitwisseling_BG_Naar_LVBB = "BG -> LVBB"

    def IsGelijkAan (self, commit : 'Commit'):
        """Geeft aan of twee commits hetzelfde zijn
        """
        if commit is None:
            return False
        return self._Branch == commit._Branch and self.GemaaktOp == commit.GemaaktOp

#----------------------------------------------------------------------
#
# InstrumentInformatie: de informatie die over een instrument bijgehouden
# moet worden op de branch
#
#----------------------------------------------------------------------
class InstrumentInformatie:

    def __init__(self, branch : Branch, instrument : Instrument, uitgangssituatie : 'Instrumentversie' = None):
        """De informatie die door een branch over een instrument wordt bijgehouden

        Argumenten:

        branch Branch  branch die de informatie beheert.
        instrument Instrument Beschrijving van het instrument waarop deze informatie betrekking heeft
        instrumentversie InstrumentInformatie instrumentversie die de initiële versie voor deze branch is
        uitgangssituatie Instrumentversie instrumentversie die de uitgangssituatie voor deze branch iss
        """
        self._Branch = branch
        self._Instrument = instrument
        #--------------------------------------------------------------
        # Intern versiebeheer
        #--------------------------------------------------------------
        # De actuele versie van het instrument.
        self.Instrumentversie : Instrumentversie = Instrumentversie (uitgangssituatie)
        # De versie van dit instrument ten tijde van het aanmaken van de branch
        # None als het instrument op deze branch is ontstaan
        self.Uitgangssituatie : Instrumentversie = uitgangssituatie
        #--------------------------------------------------------------
        # Voortgang van uitwisseling met LVBB
        #--------------------------------------------------------------
        # De versie van het instrument op deze branch die eerder is uitgewisseld met de LVBB
        # None als er nog geen versie is uitgewisseld, of als het instrument is teruggetrokken.
        self.UitgewisseldeVersie : Instrumentversie = None
        # De versies waarmee de branch vervlochten is sinds de laatste uitwisseling
        self.VervlochtenVersie : List[Instrumentversie] = []
        # De versies waarmee de branch ontvlochten is sinds de laatste uitwisseling
        self.OntvlochtenVersie : List[Instrumentversie] = []

    def IsGewijzigdInBranch (self):
        """Geeft aan of de instrumentversie is gewijzigd op de branch die de instrumentversie beheert
        """
        if not self.UitgewisseldeVersie is None:
            return True
        if not self.Uitgangssituatie is None:
            return not self.Instrumentversie.IsGelijkAan (self.Uitgangssituatie)
        return not (self.Instrumentversie.ExpressionId is None and self.Instrumentversie.IsJuridischUitgewerkt)

    def IsGewijzigd (self):
        """Geeft aan of de instrumentversie is gewijzigd sinds de laatste uitwisseling
        """
        if len (self.VervlochtenVersie) or len (self.OntvlochtenVersie) > 0:
            return True
        if not self.UitgewisseldeVersie is None:
            return not self.Instrumentversie.IsGelijkAan (self.UitgewisseldeVersie)
        if not self.Uitgangssituatie is None:
            return not self.Instrumentversie.IsGelijkAan (self.Uitgangssituatie)
        return not (self.Instrumentversie.ExpressionId is None and self.Instrumentversie.IsJuridischUitgewerkt)

    def WijzigInstrument (self, commit: 'Commit', expressionId : str) -> 'Instrumentversie':
        """Voer een nieuwe instrumentversie op voor het instrument

        Argumenten:

        commit Commit  Commit waar de wijziging deel van uitmaakt
        expressionId string Identificatie van de nieuwe versie; None als het een onbekende versie is
        """
        self.Instrumentversie = Instrumentversie ()
        self.Instrumentversie.ExpressionId = expressionId
        self.Instrumentversie.IsJuridischUitgewerkt = False
        commit.Instrumentversies[self._Instrument.WorkId] = copy (self.Instrumentversie)
        return self.Instrumentversie

    def TrekInstrumentIn (self, commit: 'Commit'):
        """Trek het instrument in

        Argumenten:

        commit Commit  Commit waar de wijziging deel van uitmaakt
        """
        self.Instrumentversie = Instrumentversie ()
        self.Instrumentversie.ExpressionId = None
        self.Instrumentversie.IsJuridischUitgewerkt = True
        commit.Instrumentversies[self._Instrument.WorkId] = copy (self.Instrumentversie)


    def TrekWijzigingTerug (self, commit: 'Commit'):
        """Trek de wijziging van het instrument voor deze branch terug

        Argumenten:

        commit Commit  Commit waar de wijziging deel van uitmaakt
        """
        self.Instrumentversie = Instrumentversie (self.Uitgangssituatie)
        commit.Instrumentversies[self._Instrument.WorkId] = copy (self.Instrumentversie)
        self.VervlochtenVersie = []
        self.OntvlochtenVersie = []

#----------------------------------------------------------------------
#
# Instrumentversie
#
#----------------------------------------------------------------------
class Instrumentversie:

    def __init__(self, uitgangssituatie : 'Instrumentversie' = None):
        """Maak een nieuwe instantie voor een instrumentversie.

        Argumenten:

        uitgangssituatie Instrumentversie instrumentversie die de uitgangssituatie voor deze versie iss
        """
        #--------------------------------------------------------------
        # Intern versiebeheer
        #--------------------------------------------------------------
        # ExpressionId van de instrumentversie
        # Als IsJuridischUitgewerkt True is, dan is de waarde None. Anders is het de waarde
        # zoals opgegeven of (als er geen waarde is opgegeven) de waarde afgeleid van de uitgangssituatie.
        # Als de ExpressionId in dat geval None is gaat het om een onbekende versie.
        self.ExpressionId = None if uitgangssituatie is None else uitgangssituatie.ExpressionId
        # Geeft aan of de instrumentversie juridisch uitgewerkt is (dus ingetrokken is/moet worden)
        # None als er nog geen versie bestaat
        self.IsJuridischUitgewerkt : bool = None if uitgangssituatie is None else uitgangssituatie.IsJuridischUitgewerkt
        # ExpressionId  IsJuridischUitgewerkt
        # None          None                   (Nog) geen versie gespecificeerd
        # None          False                  Juridisch in werking, Onbekende versie
        # None          True                   Juridisch uitgewerkt, versie niet relevant
        # Niet-None     False                  Juridisch in werking, versie bekend
        #--------------------------------------------------------------
        # Voortgang van uitwisseling met LVBB
        #--------------------------------------------------------------
        # Tijdstip waarop deze instrumentversie is uitgewisseld met de LVBB.
        # None als de versie nog niet is uitgewisseld
        self.UitgewisseldOp : str = None
        # Doel(en) waarvoor de versie is uitgewisseld
        self.UitgewisseldVoor : Set[Doel] = None

    def IsJuridischInWerking (self):
        """Geeft aan of het instrument juridisch bestaat"""
        return self.IsJuridischUitgewerkt == False

    def BestaatOfHeeftBestaan (self):
        """Geeft aan of het instrument gedurende enige tijd juridisch heeft (of zal) bestaan"""
        return not self.IsJuridischUitgewerkt is None

    def IsGelijkAan (self, instrumentversie: 'Instrumentversie'):
        """ Vergelijk deze instrumentversie met een andere instantie en geef aan of ze gelijk zijn

        Argumenten:

        instrumentversie Instrumentversie  Andere instrumentversie
        """
        if instrumentversie is None:
            return False
        if self.IsJuridischUitgewerkt:
            return instrumentversie.IsJuridischUitgewerkt
        return self.ExpressionId == instrumentversie.ExpressionId

    @staticmethod
    def ZijnGelijk (instrumentversie1: 'Instrumentversie', instrumentversie2: 'Instrumentversie'):
        """ Vergelijk twee instrumentversies en geef aan of ze gelijk zijn

        Argumenten:

        instrumentversie1 Instrumentversie  De ene instrumentversie
        instrumentversie2 Instrumentversie  De andere instrumentversie
        """
        if instrumentversie1 is None:
            return instrumentversie2 is None
        return instrumentversie1.IsGelijkAan (instrumentversie2)

#----------------------------------------------------------------------
#
# Tijdstempels
#
#----------------------------------------------------------------------
class Tijdstempels:

    def __init__(self):
        """Maak een nieuwe instantie van de tijdstempels.
        """
        # De waarde van de juridischWerkendVanaf tijdstempel, of None als die niet gezet is.
        self.JuridischWerkendVanaf = None
        # De waarde van de geldigVanaf tijdstempel, of None als die niet gezet is.
        self.GeldigVanaf = None

    def IsGelijkAan (self, tijdstempels: 'Tijdstempels'):
        """ Vergelijk deze tijdstempels met een andere instantie en geef aan of ze gelijk zijn

        Argumenten:

        tijdstempels Tijdstempels  Andere instantie van de tijdstempels
        """
        if self.JuridischWerkendVanaf is None:
            return tijdstempels.JuridischWerkendVanaf is None
        elif self.JuridischWerkendVanaf != tijdstempels.JuridischWerkendVanaf:
            return False
        if self.GeldigVanaf is None or self.GeldigVanaf == self.JuridischWerkendVanaf:
            return tijdstempels.GeldigVanaf is None or tijdstempels.GeldigVanaf == self.JuridischWerkendVanaf
        elif self.GeldigVanaf != tijdstempels.GeldigVanaf:
            return False
        return True

#endregion

#======================================================================
#
# Consolidatie per datum inwerkingtreding
#
#======================================================================

#region Consolidatie
#----------------------------------------------------------------------
#
# Consolidatie: Geldigheid/consolidatie van een of meer doelen.
#
#----------------------------------------------------------------------
class Consolidatie:

    def __init__(self, juridischGeldigVanaf : str, branches : List[Branch]):
        """Maak een nieuwe instanntie aan.
        
        Argumenten:

        juridischGeldigVanaf str Datum van inwerkingtreding waarvoor de geldigheid beschreven is
        branches [] Lijst met branches die op dit moment tegelijk in werking treden
                    Equivalent van inwerkingtredingsdoelen in het STOP toestandenmodel
        """
        #--------------------------------------------------------------
        # Ondersteuning consolidatieproces
        #--------------------------------------------------------------
        self.JuridischGeldigVanaf = juridischGeldigVanaf
        self.Branches = branches
        # Geeft aan of de consolidatie compleet is. Dit is niet het geval als ook
        # maar één van de regelingen niet geconsolideerd is
        self.IsCompleet = True
        # Geeft aan of alle informatie in de branches uitgewisseld is.
        self.IsUitgewisseld = True
        # De geconsolideerde versie voor elk instrument. Als geen geconsolideerde versie voor een
        # instrument beschikbaar is, is de versie None.
        self.Instrumentversies : Dict[str,Instrumentversie] = {}

    @staticmethod
    def _WerkConsolidatieBij(versiebeheer: Versiebeheerinformatie, applicatielog : Meldingen, verslag: Meldingen, heden: str) -> bool:
        """Werk de consolidatie bij op basis van de huidige stand van het interne versiebeheer.
        Voor de activiteiten van BG maakt het niet uit of dit alles al gepubliceerd is; de aanname 
        is dat publicatie tijdig zal plaatsvinden. Oplossen van samenloop zal al voorafgaand aan de 
        publicatie kunnen gebeuren.

        Argumenten:

        versiebeheer Versiebeheerinformatie Stand van de versiebeheerinformatie
        applicatielog Meldingen  Meldingen voor fouten/waarschuwingen voor het scenario
        verslag Meldingen  Meldingen voor de uitvoering van de consolidatie
        heden str  De datum waarop de consolidatie uitgevoerd wordt

        Geeft terug of de consolidatie bijgewerkt kon worden
        """
        ok = True

        # In deze simulator wordt de hele consolidatie opnieuw bepaald. Dat kan slimmer,
        # maar in deze simulator gaat het nooit om grote aantallen dus heeft eenvoudige 
        # code de voorkeur
        versiebeheer.Consolidatie = []

        # Zoek uit welke branches tegelijk in werking treden
        branchesPerJWV : Dict[str,List[Branch]] = { }
        for branch in versiebeheer.Branches.values ():
            if branch.Tijdstempels.JuridischWerkendVanaf is None:
                continue
            lijst = branchesPerJWV.get (branch.Tijdstempels.JuridischWerkendVanaf)
            if lijst is None:
                branchesPerJWV[branch.Tijdstempels.JuridischWerkendVanaf] = lijst = []
            lijst.append (branch)

        laatstGemaaktOp : Dict[Branch,str] = {} # Laatste publicatie per branch, voor elke branch die in werking is
        metBijdragenVan : Dict[Branch,Set[Branch]] = {} # Alle branches (value) die bijdragen aan een branch (key)
        for juridischWerkendVanaf in sorted (branchesPerJWV.keys ()):
            # Maak een nieuwe consolidatie
            consolidatie = Consolidatie (juridischWerkendVanaf, branchesPerJWV[juridischWerkendVanaf])
            versiebeheer.Consolidatie.append (consolidatie)

            if consolidatie.IsCompleet:
                # De regelingversie van de consolidatie bevat tenminste de wijzigingen van de consolidatie.Branches
                consolidatieHeeftBijdragenVan = set (consolidatie.Branches)
                for branch in consolidatie.Branches:
                    # Bewaar de laatste wijziging van de branch, en de bijdragen (die later nog uitgebreid worden)
                    laatstGemaaktOp[branch] = branch.Commits[-1].GemaaktOp
                    metBijdragenVan[branch] = consolidatieHeeftBijdragenVan
                for branch in consolidatie.Branches:
                    for vervlochten, gemaaktOp in branch.VervlochtenMet.items ():
                        # Bekijk wat de laatste wijziging van de vervlochten branch is
                        laatstGO = laatstGemaaktOp.get (vervlochten)
                        if laatstGO is None:
                            # Vervlochten branch is nog niet in werking, of is later gewijzigd
                            consolidatie.IsCompleet = False
                            verslag.Informatie ("Consolidatie: de branch '" + branch._Doel.Naam + "' treedt in werking met wijzigingen uit branch '" + vervlochten._Doel.Naam + "' die nog niet in werking zijn")
                        else:
                            if gemaaktOp < laatstGO:
                                # Vervlochten branch is nog gewijzigd nadat de vervlechting heeft plaatsgevonden
                                consolidatie.IsCompleet = False
                                verslag.Informatie ("Consolidatie: de inhoud van branch '" + branch._Doel.Naam + "' is nog niet bijgewerkt met de laatste wijzigingen uit branch '" + vervlochten._Doel.Naam + "'")
                            # De regelingversie van de consolidatie bevat ook de wijzigingen van de branches die aan de vervlochten branch bijdragen
                            consolidatieHeeftBijdragenVan.update (metBijdragenVan[vervlochten])

                # De keys van de laatstGemaaktOp zijn de branches die in werking zijn. 
                # De regelingversie voor de consolidatie moet een bijdrage hebben voor elke versie
                ontbreekt = set (laatstGemaaktOp.keys()).difference (consolidatieHeeftBijdragenVan)
                if len (ontbreekt) > 0:
                    consolidatie.IsCompleet = False
                    verslag.Informatie ("Consolidatie: de wijzigingen uit de branch '" + "', '".join (b._Doel.Naam for b in ontbreekt) + "' zijn nog niet meegenomen")

            if consolidatie.IsCompleet:
                versiesVerschillend : Set[str] = set ()
                for branch in consolidatie.Branches:
                    nogUitwisselen = False
                    for workId, info in branch.Instrumentversies.items ():
                        versie = consolidatie.Instrumentversies.get (workId)
                        if versie is None:
                            # Nog geen versie bekend
                            consolidatie.Instrumentversies[workId] = copy (info.Instrumentversie)
                        elif not info.IsGelijkAan (versie):
                            # Verschillende versies voor hetzelfde work
                            consolidatie.IsCompleet = False
                            versiesVerschillend.add (info._Instrument.Naam)
                        if info.IsGewijzigd ():
                            nogUitwisselen = True
                    if nogUitwisselen:
                        consolidatie.IsUitgewisseld = False
                        verslag.Informatie ("Consolidatie: de inhoud van branch '" + branch._Doel.Naam + "' moet nog uitgewisseld worden met de landelijke voorzieningen")

                if len (versiesVerschillend) > 0:
                    verslag.Informatie ("Consolidatie: verschillende versies gespecificeerd voor '" + "', '".join (sorted (versiesVerschillend)) + "' voor de branches: '" + "', '".join (sorted (b._Doel.Naam for b in consolidatie.Branches)) + "'")

            if not consolidatie.IsCompleet:
                # Instrumentversies zijn niet betrouwbaar
                consolidatie.Instrumentversies = {}
                consolidatie.IsUitgewisseld = False
                verslag.Informatie ("De consolidatie voor JuridischWerkendVanaf = " + juridischWerkendVanaf + " is nog niet voltooid. Het gaat om de branches: '" + "', '".join (sorted (b._Doel.Naam for b in consolidatie.Branches)) + "'.")
                # Het heeft geen zin volgende consolidaties uit te rekenen
                if juridischWerkendVanaf < heden:
                    # Maak wel een incomplete voor heden
                    consolidatie = Consolidatie (heden, [])
                    consolidatie.IsCompleet = False
                    consolidatie.IsUitgewisseld = False
                    break

        return ok

#endregion

#======================================================================
#
# ConsolidatieInformatie
#
# Conversie van versiebeheer naar STOP ConsolidatieInformatie
# (en in deze simulator omgekeerd om ConsolidatieInformatie zonder
# BG-activiteit te kunnen verwerken)
#
#======================================================================

#region ConsolidatieInformatie
#----------------------------------------------------------------------
#
# ConsolidatieInformatieMaker
#
# Leidt de consolidatie-informatie af uit het interne versiebeheer van
# het bevoegd gezag. Dit is onderdeel van een actie in de 
# procesbegeleiding die tot uitwisseling met de LVBB overgaat.
#
#----------------------------------------------------------------------
class ConsolidatieInformatieMaker:

    def __init__ (self, applicatielog : Meldingen, verslag : Meldingen, gemaaktOp : str):
        """Maak de modulemaker aan

        Argumenten

        applicatielog Meldingen  Meldingen voor fouten/waarschuwingen over het scenario
        verslag Meldingen  Meldingen over het versiebsheer dat de simulator uitvoert
        gemaaktOp string  Tijdstip waarop de activiteit uitgevoerd wordt
        """
        self._Log = applicatielog
        self._Verslag = verslag
        self._ConsolidatieInformatie = ConsolidatieInformatie (None, None)
        self._ConsolidatieInformatie.GemaaktOp = gemaaktOp
        self._ConsolidatieInformatie.OntvangenOp = gemaaktOp[0:10]
        self._ConsolidatieInformatie._BekendOp = gemaaktOp[0:10]
        self._HeeftInhoud = False
        self.IsValide = True

    def ConsolidatieInformatie (self):
        """Geeft de samengestelde module, of None als de module leeg is
        """
        if self.IsValide and self._HeeftInhoud:
            return self._ConsolidatieInformatie

    def VoegToe (self, branch : Branch, inPublicatie : bool) -> bool:
        """Voeg de consolidatie informatie toe om wijzigingen in de branch door te geven

        Argumenten:

        branch Branch  Inhoud van de branch die doorgegeven moet worden
        inPublicatie bool  Geeft aan dat de inhoud van de branch in de publicatie staat vermeld, dat verwezen kan worden naar de tekst van de publicatie.

        Geeft aan of er consolidatie-informatie is toegevoegd
        """

        def _VoegBasisversieToe (basisversies : Dict[Doel,Momentopname], info: InstrumentInformatie):
            if not info.UitgewisseldeVersie is None:
                basisversies[info._Branch._Doel] = Momentopname (info._Branch._Doel, info.UitgewisseldeVersie.UitgewisseldOp)
            elif not info.Uitgangssituatie is None:
                if info.Uitgangssituatie.UitgewisseldOp is None:
                    self._Log.Fout ("Basisversie '" + info.Uitgangssituatie.ExpressionId + "' voor '" + info.Instrumentversie.ExpressionId + "' is nog niet met de LV uitgewisseld")
                    self.IsValide = False
                else:
                    doel = list(info.Uitgangssituatie.UitgewisseldVoor)[0]
                    basisversies[doel] = Momentopname (doel, info.Uitgangssituatie.UitgewisseldOp)

        meldtMeerdereBranches = False # Meldt dat een instrumentversie voor meerdere doelen wordt doorgegeven
        veranderRenvooi = False # Na uitwisseling van een instrumentversie verschuift de renvooi
        for workId, info in branch.Instrumentversies.items ():
            elt = None
            if info.Instrumentversie.IsGelijkAan (info.Uitgangssituatie):
                if not info.UitgewisseldeVersie is None:
                    # Trek de wijziging terug
                    if info.UitgewisseldeVersie.IsJuridischUitgewerkt:
                        elt = TerugtrekkingIntrekking (self._ConsolidatieInformatie, branch._Doel, workId)
                        self._ConsolidatieInformatie.TerugtrekkingenIntrekking.append (elt)
                    else:
                        elt = Terugtrekking (self._ConsolidatieInformatie, branch._Doel, workId)
                        self._ConsolidatieInformatie.Terugtrekkingen.append (elt)
                    _VoegBasisversieToe (elt.Basisversies, info)
                    self._Verslag.Informatie  ("ConsolidatieInformatie voor branch '" + branch._Doel.Naam + "': terugtrekking van '" + info._Instrument.Naam + "'")
                # Reset de uitwisselinginformatie
                info.OntvlochtenVersie = []
                info.VervlochtenVersie = []
                info.UitgewisseldeVersie = None
                onderzoekResetRenvooi = True
                veranderRenvooi = True
            elif info.IsGewijzigd () or (not branch._VastgesteldeVersieGepubliceerd and info.IsGewijzigdInBranch ()):
                veranderRenvooi = True
                if not info.IsGewijzigd ():
                    info.Instrumentversie.ExpressionId = info._Instrument.MaakExpressionId (self._ConsolidatieInformatie.GemaaktOp, branch)
                    branch.Commits[-1].Instrumentversies[workId] = copy (info.Instrumentversie)
                    self._Verslag.Informatie  ("Dezelfde versie van '" + info._Instrument.Naam + "' voor branch '" + branch._Doel.Naam + "' doorgegeven onder een andere expressionId want het expressionId moet voor elke publicatie uniek zijn")
                info.Instrumentversie.UitgewisseldOp = self._ConsolidatieInformatie.GemaaktOp
                info.Instrumentversie.UitgewisseldVoor = set ([branch._Doel])
                if info.Instrumentversie.IsJuridischUitgewerkt:
                    # Intrekking
                    elt = Intrekking (self._ConsolidatieInformatie, branch._Doel, workId)
                    _VoegBasisversieToe (elt.Basisversies, info)
                    self._ConsolidatieInformatie.Intrekkingen.append (elt)
                    # Ver-/ont-vlechten is niet interessant
                    self._Verslag.Informatie  ("ConsolidatieInformatie voor branch '" + branch._Doel.Naam + "': intrekking van '" + info._Instrument.Naam + "'")
                elif info.Instrumentversie.ExpressionId is None:
                    # Onbekende versie, gaat over het verleden dus alleen voor deze branch
                    elt = BeoogdeVersie (self._ConsolidatieInformatie, branch._Doel, workId, None)
                    _VoegBasisversieToe (elt.Basisversies, info)
                    self._ConsolidatieInformatie.BeoogdeVersies.append (elt)
                    # Ver-/ont-vlechten is niet interessant
                    self._Verslag.Informatie  ("ConsolidatieInformatie voor branch '" + branch._Doel.Naam + "': onbekende versie voor '" + info._Instrument.Naam + "'")
                else:
                    # Nieuwe instrumentversie
                    alleBranches = [branch] # Deze moet vooraan staan
                    if not branch.DeeltInstrumentversiesMet is None:
                        meldtMeerdereBranches = True
                        for b in branch.DeeltInstrumentversiesMet:
                            if b != branch:
                                alleBranches.append (b)
                    info.Instrumentversie.UitgewisseldVoor = [b._Doel for b in alleBranches]
                    elt = BeoogdeVersie (self._ConsolidatieInformatie, info.Instrumentversie.UitgewisseldVoor, workId, info.Instrumentversie.ExpressionId)
                    for b in alleBranches:
                        b_info = b.Instrumentversies[workId]
                        _VoegBasisversieToe (elt.Basisversies, b_info)
                        if b != branch:
                            b_info.Instrumentversie.UitgewisseldOp = info.Instrumentversie.UitgewisseldOp
                            b_info.Instrumentversie.UitgewisseldVoor = info.Instrumentversie.UitgewisseldVoor
                            b_info.VervlochtenVersie = []
                            b_info.OntvlochtenVersie = []
                            b_info.UitgewisseldeVersie = info.Instrumentversie
                    self._ConsolidatieInformatie.BeoogdeVersies.append (elt)
                    for versie in info.OntvlochtenVersie:
                        if versie.UitgewisseldOp is None:
                            self._Log.Fout ("Ontvlochten versie '" + versie.ExpressionId + "' voor '" + info.Instrumentversie.ExpressionId + "' is nog niet met de LV uitgewisseld")
                            self.IsValide = False
                        else:
                            for doel in versie.UitgewisseldVoor:
                                elt.OntvlochtenVersies[doel] = versie.UitgewisseldOp
                    for versie in info.VervlochtenVersie:
                        if versie.UitgewisseldOp is None:
                            self._Log.Fout ("Vervlochten versie '" + versie.ExpressionId + "' voor '" + info.Instrumentversie.ExpressionId + "' is nog niet met de LV uitgewisseld")
                            self.IsValide = False
                        else:
                            for doel in versie.UitgewisseldVoor:
                                elt.VervlochtenVersies[doel] = versie.UitgewisseldOp
                    self._Verslag.Informatie  ("ConsolidatieInformatie voor branch '" + branch._Doel.Naam + "': nieuwe versie voor '" + info._Instrument.Naam + "': " + info.Instrumentversie.ExpressionId)

                # Werk de uitwisselinginformatie bij
                info.OntvlochtenVersie = []
                info.VervlochtenVersie = []
                info.UitgewisseldeVersie = copy (info.Instrumentversie)

            if not elt is None:
                elt.eId = 'eId_publicatie_wijzigart' if inPublicatie else None
                elt._BekendOp = branch.BekendOp
        if meldtMeerdereBranches:
            self._Verslag.Informatie ("ConsolidatieInformatie voor branch '" + branch._Doel.Naam + "': versies worden ook doorgegeven voor '" + "', '".join (b._Doel.Naam for b in alleBranches if b != branch) + "'")

        leidtTotUitwisseling = veranderRenvooi
        if not branch.Tijdstempels.IsGelijkAan (branch.UitgewisseldeTijdstempels):
            if branch.Tijdstempels.JuridischWerkendVanaf is None:
                elt = TerugtrekkingTijdstempel (self._ConsolidatieInformatie)
                elt._BekendOp = branch.BekendOp
                elt.Doel = branch._Doel
                elt.eId = 'eId_publicatie_jwv' if inPublicatie else None
                elt.IsGeldigVanaf = False
                self._ConsolidatieInformatie.TijdstempelTerugtrekkingen.append (elt)
                if not branch.UitgewisseldeTijdstempels.GeldigVanaf is None:
                    elt = TerugtrekkingTijdstempel (self._ConsolidatieInformatie)
                    elt._BekendOp = branch.BekendOp
                    elt.Doel = branch._Doel
                    elt.eId = 'eId_publicatie_gv' if inPublicatie else None
                    elt.IsGeldigVanaf = True
                    self._ConsolidatieInformatie.TijdstempelTerugtrekkingen.append (elt)
                self._Verslag.Informatie  ("ConsolidatieInformatie voor branch '" + branch._Doel.Naam + "': terugtrekking tijdstempels")
                leidtTotUitwisseling = True
            else:
                elt = Tijdstempel (self._ConsolidatieInformatie)
                elt._BekendOp = branch.BekendOp
                elt.Datum = branch.Tijdstempels.JuridischWerkendVanaf 
                elt.Doel = branch._Doel
                elt.eId = 'eId_publicatie_jwv' if inPublicatie else None
                elt.IsGeldigVanaf = False
                self._ConsolidatieInformatie.Tijdstempels.append (elt)
                if not branch.Tijdstempels.GeldigVanaf is None:
                    elt = Tijdstempel (self._ConsolidatieInformatie)
                    elt._BekendOp = branch.BekendOp
                    elt.Datum = branch.Tijdstempels.GeldigVanaf
                    elt.Doel = branch._Doel
                    elt.eId = 'eId_publicatie_gv' if inPublicatie else None
                    elt.IsGeldigVanaf = True
                    self._ConsolidatieInformatie.Tijdstempels.append (elt)
                self._Verslag.Informatie  ("ConsolidatieInformatie voor branch '" + branch._Doel.Naam + "': tijdstempels")
                leidtTotUitwisseling = True
            branch.UitgewisseldeTijdstempels = branch.Tijdstempels

        branch.BekendOp = None
        if leidtTotUitwisseling:
            branch.LaatsteGemaaktOp = self._ConsolidatieInformatie.GemaaktOp
            self._HeeftInhoud = True

        if veranderRenvooi:
            if branch._VastgesteldeVersieGepubliceerd:
                branch.Uitgangssituatie_Renvooi = branch.Commits[-1]
                branch.Uitgangssituatie_Renvooi.Uitgangssituatie_Renvooi = branch.Uitgangssituatie_Renvooi
                self._Verslag.Informatie ("De renvooi in branch '" + branch._Doel.Naam + "' moet vanaf nu gegeven worden ten opzichte van de inhoud van dezelfde branch per " + branch.Uitgangssituatie_Renvooi.GemaaktOp)

        return leidtTotUitwisseling

#======================================================================
#
# ConsolidatieInformatieVerwerker
#
#======================================================================
#
# Werk het interne versiebeheer bij met de informatie uit een
# consolidatie-informatie module die voor een van de "overige projecten"
# is opgesteld. Voor deze projecten wordt geen procesbegeleiding
# gedaan, maar worden de consolidatie-informatie modules als invoer 
# voor het scenario gespecificeerd. Deze code zal geen equivalent 
# kennen in BG-software.
#
#======================================================================
class ConsolidatieInformatieVerwerker:
#----------------------------------------------------------------------
#
# Verwerken van de consolidatie informatie die niet vanuit een actie
# van een project is opgesteld, maar direct als invoer voor het
# scenario is opgegeven. Werkt het versiebeheer bij zoals bevoegd
# gezag dat bijhoudt.
#
#----------------------------------------------------------------------
    @staticmethod
    def WerkBij (log: Meldingen, scenario, consolidatieInformatie: ConsolidatieInformatie) -> bool:
        """Werk de BG-versiebeheerinformatie bij aan de hand van consolidatie-informatie.

        Argumenten:

        log Meldingen  Verzameling van meldingen over de uitvoering van het scenario
        scenario Scenario  Gegevens over het scenario en de resultaten daarvan
        consolidatieInformatie ConsolidatieInformatie  De consolidatie-informatie voor een uitwisseling 
                                                       die als invoer voor het scenario is opgegeven

        Geeft aan of de verwerking goed is verlopen
        """
        maker = ConsolidatieInformatieVerwerker (log, scenario, consolidatieInformatie)
        return maker._WerkVersiebeheerBij ()

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
    def __init__(self, log: Meldingen, scenario, consolidatieInformatie : ConsolidatieInformatie):
        """Maak een nieuwe instantie aan.

        Argumenten:

        log Meldingen  Verzameling van meldingen over de uitvoering van het scenario
        scenario Scenario  Gegevens over het scenario en de resultaten daarvan
        consolidatieInformatie ConsolidatieInformatie  De consolidatie-informatie voor een uitwisseling
        """
        self._Log = log
        self._Versiebeheer : Versiebeheerinformatie = scenario.BGVersiebeheerinformatie
        self._ConsolidatieInformatie = consolidatieInformatie

#----------------------------------------------------------------------
#
# _WerkVersiebeheerBij: bijwerken van versiebeheer aan de hand van 
# consolidatie-informatie die als invoer voor het scenario is opgegeven
#
#----------------------------------------------------------------------
    def _WerkVersiebeheerBij (self):
        """Werk het versiebeheer bij aan de hand van de uitgewisselde consolidatie-informatie.
        Geeft terug of de simulatie door kan gaan.
        """
        isValide = True

        def __Branch (doel: Doel, moetBestaan : bool) -> Branch:
            """Geef de branch die hoort bij het doel"""
            branch = self._Versiebeheer.Branches.get (doel)
            if branch is None:
                if moetBestaan:
                    self._Log.Fout ("Tijdstempel voor doel '" + str(doel) + "' voordat er een terugtrekking of beoogde instrumentversie is uitgewisseld. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                else:
                    self._Versiebeheer.Branches[doel] = branch = Branch (self._Versiebeheer, doel, self._ConsolidatieInformatie.GemaaktOp)
                    branch.VastgesteldeVersieIsGepubliceerd = True
                    branch.Project = None
                    branch.InteractieNaam = doel.Naam + ' (niet via project)'
                    branch.Tijdstempels = branch.UitgewisseldeTijdstempels # Hou de tijdstempels in sync
            elif not branch.Project is None:
                self._Log.Fout ("Doel '" + str(doel) + "' wordt via projecten beheerd; daarvoor kan geen ConsolidatieInformatie gespecificeerd worden. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                return
            return branch

        def __WerkInstrumentInformatieBij (doel: Doel, voorInstrument: VoorInstrument, expressionId: str, isJuridischUitgewerkt: bool) -> InstrumentInformatie:
            """Werk de InstrumentInformatie bij en geef die terug"""
            branch = __Branch (doel, False)
            if branch is None:
                return

            instrumentversie = Instrumentversie ()
            instrumentversie.ExpressionId = expressionId
            instrumentversie.IsJuridischUitgewerkt = isJuridischUitgewerkt
            instrumentversie.UitgewisseldOp = self._ConsolidatieInformatie.GemaaktOp
            instrumentversie.UitgewisseldVoor = voorInstrument.Doelen

            instrumentInfo = branch.Instrumentversies.get (voorInstrument.WorkId)
            if instrumentInfo is None:
                # Eerste vermelding van dit instrument
                instrument = Instrument.Bepaal (voorInstrument.WorkId)
                if instrument is None:
                    self._Log.Fout ("Van het instrument '" + voorInstrument.WorkId + "' kan niet bepaald worden wat het is. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                    return
                branch.Instrumentversies[voorInstrument.WorkId] = instrumentInfo = InstrumentInformatie (branch, instrument)
            instrumentInfo.Instrumentversie = instrumentversie
            instrumentInfo.UitgewisseldeVersie = instrumentversie
            return instrumentInfo


        # Begin met de BeoogdeRegelingen
        for beoogdeVersie in self._ConsolidatieInformatie.BeoogdeVersies:
            for doel in beoogdeVersie.Doelen:
                instrumentInfo = __WerkInstrumentInformatieBij (doel, beoogdeVersie.ExpressionId, False)
                if instrumentInfo is None:
                    isValide = False
                self._Scenario.Procesvoortgang.BekendeInstrumenten.add (beoogdeVersie.WorkId)
                if not beoogdeVersie.ExpressionId is None:
                    self._Scenario.Procesvoortgang.PubliekeInstrumentversies.add (beoogdeVersie.ExpressionId)

        # Intrekkingen
        for intrekking in self._ConsolidatieInformatie.Intrekkingen:
            for doel in intrekking.Doelen:
                instrumentInfo = __WerkInstrumentInformatieBij (doel, None, True)
                if instrumentInfo is None:
                    isValide = False

        # Terugtrekking van iets van een instrument. Hier valideren we niet of het de juiste soort terugtrekking is, dat wordt gedaan
        # (in deze applicatie) bij het verwerken in de versiebeheerinformatie voor het ontvangende systeem
        for terugtrekking in [*self._ConsolidatieInformatie.Terugtrekkingen, *self._ConsolidatieInformatie.TerugtrekkingenIntrekking]:
            for doel in terugtrekking.Doelen:
                instrumentInfo = __WerkInstrumentInformatieBij (doel, None, False)
                if instrumentInfo is None:
                    isValide = False
                else:
                    instrumentInfo.IsGewijzigd = False
                    instrumentInfo.Instrumentversie = None

        # Tijdstempels
        for tijdstempel in self._ConsolidatieInformatie.Tijdstempels:
            branch = __Branch (tijdstempel.Doel, True)
            if branch is None:
                isValide = False
            else:
                if tijdstempel.IsGeldigVanaf:
                    branch.UitgewisseldeTijdstempels.GeldigVanaf = tijdstempel.Datum
                else:
                    branch.UitgewisseldeTijdstempels.JuridischWerkendVanaf = tijdstempel.Datum

        for tijdstempel in self._ConsolidatieInformatie.TijdstempelTerugtrekkingen:
            branch = __Branch (tijdstempel.Doel, True)
            if branch is None:
                isValide = False
            else:
                if tijdstempel.IsGeldigVanaf:
                    branch.UitgewisseldeTijdstempels.GeldigVanaf = None
                else:
                    branch.UitgewisseldeTijdstempels.JuridischWerkendVanaf = None
                    branch.UitgewisseldeTijdstempels.GeldigVanaf = None

        return isValide
#endregion
