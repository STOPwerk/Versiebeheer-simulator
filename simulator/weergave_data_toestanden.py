#======================================================================
#
# In-memory representatie van uitbreidingen op de ActueleToestanden
# en CompleteToestanden modules uit STOP en het interne datamodel.
#
#======================================================================
#
# Deze uitbreidingen zijn nodig om de weergave in deze applicatie te
# kunnen verzorgen. In een productie-waardige applicatie is deze
# informatie niet nodig.
#
# De minimale uitbreiding op de STOP modules voor het bepalen van de
# toestanden (het interne datamodel) staat in data_lv_toestanden.py.
#
#======================================================================

from typing import List

from data_doel import Doel
from data_lv_toestanden import ToestandActueel as DataToestandActueel, ToestandCompleet as SataToestandCompleet
from stop_completetoestanden import Toestand as STOPToestand, OnvolledigeVersie as STOPOnvolledigeVersie
from stop_toestand import NogTeConsolideren, Toestandidentificatie as STOPToestandidentificatie

#======================================================================
#
# Uitbreiding van de toestand-inhoud klassen
#
#======================================================================
class ConsolidatieprocesInformatie (NogTeConsolideren):
    def __init__ (self):
        super().__init__ ()

        # De identificatie van de instrumentversie die de inhoud van de toestand geeft;
        # kan None zijn. Dit is een uitkomst van het consolidatieproces
        self.Instrumentversie = None

        # De kandidaat-instrumentversie voor deze toestand
        # Alleen nodig voor weergave
        self.KandidaatInstrumentversie = None

        # Biasisversiedoelen van de toestand
        self.Basisversiedoelen = None

        # Doelen die tegelijk in werking treden maar die niet allemaal
        # dezelfde status voorschrijven voor de toestand. Er kan sprake
        # zijn van verschillende beoogde versies of combinatie van intrekking en versie(s).
        # Lijst met instanties van TegensprekendDoel.
        self.TegensprekendeDoelen = []

        # De meldingen met uitleg over het samenstellen van de toestand. 
        # Alleen nodig voor weergave.
        self._Uitleg = []

#----------------------------------------------------------------------
# Actuele toestanden
#----------------------------------------------------------------------
class ToestandActueel (DataToestandActueel):

    def __init__ (self):
        super().__init__ ()
        # Informatie over het verloop van het consolidatieproces
        # Instantie van ConsolidatieprocesInformatie
        self._Consolidatieproces = ConsolidatieprocesInformatie()
        # Unieke identificatie van een toestand, als combinatie van een ID + tijdreis
        # Voor de weergave wordt er een uniek nummer aan toegekend,
        # zodat verschillende weergaven (stukjes HTML) de toestand kunnen herkennen
        # en dezelfde toestand kunnen laten
        self.UniekId = None
        # Index van de toestand's identificatie; alleen nodig om UniekId toe te kennen
        self.Identificatie = None


#----------------------------------------------------------------------
# Complete toestanden
#----------------------------------------------------------------------
class ToestandCompleet (SataToestandCompleet):

    def __init__ (self):
        super().__init__ ()
        # Tijdstip van de uitwisseling waarin deze toestand is ontstaan
        # Alleen nodig voor de weergave
        self._GemaaktOp = None
        # Tijdstip waarop alle informatie voor deze toestand bekend was.
        # Alleen nodig voor de weergave
        self._BekendOp = None
        # Informatie over het verloop van het consolidatieproces
        # Instantie van ConsolidatieprocesInformatie
        self._Consolidatieproces = ConsolidatieprocesInformatie()

#----------------------------------------------------------------------
# Onvolledige versies
#----------------------------------------------------------------------
class OnvolledigeVersie (STOPOnvolledigeVersie):

    def __init__ (self):
        super().__init__ ()

        # De doelen waarvoor de instrumentversie is gemaakt
        self._InstrumentversieDoelen = None
        # De momentopname waarin de instrumentversie is uitgewisseld
        self._InstrumentversieGemaaktOp = None

        # De publicaties die geraadpleegd moeten worden ter aanvulling op de instrumentversie
        # Set van URL
        self.TeVerwerkenPublicaties = set()
        self.TeOntvlechtenPublicaties = set()

        # De meldingen met uitleg over het samenstellen van de toestand. 
        # Alleen nodig voor weergave.
        self._Uitleg = []

#======================================================================
#
# Complete toestanden
#
#======================================================================

#----------------------------------------------------------------------
# `Meldingen voor het bepalen van toestanden
#----------------------------------------------------------------------
class Toestandidentificatie (STOPToestandidentificatie):

    def __init__ (self):
        super().__init__ ()
        # Tijdstip van de uitwisseling waarin deze toestand is ontstaan
        # Alleen nodig voor de weergave
        self._GemaaktOp = None
        # De meldingen met uitleg over het bepalen van de toestand. 
        # Alleen nodig voor weergave.
        self._Uitleg = []

#----------------------------------------------------------------------
# Evolutie zichtbaar in weergave
#----------------------------------------------------------------------
# In deze applicatie worden alle Toestand instanties van twee extra
# attributen voorzien om bij weergave van het resultaat inzicht te
# geven in de evolutie van de toestanden.
#
# In een productie-waardige applicatie is dit niet nodig, dan kan met
# de Toestand uit stop_completetoestanden.py worden volstaan.
#----------------------------------------------------------------------
class Toestand (STOPToestand):

    def __init__ (self):
        super ().__init__()
        # Tijdstip van de uitwisseling waarin deze toestand is ontstaan
        # Alleen nodig voor de weergave
        self.GemaaktOp = None
        # Tijdstip van de uitwisseling waarin deze toestand is overschreven door een andere
        # Alleen nodig voor de weergave
        self.OverschrevenOp = None
        # Beschrijving van de toestand als tijdreis
        self._Beschrijving = None
        # De meldingen met uitleg over het bepalen van de toestand. 
        # Alleen nodig voor weergave.
        self._Uitleg = []
        # Unieke identificatie van een toestand, als combinatie van een ID + tijdreis
        # Voor de weergave wordt er een uniek nummer aan toegekend,
        # zodat verschillende weergaven (stukjes HTML) de toestand kunnen herkennen
        # en dezelfde toestand kunnen laten
        self.UniekId = None
        # Annotatieversies die voor deze
        self._Annotaties = []

class AnnotatieBijToestand:

    def __init__(self, annotatie):
        """Maak een annotatieversie aan voor een toestand
        
        Argumenten:
        
        annotatie Annotatie annotatie waarvoor tenminste één versie de toestand beschrijft"""
        self.Annotatie = annotatie
        # De gevonden uitwisselingen
        self.Uitwisseling = []
