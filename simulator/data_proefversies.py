#======================================================================
#
# Intern datamodel voor proefversies. Het is een uitbreiding op de
# de STOP Proefversies module waarin de annotaties worden meegenomen. 
# Welke annotaties bij een proefversie horen is afleidbaar voor
# elk STOP-gebruikend systeem dat over de uitwisseling van de
# annotaties beschikt en over de STOP Proefversies module.
#
#======================================================================

from stop_proefversies import Proefversie as STOPProefversie

#----------------------------------------------------------------------
# Proefversie
#----------------------------------------------------------------------
class Proefversie (STOPProefversie):

    def __init__ (self):
        """Maak een lege proefversie aan"""
        super().__init__ ()
        # Annotaties die voor de proefversie gebruikt moeten worden
        # Lijst met instanties van ProefversieAnnotatie
        self.Annotaties = []

class ProefversieAnnotatie:

    def __init__ (self):
        # Naam van de annotatie
        self.Naam = None
        # De versie van de annotatie die gebruikt moet worden voor de proefversie
        self.Versie = None
        # Annotatie waar dit een versie van is
        self._Annotatie = None
