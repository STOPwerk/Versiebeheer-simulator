#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# Implementatie van de activiteit van een adviesbureau i.s.m.
# een bevoegd gezag: wissel regelgeving uit die het adviesbureau
# heeft aangepast / nog moet aanpassen.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from data_bg_procesverloop import Branch, InteractieMelding, Activiteitverloop, UitgewisseldeSTOPModule
from data_bg_versiebeheer import Consolidatie, Commit
from data_doel import Doel
from proces_bg_activiteit import Activiteit
from stop_momentopname import InstrumentversieInformatie, Momentopname

#======================================================================
#
# Wissel regelgeving uit tussen adviesbureau en bevoegd gezag
#
#======================================================================
class Activiteit_Uitwisseling (Activiteit):
    def __init__ (self):
        super ().__init__ ()
        self._AlleenBG = False
        self._Branch : str = None

    def _LeesData (self, log, pad) -> bool:
        return True

    def _VoerUit (self, context: Activiteit._VoerUitContext):
        """Voer de activiteit uit.
        """
        if len (context.ProjectStatus.Branches) != 1:
            self._LogFout (context, "is alleen mogelijk als het project slechts één branch heeft (beperking van de simulator)")
            return
        branch = context.ProjectStatus.Branches[0]
        module = Momentopname ()
        module.Doel = branch._Doel
        module.GemaaktOp = self.UitgevoerdOp
        commit = context.MaakCommit (branch)

        # Voor weergave op de resultaatpagina:
        if context.ProjectStatus.UitgevoerdDoor == Activiteitverloop._Uitvoerder_Adviesbureau:
            context.Activiteitverloop.Naam = "Oplevering"
            context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, '''Levert de aangepaste regelgeving op aan het bevoegd gezag''')
            context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Het bevoegd gezag neemt de regelgeving voor de branch '" + branch._Doel.Naam + "' over in de eigen software")
            context.ProjectStatus.UitgevoerdDoor = Activiteitverloop._Uitvoerder_BevoegdGezag
            commit.SoortUitwisseling = Commit._Uitwisseling_Adviesbureau_Naar_BG

            # Maak de InstrumentversieInformatie module
            for workId, info in branch.Instrumentversies.items ():
                if not info.Instrumentversie.ExpressionId is None:
                    instrument = InstrumentversieInformatie ()
                    instrument.WorkId = workId
                    instrument._ExpressionId = info.Instrumentversie.ExpressionId
                    if context.ProjectStatus.LaatstUitgewisseldDoor is None:
                        # Komt van de downloadservice, gebruik dus de uitgangssituatie
                        instrument.Basisversie_Doel = list (info.Uitgangssituatie.UitgewisseldVoor)[0]
                        instrument.Basisversie_GemaaktOp = info.Uitgangssituatie.UitgewisseldOp
                    else:
                        # Komt van bevoegd gezag, dus voor hetzelfde doel
                        instrument.Basisversie_Doel = branch._Doel
                        instrument.Basisversie_GemaaktOp = context.ProjectStatus.LaatstUitgewisseldOp
                    module.Instrumentversies.append (instrument)
        else:
            context.Activiteitverloop.Naam = "Verstrek opdracht"
            context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, '''Verstrekt een opdracht tot aanpassing van de regelgeving aan een afviesbureau, en levert de versie van de regelgeving mee waar het adviesbureau aan moet werken.''')
            context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Het adviesbureau neemt de regelgeving over in de eigen software.")
            context.ProjectStatus.UitgevoerdDoor = Activiteitverloop._Uitvoerder_Adviesbureau
            commit.SoortUitwisseling = Commit._Uitwisseling_BG_Naar_Adviesbureau

        context.ProjectStatus.LaatstUitgewisseldDoor = context.Activiteitverloop.UitgevoerdDoor
        context.ProjectStatus.LaatstUitgewisseldOp = self.UitgevoerdOp
        context.Activiteitverloop.Uitgewisseld.append (UitgewisseldeSTOPModule (workId, module, context.ProjectStatus.LaatstUitgewisseldDoor, context.ProjectStatus.UitgevoerdDoor))



