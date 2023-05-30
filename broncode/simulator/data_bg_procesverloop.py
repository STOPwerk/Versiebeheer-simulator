#======================================================================
#
# Resultaten van de uitvoering van activiteiten door het bevoegd gezag
# of een adviesbureau.
#
#======================================================================
#
# Als de simulatie ook het proces bij het bevoegd gezag simuleert, dan 
# wordt voor informatie over de voortgang van het proces bijgehouden.
# In deze module staat het datamodel daarvoor. Het is niet representatief 
# voor de informatie die echte bevoegd gezag software bijhoudt.
#
#======================================================================
from typing import Dict, List, Set, Tuple

from data_doel import Doel
from data_bg_versiebeheer import Branch as VersiebeheerBranch

#----------------------------------------------------------------------
#
# Procesvoortgang: informatie die in deze applicatie wordt bijgehouden
#                  over de uitkomsten van de activiteiten van het
#                  bevoegd gezag en adviesbureaus.
#
#----------------------------------------------------------------------
class Procesvoortgang:

    def __init__ (self):
        """Maak een nieuwe instantie van de procesvoortgang bij het bevoegd gezag.
        """
        # Informatie over de status van de projecten
        # Key = naam van project
        self.Projecten : Dict[str,Projectstatus] = {}
        # De resultaten van de activiteiten, op volgorde van uitvoeren
        self.Activiteiten : List[Activiteitverloop] = []
        # Alle gepubliceerde instrumentversies - deze versies hoeven niet
        # opnieuw uitgewisseld te worden (althans niet in deze simulator)
        self.PubliekeInstrumentversies = set ()

#======================================================================
#
# Projectverloop
#
#======================================================================

class Projectstatus:

    def __init__(self, naam : str, gestartOp : str):
        """Maak een nieuwe projectstatus aan
        
        Argumenten:

        naam str  De naam van het project
        gestartOp str Tijdstip waarop het project gestart is
        """
        self.Naam = naam
        self.GestartOp = gestartOp
        # Degene die als laatste een activiteit voor dit project heeft uitgevoerd: adviesbureau of bevoegd gezag
        self.UitgevoerdDoor : str = None
        # De branches die in dit project beheerd worden
        self.Branches : List[Branch] = []

class UitgewisseldeSTOPModule:

    def __init__(self, instrument : str, module, van: str, naar: str):
        """Een STOP module die als onderdeel van de stap uitgewisseld wordt.
        Alleen gebruikt voor weergave.
        
        Argumenten:

        instrument str Het work-ID van het instrument waar de module bij hoort
        module object De STOP module(s) die voor deze actie uitgewisseld wordt
                      Instantie van een klasse die de methode self.ModuleXml() implementeert
        van str Ketenpartij die de module opstuurt
        naar str Ketenpartij die de module ontvangt
        """
        self.Instrument = instrument
        self.Module = module
        self.Van = van
        self.Naar = naar

class UitgewisseldMaarNietViaSTOP:

    def __init__(self):
        """Geeft aan dat er wel informatie uitgewisseld wordt, maar niet via STOP
        Alleen gebruikt voor weergave.
        """
        self.Module = self
        self.Van = Activiteitverloop._Uitvoerder_BevoegdGezag
        self.Naar = 'n.v.t.'

    def ModuleXml (self):
        return ['<!-- Informatie is niet in STOP uitgewisseld -->']

class Activiteitverloop:

    def __init__(self, uitgevoerdOp : str, naam : str):
        """Maak een nieuw verslag van een activiteit aan

        Argumenten:

        uitgevoerdOp str Tijdstip waarop de activiteit is uitgevoerd
        naam str Naam waarmee de activiteit in een overzicht van BG activiteiten weergegeven moet worden.
                 Als dit None is, wordt de activiteit niet weergegeven.
        """
        self.UitgevoerdOp = uitgevoerdOp
        self.Naam = naam
        # Beschrijving van de actie
        self.Beschrijving : str = None
        # Work-ID van het instrument waar deze activiteit betrekking op heeft
        self.Instrument : str = None
        # Degene die de actie heeft uitgevoerd: adviesbureau of bevoegd gezag
        self.UitgevoerdDoor = Activiteitverloop._Uitvoerder_BevoegdGezag
        # Alleen voor weergave: de STOP module(s) die in de keten uitgewisseld worden
        self.Uitgewisseld : List[UitgewisseldeSTOPModule] = []
        # De publicatie die is uitgegeven naar aanleiding van de activiteit
        self.Publicatie : str = None

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
        self.Uitvoerder = Activiteitverloop._Uitvoerder_BevoegdGezag
