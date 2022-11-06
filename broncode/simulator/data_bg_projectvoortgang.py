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
from data_bg_project import Project, ProjectActie, Instrumentversie
from data_bg_versiebeheer import Versiebeheer, Branch as VersiebeheerBranch
from weergave_data_bg_versiebeheer import VersiebeheerWeergave

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
        self._Versiebeheer : VersiebeheerWeergave = None
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
