#======================================================================
#
# In-memory model voor het relateren van annotatieversies aan
# actuele toestanden. Dat kan op twee manieren: via de annotaties
# van proefversies, of via synchronisatie aan de hand van doelen.
# Dit model brengt beide bijeen. Het maakt ex-tunc tijdreizen
# op de annotatieversies mogelijk.
#
#======================================================================

from typing import List

from data_annotatie import Annotatie, AnnotatieVersie
from data_proefversies import Proefversie, ProefversieAnnotatie
from stop_actueletoestanden import ActueleToestanden
from weergave_data_toestanden import  ToestandActueel

class ActueleAnnotatieVersie:

    def __init__(self, versies, uitleg):
        # Versie(s) van de annotatie afgeleid uit de proefversie
        # Lijst met instanties van AnnotatieVersie, gesorteerd op _Nummer
        self.Versies = versies
        # Alleen voor weergave: uitleg (indien nodig) waarom de versie is zoals die is
        self.Uitleg = uitleg

class ExTuncToestand:

    def __init__(self, tijdstip, juridischWerkendVanaf, inhoud):
        # Het tijdstip waarop er iets aan de annotatie of inhoud van de actuele toestandwijzigt
        self.Tijdstip = tijdstip
        # Eerste datum waarop de wijziging juridisch in werking is
        self.JuridischWerkendVanaf = juridischWerkendVanaf
        # De inhoud van de actuele toestand of de annotatieversie die deze toestand
        # beschrijft, als index in de ToestandInhoud
        self.Inhoud = inhoud

class ExTuncTijdlijn:

    def __init__ (self):
        # De tijdstempels voor het voorkomen van een bepaalde versie van het instrument
        # of van aan annotatie, geschikt voor tijdreizen (dus net als bij CompleteToestanden)
        # Lijst met instanties van ExTuncToestand
        self.Toestanden = []
        # Bij elkaar horende instrumentversie en annotaties die de inhoud toestand weergeven
        # Lijst met instanties van ToestandActueel (actuele toestand) of ActueleAnnotatieVersie
        self.ToestandInhoud = []

class ActueleToestandenMetAnnotaties:

    def __init__ (self, annotaties: List[Annotatie]):
        # De toestanden met voorkomens van annotaties, aflopend gesorteerd op tijdstip
        # Lijst met instanties van ActueleToestandMetAnnotarties
        self.ActueleToestanden = ExTuncTijdlijn ()
        # De annotatieversies die via proefversies aan de actuele toestand gekoppeld kunnen worden
        # Key = Annotatie, value = ExTuncTijdlijn
        self.UitProefversies = { a : ExTuncTijdlijn () for a in annotaties if a.ViaVersiebeheer }
        # De annotatieversies die aan de hand van de inwerkingtredingsdoelen van de actuele toestand 
        # gekoppeld worden, waarbij een annotatieversie voor die specifieke toestand bedoeld moet zijn.
        # Key = Annotatie, value = ExTuncTijdlijn
        self.VoorToestandViaDoelen = { a : ExTuncTijdlijn () for a in annotaties }
        # De annotatieversies die aan de hand van de inwerkingtredingsdoelen van de actuele toestand 
        # gekoppeld worden, waarbij een annotatieversie voor een specifiek doel bedoeld is.
        # Key = Annotatie, value = ExTuncTijdlijn
        self.VoorDoel = { a : ExTuncTijdlijn () for a in annotaties }
