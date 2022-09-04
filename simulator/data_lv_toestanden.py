#======================================================================
#
# In-memory representatie van uitbreidingen op de ActueleToestanden
# en CompleteToestanden modules uit STOP.
#
#======================================================================
#
# Het interne datamodel voor toestanden van deze applicatie is
# uitgebreider dan dat van STOP, om het administreren van de toestanden
# te faciliteren.
# 
# Om extra informatie te presenteren over de bepaling van de toestanden
# en om de weergavecode te vereenvoudigen zijn er extra attributen 
# aan andere STOP elementen toegevoegd; die staan in
# weergave_data_toestanden.py.
#
#======================================================================

from typing import List

from stop_actueletoestanden import ToestandActueel as STOPToestandActueel
from stop_completetoestanden import CompleteToestanden as STOPCompleteToestanden, ToestandCompleet as STOPToestandCompleet, Tijdreisfilter, ToestandCompleet
from stop_toestand import Toestandidentificatie

#======================================================================
#
# Inhoud van de toestanden
#
#----------------------------------------------------------------------
#
# De basisversiedoelen hoeven niet uitgeleverd te worden maar spelen
# wel een rol bij de consolidatie
#
#======================================================================

#----------------------------------------------------------------------
# ToestandActueel
#----------------------------------------------------------------------
class ToestandActueel (STOPToestandActueel):

    def __init__(self):
        super ().__init__ ()
        # De doelen die ook nog in deze toestand verwerkt zijn
        # Lijst met instanties van Doel
        self.Basisversiedoelen = []
        # Geeft aan of de actuele toestand nog actueel
        # is. In deze applicatie worden de niet-actuele ActueleToestanden nog
        # wel bepaald omdat het effect van bijvoorbeeld een vernietiging van een
        # besluit in een ver verleden het eenvoudigste uit te leggen is via 
        # ActueleToestanden - inzichtelijker dan voor het volledig tijdreizen
        # met CompleteToestanden.
        self.NietMeerActueel = False

#----------------------------------------------------------------------
# ToestandCompleet
#----------------------------------------------------------------------
class ToestandCompleet (STOPToestandCompleet):

    def __init__(self):
        super ().__init__ ()
        # De doelen die ook nog in deze toestand verwerkt zijn
        # Lijst met instanties van Doel
        self.Basisversiedoelen = []


#======================================================================
#
# Complete toestanden
#
#======================================================================

#----------------------------------------------------------------------
# Index van inhoud
#----------------------------------------------------------------------
class CompleteToestanden (STOPCompleteToestanden):

    def __init__(self, toestandIdentificatie : List[Toestandidentificatie]):
        """Maak nieuwe complete toestanden aan
        
        Argumenten:
        toestandIdentificatie Toestandidentificatie[] Lijst met toestandidentificaties; deze wordt bijgehouden in dat_consolidatie 
                                                      omdat de identificaties gedeeld worden met de actuele toestanden
        toestandInhoudIndex {} Opslag van toestand inhoud. In deze applicatie gedeeld met alle andere instrumenten 
        """
        super().__init__()
        # De ToestandInhoud moet een array van unieke ToestandCompleet instanties zijn
        # In een productie-waardige applicatie zou daarvoor netjes een vergelijking van toestanden
        # gecodeerd kunnen worden, en/of iets met een hash, zodat opslag en geheugengebruik binnen
        # de perken blijft. Voor deze applicatie wordt een sneller te programmeren manier gebruikt
        # door de XML van de ToestandCompleet als key in een collectie te gebruiken.
        # key = XML voor ToestandCompleet, value = index van ToestandCompleet in ToestandInhoud
        self.ToestandIdentificatie = toestandIdentificatie
        self._ToestandInhoudIndex = {}
        self.Tijdreisfilter = Tijdreisfilter ()

    def ToestandInhoudIndex (self, toestandInhoud : ToestandCompleet):
        """Geef de index van de inhoud in het ToestandInhoud array.
        Als de inhoud nog niet in het array staat, voeg het dan toe.
        
        Argumenten:
        toestandInhoud ToestandCompleet  Volledige inhoud van de toestand
        """
        xml = '\n'.join (toestandInhoud.ModuleXmlElement (0))
        index = self._ToestandInhoudIndex.get (xml)
        if index is None:
            self._ToestandInhoudIndex[xml] = index = len (self.ToestandInhoud)
            self.ToestandInhoud.append (toestandInhoud)
        return index
