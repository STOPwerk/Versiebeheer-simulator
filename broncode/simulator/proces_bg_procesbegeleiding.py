#======================================================================
#
# Simulatie van de procesbegeleiding, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# De acties die het bevoegd gezag kan uitvoeren zijn geformuleerd
# als stappen in het proces van opstellen, uitwisselen en 
# consolideren van regelgeving. Productie-waardige software
# zou een eindgebruiker aan de hand nemen en aangeven welke versies
# van de regelgeving gemaakt moeten worden. In deze simulator
# uit zich dat in de argumenten voor een actie, en de validatie
# of een actie passend is gezien de staat van de regelgeving.
#
# De Procesbegeleiding in deze module valideert of een actie 
# uitgevoerd kan worden, en bepaalt daarna het effect van de actie 
# op (de simulatie van) het interne versiebeheer van het bevoegd
# gezag.
#
#======================================================================

from typing import Dict, List, Tuple

from applicatie_meldingen import Meldingen
from data_bg_project import ProjectActie, ProjectActie_NieuwDoel, ProjectActie_Download, ProjectActie_Uitwisseling, ProjectActie_Wijziging, ProjectActie_Publicatie
from data_bg_projectvoortgang import Projectvoortgang, Branch, Projectstatus, ProjectactieResultaat, UitgewisseldeSTOPModule, UitgewisseldMaarNietViaSTOP
from data_bg_versiebeheer import InstrumentInformatie, Instrumentversie
from data_doel import Doel
from proces_bg_consolidatieinformatie import ConsolidatieInformatieMaker
from stop_momentopname import DownloadserviceModules, Momentopname, InstrumentversieInformatie
from stop_consolidatieinformatie import ConsolidatieInformatie

#======================================================================
#
# Basisklasse voor de uitvoering van acties
#
#======================================================================
class Procesbegeleiding:

#----------------------------------------------------------------------
#
# Uitvoering van de actie.
#
#----------------------------------------------------------------------
    @staticmethod
    def VoerUit (log: Meldingen, scenario, actie: ProjectActie) -> Tuple[bool, ConsolidatieInformatie, ProjectactieResultaat]:
        """Voer de projectactie uit.

        Argumenten:

        log Meldingen  Verzameling van meldingen over de uitvoering van het scenario
        scenario Scenario  Invoer en uitvoer van het scenario, bevat informatie over het versiebeheer zoals bevoegd gezag dat uitvoert.
        actie ProjectActie  De actie die in het project wordt uitgevoerd

        Geeft (isValide,ConsolidatieInformatie, ProjectactieResultaat) terug die volgt uit de actie.
        """

        # Maak de uitvoerder van de actie aan
        if not actie.SoortActie in Procesbegeleiding._Uitvoerders:
            log.Fout ("Geen code beschikbaar om actie uit te voeren: '" + actie.SoortActie + "'")
        else:
            uitvoerder = Procesbegeleiding._Uitvoerders[actie.SoortActie] ()
            uitvoerder._Log = log
            uitvoerder._Scenario = scenario
            uitvoerder._Projectvoortgang = scenario.Projectvoortgang
            uitvoerder._Projectstatus = uitvoerder._Projectvoortgang.Projecten.get (actie._Project.Code)
            if uitvoerder._Projectstatus is None:
                uitvoerder._Projectvoortgang.Projecten[actie._Project.Code] = uitvoerder._Projectstatus = Projectstatus (actie._Project)
            uitvoerder._Resultaat = ProjectactieResultaat (actie)

            # Voer de actie uit en geef de resulterende ConsolidatieInformatie terug
            if not uitvoerder.VoerUit (actie):
                return (False, None, None)
            uitvoerder._Projectvoortgang.Projectacties.append (uitvoerder._Resultaat)
            if len (uitvoerder._Resultaat.Uitgewisseld) > 0 and isinstance (uitvoerder._Resultaat.Uitgewisseld[0].Module, ConsolidatieInformatie):
                return (True, uitvoerder._Resultaat.Uitgewisseld[0].Module, uitvoerder._Resultaat)
            return (True, None, uitvoerder._Resultaat)

    # Constructors om de uitvoerders van de acties te maken op basis van de SoortActie
    _Uitvoerders = {
        ProjectActie._SoortActie_NieuwDoel: (lambda : _VoerUit_NieuwDoel()),
        ProjectActie._SoortActie_Download: (lambda : _VoerUit_Download()),
        ProjectActie._SoortActie_Uitwisseling: (lambda : _VoerUit_Uitwisseling()),
        ProjectActie._SoortActie_Wijziging: (lambda : _VoerUit_Wijziging()),
        #ProjectActie._SoortActie_BijwerkenUitgangssituatie: (lambda : _VoerUit_BijwerkenUitgangssituatie()),
        ProjectActie._SoortActie_Publicatie: (lambda : _VoerUit_Publicatie())
    }

#----------------------------------------------------------------------
#
# Implementatie van gemeenschappelijke functionaliteit
#
#----------------------------------------------------------------------
    def __init__ (self):
        """Maak een nieuwe uitvoerder aan"""
        # Verzameling van meldingen over de uitvoering van het scenario
        self._Log : Meldingen = None
        # Via het scenario is de geldende regelgeving uit de LVBB beschikbaar.
        self._Scenario = None
        # Informatie over het versiebeheer zoals bevoegd gezag dat uitvoert.
        self._Projectvoortgang : Projectvoortgang = None
        # De status van het project bij de start van de actie
        self._Projectstatus : Projectstatus = None
        # Het resultaat van de actie
        self._Resultaat : ProjectactieResultaat = None

    def _LogFout (self, melding):
        """Meld een fout bij de uitvoering van de actie. Hierbij wordt de projectcode en
        de actie voor de melding geplaatst.

        Argumenten:

        melding string Tekst van de foutmelding
        """
        self._Log.Fout ("Project '" + self._Projectstatus._Project.Code + "', actie '" + self._Resultaat._Projectactie.SoortActie + "' @" + self._Resultaat._Projectactie.UitgevoerdOp + ": " + melding)

    def _LogInfo (self, melding):
        """Geef een melding over de uitvoering van de actie. Hierbij wordt de projectcode en
        de actie voor de melding geplaatst.

        Argumenten:

        melding string Tekst van de melding
        """
        self._Log.Info ("Project '" + self._Projectstatus._Project.Code + "', actie '" + self._Resultaat._Projectactie.SoortActie + "' @" + self._Resultaat._Projectactie.UitgevoerdOp + ": " + melding)

    def _Branch (self, doel: Doel) -> Branch:
        """Geef de branch terug. De branch moet eerder gemaakt zijn in een project of uit een ConsolidatieInformatie module.
        Een bestaande branch wordt onderdeel gemaakt van het project als dat nog niet gebeurd is.

        Argumenten:

        doel Doel  Doel als identificatie van de branch
        """
        branch = self._Projectstatus.ExterneBranches.get (doel)
        if branch is None:
            branch = self._Projectstatus.Branches.get (doel)
            if branch is None:
                branch = self._Projectvoortgang.Versiebeheer.Branches.get (doel)
                if not branch is None:
                    if not branch._ViaProject:
                        self.LogFout ("branch '" + str(doel) + "' wordt niet via projecten beheerd en kan hier niet gebruikt worden,")
                    else:
                        self._Projectstatus.Branches[doel] = branch
        return branch

    def _VindInstrumentversie_Branch (self, workId : str, branch : Branch) -> Instrumentversie:
        """Vind de instrumentversie voor een instrument als die overgenomen moet worden van een branch

        Argumenten:

        workId string  Work-identificatie van het instrument
        branch Branch  Branch waarvan het instrument overgenomen moet worden

        Geef de instrumentversie terug, of None als er geen instrumentversie gevonden is of het instrument 
        juridisch uitgewerkt is.
        """
        instrumentinfo = branch.Instrumentversies.get (workId)
        if instrumentinfo is None:
            # Instrument onbekend
            self._LogFout ("instrument '" + workId + "' wordt niet beheerd op branch " + str(branch._Doel))
            return None
        if instrumentinfo.Instrumentversie is None:
            # Instrumentversie onbekend
            self._LogFout ("instrument '" + workId + "' heeft een onbekende instrumentversie voor branch " + str(branch._Doel))
            return None
        if instrumentinfo.Instrumentversie.IsJuridischUitgewerkt:
            # Juridisch uitgewerkt, dus geen versie
            self._LogFout ("instrument '" + workId + "' is juridisch uitgewerkt op branch " + str(branch._Doel))
            return None
        if instrumentinfo.IsGewijzigd:
            # Geef de instrumentversie instantie terug, die zal later de gegevens over de uitwisseling bevatten
            return instrumentinfo.Instrumentversie
        # Geef de uitgangssituatie terug, die bevat al de gegevens over de uitwisseling van de instrumentversie
        return instrumentinfo.Uitgangssituatie


    def _VindInstrumentversie_GeldigOp (self, workId: str, geldigOp : str) -> Instrumentversie:
        """Vind de geldige versie voor een instrument op basis van de publiek gemaakte informatie;
        de interne nog niet gepubliceerde gegevens worden niet meegenomen.

        Argumenten:

        workId string  Work-identificatie van het instrument
        geldigOp string  Datum waarop de regelgeving geldig moet zijn

        Geef een lijst met de geldende momentopnamen terug, of None als er geen versie gevonden is of als het 
        instrument juridisch uitgewerkt is.
        """
        geldigeMomentopnamen : List[Instrumentversie] = None
        juridischGeldigVanaf = None # Grootste jwv-datum die kleiner of gelijk aan geldigOp
        juridischUitgewerktVanaf = None # Grootste jwv-datum die kleiner of gelijk aan geldigOp waarop het instrument juridisch uitgewerkt is

        # Onderzoek alle bekende branches en momentopnamen
        for branch in self._Projectvoortgang.Versiebeheer.Branches.values ():
            if not branch.PubliekeTijdstempels.JuridischWerkendVanaf is None and branch.PubliekeTijdstempels.JuridischWerkendVanaf <= geldigOp:
                momentopname = branch.PubliekeInstrumentversies.get (workId)
                if not momentopname is None:
                    # Branch is in werking en weet iets over het instrument
                    if juridischUitgewerktVanaf is None or juridischUitgewerktVanaf < branch.PubliekeTijdstempels.JuridischWerkendVanaf:
                        # Instrument is al juridisch uitgewerkt
                        continue
                    if momentopname.IsJuridischUitgewerkt:
                        # Is er sprake van een nieuwe of eerdere uitwerkingtreding?
                        if juridischUitgewerktVanaf is None or juridischUitgewerktVanaf > branch.PubliekeTijdstempels.JuridischWerkendVanaf:
                            # Instrument is vanaf dit (eerdere) moment juridisch uitgewerkt
                            juridischUitgewerktVanaf = branch.PubliekeTijdstempels.JuridischWerkendVanaf
                            geldigeMomentopnamen = None

                    elif juridischUitgewerktVanaf is None: # Wijzigingen na uitwerkingtreding worden genegeerd
                        # Is er sprake van een nieuwe of latere inwerkingtreding?
                        if juridischGeldigVanaf is None or juridischGeldigVanaf < branch.PubliekeTijdstempels.JuridischWerkendVanaf:
                            # Nieuwe grootste jwv-datum
                            juridischGeldigVanaf = branch.PubliekeTijdstempels.JuridischWerkendVanaf
                            geldigeMomentopnamen = [MomentopnameVerwijzing(momentopname)]
                        elif juridischGeldigVanaf == branch.PubliekeTijdstempels.JuridischWerkendVanaf:
                            # Nog een doel voor de instrumentversie
                            geldigeMomentopnamen.append (MomentopnameVerwijzing(momentopname))

        return geldigeMomentopnamen


    def _NeemInstrumentversiesOver (self, branch : Branch, uitgangssituatie_doel : Doel, uitgangssituatie_geldigOp : str, nieuweInstrumentversies : Dict[str,Instrumentversie], registreerNieuweWorks : bool = True) -> bool:
        """Neem de nieuw gespecificeerde instrumentversies over in de branch

        Argumenten:

        branch Branch  Branch waarin de specificaties verwerkt moeten worden
        uitgangssituatie_doel Doel  Indien niet None: de instrumentversies geven de wijziging aan ten opzichte van de inhoud van de aangegeven branch.
                                    Als er nog geen instrumentversies door de branch beheerd worden, dan worden de instrumentversies van de branch overgenomen.
        uitgangssituatie_geldigOp str  Indien niet None: de instrumentversies geven de wijziging aan ten opzichte van de regelgeving die op het aangegeven tijdstip geldig is.
                                    Als er nog geen instrumentversies door de branch beheerd worden, dan worden de geldige instrumentversies overgenomen.
        nieuweInstrumentversies {}  Specificatie van de instrumentversies zoals ze na afloop van de actie moeten zijn
        registreerNieuweWorks bool  Geeft aan dat een nieuw work als bekend bij het BG geregistreerd moet worden.

        Geeft terug of het overnemen zonder fouten is gebeurd.
        """
        succes = True

        # Bepaal de collectie van instrumentversies die de uitgangssituatie vormen
        uitgangssituatie : Dict[str,Instrumentversie] = {}
        if not uitgangssituatie_doel is None:
            #
            # Uitgangssituatie: versies van een andere branch
            #
            if not uitgangssituatie_geldigOp is None:
                self._LogFout ("Dubbele uitgangssituatie opgegeven: doel '" + str(uitgangssituatie_doel) + "' en geldig op " + uitgangssituatie_geldigOp)
                return False
            if not branch.Uitgangssituatie_Doel is None and branch.Uitgangssituatie_Doel._Doel != uitgangssituatie_doel:
                self._LogFout ("De simulator staat niet toe dat als uitgangspunt een doel '" + str(uitgangssituatie_doel) + "' anders dan het eerder opgegeven doel '" + str(branch.Uitgangssituatie_Doel) + "' gekozen wordt")
                return False
            if not branch.Uitgangssituatie_GeldigOp is None:
                self._LogFout ("De simulator staat niet toe dat als uitgangspunt een doel '" + str(uitgangssituatie_doel) + "' gekozen wordt terwijl eerder voor de geldende regeling is gekozen")
                return False
            uitgangssituatie_branch = self._Projectvoortgang.Versiebeheer.Branches.get (uitgangssituatie_doel)
            if uitgangssituatie_branch is None:
                self._LogFout ("onbekend doel: '" + str(uitgangssituatie_doel) + "'")
                return False
            self._Resultaat.Data.append (('Uitgangssituatie is branch', [uitgangssituatie_doel]))
            branch.Uitgangssituatie_Doel = uitgangssituatie_branch
            branch.Uitgangssituatie_GeldigOp = None
            branch.Uitgangssituatie_LaatstGewijzigdOp = [(uitgangssituatie_branch, uitgangssituatie_branch.LaatstGewijzigdOp)]
            uitgangssituatie = uitgangssituatie_branch.Instrumentversies

        elif not uitgangssituatie_geldigOp is None:
            #
            # Uitgangssituatie: geldende regeling op een bepaald moment
            #
            if not branch.Uitgangssituatie_Doel is None:
                self._LogFout ("De simulator staat niet toe dat als uitgangspunt de op " + uitgangssituatie_geldigOp + " geldende regeling gekozen wordt terwijl eerder een doel '" + str(branch.Uitgangssituatie_Doel) + "' is gekozen")
                return False
            self._Resultaat.Data.append (('Uitgangssituatie regelgeving geldend op', [uitgangssituatie_geldigOp]))
            branch.Uitgangssituatie_Doel = uitgangssituatie_branch
            branch.Uitgangssituatie_GeldigOp = None
            branch.Uitgangssituatie_LaatstGewijzigdOp = [(uitgangssituatie_branch, uitgangssituatie_branch.LaatstGewijzigdOp)]


        # Overschrijf evt de uitgangssituatie met de nieuwe versies
        for workId, instrumentversie in nieuweInstrumentversies.items ():
            uitgangssituatie[workId] = instrumentversie

        # Werk de branch bij
        for workId, instrumentversie in uitgangssituatie.items ():
            instrumentinfo = branch.Instrumentversies.get (workId)
            if instrumentinfo is None:
                if instrumentversie.IsTeruggetrokken:
                    self._LogInfo ("Terugtrekking van instrument '" + workId + "' genegeerd; instrument wordt niet beheerd als onderdeel van de branch voor doel '" + str(branch._Doel) + "'")
                    continue
                # Dit mag alleen een initiële versie voor een nieuw instrument zijn (in deze simulator),
                # want de simulator kan niet vanaf dit punt de uitgangssituatie voor een bestaand instrument bepalen.
                # Dat is in principe wel mogelijk, maar te complex voor deze software.
                if workId in self._Projectvoortgang.BekendeInstrumenten:
                    self._LogFout ("Bestaand instrument '" + workId + "' wordt niet beheerd als onderdeel van de branch voor doel '" + str(branch._Doel) + "'")
                    succes = False
                    continue
                if instrumentversie.IsJuridischUitgewerkt:
                    self._LogInfo ("Nog niet bestaand instrument '" + workId + "' kan niet meteen al ingetrokken worden voor doel '" + str(branch._Doel) + "'")
                    succes = False
                    continue
                if instrumentversie.ExpressionId is None:
                    self._LogInfo ("Initiële versie van een nieuw instrument '" + workId + "' kan niet onbekend zijn; doel '" + str(branch._Doel) + "'")
                    succes = False
                    continue
                branch.InterneInstrumentversies[workId] = instrumentinfo = MomentopnameInstrument (branch, workId)
                instrumentinfo.ExpressionId = instrumentversie.ExpressionId
                if registreerNieuweWorks:
                    self._Projectvoortgang.BekendeInstrumenten.add (workId)
            else:
                if instrumentversie.IsJuridischUitgewerkt:
                    if not instrumentinfo.IsJuridischUitgewerkt:
                        instrumentinfo.ExpressionId = None
                        instrumentinfo.IsJuridischUitgewerkt = True
                        instrumentinfo.IsTeruggetrokken = False
                        instrumentinfo.Versie += 1
                elif instrumentversie.IsTeruggetrokken:
                    if not instrumentinfo.IsTeruggetrokken:
                        instrumentinfo.ExpressionId = None
                        instrumentinfo.IsJuridischUitgewerkt = False
                        instrumentinfo.IsTeruggetrokken = True
                        instrumentinfo.Versie += 1
                else:
                    if instrumentversie.ExpressionId != instrumentinfo.ExpressionId or instrumentinfo.IsJuridischUitgewerkt or instrumentinfo.IsTeruggetrokken: 
                        instrumentinfo.ExpressionId = instrumentversie.ExpressionId
                        instrumentinfo.IsJuridischUitgewerkt = False
                        instrumentinfo.IsTeruggetrokken = False
                        instrumentinfo.Versie += 1 

        return succes


#======================================================================
#
# Implementatie van de specifieke acties
#
#======================================================================

#----------------------------------------------------------------------
#
# Projectactie: nieuw doel
#
#----------------------------------------------------------------------
#
# Deze actie wordt uitgevoerd door het bevoegd gezag om in een project 
# aan een (nieuwe) branch te gaan werken.
#
#----------------------------------------------------------------------
class _VoerUit_NieuwDoel (Procesbegeleiding):

    def __init__ (self):
        super ().__init__ ()

    def VoerUit (self, actie: ProjectActie_NieuwDoel):
        """Start een nieuwe branch door het bevoegd gezag
        """
        self._Resultaat.UitgevoerdDoor = ProjectactieResultaat._Uitvoerder_BevoegdGezag
        succes = True

        # Maak een nieuwe branch
        if actie.Doel in self._Projectvoortgang.Versiebeheer.Branches:
            self._LogFout ("branch bestaat al voor doel: '" + str(actie.Doel) + "'")
            return False
        self._Projectvoortgang.Versiebeheer.Branches[actie.Doel] = branch = Branch (actie.Doel)
        self._Projectstatus.Branches[actie.Doel] = branch
        branch._ViaProject = True
        branch.Uitvoerder = ProjectactieResultaat._Uitvoerder_BevoegdGezag
        self._Resultaat.Data.append (('Doel', [actie.Doel]))

        for workId in actie.Instrumenten:
            # Maak de instrumentversies aan met een vooralsnog onbekende versie
            branch.Instrumentversies[workId] = InstrumentInformatie (branch)


        if not actie.GebaseerdOp_Doel is None:
            # Het project is een expliciete aftakking van het opgegeven doel.
            basisBranch = self._Projectvoortgang.Versiebeheer.Branches.get (actie.GebaseerdOp_Doel)
            if basisBranch is None:
                self._LogFout ("onbekend doel: '" + str(actie.GebaseerdOp_Doel) + "'")
                return False
            branch.Uitgangssituatie_Doel = basisBranch
            self._Resultaat.Data.append (('Branch van', [actie.GebaseerdOp_Doel]))
            for workId in actie.Instrumenten:
                # Maak de instrumentinformatie voor dit instrument
                instrumentinfo = branch.Instrumentversies[workId]
                instrumentinfo.Uitgangssituatie = self._VindInstrumentversie_Branch (basisBranch)
                if instrumentinfo.Uitgangssituatie is None:
                    succes = False

        elif not actie.GebaseerdOp_GeldigOp is None:
            # Ga uit van de geldende regelgeving volgens de interne administratie
            branch.Uitgangssituatie_GeldigOp = actie.actie.GebaseerdOp_GeldigOp
            self._Resultaat.Data.append (('Uitgangssituatie d.d.', [actie.actie.GebaseerdOp_GeldigOp]))
            for workId in actie.Instrumenten:
                instrumentinfo = branch.Instrumentversies[workId]
                instrumentinfo.Uitgangssituatie = self._VindInstrumentversie_GeldigOp (workId, actie.GebaseerdOp_GeldigOp)
                if instrumentinfo.Uitgangssituatie is None:
                    succes = False

        for workId in actie.Instrumenten:
            # Maak de actuele instrumentversies aan
            instrumentinfo = branch.Instrumentversies[workId]
            if not instrumentinfo.Uitgangssituatie is None:
                instrumentinfo.Instrumentversie = Instrumentversie ()
                instrumentinfo.Instrumentversie.ExpressionId = instrumentinfo.Uitgangssituatie.ExpressionId
                instrumentinfo.Instrumentversie.UitgewisseldVoor = [branch._Doel]

        return succes

#----------------------------------------------------------------------
#
# Projectactie: download
#
#----------------------------------------------------------------------
#
# Deze actie wordt uitgevoerd door een adviesbureau. Een adviesbureau
# voert zelf geen versiebeheer maar werkt aan een enkele (nieuwe)
# versie.
#
#----------------------------------------------------------------------
class _VoerUit_Download (Procesbegeleiding):

    def __init__ (self):
        super ().__init__ ()

    def VoerUit (self, actie: ProjectActie_Download):
        """Start een nieuwe branch bij/door een adviesbureau op basis van de gedownloade regelgeving
        """
        self._Resultaat.UitgevoerdDoor = ProjectactieResultaat._Uitvoerder_Adviesbureau
        succes = True

        # Maak een nieuwe branch
        if actie.Doel in self._Projectvoortgang.Versiebeheer.Branches:
            self._LogFout ("branch bestaat al voor doel: '" + str(actie.Doel) + "'")
            return False
        branch = self._Projectstatus.ExterneBranches.get (actie.Doel)
        self._Projectstatus.ExterneBranches[actie.Doel] = branch = Branch (actie.Doel)
        branch.Uitvoerder = ProjectactieResultaat._Uitvoerder_Adviesbureau
        self._Resultaat.Data.append (('Doel', [actie.Doel]))

        # Gebruik als STOP-module de momentopnames die de downloadservice meelevert
        module = DownloadserviceModules ()
        self._Resultaat.Uitgewisseld.append (UitgewisseldeSTOPModule (module, ProjectactieResultaat._Uitvoerder_LVBB, branch.Uitvoerder))

        # Zoek de geldende versie op van elk van de instrumenten
        branch.Uitgangssituatie_GeldigOp = actie.actie.GebaseerdOp_GeldigOp
        self._Resultaat.Data.append (('Branch van', ['Geldig op ' + actie.GebaseerdOp_GeldigOp]))
        for workId in actie.Instrumenten:
            branch.Instrumentversies[workId] = instrumentinfo = InstrumentInformatie (branch)

            geconsolideerd = self._Scenario.GeconsolideerdeInstrument (workId)
            if geconsolideerd is None or geconsolideerd.ActueleToestanden is None:
                self._LogFout ("onbekend instrument: '" + workId + "'")
                succes = False
                continue
            geldigeToestand = None
            for toestand in geconsolideerd.ActueleToestanden.Toestanden:
                if not toestand.NietMeerActueel and toestand.JuridischWerkendVanaf <= actie.GebaseerdOp_GeldigOp and (toestand.JuridischWerkendTot is None or actie.GebaseerdOp_GeldigOp < toestand.JuridischWerkendTot):
                    geldigeToestand = toestand
                    break
            if geldigeToestand is None:
                self._LogFout ("instrument: '" + workId + "' geen actuele toestand bekend die geldig is op " + actie.GebaseerdOp_GeldigOp)
                succes = False
                continue
            if geldigeToestand.Instrumentversie is None:
                self._LogFout ("instrument: '" + workId + "' geen instrumentversie bekend voor de actuele toestand die geldig is op " + actie.GebaseerdOp_GeldigOp)
                succes = False
                continue

            # Geldende toestand gevonden!

            # Maak de momentopname die de downloadservice meelevert
            stop_mo = Momentopname ()
            stop_mo.Doel = geldigeToestand.Inwerkingtredingsdoelen[0] # Downloadservice kiest er 1
            # GemaaktOp is niet beschikbaar via actuele toestanden, maar de downloadservice geeft dit wel mee
            # In deze simulator: haal het tijdstip uit het versiebeheer van BG
            stop_mo.GemaaktOp = self._Projectvoortgang.Versiebeheer.Branches[stop_mo.Doel].Instrumentversies[workId].UitgewisseldeVersie.UitgewisseldOp
            module.Modules[geldigeToestand.Instrumentversie] = stop_mo

            # Maak de instrumentinformatie
            instrumentinfo.Uitgangssituatie = Instrumentversie ()
            instrumentinfo.Uitgangssituatie.ExpressionId = geldigeToestand.Instrumentversie
            instrumentinfo.Uitgangssituatie.UitgewisseldOp = stop_mo.GemaaktOp
            instrumentinfo.Uitgangssituatie.UitgewisseldVoor = [stop_mo.Doel]
            instrumentinfo.Instrumentversie = Instrumentversie ()
            instrumentinfo.Instrumentversie.ExpressionId = geldigeToestand.Instrumentversie
            instrumentinfo.Instrumentversie.UitgewisseldVoor = [actie.Doel]

        return succes

#----------------------------------------------------------------------
#
# Projectactie: uitwisseling
#
#----------------------------------------------------------------------
#
# Deze actie wordt uitgevoerd door ofwel het adviesbureau om de 
# aangepaste versie aan het bevoegd gezag te leveren, ofwel door
# het bevoegd gezag om de startversie aan een adviesbureau te geven.
#
#----------------------------------------------------------------------
class _VoerUit_Uitwisseling (Procesbegeleiding):

    def __init__ (self):
        super ().__init__ ()

    def VoerUit (self, actie: ProjectActie_Uitwisseling):
        """Wissel de instrumentversies in een branch uit
        """
        succes = True

        branch = self._Branch (actie.Doel)
        if branch is None:
            self._LogFout ("onbekend doel '" + str(actie.Doel) + "'")
            return False
        self._Resultaat.Data.append (('Doel', [actie.Doel]))

        self._Resultaat.UitgevoerdDoor = branch.Uitvoerder
        if branch.Uitvoerder == ProjectactieResultaat._Uitvoerder_Adviesbureau:
            #----------------------------------------------------------
            # Van adviesbureau naar bevoegd gezag
            #----------------------------------------------------------
            del self._Projectstatus.ExterneBranches[actie.Doel]
            bgBranch = self._Projectstatus.Branches.get (actie.Doel)
            if bgBranch is None:
                # Door adviesbureau gedownload, neem branch over
                self._Projectstatus.Branches[actie.Doel] = branch
                branch.Uitvoerder = ProjectactieResultaat._Uitvoerder_BevoegdGezag
            else:
                # Eerder door BG uitgeleverd, neem instrumentversies over
                for workId, instrumentinfo in branch.Instrumentversies.items ():
                    bgVersie = bgBranch.Instrumentversies.get (workId)
                    if bgVersie is None:
                        if not instrumentinfo.IsGewijzigd:
                            continue
                        if workId in self._Projectvoortgang.BekendeInstrumenten:
                            self._LogFout ("Bestaand instrument '" + workId + "' is niet door BG aan het adviesbureau doorgegeven")
                            succes = False
                            continue
                        bgBranch.Instrumentversies[workId] = bgVersie = InstrumentInformatie (bgBranch)
                        self._Projectvoortgang.BekendeInstrumenten.add (workId)
                    bgVersie.Instrumentversie = instrumentinfo.Instrumentversie
                    bgVersie.IsGewijzigd = Instrumentversie.ZijnGelijk (bgVersie.Instrumentversie, bgVersie.Uitgangssituatie)

            # Stel de momentopname voor de uitwisseling op
            stop_mo = Momentopname ()
            self._Resultaat.Uitgewisseld.append (UitgewisseldeSTOPModule (stop_mo, ProjectactieResultaat._Uitvoerder_Adviesbureau, ProjectactieResultaat._Uitvoerder_BevoegdGezag))
            stop_mo.Doel = actie.Doel
            stop_mo.GemaaktOp = actie.UitgevoerdOp
            if bgBranch is None:
                # Voeg de uitgangssituatie alleen toe als gestart wordt met een download
                for workId, instrumentinfo in branch.Instrumentversies.items ():
                    if not instrumentinfo.Instrumentversie is None and not instrumentinfo.Instrumentversie.IsJuridischUitgewerkt:
                        # Uitgangssituatie als gedownload, BranchBasisversie als geleverd door BG
                        instrumentversieinfo = InstrumentversieInformatie ()
                        instrumentversieinfo.Basisversie_Doel = instrumentinfo.Uitgangssituatie.UitgewisseldVoor[0]
                        instrumentversieinfo.Basisversie_GemaaktOp = instrumentinfo.Uitgangssituatie.UitgewisseldOp
                        instrumentversieinfo.WorkId = workId
                        instrumentversieinfo._ExpressionId = instrumentinfo.Instrumentversie.ExpressionId
                        stop_mo.Instrumentversies.append (instrumentversieinfo)

        else:
            #----------------------------------------------------------
            # Van bevoegd gezag naar adviesbureau
            #----------------------------------------------------------
            # Maak een aparte branch voor het adviesbureau aan
            self._Projectstatus.ExterneBranches[actie.Doel] = abBranch = Branch (actie.Doel) 
            abBranch.UitgevoerdDoor = ProjectactieResultaat._Uitvoerder_Adviesbureau
            for workId, instrumentinfo in branch.Instrumentversies.items ():
                # Neem de instrumentversies over
                if not instrumentinfo.Instrumentversie.IsJuridischUitgewerkt:
                    abBranch.Instrumentversies[workId] = instrumentinfo = InstrumentInformatie (abBranch)
                    instrumentinfo.Uitgangssituatie = Instrumentversie ()
                    instrumentinfo.Uitgangssituatie.ExpressionId = instrumentinfo.Instrumentversie.ExpressionId
                    instrumentinfo.Uitgangssituatie.UitgewisseldOp = actie.UitgevoerdOp
                    instrumentinfo.Uitgangssituatie.UitgewisseldVoor = [actie.Doel]
                    instrumentinfo.Instrumentversie = Instrumentversie ()
                    instrumentinfo.Instrumentversie.ExpressionId = instrumentinfo.Instrumentversie.ExpressionId
                    instrumentinfo.Instrumentversie.UitgewisseldVoor = [actie.Doel]

            # Stel de momentopname voor de uitwisseling op
            stop_mo = Momentopname ()
            self._Resultaat.Uitgewisseld.append (UitgewisseldeSTOPModule (stop_mo, ProjectactieResultaat._Uitvoerder_BevoegdGezag, ProjectactieResultaat._Uitvoerder_Adviesbureau))
            stop_mo.Doel = actie.Doel
            stop_mo.GemaaktOp = actie.UitgevoerdOp

        return succes

#----------------------------------------------------------------------
#
# Projectactie: wijziging
#
#----------------------------------------------------------------------
#
# Deze actie wordt uitgevoerd door ofwel het adviesbureau ofwel het
# bevoegd gezag. De instrumentversies op de branch worden aangepast.
#
#----------------------------------------------------------------------
class _VoerUit_Wijziging (Procesbegeleiding):

    def __init__ (self):
        super ().__init__ ()

    def VoerUit (self, actie: ProjectActie_Wijziging):
        """Wissel de instrumentversies in een branch uit
        """
        succes = True
        branch = self._Branch (actie.Doel)
        if branch is None:
            self._LogFout ("onbekend doel '" + str(actie.Doel) + "'")
            return False
        self._Resultaat.Data.append (('Doel', [actie.Doel]))

        self._Resultaat.UitgevoerdDoor = branch.Uitvoerder
        if branch.Uitvoerder == ProjectactieResultaat._Uitvoerder_Adviesbureau:
            if not self._NeemInstrumentversiesOver (branch, actie.Instrumentversies, False):
                succes = False
            if not actie.JuridischWerkendVanaf is None or not actie.GeldigVanaf is None:
                self._LogFout ("adviesbureau mag geen tijdstempels specificeren")
        else:
            if not self._NeemInstrumentversiesOver (branch, actie.Instrumentversies):
                succes = False
            if not actie.JuridischWerkendVanaf is None:
                if actie.JuridischWerkendVanaf == '-':
                    if not branch.Tijdstempels.JuridischWerkendVanaf is None:
                        branch.Tijdstempels.JuridischWerkendVanaf = None
                        # GeldigVanaf kan niet bestaan zonder JuridischWerkendVanaf
                        branch.Tijdstempels.GeldigVanaf = None
                elif actie.JuridischWerkendVanaf != branch.Tijdstempels.JuridischWerkendVanaf:
                    branch.Tijdstempels.JuridischWerkendVanaf = actie.JuridischWerkendVanaf
            if not branch.Tijdstempels.JuridischWerkendVanaf is None and not actie.GeldigVanaf is None:
                if actie.GeldigVanaf == '-':
                    if not branch.Tijdstempels.GeldigVanaf is None:
                        branch.Tijdstempels.GeldigVanaf = None
                elif actie.GeldigVanaf != branch.Tijdstempels.GeldigVanaf:
                    branch.Tijdstempels.GeldigVanaf = actie.GeldigVanaf

        return succes

#----------------------------------------------------------------------
#
# Projectactie: Publicatie
#
#----------------------------------------------------------------------
#
# Deze actie wordt uitgevoerd door het bevoegd gezag. 
# Er wordt een publicatie gemaakt voor de gewijzigde instrumenten voor
# één of meer doelen binnen het project.
#
#----------------------------------------------------------------------
class _VoerUit_Publicatie (Procesbegeleiding):

    def __init__ (self):
        super ().__init__ ()

    def VoerUit (self, actie: ProjectActie_Publicatie):
        """Neem wijzigingen uit een andere branch over
        """
        if not actie.SoortPublicatie in ProjectActie_Publicatie._SoortPublicatie_ViaSTOPVersiebeheer:
            self._Resultaat.Uitgewisseld.append (UitgewisseldMaarNietViaSTOP ())
            return True
        isConceptOfOntwerp = not actie.SoortPublicatie in ProjectActie_Publicatie._SoortPublicatie_GeenConceptOfOntwerp

        succes = True
        consolidatieInformatie = ConsolidatieInformatie (self._Log, '(gemaakt voor projectactie)')
        self._Resultaat.Uitgewisseld.append (UitgewisseldeSTOPModule (consolidatieInformatie, ProjectactieResultaat._Uitvoerder_BevoegdGezag, ProjectactieResultaat._Uitvoerder_LVBB))
        consolidatieInformatie.GemaaktOp = actie.UitgevoerdOp
        consolidatieInformatie.OntvangenOp = consolidatieInformatie._BekendOp = actie.UitgevoerdOp[0:10]

        # Lijst met alle elementen (en extra info) in de module
        elementen : List[_VoerUit_Publicatie._ElementMetRelaties] = []

        doelen = sorted (actie.Doelen, key = lambda d: str(d))
        self._Resultaat.Data.append (('Doel', doelen))
        for doel in doelen:
            branch = self._Branch (doel)
            if branch is None:
                self._LogFout ("onbekend doel '" + str(doel) + "'")
                succes = False
                continue
            if branch.Uitvoerder != ProjectactieResultaat._Uitvoerder_BevoegdGezag:
                self._LogFout ("instrumentversies voor doel '" + str(doel) + "' zijn nog onderhanden bij een adviesbureau; dit scenario wordt niet ondersteund door deze simulator")
                succes = False
                continue

            for workId in sorted (branch.InterneInstrumentversies.keys ()):
                momentopname = branch.InterneInstrumentversies[workId]
                gepubliceerd = branch.PubliekeInstrumentversies.get (workId)

                # Bepaal de basisversie(s) voor een eventueel element in de consolidatie-informatie
                basisversies = None
                if not gepubliceerd is None:
                    if gepubliceerd.Versie == momentopname.Versie:
                        # De informatie is niet gewijzigd sinds de laatste publicatie
                        # De informatie hoeft niet opgenomen te worden in deze publicatie/revisie
                        continue
                    # Basisversie is vorige publicatie/revisie
                    basisversies = [gepubliceerd]
                else:
                    # Eerste publicatie, kies momentopname van laatstgebruikte uitgangssituatie
                    # Die is None voor een initiële versie van een regeling/informatieobject
                    if not momentopname.Uitgangssituatie is None:
                        # Een van de basisversies is genoeg
                        basisversies = [momentopname.Uitgangssituatie[0].Momentopname]

                # Bepaal de vermelding in de consolidatie-informatie
                if momentopname.IsTeruggetrokken:
                    #--------------------------------------------------
                    # Eerder gepubliceerde wijziging is teruggetrokken
                    #--------------------------------------------------
                    if gepubliceerd.IsJuridischUitgewerkt:
                        element = _VoerUit_Publicatie._ElementMetRelaties (TerugtrekkingIntrekking (consolidatieInformatie, [branch._Doel], workId), basisversies)
                        consolidatieInformatie.TerugtrekkingenIntrekking.append (element.Element)
                    else:
                        element = _VoerUit_Publicatie._ElementMetRelaties (Terugtrekking (consolidatieInformatie, [branch._Doel], workId), basisversies)
                        consolidatieInformatie.Terugtrekkingen.append (element.Element)

                elif momentopname.IsJuridischUitgewerkt:
                    #--------------------------------------------------
                    # Intrekking is nog niet gepubliceerd
                    #--------------------------------------------------
                    element = _VoerUit_Publicatie._ElementMetRelaties (Intrekking (consolidatieInformatie, [branch._Doel], workId), basisversies)
                    consolidatieInformatie.Intrekkingen.append (element.Element)

                else:
                    #--------------------------------------------------
                    # Beoogde versie is nog niet gepubliceerd
                    #--------------------------------------------------
                    if branch.TreedtGelijktijdigInWerkingMet is None:
                        doelen = [branch._Doel]
                    else:
                        # Versie voor meerdere doelen, nl alle doelen waarvoor dit work beheerd wordt
                        doelen = []
                        nieuweBasisversies = []
                        for andereBranch in branch.TreedtGelijktijdigInWerkingMet:
                            # Alleen eerder gepubliceerde doelen/versies kunnen als basisversie worden gebruikt
                            andereMO = branch.PubliekeInstrumentversies.get (workId)
                            if not andereMO is None:
                                doelen.append (andereBranch._Doel)
                                nieuweBasisversies.append (andereMO.BasisVoorWijziging)
                        if len (doelen) > 1:
                            # De versie is inderdaad van toepassing voor meerdere doelen
                            basisversies = nieuweBasisversies
                    
                    element = _VoerUit_Publicatie._ElementMetRelaties (BeoogdeVersie (consolidatieInformatie, doelen, workId, momentopname.ExpressionId), basisversies)
                    consolidatieInformatie.BeoogdeVersies.append (element.Element)

                    # TODO: vervlechtingen e.d.

                # Markeer als gepubliceerd
                momentopname.IsGepubliceerd (actie.UitgevoerdOp, isConceptOfOntwerp)

                # Stel het leggen van relaties uit, want er kan naar andere elementen in deze consolidatie-informatie verwezen worden
                # waarvan de gemaaktOp nog niet gezet is.
                if not element is None:
                    elementen.append (element)

        # Nu zouden de relaties gelegd moeten kunnen worden
        for element in elementen:
            element.VoegRelatiesToe ()
        
        # Voeg tijdstempels toe
        for doel in doelen:
            branch = self._Branch (doel)
            if branch.InterneTijdstempels.Versie != branch.PubliekeTijdstempels.Versie:
                # Tijdstempels zijn gewijzigd
                if not branch.InterneTijdstempels.JuridischWerkendVanaf is None:
                    if branch.InterneTijdstempels.JuridischWerkendVanaf != branch.PubliekeTijdstempels.JuridischWerkendVanaf:
                        #--------------------------------------------------
                        # Tijdstempel heeft een (nieuwe) waarde
                        #--------------------------------------------------
                        element = Tijdstempel (consolidatieInformatie)
                        element.Doel = doel
                        element.Datum = branch.InterneTijdstempels.JuridischWerkendVanaf
                        element.IsGeldigVanaf = False
                        consolidatieInformatie.Tijdstempels.append (element)

                    if not branch.InterneTijdstempels.GeldigVanaf is None and branch.InterneTijdstempels.GeldigVanaf != branch.PubliekeTijdstempels.GeldigVanaf:
                        #--------------------------------------------------
                        # Tijdstempel heeft een (nieuwe) waarde
                        #--------------------------------------------------
                        element = Tijdstempel (consolidatieInformatie)
                        element.Doel = doel
                        element.Datum = branch.InterneTijdstempels.GeldigVanaf
                        element.IsGeldigVanaf = True
                        consolidatieInformatie.Tijdstempels.append (element)

                elif not branch.PubliekeTijdstempels.JuridischWerkendVanaf is None:
                    #--------------------------------------------------
                    # Tijdstempel is teruggetrokken
                    #--------------------------------------------------
                    element = TerugtrekkingTijdstempel (consolidatieInformatie)
                    element.Doel = doel
                    element.IsGeldigVanaf = False
                    consolidatieInformatie.TijdstempelTerugtrekkingen.append ()

                if branch.InterneTijdstempels.GeldigVanaf is None and not branch.PubliekeTijdstempels.GeldigVanaf is None:
                    #--------------------------------------------------
                    # Tijdstempel is teruggetrokken
                    #--------------------------------------------------
                    element = TerugtrekkingTijdstempel (consolidatieInformatie)
                    element.Doel = doel
                    element.IsGeldigVanaf = True
                    consolidatieInformatie.TijdstempelTerugtrekkingen.append (element)

                # Markeer als gepubliceerd
                branch.InterneTijdstempels.IsGepubliceerd ()

        return succes
 
    class _ElementMetRelaties:
        def __init__ (self, element, basisversies):
            """Maak een nieuw in-memory bakje met de te leggen relaties
            """
            self.Element = element
            self.Basisversies = basisversies
            self.VervlochtenMet = []
            self.OntvlochtenMet = []

        def VoegRelatiesToe (self):
            # Voeg de relaties toe aan de consolidatie-informatie
            if not self.Basisversies is None:
                for momentopname in self.Basisversies:
                    self.Element.Basisversies[momentopname._Branch._Doel] = CI_Momentopname (momentopname._Branch._Doel, momentopname.GemaaktOp)






