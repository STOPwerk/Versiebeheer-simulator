#======================================================================
#
# Resultaten van projecten bij het bevoegd gezag.
#
#======================================================================
#
# Als de simulatie ook het projectmatig werken bij het bevoegd gezag
# simuleert, dan wordt voor het bevoegd gezag informatie over de
# voortgang van projecten en over het versiebeheer bijgehouden.
# In een productie-waardige applicatie zal deze informatie wellicht
# af te leiden zijn uit de gegevens van het onderliggende
# versiebeheersysteem of database.
#
# In deze module staat een datamodel voor de informatie die deze
# applicatie bijhoudt over de inrichting en voortgang van projecten.
# Het is niet representatief voor de informatie die echte bevoegd gezag
# software bijhoudt - dat kan erg verschillen zijn.
#
#======================================================================

from typing import Dict, List, Tuple
from data_doel import Doel
from data_bg_project import Project, ProjectActie
from data_bg_versiebeheer import Versiebeheer, Branch as VersiebeheerBranch

#----------------------------------------------------------------------
#
# Projectvoortgang: informatie die in deze applicatie wordt bijgehouden
#                   over de uitkomsten van de acties van het bevoegd gezag.
#
#----------------------------------------------------------------------
class Projectvoortgang:

    def __init__ (self):
        """Maak een nieuwe instantie van het versiebeheer bij het bevoegd gezag.
        """
        # Informatie over de status van de projecten
        # Key = code van project
        self.Projecten : Dict[str,Projectstatus] = {}
        # De resultaten van de projectacties, op volgorde van uitvoeren
        self.Projectacties : List[ProjectactieResultaat] = []
        # Het interne versiebeheer van het bevoegd gezag
        self.Versiebeheer = Versiebeheer ()
        # Alle workId van instrumenten die bij BG bekend zijn. Wijzigingen
        # voor deze works mogen alleen in projecten gedaan worden als het
        # work expliciet als te beheren instrument aan een branch is toegevoegd.
        self.BekendeInstrumenten = set ()
        # Alle gepubliceerde instrumentversies - deze versies hoeven niet
        # opnieuw uitgewisseld te worden (althans niet in deze simulator)
        self.PubliekeInstrumentversies = set ()

#======================================================================
#
# Projectverloop
#
#======================================================================

class Projectstatus:

    def __init__(self, project : Project):
        """Maak een nieuwe projectstatus aan
        
        Argumenten:

        project Project  Het project waarvoor de status wordt aangemaakt
        """
        self._Project = project
        # De branches waar in het project aan gewerkt wordt door het bevoegd gezag
        self.Branches : Dict[Doel,Branch] = {}
        # De branches waar in het project aan gewerkt wordt door een adviesbureau
        self.ExterneBranches : Dict[Doel,Branch] = {}

class InstrumentMutatie:

    def __init__ (self):
        """Maak een nieuwe instantie aan van een mutatie van een instrument
        """
        # Een lijst met de expressionId van de mogelijke was-versies voor de mutatie
        # en het doel van de branch waaraan de versie ontleend is.
        self.Was : List[Tuple[Doel,str]] = []
        # De expressionId van de wordt-versie van de mutatie
        self.Wordt : str = None
        # Geeft aan of de mutatie juridische betekenis heeft en dus onderdeel moet zijn
        # van een juridische tekst. Als dat niet zo is, dan is de mutatie een redactioneel
        # product dat in het kader van het consolideren gemaakt wordt.
        self.IsJuridisch : bool = None

class UitgewisseldeSTOPModule:

    def __init__(self, module, van: str, naar: str):
        """Een STOP module die als onderdeel van de stap uitgewisseld wordt.
        Alleen gebruikt voor weergave.
        
        Argumenten:

        module object De STOP module(s) die voor deze actie uitgewisseld wordt
                      Instantie van een klasse die de methode self.ModuleXml() implementeert
        van str Ketenpartij die de module opstuurt
        naar str Ketenpartij die de module ontvangt
        """
        self.Module = module
        self.Van = van
        self.Naar = naar

class UitgewisseldMaarNietViaSTOP:

    def __init__(self):
        """Geeft aan dat er wel informatie uitgewisseld wordt, maar niet via STOP
        Alleen gebruikt voor weergave.
        """
        self.Module = self
        self.Van = ProjectactieResultaat._Uitvoerder_BevoegdGezag
        self.Naar = 'n.v.t.'

    def ModuleXml (self):
        return ['<!-- Informatie is niet in STOP uitgewisseld -->']

class ProjectactieResultaat:

    def __init__(self, projectactie):
        self._Projectactie : ProjectActie = projectactie
        # Degene die de actie heeft uitgevoerd: adviesbureau of bevoegd gezag
        self.UitgevoerdDoor = ProjectactieResultaat._Uitvoerder_BevoegdGezag
        # Parameters en data voor de actie; alleen voor weergave
        self.Data : List[Tuple[str,List[str]]] = []
        # Kopie van het interne versiebeheer dat resulteert uit de projectactie
        self._Versiebeheer : Versiebeheer = None # instantie is VersiebeheerWeergave 
        # Een overzicht van de mutaties die leiden tot de nieuwe versies in het versiebeheer
        # als gevolg van deze acties.
        self.Mutaties : List[InstrumentMutatie] = []
        # Alleen voor weergave: de STOP module(s) die in de keten uitgewisseld worden
        self.Uitgewisseld : List[UitgewisseldeSTOPModule] = []

    _Uitvoerder_BevoegdGezag = 'Bevoegd gezag'
    _Uitvoerder_Adviesbureau = 'Adviesbureau'
    _Uitvoerder_LVBB = 'LVBB'

#======================================================================
#
# Voor de interne administratie van de simulator moet extra informatie
# in het interne versiebeheer bijgehouden worden.
#
#======================================================================

class Branch (VersiebeheerBranch):

    def __init__(self, doel : Doel):
        """Maak een nieuwe branch aan

        Argumenten:

        doel Doel  Instantie van het doel waar de branch voor aangemaakt is
        """
        super().__init__ (doel)
        # Geeft aan of de branch via projecten wordt beheerd. In deze simulator kan 
        # een branch ofwel via een project beheerd worden, ofwel geheel via 
        # ConsolidatieInformatie modules worden bestuurd. Voor de besturing via
        # projecten maakt het niet uit of dat door één of door meerdere projecten
        # gedaan wordt - het is dus mogelijk een naorog/redactie als apart project
        # op te nemen.
        self._ViaProject = False
        # Degene die op dit moment aan de branch werkt: adviesbureau of bevoegd gezag
        self.Uitvoerder = ProjectactieResultaat._Uitvoerder_BevoegdGezag
        # Als de branch een versie van regelgeving beschrijft die als uitgangssituatie
        # het resultaat van een ander doel heeft, dan is dat doel opgegeven als:
        self.Uitgangssituatie_Doel : Branch = None
        # Als de branch een versie van regelgeving beschrijft die als uitgangssituatie
        # de publiek bekende geldende regelgeving heeft, dan is de datum waarop de
        # regelgeving geldig is gegeven als:
        self.Uitgangssituatie_GeldigOp = None
        #--------------------------------------------------------------
        # Ondersteuning consolidatieproces
        #--------------------------------------------------------------
        # Tijdstip van de laatste wijziging van de branches waar de Uitgangssituatie
        # van afkomstig is. Latere wijzigingen in de uitgangssituatie zijn (nog)
        # niet in deze branch verwerkt.
        # None als deze branch geen uitgangssituatie kent.
        self.Uitgangssituatie_LaatstGewijzigdOp : List[Tuple[Branch,str]] = None
