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
#======================================================================

from typing import Dict, List, Set, Tuple
from applicatie_meldingen import Meldingen
from data_doel import Doel

#======================================================================
#
# Versiebeheerinformatie: minimale informatie die in de bevoegd gezag
#                         software beschikbaar moet zijn.
#
#======================================================================

#----------------------------------------------------------------------
#
# Versiebeheer
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

    def MaakExpressionId (self, activiteit, branch):
        """Maak een expressionId voor een nieuwe instrumentversie

        Argumenten:

        activiteit Activiteit  De activiteit die door BG wordt uitgevoerd
        branch Branch  De branch waarvoor de instrumentversie wordt aangemaakt
        """
        expressionId = self.WorkId
        if self._Soort == "Regeling":
            expressionId += "/nl"
        expressionId += "@" + activiteit.UitgevoerdOp[0:10] + ";" + branch._Doel.Naam
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

class Momentopname:
    def __init__ (self, branch: 'Branch', gemaaktOp : str):
        """Maak een nieuwe momentopname aan

        Argumenten:
        branch Branch  branch waar de momentopname van gemaakt wordt
        gemaaktOp str  tijdstip van de momentopname
        """
        self.Branch = branch
        self.GemaaktOp = gemaaktOp

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
        # Geeft aan dat de branch in werking treedt als alle opgegeven branches in werking getreden zijn
        # (naast Uitgangssituatie_Doel)
        self.TreedtConditioneelInWerkingMet : Set[Branch] = None
        #--------------------------------------------------------------
        # Intern versiebeheer
        #--------------------------------------------------------------
        # De actuele (interne, binnen de creatie-keten) stand van de instrumentversies
        # key = work-Id
        self.Instrumentversies : Dict[str,InstrumentInformatie] = {}
        # De actuele (interne, binnen de creatie-keten) waarden van de tijdstempels
        self.Tijdstempels = Tijdstempels ()
        #--------------------------------------------------------------
        # Ondersteuning consolidatieproces
        #--------------------------------------------------------------
        # Tijdstip van de laatste keer dat de inhoud van deze branch is gewijzigd 
        self.LaatstGewijzigdOp : str = None
        #--------------------------------------------------------------
        # Voortgang van uitwisseling met LVBB
        #--------------------------------------------------------------
        # Momentopname waarop de instrumentversies in deze branch zijn gebaseerd.
        # None als deze branch geen uitgangssituatie kent, een momentopname van
        # deze branch nadat de branch al een keer is uitgewisseld
        self.GebaseerdOp : Momentopname = None
        # Datum waarop de inhoud van deze branch publiek bekend is geworden.
        # None als dat pas bij publicatie het geval is; heeft een waarde bij de uitspraak van de rechter
        self.BekendOp : str = None
        # De waarden van de tijdstempels zoals die voor het laatst zijn uitgewisseld met de LVBB 
        # voor deze branch
        self.UitgewisseldeTijdstempels = Tijdstempels ()
        #--------------------------------------------------------------
        # Weergave op de resultaatpagina
        #--------------------------------------------------------------
        self.Commits : List[Commit] = []
        

    def BaseerOpBranch (self, verslag: Meldingen, commit: 'Commit', branch: 'Branch'):
        """Neem de inhoud van de branch over

        Argumenten

        verslag Meldingen  log om vsat te leggen hoe het versiebeheer is uitgevoerd
        commit Commit  Commit waar de wijziging deel van uitmaakt
        branch Branch  branch waarop de huidige branch is gebaseerd
        """
        verslag.Informatie ("Branch '" + self._Doel.Naam + "' heeft als uitgangspunt branch '" + branch._Doel.Naam + "'")
        self.Uitgangssituatie_Doel = branch._Doel
        self.GebaseerdOp = branch
        self.Instrumentversies = { workId: InstrumentInformatie (self, huidigeVersie._Instrument, huidigeVersie.Instrumentversie) for workId, huidigeVersie in branch.Instrumentversies.items () }
        commit.Instrumentversies = { workId : info.Instrumentversie for workId, info in self.Instrumentversies.items () }
        commit.Basisversie = self.GebaseerdOp.Commits[-1]

    def NeemVeranderdeBranchVersieOver (self, verslag: Meldingen, commit: 'Commit'):
        """Neem de wijzigingen uit de branch over die het uitgangspunt is voor deze branch

        Argumenten

        verslag Meldingen  log om vsat te leggen hoe het versiebeheer is uitgevoerd
        commit Commit  Commit waar de wijziging deel van uitmaakt

        Geeft een array terug met de workId van de instrumenten die niet zijn bijgewerkt omdat ze op de branch zijn gewijzigd
        """
        nietBijgewerkt = []
        for workId, nieuweVersie in self.Uitgangssituatie_Doel.Instrumentversies.items ():
            huidigeVersie = self.Instrumentversies.get (workId)
            if huidigeVersie is None or not huidigeVersie.IsGewijzigdInBranch ():
                # Deze versie moet overgenomen worden
                commit.Instrumentversies[workId] = self.Instrumentversies[workId] = InstrumentInformatie (self, self._Versiebeheer.Instrumenten[workId], nieuweVersie.Instrumentversie)
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
            self.GebaseerdOp = consolidatie.Branches[0] # Elke branch is goed
            verslag.Informatie ("Branch '" + self._Doel.Naam + "' is gebaseerd op de inhoud van branch '" + self.GebaseerdOp.Naam + "'")
            self.Instrumentversies = { workId: InstrumentInformatie (self, self._Versiebeheer.Instrumenten[workId], huidigeVersie) for workId, huidigeVersie in consolidatie.Instrumentversies.items () }
            commit.Instrumentversies = { workId : info.Instrumentversie for workId, info in self.Instrumentversies.items () }
            commit.Basisversie = self.GebaseerdOp.Commits[-1]

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
        if self.GebaseerdOp != self._Doel:
            self.GebaseerdOp = consolidatie.Branches[0] # Elke branch is goed
            verslag.Informatie ("Omdat branch '" + self._Doel.Naam + "' nog niet is uitgewisseld, wordt de branch vanaf nu beschouwd als gebaseerd op de inhoud van branch '" + self.GebaseerdOp.Naam + "'")
            commit.Basisversie = self.GebaseerdOp.Commits[-1]
        nietBijgewerkt = []
        for workId, nieuweVersie in consolidatie.Instrumentversies.items ():
            huidigeVersie = self.Instrumentversies.get (workId)
            if huidigeVersie is None or not huidigeVersie.IsGewijzigdInBranch ():
                # Deze versie moet overgenomen worden
                commit.Instrumentversies[workId] = self.Instrumentversies[workId] = InstrumentInformatie (self, self._Versiebeheer.Instrumenten[workId], nieuweVersie)
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
        self.Tijdstempels.JuridischWerkendVanaf = geldigVanaf
        self.Tijdstempels.GeldigVanaf = geldigVanaf
        commit.Tijdstempels = self.Tijdstempels

class Commit:

    def __init__(self, branch : Branch, gemaaktOp : str, volgnummer : int = 1):
        """Informatie over een commit / bijwerken van de inhoud van een branch. In de simulator wordt het bijgehouden
        om in de resultaatpagina het in het versiebeheer te kunnen tonen. De informatie die nodig is om de uitwisseling
        met de LVBB te faciliteren staat in de branch zelf en is de optelsom van alle wijzigingen.

        Argumenten:

        branch Branch  Branch waarvoor de commit aangemaakt is
        gemaaktOp string  Tijdstip van wijziging van de branch
        volgnummer int  Volgnummer van de commit
        """
        self._Branch = branch
        branch.Commits.append (self)
        self.GemaaktOp = gemaaktOp
        # Sommige activiteiten leiden tot meerdere opeenvolgende aanpassingen
        # in het versiebeheer. In productiewaardige software zouden de aanpassingen
        # elk een opvolgend gemaaktOp tijdstip hebben. In de simulator wordt de volgorde
        # via een volgnummer vastgelegd. Dit is alleen nodig voor de weergave op de 
        # resultaatpagina.
        self.Volgnummer = volgnummer
        # De gewijzigde (interne, binnen de creatie-keten) instrumentversies
        # key = work-Id
        self.Instrumentversies : Dict[str,Instrumentversie] = {}
        # De bijgewerkte (interne, binnen de creatie-keten) waarden van de tijdstempels
        self.Tijdstempels : Tijdstempels = None
        # De commit van een andere branch die nu als basisversie gebruikt wordt
        self.Basisversie : Commit = None
        # De commits van andere branches waarmee deze branch vervlochten is bij deze wijziging
        self.VervlochtenVersie : List[Commit] = []
        # De commits van andere branches waarmee deze branch ontvlochten is bij deze wijziging
        self.OntvlochtenVersie : List[Commit] = []
        # Soort uitwisseling waar deze commit deel van uitmaakt; een van de _Uitwisseling_ waarden
        self.SoortUitwisseling : str = None

    _Uitwisseling_LVBB_Naar_Adviesbureau = "LVBB -> Adviesbureau"
    _Uitwisseling_BG_Naar_Adviesbureau = "BG -> Adviesbureau"
    _Uitwisseling_Adviesbureau_Naar_BG = "Adviesbureau -> BG"
    _Uitwisseling_BG_Naar_LVBB = "BG -> LVBB"



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
        return self.IsGewijzigd ()

    def IsGewijzigd (self):
        """Geeft aan of de instrumentversie is gewijzigd sinds de laatste uitwisseling
        """
        if len (self.VervlochtenVersie) or len (self.OntvlochtenVersie) > 0:
            return True
        if not self.Uitgangssituatie is None and not self.Instrumentversie.IsGelijkAan (self.Uitgangssituatie):
            return True
        return False

    def WijzigInstrument (self, commit: 'Commit', expressionId : str) -> 'Instrumentversie':
        """Voer een nieuwe instrumentversie op voor het instrument

        Argumenten:

        commit Commit  Commit waar de wijziging deel van uitmaakt
        expressionId string Identificatie van de nieuwe versie; None als het een onbekende versie is
        """
        self.Instrumentversie = Instrumentversie ()
        self.Instrumentversie.ExpressionId = expressionId
        self.Instrumentversie.IsJuridischUitgewerkt = False
        commit.Instrumentversies[self._Instrument.WorkId] = self.Instrumentversie
        return self.Instrumentversie

    def TrekInstrumentIn (self, commit: 'Commit'):
        """Trek het instrument in

        Argumenten:

        commit Commit  Commit waar de wijziging deel van uitmaakt
        """
        self.Instrumentversie = Instrumentversie ()
        self.Instrumentversie.ExpressionId = None
        self.Instrumentversie.IsJuridischUitgewerkt = True
        commit.Instrumentversies[self._Instrument.WorkId] = self.Instrumentversie


    def TrekWijzigingTerug (self, commit: 'Commit'):
        """Trek de wijziging van het instrument voor deze branch terug

        Argumenten:

        commit Commit  Commit waar de wijziging deel van uitmaakt
        """
        self.Instrumentversie = Instrumentversie (self.Uitgangssituatie)
        commit.Instrumentversies[self._Instrument.WorkId] = self.Instrumentversie
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
        return self.ExpressionId != instrumentversie.ExpressionId

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

#======================================================================
#
# Consolidatie per datum inwerkingtreding
#
#======================================================================

#----------------------------------------------------------------------
#
# Consolidatie: Geldigheid/consolidatie van een of meer doelen.
#
#----------------------------------------------------------------------
class Consolidatie:

    def __init__(self, juridischGeldigVanaf : str):
        """Maak een nieuwe instanntie aan.
        
        Argumenten:

        juridischGeldigVanaf str Datum van inwerkingtreding waarvoor de geldigheid beschreven is
        """
        #--------------------------------------------------------------
        # Ondersteuning consolidatieproces
        #--------------------------------------------------------------
        self.JuridischGeldigVanaf = juridischGeldigVanaf
        # Geeft aan of de consolidatie compleet is. Dit is niet het geval als ook
        # maar één van de regelingen niet geconsolideerd is
        self.IsCompleet = False
        # Lijst met branches die op dit moment tegelijk in werking treden
        # Equivalent van inwerkingtredingsdoelen in het STOP toestandenmodel
        self.Branches : Set[Branch] = set()
        # De geconsolideerde versie voor elk instrument. Als geen geconsolideerde versie voor een
        # instrument beschikbaar is, is de versie None.
        self.Instrumentversies : Dict[str,Instrumentversie] = {}
