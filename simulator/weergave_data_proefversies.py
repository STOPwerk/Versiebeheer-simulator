#======================================================================
#
# In-memory representatie van uitbreidingen op de Proefversies
# modules uit STOP en het interne datamodel.
#
#======================================================================
#
# Deze uitbreidingen zijn nodig om de weergave in deze applicatie te
# kunnen verzorgen. In een productie-waardige applicatie is deze
# informatie niet nodig.
#
# De minimale uitbreiding op de STOP modules voor het bepalen van de
# proefversies (het interne datamodel) staat in data_proefversies.py.
#
#======================================================================

from data_proefversies import Proefversie as DataProefversie, ProefversieAnnotatie as DataProefversieAnnotatie
from stop_proefversies import Proefversies as STOPProefversies

#----------------------------------------------------------------------
#
# Proefversies module
#
#----------------------------------------------------------------------
#
# In deze applicatie wordt elke proefversie afzonderlijk in een
# Proefversies module getoond. Volgens STOP zijn dat alle proefversies
# in een uitwisseling, maar dat maakt de presentatie van de resultaten
# onoverzichtelijk.
#
#----------------------------------------------------------------------
class Proefversies(STOPProefversies):

    def __init__(self, bekendOp, ontvangenOp, proefversie):
        """Maak een module aan voor een enkele proefversie"""
        super().__init__()
        self.BekendOp = bekendOp
        self.OntvangenOp = ontvangenOp
        self.Proefversies.append (proefversie)


    def ModuleXmlAttributen (self):
        """Voeg extra attributen toe"""
        return ['',
                '<!-- Overige regeling-/informatieobjectversies uit de uitwisseling -->']

#----------------------------------------------------------------------
# Proefversie
#----------------------------------------------------------------------
class Proefversie (DataProefversie):

    def __init__ (self):
        """Maak een lege proefversie aan"""
        super().__init__ ()
        # Uitleg over de constructie van de proefversie
        # Lijst van instanties van Melding
        self._Uitleg = []
        # Een unieke ID voor de proefversie voor UX doeleinden
        self._UniekeId = None

class ProefversieAnnotatie (DataProefversieAnnotatie):

    def __init__ (self):
        super().__init__ ()
        # Uitleg over de selectie van de annotatie
        # Lijst van instanties van Melding
        self._Uitleg = []
        # De delen van branches die onderzocht zijn
        # Lijst met tuples (doel, vanaf, totEnMet)
        self._Onderzocht = []
        # Uitwisselingen waar een tegenstrijdige versie tegengekomen is
        # Lijst met tuples (doel, gemaaktOp)
        self._Tegenstrijdig = []
        # Uitwisselingen die aanleiding geven tot een vermelding in _Tegenstrijdig
        self._TegenstrijdigeVersies = set ()
        # Uitwisselingen die als bron tegengekomen zijn
        # Lijst met tuples (doel, gemaaktOp)
        self._Bronnen = []
