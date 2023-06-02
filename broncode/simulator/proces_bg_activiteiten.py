#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# De activiteiten die het bevoegd gezag kan uitvoeren zijn geformuleerd
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
# gezag. Het laat ook zien welke aanvullende instructies aan BG 
# gegeven moeten worden om de activiteit uit te voeren.
#
# De systematiek is: de specificatie (typisch bg_proces.json) bevat
# de specificatie van een Activiteit. De klasse voor een specifieke
# Activiteit implementeert ook de uitvoering ervan. Die resulteert
# enerzijds in een Procesbegeleiding - een beschrijving van de
# activiteit plus instructies voor de uitvoering ervan - en anderzijds
# in het bijwerken van het BG-versiebeheer.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from datetime import datetime, timedelta
from math import floor

from applicatie_meldingen import Meldingen
from data_bg_procesverloop import Activiteitverloop, Procesvoortgang, Projectstatus, Branch
from data_bg_versiebeheer import Versiebeheerinformatie, Commit, Instrument, InstrumentInformatie, Instrumentversie, Consolidatie
from data_doel import Doel
from data_validatie import Valideer
from stop_consolidatieinformatie import ConsolidatieInformatie

#======================================================================
#
# Representatie van de specificatie van het proces bij een BG
# (inclusief adviesbureaus).
#
#======================================================================

class BGProces:
#----------------------------------------------------------------------
# Inlezen specificatie
#----------------------------------------------------------------------
    @staticmethod
    def LeesJson (log : Meldingen, pad : str, data):
        """Lees de inhoud van de module uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        data string  JSON specificatie van het proces
        
        Resultaat van de methode is een BGProces instantie, of None als de JSON 
        geen specificatie van het BG proces is
        """
        if not "BGCode" in data:
            return None
        bgprocess = BGProces ()
        bgprocess.BGCode = data["BGCode"]
        if "Beschrijving" in data:
            bgprocess.Beschrijving = data["Beschrijving"]
        if "Startdatum" in data:
            if Valideer.Datum (data["Startdatum"]) is None:
                log.Fout ("Startdatum (" + data["Startdatum"] + ") is geen valide datum in '" + pad + "'")
                bgprocess._IsValide = False
            else:
                try:
                    bgprocess._Startdatum = datetime (int (data["Startdatum"][0:4]), int (data["Startdatum"][5:7]), int (data["Startdatum"][8:10]))
                except Exception as e:
                    log.Fout ("Startdatum is geen valide datum in '" + pad + "': " + str(e))
                    bgprocess._IsValide = False
        else:
            log.Fout ("Startdatum ontbreekt in '" + pad + "'")
            bgprocess._IsValide = False

        if "Projecten" in data:
            for project, activiteiten in data["Projecten"].items ():
                bgprocess.Projecten.add (project)
                for activiteit in activiteiten:
                    a = Activiteit.LeesJson (log, pad, bgprocess, project, activiteit)
                    if a is None:
                        bgprocess._IsValide = False
                    else:
                        bgprocess.Activiteiten.append (a)
        if "Overig" in data:
            for activiteit in data["Overig"]:
                a = Activiteit.LeesJson (log, pad, bgprocess, None, activiteit)
                if a is None:
                    bgprocess._IsValide = False
                else:
                    bgprocess.Activiteiten.append (a)

        if bgprocess._IsValide:
            if len (bgprocess.Activiteiten) == 0:
                log.Waarschuwing ("Geen activiteiten gespecificeerd in '" + pad + "': " + str(e))
            else:
                bgprocess.Activiteiten.sort (key = lambda x: x.UitgevoerdOp)
        return bgprocess

#----------------------------------------------------------------------
# Initialisatie en overige eigenschappen
#----------------------------------------------------------------------
    def __init__ (self):
        # Code te gebruiken bij het bepalen van de AKN/JOIN workId
        self.BGCode: str = None
        # Beschrijving van het scenario, als alternatief voor de beschrijving in 
        self.Beschrijving: str = None
        # Startdatum van het scenario; wordt overschreven door de specificatie
        self._Startdatum = datetime.now ()
        # De namen van de projecten in de specificatie
        self.Projecten : Set[str] = set()
        # Ingelezen activiteiten, gesorteerd op het tijdstip van uitvoering
        self.Activiteiten : List[Activiteit] = []
        # Geeft aan of de specificatie valide is
        self._IsValide = True

#======================================================================
#
# Basisklasse voor de specificatie en uitvoering van een BG-activiteit
#
#======================================================================
class Activiteit:

#----------------------------------------------------------------------
# Inlezen specificatie
#----------------------------------------------------------------------
    @staticmethod
    def LeesJson (log : Meldingen, pad : str, bgprocess : BGProces, project: str, data) -> 'Activiteit':
        """Lees de inhoud van de module uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        bgprocess BGProces Proces waar dit een activiteit voor is
        project string Naam van het project
        data {}  JSON specificatie van de activiteit
        
        Resultaat van de methode is een Activiteit instantie, of None als de JSON 
        geen specificatie van een (bekende) activiteit is
        """
        ok = True
        if "Tijdstip" in data:
            dag = floor (data["Tijdstip"])
            uur = round (100*(data["Tijdstip"] - dag))
            tijdstip = bgprocess._Startdatum + timedelta (days = 0 if dag < 0 else dag, hours = uur if uur < 24 else 24)
            del data["Tijdstip"]
        else:
            log.Fout ("Tijdstip ontbreekt in een activiteit van " + ("'Overig'" if project is None else "project '" + project + "'") + " in '" + pad + "'")
            ok = False
            tijdstip = bgprocess._Startdatum

        if not "Soort" in data:
            log.Fout ("Soort ontbreekt in een activiteit van " + ("'Overig'" if project is None else "project '" + project + "'") + " in '" + pad + "'")
            return
        constructor = Activiteit._Constructors.get (data["Soort"])
        if constructor is None:
            log.Fout ("Onbekende Soort='" + data["Soort"] + "' voor een activiteit van " + ("'Overig'" if project is None else "project '" + project + "'") + " in '" + pad + "'")
            return
        activiteit : Activiteit = constructor ()
        activiteit._BGProcess = bgprocess
        activiteit._Soort = data["Soort"]
        del data["Soort"]
        activiteit._Data = data
        activiteit.Project = project
        activiteit.UitgevoerdOp = tijdstip.strftime ("%Y-%m-%dT%H:%M:%SZ")

        if not activiteit._LeesData (log, pad):
            ok = False
        if ok:
            return activiteit

    _Constructors = {
        "MaakBranch": lambda : Versiebeheer_MaakBranch (),
        "Wijziging": lambda : Versiebeheer_Commit ()
    }

    def _LeesData (self, log, pad) -> bool:
        """Lees de specificatie van de activiteit uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        
        Resultaat van de methode geeft aan of het inlezen geslaagd is
        """
        raise Exception ("_LeesData niet geïmplementeerd")

#----------------------------------------------------------------------
# Initialisatie en overige eigenschappen
#----------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        # Specificatie van het proces
        self._BGProcess : BGProces = None
        # Soort activiteit
        self._Soort : str = None
        # Specificatie van de activiteit voor zover niet bij het inlezen omgezets
        self._Data = None
        # Geeft aan dat de activiteit binnen een project uitgevoerd dient te worden
        self._ProjectVerplicht : bool = True
        # Tijdstip waarop de activiteit uitgevoerd is
        self.UitgevoerdOp : str = None
        # Project waarvoor de activiteit uitgevoerd wordt
        self.Project : str = None
        # Als de activiteit leidt tot een uitwisseling: de naam van de uitwisseling
        self.UitwisselingNaam = None
        # Soort publicatie die volgt uit deze activiteit
        self.SoortPublicatie : str = None

#----------------------------------------------------------------------
# Uitvoering
#----------------------------------------------------------------------
    def VoerUit (self, log : Meldingen, scenario, gebeurtenis) -> Tuple[bool,Activiteitverloop]:
        """Voer de activiteit uit
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        scenario Scenario  Informatie over en uitkomsten van het scenario
        gebeurtenis Scenario.Gebeurtenis Gebeurtenis waarvan deze activiteit onderdeel is
        
        Resultaat van de methode geeft aan of de uitvoering geslaagd is, en geeft het resulterende Activiteitverloop
        """
        activiteitverloop = Activiteitverloop (self.UitgevoerdOp, )
        context = Activiteit._VoerUitContext (log, scenario, activiteitverloop)
        
        if not self.Project is None:
            context.ProjectStatus = scenario.Procesvoortgang.Projecten.get (self.Project)
            if context.ProjectStatus is None:
                context.ProjectStatus = Projectstatus (self.Project, self.UitgevoerdOp)
                scenario.Procesvoortgang.Projecten[self.Project] = context.ProjectStatus
            context.Activiteitverloop.UitgevoerdDoor = context.ProjectStatus.UitgevoerdDoor
            context.Activiteitverloop.Projecten.add (self.Project)
        elif self._ProjectVerplicht:
            self._LogFout (context, "de activiteit moet als onderdeel van een project uitgevoerd worden")
            return
        self._VoerUit (context)
        if activiteitverloop.Naam is None:
            activiteitverloop.Naam = self._Soort
        gebeurtenis.ConsolidatieInformatie = context.ConsolidatieInformatie
        return (context.Succes, context.Activiteitverloop)

    class _VoerUitContext:
        def __init__(self, log : Meldingen, scenario, resultaat: Activiteitverloop):
            self.Log = log;
            self.Scenario = scenario
            self.Procesvoortgang : Procesvoortgang = scenario.Procesvoortgang
            self.Versiebeheer : Versiebeheerinformatie = scenario.BGVersiebeheerinformatie
            # Rapportage over de activiteit
            self.Activiteitverloop = resultaat
            self.Procesvoortgang.Activiteiten.append (resultaat)
            # Status van het project waartoe de activiteit behoort
            self.ProjectStatus : Projectstatus = None 
            # Resulterende consolidatie-informatie
            self.ConsolidatieInformatie : ConsolidatieInformatie = None
            # Geeft aan of de uitvoering succesvol was.
            self.Succes = True

        def MaakCommit (self, branch : Branch, volgnummer : int = 1):
            """Maak een commit voor weergave in de resultaatpagina.

            Argumenten:

            branch Branch  Branch waarvoor de commit aangemaakt is
            gemaaktOp string  Tijdstip van wijziging van de branch
            volgnummer int  Volgnummer van de commit
            """
            commit = Commit (branch, self.Activiteitverloop.UitgevoerdOp, volgnummer)
            self.Activiteitverloop.Commits.append (commit)
            return commit


    def _VoerUit (self, context: _VoerUitContext):
        """Voer de activiteit uit

        Argumenten:

        context _VoerUitContext Status van de simulatie en en resultaat van de activiteit
        """
        raise Exception ("_VoerUit niet geïmplementeerd")

    def _LogFout (self, context: _VoerUitContext, tekst : str):
        context.Log.Fout (self._MaakMelding (tekst))
        context.Succes = False

    def _MaakMelding (self, tekst : str):
        return "BG activiteit " + self._Soort + " (" + self.UitgevoerdOp + "): " + tekst


#======================================================================
#
# Activiteiten tbv versiebeheer
#
#======================================================================

#----------------------------------------------------------------------
#
# Wijziging van instrumentversies en/of tijdstempels in de branch
#
#----------------------------------------------------------------------
class Versiebeheer_Commit (Activiteit):
    """Commit nieuwe instrumentversies en evt annotaties voor één of meer branches. 
    Deze activiteit is tevens de basis voor een aantal andere activiteiten die daarna (of 
    daarvoor) iets met de branches doen.
    """
    def __init__ (self):
        super ().__init__ ()
        # Branches waarvoor wijzigingen zijn opgegeven
        # key = naam, value = specificatie van de wijziging (lezen bij uitvoeren van de activiteit)
        self.CommitSpecificatie : Dict[str,object] = {}

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
        if len (self.CommitSpecificatie) > 0:
            if context.Activiteitverloop.Beschrijving is None:
                context.Activiteitverloop.Beschrijving = "De eindgebruiker wijzigt de kopie van de regelgeving waaraan binnen het project wordt gewerkt."

        # Valideer dat de branches bestaan waarvoor wijzigigen zijn opgegeven
        onbekendeNamen = set(self.CommitSpecificatie.keys()).difference (b._Doel.Naam for b in context.ProjectStatus.Branches)
        if len (onbekendeNamen) > 0:
            self._LogFout (context, "het wijzigen van regelgeving moet beperkt zijn tot de branches van het project '" + self.Project + "', dus niet: '" + "', '".join (onbekendeNamen) + "'")
            return

        # Voor weergave in de resultaatpagina:
        if len (context.ProjectStatus.Branches) > 1:
            context.Activiteitverloop.MeldInteractie (True, 'Pas de regelgeving aan voor één of meer van de beoogde inwerkingtredingsmomenten (branches) in het project')
        else:
            context.Activiteitverloop.MeldInteractie (True, 'Pas de regelgeving aan in het project')

        # Pas de wijzigingen toe
        # Als dit een zelfstandige actie is zijn tijdstempels niet toegestaan, die mogen pas bij een vaststellingsbesluit toegevoegd worden.
        for naam in sorted (self.CommitSpecificatie.keys ()):
            self._VoerWijzigingenUit (context, naam, None, False)

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
        doel = Doel.DoelInstantie ('/join/id/proces/' + self._BGProcess.BGCode + '/' + naam)
        branch = context.Versiebeheer.Branches.get (doel)
        if branch is None:
            self._LogFout (context, "branch '" + naam + "' is (nog) niet aangemaakt")
            return
        if branch.Project is None:
            self._LogFout (context, "branch '" + naam + "' wordt niet via BG activiteiten beheerd maar via uitgewisselde ConsolidatieInformatie modules")
            return
        elif not self.Project is None and branch.Project != self.Project:
            self._LogFout (context, "branch '" + naam + "' wordt in project '" + branch.Project + "' beheerd maar deze activiteit is voor project '" + self.Project + "'")
            return

        regelgevingGewijzigd = False
        tijdstempelsGewijzigd = False
        # Pas de wijzigingen per instrument toe
        for workIdNaam, versie in specificatie.items ():
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
                        info.WijzigInstrument (commit, None)
                        context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Branch '" + naam + "': markeer versie als onbekend voor instrument '" + workIdNaam + "'")
                    else:
                        # Terugtrekking van de wijziging voor deze branch
                        if info is None:
                            self._LogFout (context, "geen informatie over instrument '" + workIdNaam + "' bekend voor branch '" + branch._Doel.Naam + "'; kan wijziging van instrument niet terugtrekken")
                            continue
                        info.TrekWijzigingTerug (commit)
                        context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Branch '" + naam + "': trek wijziging voor instrument '" + workIdNaam + "' terug")
                else:
                    # Nieuwe ingevoerde versie van het instrument
                    if info is None:
                        branch.Instrumentversies[instrument.WorkId] = info = InstrumentInformatie (branch, instrument)
                    expressionId = instrument.MaakExpressionId (self, branch)
                    instrumentversie = info.WijzigInstrument (commit, expressionId)
                    context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Branch '" + naam + "': nieuwe versie voor instrument '" + workIdNaam + "': " + expressionId)

                if not instrumentversie is None and isinstance (versie, dict):
                    # TODO: Annotaties gespecificeerd?
                    pass

        if tijdstempelsToegestaan:
            if "JuridischWerkendVanaf" in specificatie:
                juridischWerkendVanaf = None
                geldigVanaf = None
                if isinstance (specificatie["JuridischWerkendVanaf"], str):
                    if Valideer.Datum (specificatie["JuridischWerkendVanaf"]) is None:
                        self._LogFout (context, "JuridischWerkendVanaf (" + specificatie["JuridischWerkendVanaf"] + ") is geen valide datum")
                    else:
                        juridischWerkendVanaf = specificatie["JuridischWerkendVanaf"]
                    if "GeldigVanaf" in specificatie and isinstance (specificatie["GeldigVanaf"], str):
                        if Valideer.Datum (specificatie["GeldigVanaf"]) is None:
                            self._LogFout (context, "GeldigVanaf (" + specificatie["GeldigVanaf"] + ") is geen valide datum")
                        else:
                            geldigVanaf = specificatie["GeldigVanaf"]
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
            context.Activiteitverloop.MeldInteractie (False, 'Wijzigt ' + ('regelgeving ' if regelgevingGewijzigd else '')+ ('en ' if regelgevingGewijzigd and tijdstempelsGewijzigd else '')+ ('geldigheidsinformatie ' if tijdstempelsGewijzigd else '') + 'voor ' + branch.InteractieNaam)

#----------------------------------------------------------------------
#
# Aanmaken van een nieuwe branch
#
#----------------------------------------------------------------------
class Versiebeheer_MaakBranch (Versiebeheer_Commit):
    """Maak een nieuwe branch voor een project
    """
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
            context.Activiteitverloop.MeldInteractie (False, '''Maakt een nieuw project aan.''')
        else:
            if context.Activiteitverloop.Naam is None:
                context.Activiteitverloop.Naam = "Bereid nieuwe inwerkingtredingsmomenten voor"
            if not context.Activiteitverloop.Beschrijving:
                context.Activiteitverloop.Beschrijving = "De eindgebruiker maakt een kopie van de regelgeving om binnen het project aan te werken."

        context.Activiteitverloop.MeldInteractie (True, '''Maak voor elk beoogde inwerkingtredingsmoment een kopie van de regelgeving.
Binnen het project wordt de kopie gewijzigd zonder dat dit meteen invloed heeft op de werkzaamheden in andere projecten.''')
        context.Activiteitverloop.MeldInteractie (True, '''Geef per beoogd inwerkingtredingsmoment aan op welke manier de inwerkingtreding beoogd is. In deze simulator kan gekozen worden uit:
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
        context.Activiteitverloop.MeldInteractie (True, 'Pas eventueel de regelgeving aan na het aanmaken van de kopie')
        self._VoerMaakBranchUit (context)

    def _VoerMaakBranchUit (self, context: Activiteit._VoerUitContext):
        """Maak de opgegeven branches aan
        """
        # Klaar = branches die geïnitialiseerd zijn
        klaar : Set[Doel] = set (context.Versiebeheer.Branches.keys ())
        # nogInitialiseren = branches die niet meteen geïnitialiseerd worden
        nogInitialiseren : List[Tuple[Branch,str,Set[Doel]]] = []
        # Nu geldig: huidig geldende regelgeving
        nuGeldig : Consolidatie = None

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
        volgnummer = 0
        while len (nogInitialiseren) > 0:
            nogSteedsInitialiseren : List[Tuple[Branch,str,Set[Doel]]] = []
            nuKlaar : List[Doel] = []
            volgnummer += 1
            for branch, soort, doelen in nogInitialiseren:
                if len (set(doelen).difference (klaar)) > 0:
                    # Nog niet alle branches zijn geïnitialiseerd
                    nogSteedsInitialiseren.append ((branch, soort, doelen))
                    continue
                commit = context.MaakCommit (branch, volgnummer)

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
                    context.Activiteitverloop.MeldInteractie (False, "Maakt " + kopieNaam + " bedoeld als volgende versie van de geldende regelgeving")
                    context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Er wordt een nieuwe branch '" + branch._Doel.Naam + "' aangemaakt voor regelgeving bedoeld als volgende versie van de geldende regelgeving")
                    context.Activiteitverloop.VersiebeheerVerslag.Informatie ("De branch '" + branch._Doel.Naam + "' wordt geïdentificeerd met het doel " + branch._Doel.Identificatie)
                    if nuGeldig is None:
                        # Zoek de geldige consolidatie op
                        isLaatste = True
                        for consolidatie in context.Versiebeheer.Consolidatie:
                            if consolidatie.JuridischGeldigVanaf > self.UitgevoerdOp:
                                break
                            isLaatste = False
                            if consolidatie.IsCompleet:
                                nuGeldig = consolidatie
                                isLaatste = True
                        if not isLaatste:
                            context.Activiteitverloop.VersiebeheerVerslag.Waarschuwing ("Er is geen valide consolidatie voor de nu geldende regelgeving beschikbaar - de simulatie gaat uit van de laatst beschikbare consolidatie")
                    # Neem de huidige regelgeving als uitgangspunt
                    branch.BaseerOpGeldendeVersie (context.Activiteitverloop.VersiebeheerVerslag, commit, nuGeldig)
                else:
                    # Voor weergave op de resultaatpagina:
                    branches = [context.Versiebeheer.Branches[d] for d in doelen]
                    if len(doelen) > 1:
                        context.Activiteitverloop.MeldInteractie (False, "Maakt " + kopieNaam + " die in werking treedt zodra alle regelgeving in werking getreden is van: " + ", ".join (b.InteractieNaam for b in branches))
                        context.Activiteitverloop.VersiebeheerVerslag.Informatie ("Er wordt een nieuwe branch '" + branch._Doel.Naam + "' aangemaakt als oplossing van de samenloop van branches '" + "', '".join (d.Naam for d in doelen) + "'")
                        # Verifieer dat de eerste branch bij het project hoort
                        if not doelen[0] in set (b._Doel for b in context.ProjectStatus.Branches):
                            self._LogFout (context, "branch '" + branch._Doel.Naam + "': de eerste branch '" + doelen[0].Naam + "' waarvoor samenloop opgelost moet worden moet binnen het project liggen")
                        branch.TreedtConditioneelInWerkingMet = set (branches)
                    else:
                        context.Activiteitverloop.MeldInteractie (False, "Maakt " + kopieNaam + " die in werking treedt na " + branches[0].InteractieNaam)
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

