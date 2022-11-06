#======================================================================
#
# Verwerken van consolidatie-informatie in het versiebeheer van het
# bevoegd gezag, en het afleiden van consolidatie-informatie uit
# het interne versiebeheer.
#
#======================================================================
#
# Als met de simulator het versiebeheer bij bevoegd gezag wordt
# meegenomen, dan is de standaard manier om de acties van het 
# bevoegd gezag te specificeren via projecten en projectacties.
# Voor de uitwisseling van informatie met de LVBB wordt de
# consolidatie-informatie afgeleid uit het interne versiebeheer
# zoals de software van het bevoegd gezag dat bijhoudt. Dat is
# war de ConsolidatieInformatieMaker doet.
#
# De simulator kan, voor branches die niet via een project beheerd
# worden, ook overweg met specificaties van consolidatie-informatie
# modules. Deze worden onder de "overige projecten" geschaard. Het
# is daarmee mogelijk met de projecten in een simulator-scenario
# alleen de relevante acties van een bevoegd gezag te modelleren. 
#
# De ConsolidatieInformatieVerwerker accepteert een consolidatie-informatie
# module en gebruikt die om de versiebeheeradministratie van BG
# bij te werken, zodat de projecten en projectacties daar ook gebruik 
# van kunnen maken.
#
#======================================================================

from typing import Dict, List, Tuple

from applicatie_meldingen import Meldingen
from data_bg_project import ProjectActie
from data_bg_projectvoortgang import Projectvoortgang, ProjectactieResultaat, UitgewisseldeSTOPModule, Branch
from data_bg_versiebeheer import InstrumentInformatie, Instrumentversie
from data_doel import Doel
from stop_consolidatieinformatie import ConsolidatieInformatie, VoorInstrument, BeoogdeVersie, Intrekking, Terugtrekking, TerugtrekkingIntrekking, Tijdstempel, TerugtrekkingTijdstempel, Momentopname as CI_Momentopname

#======================================================================
#
# ConsolidatieInformatieMaker
#
#======================================================================
#
# Leidt de consolidatie-informatie af uit het interne versiebeheer van
# het bevoegd gezag. Dit is onderdeel van een actie in de 
# procesbegeleiding die tot uitwisseling met de LVBB overgaat.
#
#======================================================================
class ConsolidatieInformatieMaker:

    @staticmethod
    def VoerUit (logFout, actieResultaat: ProjectactieResultaat, branches: List[Branch]) -> ConsolidatieInformatie:
        """Leidt de consolidatie-informatie af uit de staat van het interne versiebeheer
        
        Argumenten:
        
        logFout lambda(str)  Methode om een foutmelding te doen
        actieResultaat ProjectactieResultaat  Het resultaat van de actie waarvoor de consolidatie-informatie wordt opgesteld
        branches [Branch]  De branches waarvoor de consolidatie-informatie samengesteld moet worden
        """
        maker = ConsolidatieInformatieMaker (actieResultaat, branches)
        maker._VoerUit ()

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
    def __init__(self, logFout, actieResultaat: ProjectactieResultaat, branches: List[Branch]):
        """Maak een instantie van de maker
        
        Argumenten:
        
        logFout lambda(str)  Methode om een foutmelding te doen
        actieResultaat ProjectactieResultaat  Het resultaat van de actie waarvoor de consolidatie-informatie wordt opgesteld
        branches [Branch]  De branches waarvoor de consolidatie-informatie samengesteld moet worden
        """
        self._LogFout = logFout
        self._IsValide = True
        self._Resultaat = actieResultaat
        self._Branches = list (sorted (branches, key = lambda x: str (x._Doel))) # Sortering ivm weergave op de resultaatpagina
        self._ConsolidatieInformatie = ConsolidatieInformatie (None, "(afgeleid uit intern versiebeheer)")
        self._ConsolidatieInformatie.GemaaktOp = actieResultaat._Projectactie.UitgevoerdOp
        self._ConsolidatieInformatie.OntvangenOp = self._ConsolidatieInformatie._BekendOp = actieResultaat._Projectactie.UitgevoerdOp[0:10]

    def _VoerUit (self):
        """Stel de consolidatie-informatie samen"""

        # Zoek uit welke instrumentversies uitgewisseld moeten worden
        # key = doel + work
        uitTeWisselenInstrumentversies : Dict[str,Tuple[Branch,str,InstrumentInformatie,List[Instrumentversie]]] = {}
        for branch in self._Branches:
            for workId, instrumentinfo in branch.Instrumentversies.items ():
                if instrumentinfo.Instrumentversie is None:
                    # Nog geen versie gespecificeerd
                    continue
                if not instrumentinfo.IsGewijzigd and instrumentinfo.UitgewisseldeVersie is None:
                    # Niet gewijzigd en niet eerder uitgewisseld: hoeft nu ook niet uitgewisseld te worden
                    continue

                if not Instrumentversie.ZijnGelijk (instrumentinfo.Instrumentversie, instrumentinfo.UitgewisseldeVersie):
                    # Instrumentversie is gewijzigd en wijkt af van evt eerdere uitwisseling: nu uitwiesselen

                    # Verplaats de Instrumentversie naar UitgewisseldeVersie
                    eerderUitgewisseld = instrumentinfo.UitgewisseldeVersie
                    if not eerderUitgewisseld is None:
                        eerderUitgewisseld.UitgewisseldVoor = [branch._Doel] # Alleen dit doel is interessant
                    nuUitgewisseld = instrumentinfo.Instrumentversie
                    instrumentinfo.Instrumentversie = nuUitgewisseld.copy ()
                    instrumentinfo.UitgewisseldeVersie = nuUitgewisseld

                    # Zet gemaaktOp/doelen/was-versie voor de uitwisseling
                    instrumentinfo.UitgewisseldeWasVersie
                    nuUitgewisseld.UitgewisseldOp = self._ConsolidatieInformatie.OntvangenOp
                    if nuUitgewisseld.IsJuridischUitgewerkt:
                        # Intrekking of terugtrekking
                        nuUitgewisseld.UitgewisseldVoor = [branch._Doel]
                    else:
                        # beoogde versie, bij 1 doel ook terugtrekking mogelijk
                        nuUitgewisseld.UitgewisseldVoor = [branch._Doel] if branch.TredenTegelijkInWerking is None else branch.TredenTegelijkInWerking
                    
                    # Straks verder gaan als alle gemaaktOp/doelen voor deze uitwisseling zijn toegekend
                    doelWork = str(nuUitgewisseld.UitgewisseldVoor[0]) + '\n' + workId
                    uiv = uitTeWisselenInstrumentversies.get (doelWork)
                    if uiv is None:
                        # Alleen toevoegen als (bij meerdere doelen) dit nog niet toegevoegd is
                        uitTeWisselenInstrumentversies[doelWork] = (branch, workId, instrumentinfo, [] if eerderUitgewisseld is None else [eerderUitgewisseld])
                    elif not eerderUitgewisseld is None:
                        # Alleen eerdere uitwisseling toevoegen
                        uiv[3].append (eerderUitgewisseld)

        # Neem de uit te wisselen instrumenten op in de consolidatie-informatie
        for doelWork in sorted (uitTeWisselenInstrumentversies): # Sortering ivm weergave op de resultaatpagina
            branch, workId, instrumentinfo, eerderUitgewisseld = uitTeWisselenInstrumentversies[doelWork]
            nuUitgewisseld = instrumentinfo.UitgewisseldeVersie

            element : VoorInstrument = None

            if not instrumentinfo.IsGewijzigd and len (nuUitgewisseld.UitgewisseldVoor) == 1:
                # Terugtrekking
                if eerderUitgewisseld[0].IsJuridischUitgewerkt:
                    element = TerugtrekkingIntrekking (self._ConsolidatieInformatie, nuUitgewisseld.UitgewisseldVoor, workId)
                    self._ConsolidatieInformatie.TerugtrekkingenIntrekking.append (element)
                else:
                    element = Terugtrekking (self._ConsolidatieInformatie, nuUitgewisseld.UitgewisseldVoor, workId)
                    self._ConsolidatieInformatie.Terugtrekkingen.append (element)
            elif nuUitgewisseld.IsJuridischUitgewerkt:
                # Intrekking
                element = Intrekking (self._ConsolidatieInformatie, nuUitgewisseld.UitgewisseldVoor, workId)
                self._ConsolidatieInformatie.Intrekkingen.append (element)
            else:
                # Beoogde versie
                element = BeoogdeVersie (self._ConsolidatieInformatie, nuUitgewisseld.UitgewisseldVoor, workId, nuUitgewisseld.ExpressionId)

                # TODO: vervlechting/ontvlechting

            # Maak de basisversie
            if len (eerderUitgewisseld) == 0:
                # Blijkbaar de eerste uitwisseling voor deze branch+instrumentversie
                # Neem de uitgangssituatie als basisversie
                if not instrumentinfo.Uitgangssituatie is None:
                    if instrumentinfo.Uitgangssituatie.UitgewisseldeVersie is None:
                        self._LogFout ("ConsolidatieInformatie voor doel '" + str(branch._Doel) + "', work '" + workId + "': uitgangssituatie is niet eerder uitgewisseld")
                        self._IsValide = False
                    else:
                        eerderUitgewisseld.append (instrumentinfo.Uitgangssituatie.UitgewisseldeVersie)
            for basisUitwisseling in eerderUitgewisseld:
                if basisUitwisseling.UitgewisseldVoor is None:
                    self._LogFout ("ConsolidatieInformatie voor doel '" + str(branch._Doel) + "', work '" + workId + "': basisversie is niet eerder uitgewisseld")
                    self._IsValide = False
                    continue
                for doel in basisUitwisseling.UitgewisseldVoor:
                    element.Basisversies[doel] = basisUitwisseling.UitgewisseldOp

            if not branch.BekendOp is None:
                # BekendOp is alleen relevant voor bijv uitspraak rechter.
                # In de procesbegeleiding van deze simulator wordt dan voor elke betrokken branch de BekendOp gezet.
                # Hier erop vertrouwen dat dat ook altijd het geval is, dus de BekendOp van deze branch is hetzelfde
                # als de BekendOp voor alle UitgewisseldVoor doelen.
                element._BekendOp = branch.BekendOp

        # Tijdstempels
        for branch in self._Branches:
            if not branch.Tijdstempels.IsGelijkAan (branch.UitgewisseldeTijdstempels):
                # Tijdstempels zijn gewijzigd

                def __VoegTijdstempelToe (nieuw, oud, isGeldigVanaf):
                    if nieuw != oud:
                        if not nieuw is None:
                            # Geef nieuwe waarde door
                            tijdstempel = Tijdstempel (self._ConsolidatieInformatie)
                            tijdstempel.IsGeldigVanaf = isGeldigVanaf
                            tijdstempel.Doel = branch._Doel
                            tijdstempel.Datum = nieuw
                            self._ConsolidatieInformatie.Tijdstempels.append (tijdstempel)
                        else:
                            # Trek eerdere waarde terug
                            tijdstempel = TerugtrekkingTijdstempel (self._ConsolidatieInformatie)
                            tijdstempel.IsGeldigVanaf = isGeldigVanaf
                            tijdstempel.Doel = branch._Doel
                            self._ConsolidatieInformatie.TijdstempelTerugtrekkingen.append (tijdstempel)
                        if not branch.BekendOp is None:
                            tijdstempel._BekendOp = branch.BekendOp

                __VoegTijdstempelToe (branch.Tijdstempels.JuridischWerkendVanaf, branch.UitgewisseldeTijdstempels.JuridischWerkendVanaf, False)
                __VoegTijdstempelToe (branch.Tijdstempels.GeldigVanaf, branch.UitgewisseldeTijdstempels.GeldigVanaf, True)


#======================================================================
#
# ConsolidatieInformatieVerwerker
#
#======================================================================
#
# Werk het interne versiebeheer bij met de informatie uit een
# consolidatie-informatie module die voor een van de "overige projecten"
# is opgesteld. Voor deze projecten wordt geen procesbegeleiding
# gedaan, maar worden de consolidatie-informatie modules als invoer 
# voor het scenario gespecificeerd.
#
#======================================================================
class ConsolidatieInformatieVerwerker:
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

        maker = ConsolidatieInformatieVerwerker (log, voortgang, consolidatieInformatie)
        return (maker._WerkVersiebeheerBij (), resultaat)

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
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

#----------------------------------------------------------------------
#
# _WerkVersiebeheerBij: bijwerken van versiebeheer aan de hand van 
# consolidatie-informatie die als invoer voor het scenario is opgegeven
#
#----------------------------------------------------------------------
    def _WerkVersiebeheerBij (self):
        """Werk het versiebeheer bij aan de hand van de uitgewisselde consolidatie-informatie.
        Geeft terug of de simulatie door kan gaan.
        """
        isValide = True

        def __Branch (doel: Doel, moetBestaan : bool) -> Branch:
            """Geef de branch die hoort bij het doel"""
            branch = self._Voortgang.Versiebeheer.Branches.get (doel)
            if branch is None:
                if moetBestaan:
                    self._Log.Fout ("Tijdstempel voor doel '" + str(doel) + "' voordat er een terugtrekking of beoogde instrumentversie is uitgewisseld. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                else:
                    self._Voortgang.Versiebeheer.Branches[doel] = branch = Branch (doel)
                    branch.Tijdstempels = branch.UitgewisseldeTijdstempels # Hou de tijdstempels in sync
            elif branch._ViaProject:
                self._Log.Fout ("Doel '" + str(doel) + "' wordt via projecten beheerd; daarvoor kan geen ConsolidatieInformatie gespecificeerd worden. Bestand: '" + self._ConsolidatieInformatie.Pad + "'")
                return
            return branch

        def __WerkInstrumentInformatieBij (doel: Doel, voorInstrument: VoorInstrument, expressionId: str, isJuridischUitgewerkt: bool) -> InstrumentInformatie:
            """Werk de InstrumentInformatie bij en geef die terug"""
            branch = __Branch (doel, False)
            if branch is None:
                return

            instrumentversie = Instrumentversie ()
            instrumentversie.ExpressionId = expressionId
            instrumentversie.IsJuridischUitgewerkt = isJuridischUitgewerkt
            instrumentversie.UitgewisseldOp = self._ConsolidatieInformatie.GemaaktOp
            instrumentversie.UitgewisseldVoor = voorInstrument.Doelen

            instrumentInfo = branch.Instrumentversies.get (voorInstrument.WorkId)
            if instrumentInfo is None:
                # Eerste vermelding van dit instrument
                branch.Instrumentversies[voorInstrument.WorkId] = instrumentInfo = InstrumentInformatie (branch)
            instrumentInfo.Instrumentversie = instrumentversie
            instrumentInfo.UitgewisseldeVersie = instrumentversie
            instrumentInfo.IsGewijzigd = True
            return instrumentInfo


        # Begin met de BeoogdeRegelingen
        for beoogdeVersie in self._ConsolidatieInformatie.BeoogdeVersies:
            for doel in beoogdeVersie.Doelen:
                instrumentInfo = __WerkInstrumentInformatieBij (doel, beoogdeVersie.ExpressionId, False)
                if instrumentInfo is None:
                    isValide = False
                self._Voortgang.BekendeInstrumenten.add (beoogdeVersie.WorkId)
                if not beoogdeVersie.ExpressionId is None:
                    self._Voortgang.Versiebeheer.PubliekeInstrumentversies.add (beoogdeVersie.ExpressionId)

        # Intrekkingen
        for intrekking in self._ConsolidatieInformatie.Intrekkingen:
            for doel in intrekking.Doelen:
                instrumentInfo = __WerkInstrumentInformatieBij (doel, None, True)
                if instrumentInfo is None:
                    isValide = False

        # Terugtrekking van iets van een instrument. Hier valideren we niet of het de juiste soort terugtrekking is, dat wordt gedaan
        # (in deze applicatie) bij het verwerken in de versiebeheerinformatie voor het ontvangende systeem
        for terugtrekking in [*self._ConsolidatieInformatie.Terugtrekkingen, *self._ConsolidatieInformatie.TerugtrekkingenIntrekking]:
            for doel in terugtrekking.Doelen:
                instrumentInfo = __WerkInstrumentInformatieBij (doel, None, False)
                if instrumentInfo is None:
                    isValide = False
                else:
                    instrumentInfo.IsGewijzigd = False
                    instrumentInfo.Instrumentversie = None

        # Tijdstempels
        for tijdstempel in self._ConsolidatieInformatie.Tijdstempels:
            branch = __Branch (tijdstempel.Doel, True)
            if branch is None:
                isValide = False
            else:
                if tijdstempel.IsGeldigVanaf:
                    branch.UitgewisseldeTijdstempels.GeldigVanaf = tijdstempel.Datum
                else:
                    branch.UitgewisseldeTijdstempels.JuridischWerkendVanaf = tijdstempel.Datum

        for tijdstempel in self._ConsolidatieInformatie.TijdstempelTerugtrekkingen:
            branch = __Branch (tijdstempel.Doel, True)
            if branch is None:
                isValide = False
            else:
                if tijdstempel.IsGeldigVanaf:
                    branch.UitgewisseldeTijdstempels.GeldigVanaf = None
                else:
                    branch.UitgewisseldeTijdstempels.JuridischWerkendVanaf = None
                    branch.UitgewisseldeTijdstempels.GeldigVanaf = None

        return isValide
