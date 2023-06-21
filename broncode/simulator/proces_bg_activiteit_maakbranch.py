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

from data_bg_procesverloop import Branch, InteractieMelding
from data_bg_versiebeheer import Consolidatie
from data_doel import Doel
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
class Activiteit_MaakBranch (Activiteit_Wijzig):
    def __init__ (self):
        super ().__init__ ()
        # Branches die aangemaakt moeten worden
        # key = naam, value = soort, branches waarvan de branch afhankelijk is
        self.BranchSpecificatie : Dict[str,Tuple[str,Set[str]]] = {}

    def _LeesData (self, log, pad) -> bool:
        ok = True
        for naam, specificatie in self._Data.items ():
            if isinstance (specificatie, dict):
                if "Soort" in specificatie:
                    branches = []
                    if specificatie["Soort"] == "VolgendOp":
                        if not "Branch" in specificatie or not isinstance (specificatie["Branch"], str):
                            log.Fout ("Branch onbreekt/moet een string zijn voor branch '" + naam + "' in activiteit met Soort='" + self._Soort + "' in '" + pad + "'")
                            ok = False
                        else:
                            branches = [specificatie["Branch"]]
                            del specificatie["Branch"]
                    elif specificatie["Soort"] == "TegelijkMet":
                        if not "Branches" in specificatie or not isinstance (specificatie["Branches"], list) or len (specificatie["Branches"]) <= 1:
                            log.Fout ("Branches onbreekt/moet een array zijn (met minimaal 2 branchnamen) voor branch '" + naam + "' in activiteit met Soort='" + self._Soort + "' in '" + pad + "'")
                            ok = False
                        else:
                            branches = specificatie["Branches"]
                            del specificatie["Branches"]
                    elif specificatie["Soort"] != "Regulier":
                        log.Fout ("Soort onbreekt voor branch '" + naam + "' in activiteit met Soort='" + self._Soort + "' in '" + pad + "'")
                        ok = False
                    self.BranchSpecificatie[naam] = (specificatie["Soort"], branches)
                    del specificatie["Soort"]
        if not super()._LeesData (log, pad):
            ok = False
        return ok

    def _VoerUit (self, context: Activiteit._VoerUitContext):
        """Voer de activiteit uit.
        """
        isNieuwProject = self.UitgevoerdOp == context.ProjectStatus.GestartOp
        if isNieuwProject:
            if context.Activiteitverloop.Naam is None:
                context.Activiteitverloop.Naam = "Maak nieuw project"
            if not context.Activiteitverloop.Beschrijving:
                context.Activiteitverloop.Beschrijving = "De eindgebruiker start een project om aan nieuwe regelgeving te werken."
            context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, '''Maakt een nieuw project aan.''')

            context.Activiteitverloop.MeldInteractie (InteractieMelding._Instructie, '''Maak voor elk beoogde inwerkingtredingsmoment een kopie van de regelgeving.
Binnen het project wordt de kopie gewijzigd zonder dat dit meteen invloed heeft op de werkzaamheden in andere projecten.''')
            context.Activiteitverloop.MeldInteractie (InteractieMelding._Instructie, '''Maak ook een apart inwerkingtredingsmoment aan als de wijzigingen voor het
project in twee of meer besluiten zullen worden vastgelegd en het is niet zeker dat alle besluiten daadwerkelijk vastgesteld zullen worden
en/of er beroep mogelijk is tegen de besluiten, waardoor een besluit uiteindelijk tot andere regelgeving kan leiden.''')
        else:
            if context.Activiteitverloop.Naam is None:
                context.Activiteitverloop.Naam = "Bereid nieuwe inwerkingtredingsmomenten voor"
            if not context.Activiteitverloop.Beschrijving:
                context.Activiteitverloop.Beschrijving = "De eindgebruiker maakt een kopie van de regelgeving om binnen het project aan te werken."

        context.Activiteitverloop.MeldInteractie (InteractieMelding._Instructie, '''Geef per beoogd inwerkingtredingsmoment aan op welke manier de inwerkingtreding beoogd is. In deze simulator kan gekozen worden uit:
<ol>
  <li>Als volgende versie van de geldende regelgeving<br/>
  Er wordt een kopie gemaakt van de nu geldende regelgeving. Als deze niet voor alle regelingen en informatieobjecten beschikbaar is omdat de consolidatie daarvan
  nog niet is afgerond, dan wordt een eerder geldige versie gebruikt.</li>
  <li>Als vervolg op een ander beoogd inwerkingtredingsmoment binnen of buiten dit project.<br/>
  Er wordt een kopie gemaakt van de regelgeving voor dat inwerkingtredingsmoment.</li>
  <li>Als oplossing van samenloop van regelgeving voor twee of meer beoogde inwerkingtredingsmomenten; aan één ervan wordt binnen dit project gewerkt.<br/>
  Het is de bedoeling dat de samenloop-oplossing alleen in werking treedt als de laatste van de andere inwerkingtredingsmomenten in werking treedt.
  Er wordt een kopie gemaakt van de regelgeving voor het inwerkingtredingsmoment binnen dit project.</li>
</ol>
''')
        context.Activiteitverloop.MeldInteractie (InteractieMelding._Instructie, 'Pas eventueel de regelgeving aan na het aanmaken van de kopie')
        self._VoerMaakBranchUit (context)

    def _VoerMaakBranchUit (self, context: Activiteit._VoerUitContext):
        """Maak de opgegeven branches aan
        """
        # Klaar = branches die geïnitialiseerd zijn
        klaar : Set[Doel] = set (context.Versiebeheer.Branches.keys ())
        # nogInitialiseren = branches die niet meteen geïnitialiseerd worden
        nogInitialiseren : List[Tuple[Branch,str,Set[Doel]]] = []

        # Verifieer dat de nieuwe branches nog niet bestaan
        for naam, (soort, doelen) in self.BranchSpecificatie.items ():
            doel = Doel.DoelInstantie ('/join/id/proces/' + self._BGProcess.BGCode + '/' + naam)
            branch = context.Versiebeheer.Branches.get (doel)
            if not branch is None:
                self._LogFout (context, "doel '" + naam + "' bestaat al")
                continue
            # Maak de branch aan
            context.Versiebeheer.Branches[doel] = branch = Branch (context.Versiebeheer, doel, self.UitgevoerdOp)
            branch.Project = self.Project
            # Stel initialisatie nog even uit
            nogInitialiseren.append ((branch, soort, [Doel.DoelInstantie ('/join/id/proces/' + self._BGProcess.BGCode + '/' + b) for b in doelen]))

        # Initialiseer de branches
        while len (nogInitialiseren) > 0:
            nogSteedsInitialiseren : List[Tuple[Branch,str,Set[Doel]]] = []
            nuKlaar : List[Doel] = []
            for branch, soort, doelen in nogInitialiseren:
                if len (set(doelen).difference (klaar)) > 0:
                    # Nog niet alle branches zijn geïnitialiseerd
                    nogSteedsInitialiseren.append ((branch, soort, doelen))
                    continue
                commit = context.MaakCommit (branch)

                # Voeg de branch toe aan de branches voor het project
                # en maak een naam die voor eindgebruikers herkenbaar is
                context.ProjectStatus.Branches.append (branch)
                kopieNummer = len (context.ProjectStatus.Branches)
                if kopieNummer == 1:
                    # Eerste branch
                    branch.InteractieNaam = context.ProjectStatus.Naam
                    kopieNaam = 'kopie'
                else:
                    if kopieNummer == 2:
                        # Geef eerste branch ander nummer
                        context.ProjectStatus.Branches[0].InteractieNaam = 'inwerkingtredingmoment #1 in ' + context.ProjectStatus.Naam
                    branch.InteractieNaam = 'inwerkingtredingmoment #' + str(kopieNummer) + ' in ' + context.ProjectStatus.Naam
                    kopieNaam = 'kopie voor inwerkingtredingmoment #' + str(kopieNummer)

                if soort == "Regulier":
                    # Voor weergave op de resultaatpagina:
                    context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, "Maakt " + kopieNaam + " bedoeld als volgende versie van de geldende regelgeving")
                    context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Er wordt een nieuwe branch '" + branch._Doel.Naam + "' aangemaakt voor regelgeving bedoeld als volgende versie van de geldende regelgeving")
                    context.Activiteitverloop.VersiebeheerVerslag.Informatie ("De branch '" + branch._Doel.Naam + "' wordt geïdentificeerd met het doel " + branch._Doel.Identificatie)
                    # Neem de huidige regelgeving als uitgangspunt
                    branch.BaseerOpGeldendeVersie (context.Activiteitverloop.VersiebeheerVerslag, commit, context.HuidigeRegelgeving ())
                else:
                    # Voor weergave op de resultaatpagina:
                    branches = [context.Versiebeheer.Branches[d] for d in doelen]
                    if len(doelen) > 1:
                        context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, "Maakt " + kopieNaam + " die in werking treedt zodra alle regelgeving in werking getreden is van: " + ", ".join (b.InteractieNaam for b in branches))
                        context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Er wordt een nieuwe branch '" + branch._Doel.Naam + "' aangemaakt als oplossing van de samenloop van branches '" + "', '".join (d.Naam for d in doelen) + "'")
                        # Verifieer dat de eerste branch bij het project hoort
                        if not doelen[0] in set (b._Doel for b in context.ProjectStatus.Branches):
                            self._LogFout (context, "branch '" + branch._Doel.Naam + "': de eerste branch '" + doelen[0].Naam + "' waarvoor samenloop opgelost moet worden moet binnen het project liggen")
                        branch.TreedtConditioneelInWerkingMet = set (branches)
                    else:
                        context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, "Maakt " + kopieNaam + " die in werking treedt na " + branches[0].InteractieNaam)
                        context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Er wordt een nieuwe branch '" + branch._Doel.Naam + "' aangemaakt die in werking treedt na branch '" + doelen[0].Naam + "'")
                    context.Activiteitverloop.VersiebeheerVerslag.Informatie ("De branch '" + branch._Doel.Naam + "' wordt geïdentificeerd met het doel " + branch._Doel.Identificatie)
                    branch.BaseerOpBranch (context.Activiteitverloop.VersiebeheerVerslag, commit, context.Versiebeheer.Branches[doelen[0]])
                nuKlaar.append (branch._Doel)
                self._VoerWijzigingenUit (context, branch._Doel.Naam, commit, False)
            if len (nogSteedsInitialiseren) == len (nogInitialiseren):
                self._LogFout (context, "branches kunnen niet aangemaakt worden (ze verwijzen circulair naar elkaar?): '" + "', '".join (branch._Doel.Naam for branch, soort, branches in nogInitialiseren) + "'")
                return
            nogInitialiseren = nogSteedsInitialiseren
            klaar.update (nuKlaar)
            nuKlaar = []

