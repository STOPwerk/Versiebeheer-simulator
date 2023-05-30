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
class Versiebeheerinformatie:

    def __init__ (self):
        """Maak een nieuwe instantie van het versiebeheer bij het bevoegd gezag.
        """
        #--------------------------------------------------------------
        # Intern versiebeheer
        #--------------------------------------------------------------
        # Informatie over alle doelen die door bevoegd gezag beheerd worden
        self.Branches : Dict[Doel,Branch] = {}
        #--------------------------------------------------------------
        # Ondersteuning consolidatieproces
        #--------------------------------------------------------------
        # De consolidatie kan bij het bevoegd gezag op het niveau van branches
        # worden bijgehouden. Dat wordt vertaald naar informatie per instrument
        # bij het omzetten naar STOP consolidatie-informatie.
        # Lijst is gesorteerd op volgorde van inwerkingtreding/juridischGeldigVanaf
        self.Consolidatie : List[Consolidatie] = {}

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

    def __init__(self, doel : Doel, viaProject : bool):
        """Maak een nieuwe branch aan

        Argumenten:

        doel Doel  Instantie van het doel waar de branch voor aangemaakt is
        viaProject bool Geeft aan of de branch als onderdeel van een project wordt bijgehouden
        """
        self._Doel = doel
        #--------------------------------------------------------------
        # Relatie met andere branches
        #--------------------------------------------------------------
        # Als de branch een versie van regelgeving beschrijft die als uitgangssituatie
        # het resultaat van een ander doel heeft, dan is dat doel opgegeven als:
        self.Uitgangssituatie_Doel : Branch = None
        # Als de branch een versie van regelgeving beschrijft die als uitgangssituatie
        # de publiek bekende geldende regelgeving heeft, dan is de datum waarop de
        # regelgeving geldig is gegeven als:
        self.Uitgangssituatie_GeldigOp = None
        # Geeft aan dat de branch in werking treedt als alle opgegeven branches in werking getreden zijn
        self.TreedtConditioneelInWerkingMet : Set[Branch] = None
        # Branches waarvan de inhoud gelijkgehouden wordt omdat ze tegelijk in werking
        # zijn getreden / zullen treden. Deze branch is daar onderdeel van.
        # None als er geen sprake is van gelijktijdige inwerkingtreding.
        self.SimultaanBeheerdeBranches : Set[Branch] = None
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
        # Tijdstip van de laatste wijziging van de branches waar de Uitgangssituatie
        # van afkomstig is. Latere wijzigingen in de uitgangssituatie zijn (nog)
        # niet in deze branch verwerkt.
        # None als deze branch geen uitgangssituatie kent.
        self.Uitgangssituatie_LaatstGewijzigdOp : List[Tuple[Branch,str]] = None
        #--------------------------------------------------------------
        # Voortgang van uitwisseling met LVBB
        #--------------------------------------------------------------
        # De waarden van de tijdstempels zoals die voor het laatst zijn uitgewisseld met de LVBB 
        # voor deze branch
        self.UitgewisseldeTijdstempels = Tijdstempels ()
        # Datum waarop de inhoud van deze branch publiek bekend is geworden.
        # None als dat pas bij publicatie het geval is; heeft een waarde bij de uitspraak van de rechter
        self.BekendOp : str = None
        

#----------------------------------------------------------------------
#
# InstrumentInformatie: de informatie die over een instrument bijgehouden
# moet worden op de branch
#
#----------------------------------------------------------------------
class InstrumentInformatie:

    def __init__(self, branch : Branch):
        """De informatie die door een branch over een instrument wordt bijgehouden

        Argumenten:

        branch Branch  branch die de informatie beheert.
        """
        self._Branch = branch
        # De actuele versie van het instrument. Deze is None als er nog geen versie 
        # voor deze branch is opgegeven.
        #--------------------------------------------------------------
        # Intern versiebeheer
        #--------------------------------------------------------------
        self.Instrumentversie : Instrumentversie = Instrumentversie ()
        # De versie van dit instrument ten tijde van het aanmaken van de branch
        # None als het instrument op deze branch is ontstaan
        self.Uitgangssituatie : Instrumentversie = None
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

#----------------------------------------------------------------------
#
# Instrumentversie
#
#----------------------------------------------------------------------
class Instrumentversie:

    def __init__(self):
        """Maak een nieuwe instantie voor een instrumentversie.
        """
        #--------------------------------------------------------------
        # Intern versiebeheer
        #--------------------------------------------------------------
        # ExpressionId van de instrumentversie
        # Als IsJuridischUitgewerkt True is, dan is de waarde None. Anders is het de waarde
        # zoals opgegeven of (als er geen waarde is opgegeven) de waarde afgeleid van de uitgangssituatie.
        # Als de ExpressionId in dat geval None is gaat het om een onbekende versie.
        self.ExpressionId = None
        # Geeft aan of de instrumentversie juridisch uitgewerkt is (dus ingetrokken is/moet worden)
        # None als er nog geen versie bestaat
        self.IsJuridischUitgewerkt : bool = None
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
        # Geeft aan of de consolidatie nu of in de toekomst geldig is
        self.IsActueel = False
        # Status van de consolidatie
        self.Status = Consolidatie._Status_Compleet
        # Lijst met branches die op dit moment tegelijk in werking treden
        # Equivalent van inwerkingtredingsdoelen in het STOP toestandenmodel
        self.Branches : Set[Branch] = set()
        # De instrumentversies waarvan op dit moment een geconsolideerde versie beschikbaar is
        self.Instrumentversies : Dict[str,GeconsolideerdeVersie] = {}
        #--------------------------------------------------------------
        # Voortgang van uitwisseling met LVBB
        #--------------------------------------------------------------
        # Geeft aan dat voor een of meer doelen de consolidatie-informatie nog niet is uitgewisseld met de LVBB
        # None als alle informatie is uitgewisseld
        self.UitwisselingVereist = List[Doel] = None

    # Hoogste status telt.
    # Consolidatie is compleet, geen fouten gevonden
    _Status_Compleet = 0
    # Consolidatie is compleet maar een eerdere consolidatie (in werking nu of in de toekomst) is dat niet
    _Status_CompleetMaarEerdereNiet = 1
    # Consoldatie is niet compleet, in werking nu of in de toekomst
    _Status_Incompleet = 2
    # Deze consoldatie of een eerdere is niet compleet, in werking in het verleden
    _Status_IncompleetHistorisch = 3

#----------------------------------------------------------------------
#
# GeconsolideerdeVersie: Consolidatie van een instrument
#
#----------------------------------------------------------------------
class GeconsolideerdeVersie:

    def __init__(self, juridischWerkendVanaf : str):
        """Maak een nieuw overzicht aan van de geconsolideerde versie van een instrument,
        inclusief consolidatieaanwijzingen.
        """
        #--------------------------------------------------------------
        # Ondersteuning consolidatieproces
        #--------------------------------------------------------------
        # ExpressionId van de instrumentversie
        # Als IsJuridischUitgewerkt True is, dan is de waarde None. Anders is het de waarde
        # zoals vermeld. Als het None is gaat het om een onbekende of niet te bepalen versie.
        self.ExpressionId = None
        # Geeft aan of het instrument juridisch uitgewerkt is
        # None als er nog geen versie bestaat
        self.IsJuridischUitgewerkt = None
        # Geeft aan dat deze consolidatie ontstaat nadat het instrument al juridisch uitgewerkt is
        self.WijzigingNaIntrekking = False
        # Als er niet één versie voor een instrument wordt gespecificeerd, dan:
        # de verschillende expressionId (key) per versie de doelen die de versie opleveren
        self.TegenstrijdigeVersies : Dict[str, List[Doel]] = None
