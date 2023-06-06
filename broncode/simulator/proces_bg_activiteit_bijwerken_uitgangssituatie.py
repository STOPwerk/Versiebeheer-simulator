#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# Implementatie van de BG activiteit waarbij de uitgangssituatie voor 
# elke branch wordt bijgewerkt in het project. De branch wordt
# (afhankelijk van de soort branch) opnieuw gebaseerd op de op 
# dat moment geldende regelgeving of inhoud van een andere branch 
# waar de project-branch op volgt. Daarbij worden de wijzigingen 
# die tussen de oude en nieuwe uitgangssituatie zijn aangebracht 
# overgenomen in de project-branch.
#
#======================================================================

from multiprocessing import context
from typing import Dict, List, Set, Tuple

from data_bg_procesverloop import Branch, InteractieMelding
from data_bg_versiebeheer import Commit
from proces_bg_activiteit import Activiteit
from proces_bg_activiteit_wijzig import Activiteit_Wijzig

#======================================================================
#
# Werk de uitgangssituatie bij
#
# Nadat de branch is aangemaakt kan ook al meteen een wijziging worden
# doorgevoerd. Dat wordt aan de Activiteit_Wijzig gedelegeerd.
#
#======================================================================
class Activiteit_BijwerkenUitgangssituatie (Activiteit_Wijzig):
    def __init__ (self):
        super ().__init__ ()

    def _VoerUit (self, context: Activiteit._VoerUitContext):
        """Voer de activiteit uit.
        """
        context.Activiteitverloop.Naam = "Werk de uitgangssituatie bij"
        if context.Activiteitverloop.Beschrijving is None:
            context.Activiteitverloop.Beschrijving = """De eindgebruiker neemt voor het project de wijzigingen over die 
in de uitgangssituatie van het project zijn aangebracht sinds het begin van het project (of sinds de vorige keer dat de wijzigingen zijn overgenomen)."""

        for branch in context.ProjectStatus.Branches:
            if branch._VastgesteldeVersieGepubliceerd:
                self._LogFout (context, "de activiteit kan niet uitgevoerd worden nadat een vaststellingsbesluit is gepubliceerd")
                return
            # Zorg dat er een "wijziging" klaar staat voor elke branch, dan kan de activiteit per branch
            # in de _VoerWijzigingenUit methode uitgevoerd worden.
            if not branch._Doel.Naam in self.CommitSpecificatie:
                self.CommitSpecificatie[branch._Doel.Naam] = {}

        context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, "Start het bijwerken van de uitgangssituatie");
        # Voer de wijzigingen per branch uit
        super()._VoerUit (context)

    def _VoerWijzigingenUit (self, context: Activiteit._VoerUitContext, naam: str, commit: Commit, tijdstempelsToegestaan: bool):
        """De implementatie van Activiteit_Wijzig roept dit aan voor elke branch
        """
        branch = context.Versiebeheer.Branch(naam)
        if branch is None:
            self._LogFout (context, "branch '" + naam + "' is (nog) niet aangemaakt")
            return
        commit = context.MaakCommit (branch)
        if not branch.Uitgangssituatie_Doel is None:
            nogBijTeWerken = branch.NeemVeranderdeBranchVersieOver (context.Activiteitverloop.VersiebeheerVerslag, commit)
        else:
            nogBijTeWerken = branch.NeemVeranderdeGeldendeVersieOver (context.Activiteitverloop.VersiebeheerVerslag, commit, context.HuidigeRegelgeving ())
        if not nogBijTeWerken is None:
            context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Er zijn wijzigingen overgenomen voor branch '" + naam + "'")
            if len (nogBijTeWerken) > 0:
                nogBijTeWerken = [branch.Instrumentversies[w]._Instrument.Naam for w in nogBijTeWerken] # Van workId naar naam van het work
                context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Daardoor is er samenloop ontstaan voor: '" + "', '".join (nogBijTeWerken) + "'")
                context.Activiteitverloop.MeldInteractie (InteractieMelding._Instructie, "De wijzigingen voor " + branch.InteractieNaam + " kunnen niet geautomatiseerd overgenomen worden. Los de samenloop op.");
                
                nogBijTeWerken = set (nogBijTeWerken).difference (self.CommitSpecificatie[branch._Doel.Naam].keys ())
                if len (nogBijTeWerken) > 0:
                    context.Activiteitverloop.VersiebeheerVerslag.Waarschuwing ("De gebruiker geeft geen oplossing voor de samenloop van: '" + "', '".join (nogBijTeWerken) + "'. Klopt dat wel?")
                    context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, "Lost de samenloop gedeeltelijk op.");
                else:
                    context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, "Lost de samenloop op.");

        # Pas nu de wijzigingen toe.
        super ()._VoerWijzigingenUit (context, naam, commit, False)
