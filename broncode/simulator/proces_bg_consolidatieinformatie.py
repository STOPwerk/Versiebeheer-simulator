#======================================================================
#
# Verwerken van consolidatie-informatie in het versiebeheer van het
# bevoegd gezag.
#
#======================================================================
#
# Als met de simulator het versiebeheer bij bevoegd gezag wordt
# meegenomen, dan is de standaard manier om de acties van het 
# bevoegd gezag te specificeren via projecten en projectacties.
#
# De simulator kan, voor branches die niet via een project beheerd
# worden, ook overweg met specificaties van consolidatie-informatie
# modules. Deze worden onder de "overige projecten" geschaard. Het
# is daarmee mogelijk met de projecten in een simulator-scenario
# alleen de relevante acties van een bevoegd gezag te modelleren. 
#
# De ConsolidatieInformatieMaker accepteert een consolidatie-informatie
# module en gebruikt die om de versiebeheeradministratie van BG
# bij te werken, zodat de projecten en projectacties daar ook gebruik 
# van kunnen maken.
#
#======================================================================

from typing import Tuple

from applicatie_meldingen import Meldingen
from data_bg_project import ProjectActie
from data_bg_projectvoortgang import Projectvoortgang, ProjectactieResultaat, UitgewisseldeSTOPModule, Branch
from data_bg_versiebeheer import MomentopnameInstrument
from stop_consolidatieinformatie import ConsolidatieInformatie

class ConsolidatieInformatieMaker:
#----------------------------------------------------------------------
#
# Verwerken van de consolidatie informatie die niet vanuit een actie
# van een project is opgesteld, maar direct als invoer voor het
# scenario is opgegeven. Werkt het versiebeheer bij zoals bevoegd
# gezag dat bijhoudt.
#
#----------------------------------------------------------------------
    @staticmethod
    def WerkBij (log: Meldingen, voortgang: Projectvoortgang, consolidatieInformatie: ConsolidatieInformatie, actie: ProjectActie) -> Tuple[bool, ProjectactieResultaat]:
        """Werk de BG-versiebeheerinformatie bij aan de hand van consolidatie-informatie.

        Argumenten:

        log Meldingen  Verzameling van meldingen over de uitvoering van het scenario
        voortgang Projectvoortgang  Informatie over de projectvoortgang en het versiebeheer zoals bevoegd gezag dat uitvoert.
        consolidatieInformatie ConsolidatieInformatie  De consolidatie-informatie voor een uitwisseling 
                                                       die als invoer voor het scenario is opgegeven
        actie ProjectActie  De actie die correspondeert met de consolidatie-informatie

        Geeft aan of de verwerking goed is verlopen en het resultaat van de actie
        """
        resultaat = ProjectactieResultaat (actie)
        resultaat.Uitgewisseld.append (UitgewisseldeSTOPModule (consolidatieInformatie, ProjectactieResultaat._Uitvoerder_BevoegdGezag, ProjectactieResultaat._Uitvoerder_LVBB))
        voortgang.Projectacties.append (resultaat)

        maker = ConsolidatieInformatieMaker (log, voortgang, consolidatieInformatie)
        return (maker._WerkVersiebeheerBij (), resultaat)

#======================================================================
#
# Implementatie
#
#======================================================================
    def __init__(self, log: Meldingen, voortgang: Projectvoortgang, consolidatieInformatie : ConsolidatieInformatie):
        """Maak een nieuwe instantie aan.

        Argumenten:

        log Meldingen  Verzameling van meldingen over de uitvoering van het scenario
        voortgang Projectvoortgang  Informatie over de projectvoortgang en het versiebeheer zoals bevoegd gezag dat uitvoert.
        consolidatieInformatie ConsolidatieInformatie  De consolidatie-informatie voor een uitwisseling
        """
        self._Log = log
        self._Voortgang = voortgang
        self._ConsolidatieInformatie = consolidatieInformatie

#======================================================================
#
# _WerkVersiebeheerBij: bijwerken van versiebeheer aan de hand van 
# consolidatie-informatie die als invoer voor het scenario is opgegeven
#
#======================================================================
    def _WerkVersiebeheerBij (self):
        """Werk het versiebeheer bij aan de hand van de uitgewisselde consolidatie-informatie.
        Geeft terug of de simulatie door kan gaan.
        """
        isValide = True
        # Begin met de BeoogdeRegelingen
        for beoogdeVersie in self._ConsolidatieInformatie.BeoogdeVersies:
            for doel in beoogdeVersie.Doelen:
                branch = self._Voortgang.Versiebeheer.Branches.get (doel)
                if branch is None:
                    self._Voortgang.Versiebeheer.Branches[doel] = branch = Branch (doel)
                elif branch._ViaProject:
                    self._Log.Fout ("Doel '" + str(doel) + "' wordt via projecten beheerd; daarvoor kan geen ConsolidatieInformatie gespecificeerd worden. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                    isValide = False
                    continue

                momentopname = branch.PubliekeInstrumentversies.get (beoogdeVersie.WorkId)
                if momentopname is None:
                    # Eerste vermelding van dit instrument
                    branch.PubliekeInstrumentversies[beoogdeVersie.WorkId] = momentopname = MomentopnameInstrument (doel, beoogdeVersie.WorkId)
                momentopname.GemaaktOp = self._ConsolidatieInformatie.GemaaktOp
                momentopname.ExpressionId = beoogdeVersie.ExpressionId
                momentopname.IsJuridischUitgewerkt = False
                momentopname.IsTeruggetrokken = False

                self._Voortgang.BekendeInstrumenten.add (beoogdeVersie.WorkId)
                if not beoogdeVersie.ExpressionId is None:
                    self._Voortgang.Versiebeheer.PubliekeInstrumentversies.add (beoogdeVersie.ExpressionId)

        # Intrekkingen
        for intrekking in self._ConsolidatieInformatie.Intrekkingen:
            for doel in intrekking.Doelen:
                branch = self._Voortgang.Versiebeheer.Branches.get (doel)
                if branch is None:
                    self._Voortgang.Versiebeheer.Branches[doel] = branch = Branch (doel)
                elif branch._ViaProject:
                    self._Log.Fout ("Doel '" + str(doel) + "' wordt via projecten beheerd; daarvoor kan geen ConsolidatieInformatie gespecificeerd worden. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                    isValide = False
                    continue

                momentopname = branch.PubliekeInstrumentversies.get (intrekking.WorkId)
                if momentopname is None:
                    # Eerste vermelding van dit instrument
                    branch.PubliekeInstrumentversies[intrekking.WorkId] = momentopname = MomentopnameInstrument (doel, intrekking.WorkId)
                momentopname.GemaaktOp = self._ConsolidatieInformatie.GemaaktOp
                momentopname.ExpressionId = None
                momentopname.IsJuridischUitgewerkt = True
                momentopname.IsTeruggetrokken = False

        # Terugtrekking van iets van een instrument. Hier valideren we niet of het de juiste soort terugtrekking is, dat wordt gedaan
        # (in deze applicatie) bij het verwerken in de versiebeheerinformatie voor het ontvangende systeem
        for terugtrekking in [*self._ConsolidatieInformatie.Terugtrekkingen, *self._ConsolidatieInformatie.TerugtrekkingenIntrekking]:
            for doel in terugtrekking.Doelen:
                branch = self._Voortgang.Versiebeheer.Branches.get (doel)
                if branch is None:
                    self._Log.Fout ("Terugtrekking voor doel '" + str(doel) + "' voordat er een terugtrekking of beoogde instrumentversie is uitgewisseld. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                    isValide = False
                    continue
                elif branch._ViaProject:
                    self._Log.Fout ("Doel '" + str(doel) + "' wordt via projecten beheerd; daarvoor kan geen ConsolidatieInformatie gespecificeerd worden. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                    isValide = False
                    continue

                momentopname = branch.PubliekeInstrumentversies.get (terugtrekking.WorkId)
                if momentopname is None:
                    self._Log.Fout ("Terugtrekking voor instrument '" + terugtrekking.WorkId + "' en doel '" + str(doel) + "' voordat er een terugtrekking of beoogde instrumentversie is uitgewisseld. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                    isValide = False
                    continue
                momentopname.GemaaktOp = self._ConsolidatieInformatie.GemaaktOp
                momentopname.ExpressionId = None
                momentopname.IsJuridischUitgewerkt = False
                momentopname.IsTeruggetrokken = True

        # Tijdstempels
        for tijdstempel in self._ConsolidatieInformatie.Tijdstempels:
            branch = self._Voortgang.Versiebeheer.Branches.get (tijdstempel.Doel)
            if branch is None:
                self._Log.Fout ("Tijdstempel voor doel '" + str(tijdstempel.Doel) + "' voordat er een terugtrekking of beoogde instrumentversie is uitgewisseld. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                isValide = False
                continue
            elif branch._ViaProject:
                self._Log.Fout ("Doel '" + str(doel) + "' wordt via projecten beheerd; daarvoor kan geen ConsolidatieInformatie gespecificeerd worden. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                isValide = False
                continue
            if tijdstempel.IsGeldigVanaf:
                branch.PubliekeTijdstempels.GeldigVanaf = tijdstempel.Datum
            else:
                branch.PubliekeTijdstempels.JuridischWerkendVanaf = tijdstempel.Datum

        for tijdstempel in self._ConsolidatieInformatie.TijdstempelTerugtrekkingen:
            branch = self._Voortgang.Versiebeheer.Branches.get (tijdstempel.Doel)
            if branch is None:
                self._Log.Fout ("Terugtrekking tijdstempel voor doel '" + str(tijdstempel.Doel) + "' voordat er een terugtrekking of beoogde instrumentversie is uitgewisseld. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                isValide = False
                continue
            elif branch._ViaProject:
                self._Log.Fout ("Doel '" + str(doel) + "' wordt via projecten beheerd; daarvoor kan geen ConsolidatieInformatie gespecificeerd worden. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                isValide = False
                continue
            if tijdstempel.IsGeldigVanaf:
                branch.PubliekeTijdstempels.GeldigVanaf = None
            else:
                branch.PubliekeTijdstempels.JuridischWerkendVanaf = None
                branch.PubliekeTijdstempels.GeldigVanaf = None

        return isValide
