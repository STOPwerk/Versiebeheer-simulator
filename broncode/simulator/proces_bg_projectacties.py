#======================================================================
#
# Uitvoeren van een actie in een project: bepaling van het effect
# op het versiebeheer en van de uit te wisselen informatie.
#
#======================================================================
#
# Aan de hand van de projectactie wordt bepaald hoe de informatie
# over het versiebeheer wijzigt zoals dat door de software van het
# bevoegd gezag wordt bijgehouden. Tevens wordt bepaald welke
# informatie met ontvangende systemen (zoals de LVBB) uitgewisseld
# moet worden. Het opstellen van de consolidatie-informatie daarvoor
# wordt overgelaten aan ConsolidatieInformatieMaker.
#
#======================================================================

from typing import Dict, List, Tuple

from applicatie_meldingen import Meldingen
from data_bg_versiebeheer import Versiebeheer, Projectstatus, ProjectactieResultaat, Branch, MomentopnameInstrument, MomentopnameVerwijzing, UitgewisseldeSTOPModule
from data_bg_project import ProjectActie, ProjectActie_NieuwDoel, ProjectActie_Download, ProjectActie_Uitwisseling, ProjectActie_Wijziging, ProjectActie_VerwerkingUitspraakRechter, ProjectActie_Publicatie, Instrumentversie
from data_doel import Doel
from stop_consolidatieinformatie import ConsolidatieInformatie, VoorInstrument, BeoogdeVersie, Intrekking, Terugtrekking, TerugtrekkingIntrekking, Tijdstempel, TerugtrekkingTijdstempel, Momentopname as CI_Momentopname
from stop_momentopname import DownloadserviceModules, Momentopname, InstrumentversieInformatie

#======================================================================
#
# Basisklasse voor de uitvoering van acties
#
#======================================================================
class ProjectactieUitvoering:

#----------------------------------------------------------------------
#
# Uitvoering van de actie.
#
#----------------------------------------------------------------------
    @staticmethod
    def Voor (log: Meldingen, scenario, actie: ProjectActie) -> Tuple[bool, ConsolidatieInformatie, ProjectactieResultaat]:
        """Voer de projectactie uit.

        Argumenten:

        log Meldingen  Verzameling van meldingen over de uitvoering van het scenario
        versiebeheer Versiebeheer  Informatie over het versiebeheer zoals bevoegd gezag dat uitvoert.
        actie ProjectActie  De actie die in het project wordt uitgevoerd

        Geeft (isValide,ConsolidatieInformatie, ProjectactieResultaat) terug die volgt uit de actie.
        """

        # Maak de uitvoerder van de actie aan
        if not actie.SoortActie in ProjectactieUitvoering._Uitvoerders:
            log.Fout ("Geen code beschikbaar om actie uit te voeren: '" + actie.SoortActie + "'")
        else:
            uitvoerder = ProjectactieUitvoering._Uitvoerders[actie.SoortActie] ()
            uitvoerder._Log = log
            uitvoerder._Scenario = scenario
            uitvoerder._Versiebeheer = scenario.Versiebeheer
            uitvoerder._Projectstatus = uitvoerder._Versiebeheer.Projecten.get (actie._Project.Code)
            if uitvoerder._Projectstatus is None:
                uitvoerder._Versiebeheer.Projecten[actie._Project.Code] = uitvoerder._Projectstatus = Projectstatus (actie._Project)
            uitvoerder._Resultaat = ProjectactieResultaat (actie)

            # Voer de actie uit en geef de resulterende ConsolidatieInformatie terug
            if not uitvoerder.VoerUit (actie):
                return (False, None, None)
            uitvoerder._Versiebeheer.Projectacties.append (uitvoerder._Resultaat)
            if len (uitvoerder._Resultaat.Uitgewisseld) > 0 and isinstance (uitvoerder._Resultaat.Uitgewisseld[0], ConsolidatieInformatie):
                return (True, uitvoerder._Resultaat.Uitgewisseld[0], uitvoerder._Resultaat)
            return (True, None, uitvoerder._Resultaat)

    # Constructors om de uitvoerders van de acties te maken op basis van de SoortActie
    _Uitvoerders = {
        ProjectActie._SoortActie_NieuwDoel: (lambda : _VoerUit_NieuwDoel()),
        ProjectActie._SoortActie_Download: (lambda : _VoerUit_Download()),
        ProjectActie._SoortActie_Uitwisseling: (lambda : _VoerUit_Uitwisseling()),
        ProjectActie._SoortActie_Wijziging: (lambda : _VoerUit_Wijziging()),
        #ProjectActie._SoortActie_BijwerkenUitgangssituatie: (lambda : _VoerUit_BijwerkenUitgangssituatie()),
        #ProjectActie._SoortActie_VerwerkingUitspraakRechter: (lambda : _VoerUit_VerwerkingUitspraakRechter()),
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
        self._Versiebeheer : Versiebeheer = None
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
                branch = self._Versiebeheer.Branches.get (doel)
                if not branch is None:
                    if not branch._ViaProject:
                        self.LogFout ("branch '" + str(doel) + "' wordt niet via projecten beheerd en kan hier niet gebruikt worden,")
                    else:
                        self._Projectstatus.Branches[doel] = branch
        return branch

    def _VindMomentopnameVoorBranch (self, workId : str, branch : Branch) -> List[MomentopnameVerwijzing]:
        """Vind de momentopname voor een instrument als die overgenomen moet worden van een branch

        Argumenten:

        workId string  Work-identificatie van het instrument
        branch Branch  Branch waarvan het instrument overgenomen moet worden

        Geef een lijst met de  terug, of None als er geen momentopname gevonden is of het instrument 
        juridisch uitgewerkt is.
        """
        momentopname = branch.InterneInstrumentversies.get (workId)
        if momentopname is None:
            momentopname = branch.PubliekeInstrumentversies.get (workId)
            if momentopname is None:
                # Instrument onbekend
                return None
        if momentopname.IsJuridischUitgewerkt:
            # Juridisch uitgewerkt, dus geen versie
            return None
        if not momentopname.IsTeruggetrokken:
            # Niet teruggetrokken, dus dit is de momentopname
            return [MomentopnameVerwijzing (momentopname)]
        # Dan moet het de uitgangssituatie zijn
        return self.Uitgangssituatie


    def _VindMomentopnameGeldigOp (self, workId: str, geldigOp : str) -> List[MomentopnameVerwijzing]:
        """Vind de geldige versie voor een instrument op basis van de publiek gemaakte informatie;
        de interne nog niet gepubliceerde gegevens worden niet meegenomen.

        Argumenten:

        workId string  Work-identificatie van het instrument
        geldigOp string  Datum waarop de regelgeving geldig moet zijn

        Geef een lijst met de geldende momentopnamen terug, of None als er geen versie gevonden is of als het 
        instrument juridisch uitgewerkt is.
        """
        geldigeMomentopnamen : List[MomentopnameVerwijzing] = None
        juridischGeldigVanaf = None # Grootste jwv-datum die kleiner of gelijk aan geldigOp
        juridischUitgewerktVanaf = None # Grootste jwv-datum die kleiner of gelijk aan geldigOp waarop het instrument juridisch uitgewerkt is

        # Onderzoek alle bekende branches en momentopnamen
        for branch in self._Versiebeheer.Branches.values ():
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

    def _ValideerInstrumentversieVoorUitgangssituatie (self, momentopname: MomentopnameInstrument) -> bool:
        """Valideer dat de uitgangssituatie voor de momentopname daadwerkelijk een instrumentversie oplevert.

        Argumenten:

        momentopname Momentopname  Momentopname waarvoor de instrumentversie bepaald moet worden

        Geeft terug of het overnemen zonder fouten is gebeurd.
        """
        if momentopname.Uitgangssituatie is None:
            self._LogFout ("instrument '" + momentopname._WorkId + "' is niet (meer) beschikbaar in de uitgangssituatie")
            return False

        if momentopname.Uitgangssituatie[0].ExpressionId is None:
            self._LogFout ("instrument '" + momentopname._WorkId + "' heeft onbekende versie in de uitgangssituatie")
            return False

        if len (momentopname.Uitgangssituatie) > 1:
            if len (set (v.Momentopname.ExpressionId for v in momentopname.Uitgangssituatie)) > 1:
                # Geen eenduidige versie
                self._LogFout ("instrument '" + momentopname._WorkId + "' heeft meerdere kandidaat-versies in de uitgangssituatie")
                return False
        # De instrumentversie is: momentopname.Uitgangssituatie[0].Momentopname.ExpressionId
        return True


    def _NeemInstrumentversiesOver (self, branch : Branch, instrumentversies : Dict[str,Instrumentversie], registreerNieuweWorks : bool = True) -> bool:
        """Neem de nieuw gespecificeerde instrumentversies over in de branch

        Argumenten:

        branch Branch  Branch waarin de specificaties verwerkt moeten worden
        instrumentversies {}  Specificatie van de instrumentversies als onderdeel van de actie
        registreerNieuweWorks bool  Geeft aan dat een nieuw work als bekend bij het BG geregistreerd moet worden.

        Geeft terug of het overnemen zonder fouten is gebeurd.
        """
        succes = True
        for workId, instrumentversie in instrumentversies.items ():
            momentopname = branch.InterneInstrumentversies.get (workId)
            if momentopname is None:
                if instrumentversie.IsTeruggetrokken:
                    self._LogInfo ("Terugtrekking van instrument '" + workId + "' genegeerd; instrument wordt niet beheerd als onderdeel van de branch voor doel '" + str(branch._Doel) + "'")
                    continue
                # Dit mag alleen een initiële versie voor een nieuw instrument zijn (in deze simulator),
                # want de simulator kan niet vanaf dit punt de uitgangssituatie voor het instrument bepalen.
                # Dat is in principe wel mogelijk, maar te complex voor deze software.
                if workId in self._Versiebeheer.BekendeInstrumenten:
                    self._LogFout ("Bestaand instrument '" + workId + "' wordt niet beheerd als onderdeel van de branch voor doel '" + str(branch._Doel) + "'")
                    succes = False
                    continue
                if instrumentversie.IsJuridischUitgewerkt:
                    self._LogInfo ("Onbekend instrument '" + workId + "' kan niet ingetrokken worden voor doel '" + str(branch._Doel) + "'")
                    succes = False
                    continue
                if instrumentversie.ExpressionId is None:
                    self._LogInfo ("Initiële versie van een nieuw instrument '" + workId + "' kan niet onbekend zijn; doel '" + str(branch._Doel) + "'")
                    succes = False
                    continue
                branch.InterneInstrumentversies[workId] = momentopname = MomentopnameInstrument (branch, workId)
                momentopname.ExpressionId = instrumentversie.ExpressionId
                if registreerNieuweWorks:
                    self._Versiebeheer.BekendeInstrumenten.add (workId)
            else:
                if instrumentversie.IsJuridischUitgewerkt:
                    if not momentopname.IsJuridischUitgewerkt:
                        momentopname.ExpressionId = None
                        momentopname.IsJuridischUitgewerkt = True
                        momentopname.IsTeruggetrokken = False
                        momentopname.Versie += 1
                elif instrumentversie.IsTeruggetrokken:
                    if not momentopname.IsTeruggetrokken:
                        momentopname.ExpressionId = None
                        momentopname.IsJuridischUitgewerkt = False
                        momentopname.IsTeruggetrokken = True
                        momentopname.Versie += 1
                else:
                    if instrumentversie.ExpressionId != momentopname.ExpressionId or momentopname.IsJuridischUitgewerkt or momentopname.IsTeruggetrokken: 
                        momentopname.ExpressionId = instrumentversie.ExpressionId
                        momentopname.IsJuridischUitgewerkt = False
                        momentopname.IsTeruggetrokken = False
                        momentopname.Versie += 1 

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
class _VoerUit_NieuwDoel (ProjectactieUitvoering):

    def __init__ (self):
        super ().__init__ ()

    def VoerUit (self, actie: ProjectActie_NieuwDoel):
        """Start een nieuwe branch door het bevoegd gezag
        """
        self._Resultaat.UitgevoerdDoor = ProjectactieResultaat._Uitvoerder_BevoegdGezag
        succes = True

        # Maak een nieuwe branch
        if actie.Doel in self._Versiebeheer.Branches:
            self._LogFout ("branch bestaat al voor doel: '" + str(actie.Doel) + "'")
            return False
        self._Versiebeheer.Branches[actie.Doel] = branch = Branch (actie.Doel)
        self._Projectstatus.Branches[actie.Doel] = branch
        branch._ViaProject = True
        branch.Uitvoerder = ProjectactieResultaat._Uitvoerder_BevoegdGezag

        if not actie.GebaseerdOp_Doel is None:
            # Het project is een expliciete aftakking van het opgegeven doel.
            basisBranch = self._Versiebeheer.Branches.get (actie.GebaseerdOp_Doel)
            if basisBranch is None:
                self._LogFout ("onbekend doel: '" + str(actie.GebaseerdOp_Doel) + "'")
                return False
            branch.Uitgangssituatie_Doel = basisBranch
            for workId in actie.Instrumenten:
                # Maak de momentopname voor dit instrument
                momentopname = MomentopnameInstrument (branch, workId)
                momentopname.Uitgangssituatie = self._VindMomentopnameVoorBranch (basisBranch)
                if not self._ValideerInstrumentversieVoorUitgangssituatie (momentopname):
                    succes = False
                branch.InterneInstrumentversies[workId] = momentopname

        elif not actie.GebaseerdOp_GeldigOp is None:
            # Ga uit van de geldende regelgeving volgens de interne administratie
            for workId in actie.Instrumenten:
                momentopname = MomentopnameInstrument (branch, workId)
                momentopname.Uitgangssituatie = self._VindMomentopnameGeldigOp (workId, actie.GebaseerdOp_GeldigOp)
                if not self._ValideerInstrumentversieVoorUitgangssituatie (momentopname):
                    succes = False
                branch.InterneInstrumentversies[workId] = momentopname

        else: # Moet een initiële versie zijn
            for workId in actie.Instrumenten:
                # Maak de instrumentversies aan met een onbekende versie
                branch.InterneInstrumentversies[workId] = MomentopnameInstrument (branch, workId)

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
class _VoerUit_Download (ProjectactieUitvoering):

    def __init__ (self):
        super ().__init__ ()

    def VoerUit (self, actie: ProjectActie_Download):
        """Start een nieuwe branch bij/door een adviesbureau op basis van de gedownloade regelgeving
        """
        self._Resultaat.UitgevoerdDoor = ProjectactieResultaat._Uitvoerder_Adviesbureau
        succes = True

        # Maak een nieuwe branch
        if actie.Doel in self._Versiebeheer.Branches:
            self._LogFout ("branch bestaat al voor doel: '" + str(actie.Doel) + "'")
            return False
        branch = self._Projectstatus.ExterneBranches.get (actie.Doel)
        self._Projectstatus.ExterneBranches[actie.Doel] = branch = Branch (actie.Doel)
        branch.Uitvoerder = ProjectactieResultaat._Uitvoerder_Adviesbureau

        # Gebruik als STOP-module de momentopnames die de downloadservice meelevert
        module = DownloadserviceModules ()
        self._Resultaat.Uitgewisseld.append (UitgewisseldeSTOPModule (module, ProjectactieResultaat._Uitvoerder_LVBB, branch.Uitvoerder))

        # Zoek de geldende versie op van elk van de instrumenten
        for workId in actie.Instrumenten:
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
            stop_mo.GemaaktOp = self._Versiebeheer.Branches[stop_mo.Doel].PubliekeInstrumentversies[workId].GemaaktOp
            module.Modules[geldigeToestand.Instrumentversie] = stop_mo

            # Maak de momentopname van de uitgangssituatie zoals de downloadservice dat levert
            download_momentopname = MomentopnameInstrument (Branch (stop_mo.Doel), workId)
            download_momentopname.ExpressionId = geldigeToestand.Instrumentversie
            download_momentopname.IsTeruggetrokken = False
            download_momentopname.GemaaktOp = stop_mo.GemaaktOp

            # Maak de momentopname voor de branch
            momentopname = MomentopnameInstrument (branch, workId)
            momentopname.Uitgangssituatie = [ MomentopnameVerwijzing (download_momentopname) ]
            branch.InterneInstrumentversies[workId] = momentopname


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
class _VoerUit_Uitwisseling (ProjectactieUitvoering):

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
                for workId, instrumentversie in branch.InterneInstrumentversies.items ():
                    bgVersie = bgBranch.InterneInstrumentversies.get (workId)
                    if bgVersie is None:
                        if instrumentversie.IsTeruggetrokken:
                            continue
                        if workId in self._Versiebeheer.BekendeInstrumenten:
                            self._LogFout ("Bestaand instrument '" + workId + "' is niet door BG aan het adviesbureau doorgegeven")
                            succes = False
                            continue
                        bgBranch.InterneInstrumentversies[workId] = bgVersie = MomentopnameInstrument (bgBranch, workId)
                        self._Versiebeheer.BekendeInstrumenten.add (workId)
                    bgVersie.ExpressionId = instrumentversie.ExpressionId
                    bgVersie.IsJuridischUitgewerkt = instrumentversie.IsJuridischUitgewerkt
                    bgVersie.IsTeruggetrokken = instrumentversie.IsTeruggetrokken

            # Stel de momentopname voor de uitwisseling op
            stop_mo = Momentopname ()
            self._Resultaat.Uitgewisseld.append (UitgewisseldeSTOPModule (stop_mo, ProjectactieResultaat._Uitvoerder_Adviesbureau, ProjectactieResultaat._Uitvoerder_BevoegdGezag))
            stop_mo.Doel = actie.Doel
            stop_mo.GemaaktOp = actie.UitgevoerdOp
            if bgBranch is None:
                # Voeg de uitgangssituatie alleen toe als gestart wordt met een download
                for workId, momentopname in branch.InterneInstrumentversies.items ():
                    if not momentopname.IsJuridischUitgewerkt:
                        expressionId = momentopname.ActueleExpressionId ()
                        # Uitgangssituatie als gedownload, BranchBasisversie als geleverd door BG
                        basisversie = momentopname.Uitgangssituatie[0].Momentopname
                        instrumentversie = InstrumentversieInformatie ()
                        instrumentversie.Basisversie_Doel = basisversie._Branch._Doel
                        instrumentversie.Basisversie_GemaaktOp = basisversie.GemaaktOp
                        instrumentversie.WorkId = workId
                        instrumentversie._ExpressionId = expressionId
                        stop_mo.Instrumentversies.append (instrumentversie)

        else:
            #----------------------------------------------------------
            # Van bevoegd gezag naar adviesbureau
            #----------------------------------------------------------
            # Maak een aparte branch voor het adviesbureau aan
            abBranch = Branch (actie.Doel) 
            self._Projectstatus.ExterneBranches[actie.Doel] = abBranch
            abBranch.UitgevoerdDoor = ProjectactieResultaat._Uitvoerder_Adviesbureau
            for workId, momentopname in branch.InterneInstrumentversies.items ():
                # Neem de instrumentversies over
                if not momentopname.IsJuridischUitgewerkt:
                    expressionId = momentopname.ActueleExpressionId ()

                    # Maak de huidige bevoegd-gezag branch de basisversie
                    basisversie = MomentopnameInstrument (branch, workId)
                    basisversie.ExpressionId = momentopname.ActueleExpressionId ()
                    basisversie.IsTeruggetrokken = False
                    basisversie.GemaaktOp = actie.UitgevoerdOp

                    # Maak de momentopname bij het adviesbureau
                    abMomentopname = MomentopnameInstrument (bgBranch, workId)
                    abMomentopname.Uitgangssituatie = [MomentopnameVerwijzing (basisversie)]
                    abBranch.InterneInstrumentversies[workId] = basisversie

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
class _VoerUit_Wijziging (ProjectactieUitvoering):

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
        self._Resultaat.UitgevoerdDoor = branch.Uitvoerder
        if branch.Uitvoerder == ProjectactieResultaat._Uitvoerder_Adviesbureau:
            if not self._NeemInstrumentversiesOver (branch, actie.Instrumentversies, False):
                succes = False
            if not actie.JuridischWerkendVanaf is None or not actie.GeldigVanaf is None:
                self._LogFout ("adviesbureau mag geen tijdstempels specificeren")
        else:
            if not self._NeemInstrumentversiesOver (branch, actie.Instrumentversies):
                succes = False
            branch.InterneTijdstempels.JuridischWerkendVanaf = actie.JuridischWerkendVanaf
            branch.InterneTijdstempels.GeldigVanaf = actie.GeldigVanaf

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
class _VoerUit_Publicatie (ProjectactieUitvoering):

    def __init__ (self):
        super ().__init__ ()

    def VoerUit (self, actie: ProjectActie_Publicatie):
        """Neem wijzigingen uit een andere branch over
        """
        if not actie.SoortPublicatie in ProjectActie_Publicatie._SoortPublicatie_ViaSTOPVersiebeheer:
            return True
        isConceptOfOntwerp = not actie.SoortPublicatie in ProjectActie_Publicatie._SoortPublicatie_GeenConceptOfOntwerp

        succes = True
        consolidatieInformatie = ConsolidatieInformatie (self._Log, '(gemaakt voor projectactie)')
        self._Resultaat.Uitgewisseld.append (UitgewisseldeSTOPModule (consolidatieInformatie, ProjectactieResultaat._Uitvoerder_BevoegdGezag, ProjectactieResultaat._Uitvoerder_LVBB))
        consolidatieInformatie.GemaaktOp = actie.UitgevoerdOp
        consolidatieInformatie.OntvangenOp = consolidatieInformatie._BekendOp = actie.UitgevoerdOp[0:10]

        # Lijst met alle elementen (en extra info) in de module
        elementen : List[_VoerUit_Publicatie._ElementMetRelaties] = []

        for doel in sorted (actie.Doelen, key = lambda d: str(d)):
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
                if gepubliceerd is None:
                    if not momentopname.Uitgangssituatie is None:
                        # Een van de basisversies is genoeg
                        basisversies = [momentopname.Uitgangssituatie[0].Momentopname]
                elif not momentopname.BasisVoorWijziging is None:
                    basisversies = [momentopname.BasisVoorWijziging]

                # Bepaal de vermelding in de consolidatie-informatie
                if momentopname.IsTeruggetrokken:
                    if gepubliceerd is None or gepubliceerd.IsTeruggetrokken:
                        # Geen wijziging dus geen vermelding nodig
                        continue
                    #--------------------------------------------------
                    # Eerder gepubliceerde wijziging is teruggetrokken
                    #--------------------------------------------------
                    if gepubliceerd.IsJuridischUitgewerkt:
                        element = _VoerUit_Publicatie._ElementMetRelaties (TerugtrekkingIntrekking (consolidatieInformatie, [branch._Doel], workId), basisversies)
                        if consolidatieInformatie.TerugtrekkingenIntrekking is None:
                            consolidatieInformatie.TerugtrekkingenIntrekking = [element.Element]
                        else:
                            consolidatieInformatie.TerugtrekkingenIntrekking.append (element.Element)
                    else:
                        element = _VoerUit_Publicatie._ElementMetRelaties (Terugtrekking (consolidatieInformatie, [branch._Doel], workId), basisversies)
                        if consolidatieInformatie.Terugtrekkingen is None:
                            consolidatieInformatie.Terugtrekkingen = [element.Element]
                        else:
                            consolidatieInformatie.Terugtrekkingen.append (element.Element)

                elif momentopname.IsJuridischUitgewerkt:
                    if not gepubliceerd is None and gepubliceerd.IsJuridischUitgewerkt:
                        # Geen wijziging dus geen vermelding nodig
                        continue
                    #--------------------------------------------------
                    # Intrekking is nog niet gepubliceerd
                    #--------------------------------------------------
                    element = _VoerUit_Publicatie._ElementMetRelaties (Intrekking (consolidatieInformatie, [branch._Doel], workId), basisversies)
                    if consolidatieInformatie.Intrekkingen is None:
                        consolidatieInformatie.Intrekkingen = [element.Element]
                    else:
                        consolidatieInformatie.Intrekkingen.append (element.Element)

                else:
                    if not gepubliceerd is None and gepubliceerd.ExpressionId == momentopname.ExpressionId:
                        # Geen wijziging dus geen vermelding nodig
                        continue
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
                            andereMO = branch.InterneInstrumentversies.get (workId)
                            if andereMO is None:
                                andereMO = branch.InterneInstrumentversies.get (workId)
                            if not andereMO is None:
                                doelen.append (andereBranch._Doel)
                                if not andereMO.BasisVoorWijziging is None:
                                    # De basisversie verwijst alleen naar eerder gepubliceerde versies
                                    nieuweBasisversies.append (andereMO.BasisVoorWijziging)
                        if len (doelen) > 1:
                            # De versie is inderdaad van toepassing voor meerdere doelen
                            basisversies = nieuweBasisversies
                    
                    element = _VoerUit_Publicatie._ElementMetRelaties (BeoogdeVersie (consolidatieInformatie, doelen, workId, momentopname.ExpressionId), basisversies)
                    if consolidatieInformatie.BeoogdeVersies is None:
                        consolidatieInformatie.BeoogdeVersies = [element.Element]
                    else:
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
        
        return succes
 
    class _ElementMetRelaties:
        def __init__ (self, element : VoorInstrument, basisversies : List[MomentopnameInstrument]):
            """Maak een nieuw in-memory bakje met de te leggen relaties
            """
            self.Element = element
            self.Basisversies = basisversies
            self.VervlochtenMet : List[MomentopnameInstrument] = []
            self.OntvlochtenMet : List[MomentopnameInstrument] = []

        def VoegRelatiesToe (self):
            # Voeg de relaties toe aan de consolidatie-informatie
            if not self.Basisversies is None:
                for momentopname in self.Basisversies:
                    self.Element.Basisversies[momentopname._Branch._Doel] = CI_Momentopname (momentopname._Branch._Doel, momentopname.GemaaktOp)






