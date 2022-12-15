#======================================================================
#
# Simulatie van het interne versiebeheer, onderdeel van de software
# van het bevoegd gezag.
#
#======================================================================
#
# In productie-waardige software zal het interne versiebeheer
# daadwerkelijk regeling- en informateiobjectversies bevatten.
# In deze simulator wordt alleen de versieadministratie bijgehouden.
# Het doel is om te laten zien dat op basis van die administratie
# het mogelijk is om de benodigde informatie voor het STOP versiebeheer
# af te leiden/bij te houden.
#
# De methoden van het versiebeheer in de simulator zijn zo gekozen
# dat het lijkt op de manier waarop git werkt.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from applicatie_meldingen import Meldingen
from data_bg_project import InstrumentversieSpecificatie
from data_bg_projectvoortgang import Projectvoortgang, Branch
from data_bg_versiebeheer import InstrumentInformatie, Instrumentversie, Tijdstempels
from data_doel import Doel
from proces_bg_consolidatieinformatie import ConsolidatieInformatieMaker
from stop_momentopname import DownloadserviceModules, Momentopname, InstrumentversieInformatie
from stop_consolidatieinformatie import ConsolidatieInformatie

#======================================================================
#
# Uitvoeren van het versiebeheer
#
#======================================================================
class Versiebeheer:

    def __init__ (self, log : Meldingen, projectvoortgang: Projectvoortgang):
        """Maak een nieuwe versiebeheerder aan
        
        Argumenten:

        log Meldingen  Verzameling van meldingen over de uitvoering van het scenario
        projectvoortgang Projectvoortgang  Datamodel voor het interne versiebeheer bij bevoegd gesag.
                                           None voor het versiebeheer bij een adviesbureau.
        """
        self._Log = log
        # Overzicht van alle in de LVBB bekende versies
        self._PubliekeInstrumentversies = set () if projectvoortgang is None else projectvoortgang.PubliekeInstrumentversies
        # Datamodel voor het interne versiebeheer bij het bevoegd gezag
        self._Versiebeheer = None if projectvoortgang is None else projectvoortgang.Versiebeheer
        # Verzameling van branches
        self._Branches : Dict[Doel,Branch] = {} if projectvoortgang is None else projectvoortgang.Versiebeheer.Branches

#======================================================================
#
# Ophalen van actuele instrumentversies voor een branch of consolidatie
# uit het interne versiebeheer
#
#======================================================================
    class Head:
        def __init__(self):
            """Maak een nieuw overzicht van de actuele versies van de instrumenten"""
            # De branches die synchroon gehouden worden
            self.Branches : Set[Branch] = set ()
            # De actuele (interne, binnen de creatie-keten) stand van de instrumentversies
            # key = work-Id
            self.Instrumentversies : Dict[str,Instrumentversie] = {}

    def BranchHead (self,  doel : Doel) -> Head:
        """Geef de actuele instrumentversies voor de branch

        Argumenten:

        doel Doel  Doel waarvoor de branch is gemaakt

        Geeft een Head terug, of None als het doel niet bestaat in het versiebeheer
        """
        branch = self._Versiebeheer.Branches.get (doel)
        if branch is None:
            self._Log.Fout ("Doel niet bekend in het versiebeheer van het bevoegd gezag: '" + str(doel) + "'")
            return None

        # Maak de head
        head = Versiebeheer.Head ()
        head.Branches.add (branch)
        head.Instrumentversies = { w: i.Instrumentversie for w, i in branch.Instrumentversies.items () }
        return head

    def ConsolidatieHead (self, geldigOp: str, directVoorafgaand : bool) -> Head:
        """Geef de actuele instrumentversies voor de geconsolideerde regelgeving zoals 
        die nu bekend is in het interne versiebeheer van het bevoegd gezag.

        Argumenten:

        geldigOp str Datum waarop de regelgeving geldig moet zijn
        directVoorafgaand bool Als True, dan moet niet de consolidatie op de geldigOp datum 
                               maar de consoildatie op de dag ervoor genomen worden

        Geeft een Head terug, of None als er nog geen consolidatie bekend is voor die datum
        """
        # Zoek de consolidatie op
        consolidatie = None
        if not self._Versiebeheer.Consolidatie is None:
            for c in self._Versiebeheer.Consolidatie:
                if c.JuridischGeldigVanaf < geldigOp or (not directVoorafgaand and c.JuridischGeldigVanaf == geldigOp):
                    consolidatie = c
                else:
                    break
        if consolidatie is None:
            self._Log.Fout ("Geen consolidatie bekend in het versiebeheer van het bevoegd gezag op " + ('de dag voor ' if directVoorafgaand else '') + geldigOp)
            return None

        # Maak de head 
        head = Versiebeheer.Head ()
        head.Branches = consolidatie.Branches
        for workId, info in consolidatie.Instrumentversies.items ():
            versie = Instrumentversie ()
            versie.ExpressionId = info.ExpressionId
            versie.IsJuridischUitgewerkt = info.IsJuridischUitgewerkt
            head.Instrumentversies[workId] = versie
        return head

#======================================================================
#
# Aanmaken van basiselementen van het versiebeheer
#
#======================================================================
    @staticmethod
    def MaakInstrumentversie (specificatie: InstrumentversieSpecificatie) -> Instrumentversie:
        """Maak een instrumentversie die een bekende of onbekende versie representeert
        
        Argumenten:

        specificatie InstrumentversieSpecificatie Specificatie van de versie, of None als het 
                                                  instrument niet bestaat en nooit bestaan heeft
        """
        versie = Instrumentversie ()
        if not specificatie is None:
            if specificatie.IsJuridischUitgewerkt:
                versie.IsJuridischUitgewerkt = specificatie.IsJuridischUitgewerkt
            else:
                versie.IsJuridischUitgewerkt  = False
                versie.ExpressionId = specificatie.ExpressionId
        return versie

    def MaakBranch (self, doel : Doel, gebaseerdOp : Head, uitgevoerdOp: str):
        """Maak een nieuwe branch aan

        Argumenten:

        doel Doel  Doel waarvoor de branch wordt aangemaakt
        gebaseerdOp Head  Uitgangspunt voor de nieuwe branch, of None voor de branch met de initiële versie
        uitgevoerdOp str Tijdstip waarop de nieuwe informatie in het versiebeheer wordt vastgelegd

        Geeft terug of de commit zonder fouten is uitgevoerd.
        """
        if doel in self._Branches:
            self._Log.Fout ("branch bestaat al voor doel: '" + str(doel) + "'")
            return False

        self._Branches[doel] = branch = Branch (doel)
        branch.LaatstGewijzigdOp = uitgevoerdOp
        if not gebaseerdOp is None:
            for workId, versie in gebaseerdOp.Instrumentversies.items ():
                info = InstrumentInformatie (branch)
                info.Instrumentversie = versie
                info.Uitgangssituatie = versie
        return True

#======================================================================
#
# Aanpassen van de inhoud van het versiebeheer
#
#======================================================================

#----------------------------------------------------------------------
#
# Commit: Nieuwe versies van instrumenten/tijdstempels opnemen.
#         Hiermee kunnen ook brnches gemerged worden.
#
#         Deze methode kan ook gebruikt worden om wijzigingen in het 
#         versiebeheer van een adviesbureau door te voeren (voor 1 branch)
#
#----------------------------------------------------------------------
    def Commit (self, branches : List[Branch], nieuweInstrumentversies : Dict[str,InstrumentversieSpecificatie], nieuweTijdstempels : Tijdstempels, uitgevoerdOp: str, bekendOp: str = None) -> bool:
        """Werk het interne versiebeheer bij met de nieuwe versies.

        Argumenten:

        branches Branch[]  Lijst van branches waarin de regelingversies verwerkt moeten worden. Als het meerdere branches zijn, dan wordt aangenomen dat
                           vanaf dit moment alle branches synchroon bijgewerkt worden.
        nieuweInstrumentversies {}  Specificatie van de nieuwe instrumentversies; mag None zijn
        nieuweTijdstempels Tijdstempels Specificatie van de nieuwe tijdstempels; mag None zijn
        uitgevoerdOp str Tijdstip waarop de nieuwe informatie in het versiebeheer wordt vastgelegd
        bekendOp str Datum waarop de informatie bekend is geworden (bijv als gevolg van een uitspraak van een rechter). None als de bron het bevoegd gezag is.

        Geeft terug of de commit zonder fouten is uitgevoerd.
        """
        # Verwerk eerst de nieuwe versies (bij mergen van branches: de oplossingen van de merge conflicten)
        if not nieuweInstrumentversies is None:
            for workId, instrumentversie in nieuweInstrumentversies.items ():
                for branch in branches:
                    instrumentinfo = branch.Instrumentversies.get (workId)
                    if instrumentinfo is None:
                        branch.Instrumentversies[workId] = instrumentinfo = InstrumentInformatie (branch)
                    instrumentinfo.Instrumentversie = Versiebeheer.Instrumentversie (instrumentversie)
                    # In het STOP versiebeheer wordt altijd een nieuwe versie doorgegeven,
                    # behalve als er op deze branch geen versie is gespecificeerd (en dus 
                    # ook niet is overgenomen van een de uitgangspositie)
                    if instrumentinfo.Uitgangssituatie is None and not instrumentinfo.Instrumentversie.IsJuridischInWerking():
                        instrumentinfo.Instrumentversie.ExpressionId = None
                        instrumentinfo.Instrumentversie.IsJuridischUitgewerkt = None

        if not nieuweTijdstempels is None:
            for branch in branches:
                branch.Tijdstempels = nieuweTijdstempels

        for branch in branches:
            branch.BekendOp = bekendOp
            branch.LaatstGewijzigdOp = uitgevoerdOp

        # Merge of splits de branches
        alleInstrumenten = set ()
        for branch in branches:
            if not branch.SimultaanBeheerdeBranches is None:
                for sync in branch.SimultaanBeheerdeBranches:
                    if not sync in branches:
                        sync.SimultaanBeheerdeBranches.remove (branch)
                        if len (sync.SimultaanBeheerdeBranches) == 1:
                            sync.SimultaanBeheerdeBranches = None
            branch.SimultaanBeheerdeBranches = None if len(branches) == 1 else set (branches)
            if len(branches) > 1:
                alleInstrumenten.update (branch.Instrumentversies.keys ())

        # Controleer dat op alle branches dezelfde informatie staat, dwz dat de merge conflicten opgelost zijn.
        succes = True
        if len(branches) > 1:
            for workId in alleInstrumenten:
                instrumentversie = None
                for branch in branches:
                    instrumentinfo = branch.Instrumentversies.get (workId)
                    if instrumentinfo is None:
                        self._Log.Fout ("BG versiebeheer commit (" + uitgevoerdOp + "): merge conflict voor instrument '" + workId + "' niet opgelost")
                        succes = False
                        break
                    if instrumentversie is None:
                        instrumentversie = instrumentinfo.Instrumentversie
                    elif not instrumentversie.IsGelijkAan (instrumentinfo.Instrumentversie):
                        self._Log.Fout ("BG versiebeheer commit (" + uitgevoerdOp + "): merge conflict voor instrument '" + workId + "' niet opgelost")
                        succes = False
                        break

            tijdstempels = None
            for branch in branches:
                if tijdstempels is None:
                    tijdstempels = branch.Tijdstempels
                elif not tijdstempels.IsGelijkAan (branch.Tijdstempels):
                    self._Log.Fout ("BG versiebeheer commit (" + uitgevoerdOp + "): merge conflict in tijdstempels niet opgelost")
                    succes = False
                    break

        return succes

#----------------------------------------------------------------------
#
# Merge de wijzigingen uit de head in de branches, los merge conflicts 
# op en commit het resultaat naar de branches. Dit is het vervlechten
# van de wijzigingen uit andere branches in de simultaan beheerde
# branches.
#
#----------------------------------------------------------------------
    def Merge (self, teMergenBranches: Head, branches : List[Branch], nieuweInstrumentversies : Dict[str,InstrumentversieSpecificatie], uitgevoerdOp: str) -> bool:
        """Vervlecht de wijzigingen uit de branches van de opgehaalde instrumentversies in de simultaan bijgehouden branches

        Argumenten:

        teMergenBranches Head  De instrumentversies 
        branches Branch[]  Lijst van branches waarin de regelingversies verwerkt moeten worden. Als het meerdere branches zijn, dan wordt aangenomen dat
                           vanaf dit moment alle branches simultaan bijgehouden worden.
        nieuweInstrumentversies {}  Specificatie van de nieuwe instrumentversies die merge conflicten oplossen; mag None zijn
        uitgevoerdOp str Tijdstip waarop de nieuwe informatie in het versiebeheer wordt vastgelegd

        Geeft terug of de merge zonder fouten is uitgevoerd.
        """
        if teMergenBranches is None:
            return False
        succes = True

        # Controleer dat alle merge conflicts zijn opgelost
        # Alle instrumenten moeten in alle branches terugkomen, desnoods als niet gespecificeerd of juridisch uitgewerkt
        for workId, teMergenVersie in teMergenBranches.Instrumentversies.items ():
            if teMergenVersie.IsJuridischInWerking ():
                # Er moet een versie voor dit instrument op de branch bekend zijn/worden
                if workId in nieuweInstrumentversies:
                    # Merge conflict opgelost, blijkaar
                    continue
                isAanwezig = False
                for branch in branches:
                    if workId in branch.Instrumentversies:
                        isAanwezig = True
                        break
                if isAanwezig:
                    # Merge conflict opgelost door de versie op de branch te behouden, blijkbaar
                    continue
                self._Log.Fout ("BG versiebeheer merge (" + uitgevoerdOp + "): merge conflict niet opgelost, geen versie opgegeven voor instrument '" + workId + "'")
                succes = False

            elif teMergenVersie.IsJuridischUitgewerkt:
                # Er mag geen in werking zijnde versie voor dit instrument zijn
                versie = Versiebeheer.MaakInstrumentversie (nieuweInstrumentversies.get (workId))
                if not versie is None and not versie.IsJuridischInWerking ():
                    # De nieuwe versie is niet in werking
                    continue
                isAanwezig = False
                for branch in branches:
                    versie = branch.Instrumentversies.get (workId)
                    if not versie is None and versie.IsJuridischInWerking ():
                        isAanwezig = True
                        break
                if isAanwezig:
                    # Er is een versie na de uitgewerkte versie, dat kan niet.
                    self._Log.Fout ("BG versiebeheer merge (" + uitgevoerdOp + "): merge conflict niet opgelost, versie opgegeven voor instrument '" + workId + "' nadat het juridisch is uitgewerkt")
                    succes = False

        # Commit de nieuwe versies
        if not self.Commit (branches, nieuweInstrumentversies, None, uitgevoerdOp):
            succes = False

        # Ontvlechting/vervlechting registreren
        for workId, teMergenVersie in teMergenBranches.Instrumentversies.items ():
            for branch in branches:
                info = branch.Instrumentversies.get (workId)
                if not info is None:
                    # In principe gaat het om een vervlechting, maar als de te mergen
                    # versie geen initiële versie heeft, dan is er sprake van een 
                    # ontvlechting
                    if teMergenVersie.BestaatOfHeeftBestaan():
                        info.VervlochtenVersie.append (teMergenVersie)
                    else:
                        info.OntvlochtenVersie.append (teMergenVersie)

        return succes

#----------------------------------------------------------------------
#
# Unmerge: make de merge van de wijzigingen uit de head uit de branches, 
# los merge conflicts op en commit het resultaat naar de branches. 
# Dit is het ontvlechten van de wijzigingen uit andere branches in de simultaan beheerde
# branches.
#
#----------------------------------------------------------------------
    def Unmerge (self, teUnmergenBranches: Head, branches : List[Branch], nieuweInstrumentversies : Dict[str,InstrumentversieSpecificatie], uitgevoerdOp: str) -> bool:
        """Ontvlecht de wijzigingen uit de branches van de opgehaalde instrumentversies in de simultaan bijgehouden branches.

        Argumenten:

        teUnmergenBranches Head  De instrumentversies 
        branches Branch[]  Lijst van branches waarin de regelingversies verwerkt moeten worden. Als het meerdere branches zijn, dan wordt aangenomen dat
                           vanaf dit moment alle branches simultaan bijgehouden worden.
        nieuweInstrumentversies {}  Specificatie van de nieuwe instrumentversies die merge conflicten oplossen; mag None zijn
        uitgevoerdOp str Tijdstip waarop de nieuwe informatie in het versiebeheer wordt vastgelegd

        Geeft terug of de merge zonder fouten is uitgevoerd.
        """
        if teUnmergenBranches is None:
            return False
        succes = True

        # Controlerwn dat alle merge conflicts zijn opgelost is niet nodig
        # Het mag best voorkomen dat instrumentversies uit teUnmergenBranches niet in de branches
        # komen of dat er versies in branches staan die niet in teUnmergenBranches voorkomen of die 
        # daar juridisch uitgewerkt zijn. Er is (in deze simulator) niet na te gaan of alle wijzigingen 
        # uit teUnmergenBranches daadwerkelijk uit branches/nieuweInstrumentversies zijn verwijderd

        # Commit de nieuwe versies
        if not self.Commit (branches, nieuweInstrumentversies, None, uitgevoerdOp):
            succes = False

        # Ontvlechting registreren
        for workId, teUnmergenVersie in teUnmergenBranches.Instrumentversies.items ():
            for branch in branches:
                info = branch.Instrumentversies.get (workId)
                if not info is None:
                    info.OntvlochtenVersie.append (teUnmergenVersie)

        return succes
