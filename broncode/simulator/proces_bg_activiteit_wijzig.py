#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# Implementatie van de BG activiteit "Wijzig", die het aanpassen van
# de inhoud van het interne versiebeheer implementeert.
#
# Deze activiteit voert uit wat er in de specificatie staat: het
# muteren van een regeling-/informatieobjectversie (wijzigen, 
# onbekende versie toekennen, terugtrekken van een wijziging op de 
# branch, intrekken van het instrument) en bijbehorende annotaties.
# De activiteit zorgt ook voor het bijhouden van informatie voor de
# weergave in de resultaatpagina.
#
# Deze activiteit is te beschouwen als een proxy voor het versiebeheer
# dat BG-software moet uitvoeren. Voor leveranciers van BG-software 
# valt hier niets te leren.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from data_bg_procesverloop import InteractieMelding
from data_bg_versiebeheer import Commit, Instrument, InstrumentInformatie
from data_doel import Doel
from proces_bg_activiteit import Activiteit

#======================================================================
#
# Wijziging van instrumentversies en/of tijdstempels in de branch
#
# Commit nieuwe instrumentversies en evt annotaties voor één of meer
# branches. Deze activiteit is tevens de basis voor een aantal andere
# activiteiten die daarna (of daarvoor) iets met de branches doen.
#
#======================================================================
class Activiteit_Wijzig (Activiteit):
    """Commit nieuwe instrumentversies en evt annotaties voor één of meer branches. 
    Deze activiteit is tevens de basis voor een aantal andere activiteiten die daarna (of 
    daarvoor) iets met de branches doen.
    """
    def __init__ (self):
        super ().__init__ ()
        # Branches waarvoor wijzigingen zijn opgegeven
        # key = naam, value = specificatie van de wijziging (lezen bij uitvoeren van de activiteit)
        self.CommitSpecificatie : Dict[str,object] = {}
        # Geeft aan of deze activiteit tijdstempels accepteert
        # Tijdstempels zijn in het algemeen niet toegestaan, die mogen pas 
        # bij een vaststellingsbesluit toegevoegd worden.
        self.AccepteerTijdstempels : bool = False
        if type (self) == Activiteit_Wijzig:
            # Zelfstandige activiteit, mag adviesbureau ook uitvoeren
            self._AlleenBG = False

    def _LeesData (self, log, pad) -> bool:
        # De rest van de specificatie wordt bij uitvoering gelezen
        for naam, specificatie in self._Data.items ():
            if isinstance (specificatie, dict):
                self.CommitSpecificatie[naam] = specificatie
        return True

    def _VoerUit (self, context: Activiteit._VoerUitContext):
        """Voer de activiteit uit.
        """
        # Voor weergave in de resultaatpagina:
        if context.Activiteitverloop.Naam is None:
            context.Activiteitverloop.Naam = "Wijzig regelgeving"
            if len (context.ProjectStatus.Branches) > 1:
                context.Activiteitverloop.MeldInteractie (InteractieMelding._Instructie, 'Pas de regelgeving ' + ('en/of tijdstempels ' if self.AccepteerTijdstempels else '') + 'aan voor één of meer van de beoogde inwerkingtredingsmomenten (branches) in het project')
            else:
                context.Activiteitverloop.MeldInteractie (InteractieMelding._Instructie, 'Pas de regelgeving ' + ('en/of tijdstempels ' if self.AccepteerTijdstempels else '') + 'aan in het project')
        if len (self.CommitSpecificatie) > 0:
            if context.Activiteitverloop.Beschrijving is None:
                context.Activiteitverloop.Beschrijving = "De eindgebruiker wijzigt de kopie van de regelgeving waaraan binnen het project wordt gewerkt."

        # Valideer dat de branches bestaan waarvoor wijzigigen zijn opgegeven
        onbekendeNamen = set(self.CommitSpecificatie.keys()).difference (b._Doel.Naam for b in context.ProjectStatus.Branches)
        if len (onbekendeNamen) > 0:
            self._LogFout (context, "het wijzigen van regelgeving moet beperkt zijn tot de branches van het project '" + self.Project + "', dus niet: '" + "', '".join (onbekendeNamen) + "'")
            return

        # Pas de wijzigingen toe, op volgorde van de branches in het project
        # (dat is nodig voor afgeleide klassen)
        for branch in context.ProjectStatus.Branches:
            if branch._Doel.Naam in self.CommitSpecificatie:
                self._VoerWijzigingenUit (context, branch._Doel.Naam, None, self.AccepteerTijdstempels)

    def _VoerWijzigingenUit (self, context: Activiteit._VoerUitContext, naam: str, commit: Commit, tijdstempelsToegestaan: bool):
        """Neem wijzigingen voor de branches over. Alle (overgebleven) attributen 
        van de specificatie die als waarde een JSON object hebben
        worden geacht specificaties van instrumentversies voor een
        bestaande branch te zijn.

        Argumenten:

        context _VoerUitContext Context van de uitvoering
        naam string  Naam van de branch (moet in self.CommitSpecificatie voorkomen)
        commit Commit  Commit waar de wijziging deel van uitmaakt. None om een nieuwe commit aan te maken.
        tijdstempelsToegestaan boolean  Geeft aan of ook tijdstempels opgegeven mogen worden
        """
        # Valideer dat de branch bestaat, er wijzigingen zijn, en de wijzigingen toegepast mogen worden
        specificatie = self.CommitSpecificatie.get (naam)
        if specificatie is None:
            return
        branch = context.Versiebeheer.Branch (naam)
        if branch is None:
            self._LogFout (context, "branch '" + naam + "' is (nog) niet aangemaakt")
            return
        if self._ProjectVerplicht:
            if branch.Project is None:
                self._LogFout (context, "branch '" + naam + "' wordt niet via BG activiteiten beheerd maar via uitgewisselde ConsolidatieInformatie modules")
                return
            elif not self.Project is None and branch.Project != self.Project:
                self._LogFout (context, "branch '" + naam + "' wordt in project '" + branch.Project + "' beheerd maar deze activiteit is voor project '" + self.Project + "'")
                return

        # Pas de wijzigingen per instrument toe
        regelgevingGewijzigd = False
        for workIdNaam, versie in specificatie.items ():
            if workIdNaam == "JuridischWerkendVanaf" or workIdNaam == "GeldigVanaf":
                continue
            instrument = context.Versiebeheer.Instrumenten.get (workIdNaam)
            if instrument is None:
                instrument = Instrument.Bepaal (self, context.Versiebeheer, workIdNaam)
                if instrument is None:
                    self._LogFout (context, "Soort instrument kan niet bepaald worden voor '" + workIdNaam + "'")
                    continue
            info = branch.Instrumentversies.get (instrument.WorkId)
            regelgevingGewijzigd = True
            if commit is None:
                commit = context.MaakCommit (branch)

            # Invoer kan zijn:
            #   null: intrekken van instrument
            #   false: terugtrekken van instrument
            #   true: onbekende versie
            #   { ... }: bekende versie, evt met annotaties
            if versie is None:
                # Intrekking van het instrument
                if info is None:
                    self._LogFout (context, "geen informatie over instrument '" + workIdNaam + "' bekend voor branch '" + branch._Doel.Naam + "'; kan het instrument niet intrekken")
                    continue
                context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Branch '" + naam + "': markeer instrument '" + workIdNaam + "' als juridisch uitgewerkt")
                # Leg de intrekking vast in een nieuwe Instrumentversie
                info.TrekInstrumentIn (commit)
            else:
                instrumentversie = None
                if isinstance (versie, bool):
                    if versie:
                        # Nieuwe maar onbekende/niet-ingevoerde versie van het instrument
                        if info is None:
                            self._LogFout (context, "geen informatie over instrument '" + workIdNaam + "' bekend voor branch '" + branch._Doel.Naam + "'; kan geen onbekende versie specificeren")
                            continue
                        if not info.IsGewijzigdInBranch ():
                            self._LogFout (context, "instrument '" + workIdNaam + "' is niet gewijzigd voor branch '" + branch._Doel.Naam + "'; kan geen onbekende versie specificeren")
                            continue
                        info.WijzigInstrument (commit, None)
                        context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Branch '" + naam + "': markeer versie als onbekend voor instrument '" + workIdNaam + "'")
                    else:
                        # Terugtrekking van de wijziging voor deze branch
                        if info is None:
                            self._LogFout (context, "geen informatie over instrument '" + workIdNaam + "' bekend voor branch '" + branch._Doel.Naam + "'; kan wijziging van instrument niet terugtrekken")
                            continue
                        if not info.IsGewijzigdInBranch ():
                            self._LogFout (context, "instrument '" + workIdNaam + "' is niet gewijzigd voor branch '" + branch._Doel.Naam + "'; kan wijziging van instrument niet terugtrekken")
                            continue
                        info.TrekWijzigingTerug (commit)
                        context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Branch '" + naam + "': trek wijziging voor instrument '" + workIdNaam + "' terug")
                else:
                    # Nieuwe ingevoerde versie van het instrument
                    if info is None:
                        branch.Instrumentversies[instrument.WorkId] = info = InstrumentInformatie (branch, instrument)
                    expressionId = instrument.MaakExpressionId (self.UitgevoerdOp, branch)
                    instrumentversie = info.WijzigInstrument (commit, expressionId)
                    context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Branch '" + naam + "': nieuwe versie voor instrument '" + workIdNaam + "': " + expressionId)

                if not instrumentversie is None and isinstance (versie, dict):
                    # TODO: Annotaties gespecificeerd?
                    pass

        # Kijk of er tijdstempels zijn opgegeven
        tijdstempelsGewijzigd = False
        if tijdstempelsToegestaan:
            if "JuridischWerkendVanaf" in specificatie:
                geldigVanaf = None
                juridischWerkendVanaf = self._LeesTijdstip (specificatie["JuridischWerkendVanaf"], True)
                if not juridischWerkendVanaf is None and "GeldigVanaf" in specificatie:
                    geldigVanaf = self._LeesTijdstip (specificatie["GeldigVanaf"], True)
                    if geldigVanaf == juridischWerkendVanaf:
                        geldigVanaf = None
                if commit is None:
                    commit = context.MaakCommit (branch)
                branch.WijzigTijdstempels (commit, juridischWerkendVanaf, geldigVanaf)
                tijdstempelsGewijzigd = True

                context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Branch '" + naam + "': nieuwe tijdstempels JuridischWerkendVanaf " + ("-" if juridischWerkendVanaf is None else juridischWerkendVanaf) + ", GeldigVanaf " + ("-" if geldigVanaf is None else geldigVanaf))

            elif "GeldigVanaf" in specificatie:
                self._LogFout (context, "branch '" + naam + "': GeldigVanaf mag alleen in combinatie met JuridischWerkendVanaf gespecificeerd worden")
        else:
            if "JuridischWerkendVanaf" in specificatie or "GeldigVanaf" in specificatie:
                self._LogFout (context, "Tijdstempels voor branch '" + naam + "' mogen voor deze activiteit niet gespecificeerd worden")

        if regelgevingGewijzigd or tijdstempelsGewijzigd:
            context.Activiteitverloop.MeldInteractie (InteractieMelding._Eindgebruiker, 'Wijzigt ' + ('regelgeving ' if regelgevingGewijzigd else '')+ ('en ' if regelgevingGewijzigd and tijdstempelsGewijzigd else '')+ ('geldigheidsinformatie ' if tijdstempelsGewijzigd else '') + 'voor ' + branch.InteractieNaam)
