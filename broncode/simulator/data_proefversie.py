#======================================================================
#
# Intern datamodel voor proefversies. Het is een uitbreiding op de
# de STOP Proefversies module waarin de annotaties worden meegenomen. 
# Welke annotaties bij een proefversie horen is afleidbaar voor
# elk STOP-gebruikend systeem dat over de uitwisseling van de
# annotaties beschikt en over de STOP Proefversies module.
#
# De collectie proefversies tot nu toe is onderdeel van het
# versiebeheer.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from stop_proefversies import Proefversie as STOPProefversie

#----------------------------------------------------------------------
# Proefversie
#----------------------------------------------------------------------
class Proefversie (STOPProefversie):

    def __init__ (self):
        """Maak een lege proefversie aan"""
        super().__init__ ()
        # Annotaties die voor de proefversie gebruikt moeten worden
        # # key = modulenaam, value = instantie van annotatiemodule
        self.Annotaties : Dict[str,object] = {}
