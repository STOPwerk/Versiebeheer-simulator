#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# Implementatie van het generieke deel van de BG activiteiten
# die een publicatie of revisie behelzen.
#
# Deze activiteit verifieert dat alle expression-identificaties van
# de regeling- en informatieobjectversies niet eerder gepubliceerd
# zijn. Daarna wordt de consolidatie-informatie voor de publicatie
# of revisie samengesteld. De consolidatie-informatie kan in een
# afgeleide activiteit-klasse bijgesteld worden.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from data_bg_procesverloop import Branch, InteractieMelding
from data_bg_versiebeheer import Commit
from proces_bg_activiteit import Activiteit
from proces_bg_activiteit_wijzig import Activiteit_Wijzig

#======================================================================
#
# Aanmaken van een nieuw project of nieuwe branch
#
# Nadat de branch is aangemaakt kan ook al meteen een wijziging worden
# doorgevoerd. Dat wordt aan de Activiteit_Wijzig gedelegeerd.
#
#======================================================================
class Activiteit_Publiceer (Activiteit_Wijzig):
    """Maak een publicatie of revisie
    """
    def __init__ (self, soortPublicatie : str):
        super ().__init__ ()
        self.SoortPublicatie = soortPublicatie

    _Soort_Ontwerpbesluit = 'Ontwerpbesluit'
    _Soort_Vaststellingsbesluit = 'Vaststellingsbesluit'

    def _LeesData (self, log, pad) -> bool:
        ok = super ()._LeesData (log, pad)
        if not self.Project is None:
            self.UitwisselingNaam = self.SoortPublicatie + " " + self.Project
        return ok

    def _VoerUit (self, context: Activiteit._VoerUitContext):
        """Voer de activiteit uit.
        """
        if context.Activiteitverloop.Naam is None:
            context.Activiteitverloop.Naam = "Publiceer " + self._Soort.lower ()
        if context.Activiteitverloop.Beschrijving is None:
            context.Activiteitverloop.Beschrijving = "De eindgebruiker publiceert de wijzigingen in het project die zijn beschreven in een " + self._Soort.lower ()
        context.Activiteitverloop.UitwisselingMetLV = True
        # Begin met het uitvoeren van gespecificeerde wijzigingen in het versiebeheer
        context.Activiteitverloop.MeldInteractie (InteractieMelding._Instructie, 'Voer laatste aanpassingen aan de regelgeving ' + ('en/of tijdstempels ' if self.AccepteerTijdstempels else '') + 'door')
        super()._VoerUit (context)
        if not context.ProjectStatus is None:
            # Maak de consolidatie informatie
            for branch in context.ProjectStatus.Branches:
                if len (context.Activiteitverloop.Commits) == 0:
                    context.MaakCommit (branch)
                renvooi = branch.Uitgangssituatie_Renvooi
                if context.ConsolidatieInformatieMaker.VoegToe (branch, True):
                    if renvooi is None:
                        context.Activiteitverloop.MeldInteractie (InteractieMelding._Software, "Neemt de integrale regeling-/informatieobjectversie(s) op voor " + branch.InteractieNaam)
                    else:
                        context.Activiteitverloop.MeldInteractie (InteractieMelding._Software, "Maakt renvooi voor de regeling-/informatieobjectversie(s) voor " + branch.InteractieNaam + " als wijziging ten opzichte van " + renvooi._Branch.InteractieNaam)
            context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, "Controleert en verstuurt de publicatie")
