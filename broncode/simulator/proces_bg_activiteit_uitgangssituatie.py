#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# Implementatie van de uitgangssituatie van het scenario.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from data_bg_procesverloop import Branch, InteractieMelding
from data_bg_versiebeheer import Consolidatie
from data_doel import Doel
from proces_bg_activiteit import Activiteit
from proces_bg_activiteit_wijzig import Activiteit_Wijzig

#======================================================================
#
# Registreer de uitgangssituatie voor een scenario.
# Dit wordt gedaan door een revisie naar de LVBB te sturen
# met daarin de initiële versies en een iwt-datum.
#
#======================================================================
class Activiteit_Uitgangssituatie (Activiteit_Wijzig):
    """Registreer de uitgangssituatie voor een scenario
    """
    def __init__ (self):
        super ().__init__ ()
        self.AccepteerTijdstempels = True
        self._ProjectVerplicht = False
        self._Soort = "Uitgangssituatie"

    def _LeesData (self, log, pad) -> bool:
        self._Data = { 
            "start": { 
                **self._Data,
                "JuridischWerkendVanaf": 0,
                "GeldigVanaf": 0
            }
        }
        return super()._LeesData (log, pad)

    def _VoerUit (self, context: Activiteit._VoerUitContext):
        """Voer de activiteit uit.
        """
        context.Activiteitverloop.Naam = "Uitgangssituatie"
        context.Activiteitverloop.MeldInteractie (InteractieMelding._Software, '''Beschikt over in werking getreden regelgeving''')

        doel = Doel.DoelInstantie ('/join/id/proces/' + self._BGProcess.BGCode + '/start')
        context.Versiebeheer.Branches[doel] = branch = Branch (context.Versiebeheer, doel, self.UitgevoerdOp)
        branch.InteractieNaam = 'Uitgangssituatie'
        commit = context.MaakCommit (branch)
        self._VoerWijzigingenUit (context, branch._Doel.Naam, commit, True)
        context.ConsolidatieInformatieMaker.VoegToe (branch, True)


