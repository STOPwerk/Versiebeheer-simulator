#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# Implementatie van de activiteit van een adviesbureau: download de
# geldende regelgeving met de downloadservice.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from data_bg_procesverloop import Branch, InteractieMelding, Activiteitverloop, UitgewisseldeSTOPModule
from data_bg_versiebeheer import Consolidatie, Commit
from data_doel import Doel
from proces_bg_activiteit import Activiteit
from stop_momentopname import Momentopname

#======================================================================
#
# Download regelgeving met de downloadservice
#
#======================================================================
class Activiteit_Download (Activiteit):
    def __init__ (self):
        super ().__init__ ()
        self._AlleenBG = False
        self._Branch : str = None

    def _LeesData (self, log, pad) -> bool:
        ok = True
        if "Branch" in self._Data and isinstance (self._Data["Branch"], str):
            self._Branch = self._Data["Branch"]
            del self._Data["Branch"]
        else:
            log.Fout ("Branch onbreekt/moet een string zijn in activiteit met Soort='Download' in '" + pad + "'")
            ok = False
        return ok

    def _VoerUit (self, context: Activiteit._VoerUitContext):
        """Voer de activiteit uit.
        """
        if self.UitgevoerdOp != context.ProjectStatus.GestartOp:
            self._LogFout (context, "moet de eerste activiteit van een project zijn")
            return

        # Maak de branch aan
        doel = Doel.DoelInstantie ('/join/id/proces/' + self._BGProcess.BGCode + '/' + self._Branch)
        context.Versiebeheer.Branches[doel] = branch = Branch (context.Versiebeheer, doel, self.UitgevoerdOp)
        context.ProjectStatus.Branches.append (branch)
        branch.Project = self.Project
        branch.InteractieNaam = context.ProjectStatus.Naam
        commit = context.MaakCommit (branch)
        commit.SoortUitwisseling = Commit._Uitwisseling_LVBB_Naar_Adviesbureau

        # Voor weergave op de resultaatpagina:
        context.Activiteitverloop.Naam = "Download regelgeving"
        context.Activiteitverloop.UitgevoerdDoor = context.ProjectStatus.UitgevoerdDoor = Activiteitverloop._Uitvoerder_Adviesbureau
        context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, '''Haalt de geldende regelgeving op bij de landelijke voorziening''')
        context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Het adviesbureau maakt in de eigen software een nieuwe branch '" + branch._Doel.Naam + "' aan")
        context.Activiteitverloop.VersiebeheerVerslag.Informatie ("De branch '" + branch._Doel.Naam + "' wordt geïdentificeerd met het doel " + branch._Doel.Identificatie)

        # Neem de huidige regelgeving als uitgangspunt
        # Ontleen die van het bevoegd gezag ipv LVBB
        if context.HuidigeRegelgeving () is None:
            self._LogFout (context, "geen geldige regelgeving beschikbaar")
            return
        branch.BaseerOpGeldendeVersie (context.Activiteitverloop.VersiebeheerVerslag, commit, context.HuidigeRegelgeving ())

        # Maak de Momentopname modules
        for workId, info in branch.Instrumentversies.items ():
            module = Momentopname ()
            module.Doel = list (info.Uitgangssituatie.UitgewisseldVoor)[0] # De eerste is goed genoeg
            module.GemaaktOp = info.Uitgangssituatie.UitgewisseldOp
            context.Activiteitverloop.Uitgewisseld.append (UitgewisseldeSTOPModule (workId,module, Activiteitverloop._Uitvoerder_LVBB, Activiteitverloop._Uitvoerder_Adviesbureau))




