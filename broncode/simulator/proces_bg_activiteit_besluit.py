#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# Implementatie van de BG activiteit "MaakBranch", die zowel het 
# aanmaken van een nieuw project als het maken van een nieuwe branch
# binnen een bestaand project implementeert.
#
# Deze activiteit kan drie soorten nieuwe branches maken:
# - Branches die gebaseerd zijn op geldende regelgeving
# - Branches die voortbouwen op een andere branch
# - Branches die bedoeld zijn als pro-actieve oplossing van samenloop,
#   te gebruiken als twee wijzigingen niet juridisch onafhankelijk van
#   elkaar zijn en voor het oplossen van samenloop een apart besluit
#   nodig is. Door de oplossing van samenloop alvast in een van de
#   besluiten op te nemen, kan de daadwerkelijke oplossing van samenloop
#   zonder publicaties plaatsvinden.
#
# De verwachting is dat de administratie voor deze soorten branches
# door BG-software wordt gedaan en niet door de eindgebruiker. Hiervoor
# is namelijk een goed begrip van het STOP versiebeheer nodig.
#
# Deze activiteit maakt het ook mogelijk meerdere branches te maken
# in een project, zodat wijzigingen op meerdere momenten in werking
# kunnen treden of om ze in verschillende besluiten vast te stellen.
# Dat is inhoudelijke regie over de wijzigingen die typisch bij de
# eindgebruiker ligt (waar BG-software al dan niet in kan ondersteunen).
#
#======================================================================

from typing import Dict, List, Set, Tuple

from data_bg_procesverloop import Branch
from data_bg_versiebeheer import Consolidatie
from data_doel import Doel
from proces_bg_activiteit import Activiteit
from proces_bg_activiteit_publiceer import Activiteit_Publiceer

#======================================================================
#
# Aanmaken van een nieuw project of nieuwe branch
#
# Nadat de branch is aangemaakt kan ook al meteen een wijziging worden
# doorgevoerd. Dat wordt aan de Activiteit_Wijzig gedelegeerd.
#
#======================================================================
class Activiteit_PubliceerBesluit (Activiteit_Publiceer):
    """Publiceer een besluit
    """
    def __init__ (self, soortBesluit : str):
        super ().__init__ (soortBesluit)
        if soortBesluit == self._Soort_Vaststellingsbesluit:
            self.AccepteerTijdstempels = True

    def _LeesData (self, log, pad) -> bool:
        ok = super ()._LeesData (log, pad)

        # TODO: Lees procedureinformatie

        return ok

    def _VoerUit (self, context: Activiteit._VoerUitContext):
        """Voer de activiteit uit.
        """
        # Pas de laatste wijzigingen toe en publiceer het besluit
        super ()._VoerUit (context)

        if self.SoortPublicatie == self._Soort_Ontwerpbesluit:
            # Consolidatie informatie is nodig, consolidatie niet
            ci = context.ConsolidatieInformatieMaker.ConsolidatieInformatie()
            if not ci is None:
                ci.VoerConsolidatieUit = False

        elif self.SoortPublicatie == self._Soort_Vaststellingsbesluit:
            # Renvooi in het vervolg ten opzichte van het vaststellingsbesluit
            for branch in context.ProjectStatus.Branches:
                branch.VastgesteldeVersieIsGepubliceerd (context.Activiteitverloop.VersiebeheerVerslag, branch.Commits[-1])
