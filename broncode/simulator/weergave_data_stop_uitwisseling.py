#======================================================================
#
# Intern datamodel voor de weergave van de uitwisseling van
# STOP modules gedurende de simulatie
#
#======================================================================

from typing import Dict, List, Set, Tuple

#----------------------------------------------------------------------
# Collectie van uitgewisselde STOP modules
#----------------------------------------------------------------------
class UitgewisseldeSTOPModules:

    def __init__(self):
        # Uitgewisselde STOP modules
        # key: gemaaktOp
        self.Uitwisselingen: Dict[str,List[STOPModuleUitwisseling]] = {}


    def VoegToe (self, ontvangenOp : str, verzender : str, ontvanger : str, module):
        """Voeg een uitwisseling toe
        
        ontvangenOp string  Het moment van uitwisselen
        verzender   string  Het systeem dat de STOP informatie opstelt
        ontvanger   string  Het systeem dat de STOP informatie ontvangt
        module      object  In-memory representatie van een STOP module, moet een 
                            ModuleXml() methode hebben die de STOP xml producteert
        """
        lijst = self.Uitwisselingen.get (ontvangenOp)
        if lijst is None:
            self.Uitwisselingen[ontvangenOp] = lijst = []
        lijst.append (STOPModuleUitwisseling (verzender, ontvanger, module))

#----------------------------------------------------------------------
# Enkele uitwisseling van STOP modules
#----------------------------------------------------------------------
class STOPModuleUitwisseling:

    Systeem_BevoegdGezag = 'Bevoegd gezag'
    Systeem_LVBB = 'LVBB'
    Systeem_LVBBAfnemer = 'LVBB afnemer'

    def __init__ (self, verzender : str, ontvanger : str, module):
        """Maak een uitwisseling aan
        
        verzender string  Het systeem dat de STOP informatie opstelt
        ontvanger string  Het systeem dat de STOP informatie ontvangt
        module object     In-memory representatie van een STOP module, moet een 
                          ModuleXml() methode hebben die de STOP xml producteert
        """
        # Annotaties die voor de proefversie gebruikt moeten worden
        self.Verzender = verzender
        self.Ontvanger = ontvanger
        self.Module = module

#----------------------------------------------------------------------
# Snapshot van een module die in de loop van de simulatie kan wijzigen
#----------------------------------------------------------------------
class STOPModuleSnapshot:

    def __init__ (self, module):
        self._ModuleXml = module.ModuleXml ()
        self.WeergaveBeschrijving = module.WeergaveBeschrijving

    def ModuleXml (self):
        return self._ModuleXml
