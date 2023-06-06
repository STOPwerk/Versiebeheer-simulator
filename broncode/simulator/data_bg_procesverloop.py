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
from applicatie_meldingen import Meldingen

from data_doel import Doel
from data_bg_versiebeheer import Branch as VersiebeheerBranch, Commit, Consolidatie, Versiebeheerinformatie

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
        self.UitgevoerdDoor : str = Activiteitverloop._Uitvoerder_BevoegdGezag
        # Geeft aan door wie het project voor het laatst is uitgewisseld
        self.LaatstUitgewisseldDoor : str = None
        # Geeft aan op welk tijdstip het project voor het laatst is uitgewisseld
        self.LaatstUitgewisseldOp : str = None
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

    def __init__(self, uitgevoerdOp : str):
        """Maak een nieuw verslag van een activiteit aan

        Argumenten:

        uitgevoerdOp str Tijdstip waarop de activiteit is uitgevoerd
        naam str Naam waarmee de activiteit in een overzicht van BG activiteiten weergegeven moet worden.
                 Als dit None is, wordt de activiteit niet weergegeven.
        """
        self.UitgevoerdOp = uitgevoerdOp
        # Naam waarmee de activiteit in een overzicht van BG activiteiten weergegeven moet worden.
        # Als dit None is, wordt de activiteit niet weergegeven op de resultaatpagina.
        self.Naam : str = None
        # Beschrijving van de actie
        self.Beschrijving : str = None
        # Project(en) waar de activiteit onderdeel van uitmaakt/betrekking op heeft
        self.Projecten : Set[str] = set ()
        # Verslag van de interactie tussen de eindgebruiker en de software bij de uitvoering van de actie
        self.InteractieVerslag : List[InteractieMelding] = []
        # Verslag van de uitvoering van de activiteit door de simulator
        self.VersiebeheerVerslag = Meldingen (False)
        # Commits gedaan in het versiebeheer
        self.Commits : List[Commit] = []
        # De consolidatie na uitvoering van de activiteit.
        # Lijst is gesorteerd op volgorde van inwerkingtreding/juridischGeldigVanaf
        self.Consolidatie : List[Consolidatie] = {}
        # Degene die de actie heeft uitgevoerd: adviesbureau of bevoegd gezag
        self.UitgevoerdDoor = Activiteitverloop._Uitvoerder_BevoegdGezag
        # Alleen voor weergave: de STOP module(s) die in de keten uitgewisseld worden
        self.Uitgewisseld : List[UitgewisseldeSTOPModule] = []
        # Geeft aan of het een uitwisseling met de landelijke voorzieningen betreft
        self.UitwisselingMetLV : bool = False
        # Als de activiteit tot een publicatie leidt: de bron van de publicatie 
        self.Publicatiebron : str = None
        # De publicatie die is uitgegeven naar aanleiding van de activiteit
        self.Publicatie : str = None

    _Uitvoerder_BevoegdGezag = 'Bevoegd gezag'
    _Uitvoerder_Adviesbureau = 'Adviesbureau'
    _Uitvoerder_BGSoftware = 'BG-software'
    _Uitvoerder_LVBB = 'LVBB'

    def MeldInteractie (self, soortMelding : str, melding : str):
        """Voeg een interactiemelding toe aan het activiteitenverloop

        Argumenten:

        soortMelding str  Geeft aan wat voor soort melding/interactie het betreft
        melding string  Tekst van de melding
        """
        self.InteractieVerslag.append (InteractieMelding (soortMelding, melding))

class InteractieMelding:

    def __init__(self, soortMelding : str, melding : str):
        self.SoortMelding = soortMelding
        self.Melding = melding

    _Eindgebruiker = "Eindgebruiker"
    _Instructie = "Instructie"
    _Software = "BG software"

#======================================================================
#
# Voor de interne administratie van de simulator moet extra informatie
# in het interne versiebeheer bijgehouden worden.
#
#======================================================================

class Branch (VersiebeheerBranch):

    def __init__(self, versiebeheer: Versiebeheerinformatie, doel : Doel, ontstaanOp : str):
        """Maak een nieuwe branch aan

        Argumenten:

        versiebeheer Versiebeheerinformatie Versiebeheer waar deze branch onderdeel van is
        doel Doel  Instantie van het doel waar de branch voor aangemaakt is
        ontstaanOp string  Tijdstip waarop de branch is aangemaakt
        """
        super().__init__ (versiebeheer, doel, ontstaanOp)
        # Geeft aan of de branch in een projecten wordt beheerd. In deze simulator 
        # kan een branch ofwel via een project beheerd worden, ofwel geheel via 
        # ConsolidatieInformatie modules worden bestuurd. Voor de besturing via
        # een project kan de inhoud alleen via activiteiten in dat project of via
        # andere BG-activiteiten gewijzigd worden.
        self.Project : str = None
        # De aanduiding van de branch in het verslag van de interactie met de eindgebruiker
        self.InteractieNaam : str = None
