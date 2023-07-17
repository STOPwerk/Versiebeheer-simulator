#======================================================================
#
# Versiebeheerinformatie per instrument.
#
#======================================================================
#
# In Python wordt geen onderscheid gemaakt tussen regeling en
# informatieobject; de term "instrument" wordt voor beide gebruikt.
#
# De versiebeheerinformatie per instrument is een andere manier om de 
# informatie uit de ConsolidatieInformatie op te slaan, op een manier
# die het eenvoudiger maakt om de consolidatie uit te voeren. In een 
# STOP-gebruikende applicatie zou het informatiemodel de basis zijn 
# voor de interne datamodel, waar de informatie in een database
# opgeslagen wordt en via queries op te halen is.
#
# Het in-memory data model voor de versiebeheerinformatie voor deze 
# applicatie is geïmplementeerd in de Versiebeheerinformatie klasse
# en de klassen die daardoor gebruikt worden.
#
# In de applicatie wordt eerst een in-memory representatie van de
# inhoud van de XML bestanden gemaakt, zoals in de module
# stop_consolidatieinformatie is geïmplementeerd. Daarna worden 
# alle ingelezen ConsolidatieInformatie instanties omgezet naar 
# het interne datamodel. De code voor de omzetting is geïmplementeerd 
# in de klasse ConsolidatieInformatieVerwerking, die de verschillende 
# Verwerk* klassen gebruikt voor de interpretatie van de consolidatie-
# informatie.
#
#======================================================================

from typing import Dict, List

from data_doel import Doel
from data_proefversie import Proefversie
from stop_consolidatieinformatie import Momentopname

#======================================================================
#
# Datamodel voor versiebeheerinformatie: per uitwisseling, 
# per instrument en tijdstempels per doel
#
#======================================================================

#----------------------------------------------------------------------
# Startpunt voor het ophalen van de informatie
#----------------------------------------------------------------------
class Versiebeheerinformatie:

    def __init__ (self):
        """Maak een lege instantie van alle versiebeheerinformatie"""
        # Gegevens over de uitwisselingen
        self.Uitwisselingen : List[Uitwisseling] = []
        # Versiebeheer per instrument
        # key = workId
        self.Instrumenten : Dict[str,Instrument] = {}
        # Versiebeheer van tijdstempels
        # key = instantie van Doel, value = branch met instanties van MomentopnameTijdstempels
        self.Tijdstempels : Dict[Doel,Branch] = {}
        # De applicatie gebruikt de proefversie voor een instrumentversie
        # ook als instrumentversiehistorie in een ToestandCompleet
        # Om snel de proefversies te kunnen vinden wordt een index bijgehouden.
        # key = instrumentversie, value = instantie van UitgewisseldeInstrumentversie
        self._UitwisselingInstrumentversie : Dict[str,UitgewisseldeInstrumentversie] = {}
        # Doelen die al gebruikt zijn voor een van de instrumenten
        # Wordt in deze applicatie als een set bijgehouden om de verwerking van
        # de consolidatie-informatie te versnellen.
        # Set van index waarden van doelen
        self._BekendeDoelenVoorInstrumenten = set()


#======================================================================
#
# De volgende klassen beschrijven het versiebeheer per uitwisseling,
# een samenvatting wat er in elke ConsolidatieInformatie module zit.
#
# Deze informatie wordt gebruikt voor het maken van proefversies.
#
#======================================================================

class Uitwisseling:

    def __init__ (self, gemaaktOp, ontvangenOp):
        """Maak een nieuwe instantie aan

        Argumenten:
        gemaaktOp string  Tijdstip van de momentopname die in de uitwisseling zit
        ontvangenOp string  Datum dat de uitwisseling ontvangen is.
        """
        self.GemaaktOp = gemaaktOp
        # Informatie over de nieuwe instrumentversies die in deze uitwisseling worden meegegeven
        # Lijst van instanties van UitgewisseldeInstrumentversie
        self.Instrumentversies : List[UitgewisseldeInstrumentversie] = []
        # Datum dat de inhoud van de uitwisseling publiek bekend is, te gebruiken als
        # bekendOp datum in de STOP context modules die door de uitwisseling ontstaan.
        self.BekendOp = None
        # Datum dat de uitwisseling ontvangen en publiek bekend is, te gebruiken als
        # ontvangenOp datum in de STOP context modules die door de uitwisseling ontstaan.
        self.OntvangenOp = ontvangenOp
        # Nummer van het publicatieblad waarin het besluit/rectificatie/mededeling uit de uitwisseling is gepubliceerd.
        self._Publicatieblad = None
        # De consolidatie-informatie die onderdeel is van de uitwisseling
        self._ConsolidatieInformatie = None

class UitgewisseldeInstrumentversie:

    def __init__ (self, uitwisseling : Uitwisseling, instrument, doelen : List[Doel], instrumentversie : str, basisversie : Momentopname):
        """Maak een nieuwe instantie aan

        Argumenten
        uitwisseling Uitwisseling
        instrument Instrument  Instrument waarvoor een nieuwe versie uitgewisseld is
        doelen Doel[]  De doelen/branches waarvoor de versie van toepassing is
        instrumentversie string  Expression identificatie van de versie, of None als de versie onbekend is
        basisversie Momentopname  De basisversie voor deze instrumentversie (voor annotaties bij proefversie)
        """
        self._Uitwisseling = uitwisseling
        self._Instrument = instrument
        self.Doelen = doelen
        self.Instrumentversie = instrumentversie
        self.Basisversie = basisversie

#======================================================================
#
# De volgende klassen beschrijven het versiebeheer uitgesplitst naar:
#
# - Instrument: branch voor een doel bestaat uit momentopnamen
# - Tijdstempels: branch voor een doel bestaat uit momentopnamen
#
# Deze informatie wordt gebruikt voor de geauomatiseerde consolidatie,
# voor het bepalen van toestanden, wat per instrument gedaan wordt.
#
#======================================================================

#----------------------------------------------------------------------
# Instrument: versiebeheerinformatie voor een instrument
#----------------------------------------------------------------------
class Instrument:

    def __init__ (self, versiebeheerinformatie : Versiebeheerinformatie, workId):
        """Maak versiebeheerinformatie aan voor een instrument
        
        Argumenten:
        versiebeheerinformatie Versiebeheerinformatie ... waar het instrument onderdeel van is
        workId string De work identificatie van het instrument
        """
        self._Versiebeheerinformatie = versiebeheerinformatie
        self.WorkId = workId
        # De branches waarvoor het instrument gewijzigd wordt
        # value is branch met instanties van MomentopnameInstrument
        self.Branches : Dict[Doel,Branch] = {}
        # Als tijdreizen op bekendOp datum ondersteund wordt en er wordt consolidatie-informatie
        # uitgewisseld met een minimale bekendOp datum, dan moet de consolidatie voor die datum
        # en alle latere bekendOp datums gedaan worden. In deze applicatie wordt bijgehouden welke
        # bekendOp datums zijn voorgekomen.
        self.BekendOp = set()
        # Datum waarop het instrument is uitgewerkt
        self.MaterieelUitgewerkt = None
        # Doelen waarvoor de initiële versie van het instrument is gegeven.
        # Het instrument kan alleen in werking zijn als een van deze doelen in werking is
        self.InitieleDoelen = None
        # Verzameling van alle proefversies die tot nu toe zijn gemaakt
        # key = expressionId
        self.Proefversies : Dict[str,Proefversie] = {}

#----------------------------------------------------------------------
# Branch: alles wat op een enkele branch gebeurt en relevant is voor
# het instrument. De wijzigingen van de tijdstempels worden hier alleen
# in opgenomen als de wijzigingen plaatsvinden in de periode dat er
# versiebeheer voor een instrument wordt bijgehouden.
#----------------------------------------------------------------------
class Branch:

    def __init__ (self, doel : Doel):
        """Maak een lege branch aan
        
        Argumenten:
        doel Doel  Naam van de branch
        """
        self.Doel = doel
        # De uitgewisselde momentopnamen voor deze branch, op volgorde van gemaaktOp.
        # De lijst bevat naast momentopname die het instrument wijzigen, ook momentopnamen
        # die aangemaakt worden als de tijdstempels voor het doel wel wijzigen maar het
        # instrument niet.
        # Lijst met instanties van MomentopnameInstrument of MomentopnameTijdstempels.
        self.Momentopnamen = []

#----------------------------------------------------------------------
# Momentopname: gedeelde kenmerken voor MomentopnameInstrument 
# / MomentopnameTijdstempels.
#----------------------------------------------------------------------
class Momentopname:

    def __init__ (self, branch, consolidatieInformatieElement):
        """Maak een nieuwe momentopname voor een branch aan
        
        Argumenten:
        branch Branch  instantie van de branch waar de momentopname deel van uitmaakt
        consolidatieInformatieElement object ConsolidatieInforamtie element dat tot de momentopname heeft geleid
        """
        self.Branch = branch
        self.GemaaktOp = consolidatieInformatieElement.ConsolidatieInformatie.GemaaktOp
        # BekendOp is alleen nodig als tijdreizen op bekendOp ondersteund moet worden
        self.BekendOp = consolidatieInformatieElement.BekendOp ()
        # In deze applicatie, alleen voor weergave: de consolidatie=informatie elementen die de aanleiding zijn tot deze momentopname
        self._ConsolidatieInformatieElementen = [consolidatieInformatieElement]
        # Alleen weergave: symbool om deze momentopname mee te karakteriseren
        self._Symbool = None

#----------------------------------------------------------------------
# MomentopnameTijdstempels: de waarden van de tijdstempels op een 
# bepaald moment.
#----------------------------------------------------------------------
class MomentopnameTijdstempels(Momentopname):

    def __init__ (self, branch, voorTijdstempel):
        """Maak een nieuwe momentopname voor tijdstempels voor een doel aan
        
        Argumenten:
        branch Branch  instantie van de branch waar de momentopname deel van uitmaakt
        voorTijdstempel VoorTijdstempel  Element uit ConsolidatieInformatie dat de momentopname veroorzaakt
        """
        super().__init__ (branch, voorTijdstempel)

        self.Doel : Doel = voorTijdstempel.Doel
        if len (branch.Momentopnamen) == 0:
            # Geeft de waarde voor de JuridischWerkendVanaf tijdstempel
            self.JuridischWerkendVanaf = None
            # Geeft de waarde voor de geldigVanaf tijdstempel
            self.GeldigVanaf = None
        else:
            voorgaandeMomentopname = branch.Momentopnamen[-1]
            self.JuridischWerkendVanaf = voorgaandeMomentopname.JuridischWerkendVanaf
            self.GeldigVanaf = voorgaandeMomentopname.GeldigVanaf

#----------------------------------------------------------------------
# MomentopnameInstrument: beschrijft een uitwisseling van informatie
# over een instrument voor de branch.
#----------------------------------------------------------------------
class MomentopnameInstrument (Momentopname):

    def __init__ (self, branch, voorInstrument):
        """Maak een nieuwe momentopname voor een branch aan
        
        Argumenten:
        branch Branch  instantie van de branch waar de momentopname deel van uitmaakt
        voorInstrument VoorInstrument ConsolidatieInforamtie element dat tot de momentopname heeft geleid
        """
        super().__init__ (branch, voorInstrument)
        # Alle doelen waarvoor deze momentopname tegelijk een wijziging voor het instrument aangeeft
        self.Doelen : List[Doel] = voorInstrument.Doelen
        # De verwijzing(en) naar de momentopname waar de branch op gebaseerd is
        self.Basisversies : Dict[Doel,Momentopname] = {}
        # De verwijzing(en) naar de momentopname die ontvlochten zijn in deze momentopname
        self.OntvlochtenMet : Dict[Doel,Momentopname] = {}
        # De verwijzing(en) naar de momentopname die vervlochten is in deze momentopname
        self.VervlochtenMet : Dict[Doel,Momentopname] = {}

        if len (branch.Momentopnamen) == 0:
            # De expressionId van de instrumentversie, indien bekend.
            self.ExpressionId = None
            # Geeft aan of het instrument ingetrokken is
            self.IsIngetrokken = False
            # Geeft aan of het instrument niet meer wordt gewijzigd in de branch
            self.IsTeruggetrokken = True
        else:
            voorgaandeMomentopname = branch.Momentopnamen[-1]
            self.ExpressionId = voorgaandeMomentopname.ExpressionId
            self.IsIngetrokken = voorgaandeMomentopname.IsIngetrokken
            self.IsTeruggetrokken = voorgaandeMomentopname.IsTeruggetrokken

#======================================================================
#
# Voor de bepaling van de inhoud van een toestand is een samenvatting
# nodig van het versiebeheer-tot-en-met-deze-momentopname (per instrument). 
# De samenvatting is een afgeleide van de instrument-branches-momentopname
# structuur. De informatie kan iedere keer opnieuw bepaald worden,
# maar omdat het tijdsonafhankelijk is wordt het in deze applicatie
# bij de momentopname bewaard als optimalisatie.
#
#======================================================================
        # Overzicht van alle branches die al dan niet bijdragen aan het versiebeheer
        # tot nu toe (inclusief deze branch)
        # key = instantie van Doel, value = instantie van BranchBijdrage
        self.BranchesCumulatief : Dict[Doel,BranchBijdrage] = None


class BranchBijdrage:

    def __init__ (self, laatstVerwerkt : str, isOntvlochten = False):
        # Tijdstip van de laatste momentopnamen die verwerkt is in de toestand/instrumentversie
        self.LaatstVerwerkt = laatstVerwerkt
        # Geeft aan of de branch ontvlochten is.
        # Kan bij de bepaling van de bijdragen ook de waarde None hebben, als de status van ontvlechting
        # niet eenduidig bepaald kan worden, maar het resultaat van de bepaling is in dat geval invalide
        # en wordt niet bewaard.
        self.IsOntvlochten = isOntvlochten
