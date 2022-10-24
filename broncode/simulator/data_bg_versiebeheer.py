#======================================================================
#
# Versiebeheer bij een bevoegd gezag.
#
#======================================================================
#
# Als de simulatie ook het projectmatig werken bij het bevoegd gezag
# simuleert, dan wordt voor het bevoegd gezag informatie over de
# voortgang van projecten en over het versiebeheer bijgehouden.
# In een productie-waardige applicatie zal deze informatie wellicht
# af te leiden zijn uit de gegevens van het onderliggende
# versiebeheersysteem.
#
# Deze applicatie biedt geen ondersteuning voor het consolideren zelf,
# d.w.z. het helpen van de eindgebruiker door aan te geven waar
# consolidatie nodig is. ook wordt niet naar de juridische correctheid
# van de projectacties gekeken. Het doel van de simulatie is uitsluitend
# om te verkennen welke consolidatie-informatie uitgewisseld moet worden
# en hoe mutaties opgesteld moeten worden.
#
#======================================================================

from typing import Dict, List, Tuple
from data_doel import Doel
from data_bg_project import Project, ProjectActie, Instrumentversie

#----------------------------------------------------------------------
#
# Versiebeheer: minimale informatie die in de bevoegd gezag software
#               bijgehouden moet worden c.q. opvraagbaar moet zijn.
#
#----------------------------------------------------------------------
class Versiebeheer:

    def __init__ (self):
        """Maak een nieuwe instantie van het versiebeheer bij het bevoegd gezag.
        """
        # Informatie over de status van de projecten
        # Key = code van project
        self.Projecten : Dict[str,Projectstatus] = {}
        # De resultaten van de projectacties, op volgorde van uitvoeren
        self.Projectacties : List[ProjectactieResultaat] = []
        # Informatie over alle doelen die door bevoegd gezag beheerd worden
        self.Branches : Dict[Doel,Branch] = {}
        # Alle workId van instrumenten die bij BG bekend zijn. Wijzigingen
        # voor deze works mogen alleen in projecten gedaan worden als het
        # work expliciet als te beheren instrument aan een branch is toegevoegd.
        self.BekendeInstrumenten = set ()
        # Alle gepubliceerde instrumentversies - deze versies hoeven niet
        # opnieuw uitgewisseld te worden (althans niet in deze simulator)
        self.PubliekeInstrumentversies = set ()

#======================================================================
#
# Projectverloop
#
#======================================================================

class Projectstatus:

    def __init__(self, project : Project):
        """Maak een nieuwe projectstatus aan
        
        Argumenten:

        project Project  Het project waarvoor de status wordt aangemaakt
        """
        self._Project = project
        # De branches waar in het project aan gewerkt wordt door het bevoegd gezag
        self.Branches : Dict[Doel,Branch] = {}
        # De branches waar in het project aan gewerkt wordt door een adviesbureau
        self.ExterneBranches : Dict[Doel,Branch] = {}

class UitgewisseldeSTOPModule:

    def __init__(self, module, van: str, naar: str):
        """Een STOP module die als onderdeel van de stap uitgewisseld wordt.
        Alleen gebruikt voor weergave.
        
        Argumenten:

        module object De STOP module(s) die voor deze actie uitgewisseld wordt
                      Instantie van een klasse die de methode self.ModuleXml() implementeert
        van str Ketenpartij die de module opstuurt
        naar str Ketenpartij die de module ontvangt
        """
        self.Module = module
        self.Van = van
        self.Naar = naar

class UitgewisseldMaarNietViaSTOP:

    def __init__(self):
        """Geeft aan dat er wel informatie uitgewisseld wordt, maar niet via STOP
        Alleen gebruikt voor weergave.
        """
        self.Module = self
        self.Van = ProjectactieResultaat._Uitvoerder_BevoegdGezag
        self.Naar = 'n.v.t.'

    def ModuleXml (self):
        return ['<!-- Informatie is niet in STOP uitgewisseld -->']

class ProjectactieResultaat:

    def __init__(self, projectactie):
        self._Projectactie : ProjectActie = projectactie
        # Degene die de actie heeft uitgevoerd: adviesbureau of bevoegd gezag
        self.UitgevoerdDoor = ProjectactieResultaat._Uitvoerder_BevoegdGezag
        # Parameters en data voor de actie; alleen voor weergave
        self.Data : List[Tuple[str,List[str]]] = []
        # Alleen voor weergave: de STOP module(s) die in de keten uitgewisseld worden
        self.Uitgewisseld : List[UitgewisseldeSTOPModule] = []

    _Uitvoerder_BevoegdGezag = 'Bevoegd gezag'
    _Uitvoerder_Adviesbureau = 'Adviesbureau'
    _Uitvoerder_LVBB = 'LVBB'

#======================================================================
#
#
#
#======================================================================

#----------------------------------------------------------------------
#
# Branch: informatie over alle instrumenten en tijdstempels voor 
#         een enkel doel.
#
#----------------------------------------------------------------------
class Branch:

    def __init__(self, doel : Doel):
        """Maak een nieuwe branch aan

        Argumenten:

        doel Doel  Instantie van het doel waar de branch voor aangemaakt is
        """
        self._Doel = doel
        # Geeft aan of de branch via projecten wordt beheerd. In deze simulator kan 
        # een branch ofwel via een project beheerd worden, ofwel geheel via 
        # ConsolidatieInformatie modules worden bestuurd. Voor de besturing via
        # projecten maakt het niet uit of dat door één of door meerdere projecten
        # gedaan wordt - het is dus mogelijk een naorog/redactie als apart project
        # op te nemen.
        self._ViaProject = False
        # Degene die op dit moment aan de branch werkt: adviesbureau of bevoegd gezag
        self.Uitvoerder = ProjectactieResultaat._Uitvoerder_BevoegdGezag
        # Als de branch een versie van regelgeving beschrijft die als uitgangssituatie
        # het resultaat van een ander doel heeft, dan is dat doel opgegeven als:
        self.Uitgangssituatie_Doel : 'Branch' = None
        # Als de branch een versie van regelgeving beschrijft die als uitgangssituatie
        # de publiek bekende geldende regelgeving heeft, dan is de datum waarop de
        # regelgeving geldig is gegeven als:
        self.Uitgangssituatie_GeldigOp = None
        # Als deze branch dezelfde juridischWerkendVanaf heeft als een andere branch,
        # dan bevat TreedtGelijktijdigInWerkingMet een lijst met alle tegelijk in werking
        # tredende branches.
        self.TreedtGelijktijdigInWerkingMet : List['Branch'] = None
        # De actuele (interne, binnen de creatie-keten) stand van de instrumentversies
        # key = work-Id
        self.InterneInstrumentversies : Dict[str,MomentopnameInstrument] = {}
        # De actuele (interne, binnen de creatie-keten) waarden van de tijdstempels
        self.InterneTijdstempels = MomentopnameTijdstempels (self)
        # De laatst gepubliceerde stand van de instrumentversies
        # key = work-Id
        self.PubliekeInstrumentversies : Dict[str,MomentopnameInstrument] = {}
        # De laatst gepubliceerde waarden van de tijdstempels
        self.PubliekeTijdstempels = MomentopnameTijdstempels (self)

#----------------------------------------------------------------------
#
# MomentopnameInstrument: informatie over de versie van een instrument 
#                         als gevolg van alle acties in het project.
#
#----------------------------------------------------------------------
class MomentopnameInstrument:

    def __init__(self, branch : Branch, workId : str):
        """Maak een nieuwe momentopname voor een instrument. Nadat de momentopname is
        gemaakt worden de waarden ervan steeds overschreven.

        Argumenten:

        branch Branch  Instantie van de branch waar de momentopname voor aangemaakt is
        workId string  Work-identificatie van het instrument waarvan dit de momentopname is
        """
        self._Branch = branch
        self._WorkId = workId
        # ExpressionId van de instrumentversie
        # Als IsJuridischUitgewerkt True of IsTeruggetrokken True is, dan is de waarde None. Anders is het de waarde
        # zoals opgegeven of (als er geen waarde is opgegeven) de waarde afgeleid van de uitgangssituatie.
        # Als de ExpressionId in dat geval None is gaat het om een onbekende versie.
        self.ExpressionId = None
        # Geeft aan of de instrumentversie juridisch uitgewerkt is (dus ingetrokken is/moet worden)
        self.IsJuridischUitgewerkt = False
        # Geeft aan of een wijziging van het instrument geen onderdeel (meer) is van het eindbeeld voor het doel
        self.IsTeruggetrokken = True
        # De vertaling van de uitgangssituatie van de branch naar momentopnamen voor dit instrument.
        # De uitgangssituatie moet als was in een was-wordt RegelingMutatie gebruikt worden.
        # Dit is None voor een initiële versie.
        self.Uitgangssituatie : List[MomentopnameVerwijzing] = None
        # Tijdstip van de laatste uitwisseling ter publicatie van de instrumentversie
        # Deze waarde is None als de MomentopnameInstrument deel is van de InterneInstrumentversies
        # op de branch, en niet None als onderdeel van PubliekeInstrumentversies
        self.GemaaktOp = None
        # Als de wijzigingen uit een specifieke branch (anders dan de uitgangssituatie) zijn 
        # overgenomen sinds de laatste uitwisseling ter publicatie, dan worden die in VervlochtenMet 
        # vermeld. Een verandering van de uitgangssituatie wordt hier niet vermeld.
        # Deze waarde is None als de MomentopnameInstrument deel is van de PubliekeInstrumentversies
        self.VervlochtenMet : List['MomentopnameInstrument']
        # Als de wijzigingen uit een specifieke branch (anders dan de uitgangssituatie) zijn 
        # verwijderd sinds de laatste uitwisseling ter publicatie, dan worden die in OntvlochtenMet 
        # vermeld. Een verandering van de uitgangssituatie wordt hier niet vermeld.
        # Deze waarde is None als de MomentopnameInstrument deel is van de PubliekeInstrumentversies
        self.OntvlochtenMet : List['MomentopnameInstrument']
        # Versie geeft een indicatie van het aantal wijzigingen van het instrument op de branch.
        # Wordt gebruikt om te detecteren of de inhoud van de momentopname is gewijzigd.
        # Wordt ook gebruikt bij verwijzingen naar deze momentopname om te borgen dat de inhoud van
        # deze momentopname niet is gewijzigd sinds het aanmaken van de verwijzing. Preciezer: dat
        # als de verwijzing bij een publicatie wordt omgezet in een STOP-verwijzing, de STOP-verwijzing
        # naar inhoud verwijst die gelijk is aan de inhoud van de momentopname bij het aanmaken van de
        # interne verwijzing.
        self.Versie = 0

    def ActueleExpressionId (self):
        """Geef de instrumentversie zoals die op dit moment is voor de branch.

        Argumenten:

        momentopname MomentopnameInstrument Momentopname waar de ongewijzigde versie voor bepaald moet worden

        Geeft None terug als er geen versie is, '-' als het instrument juridisch uitgewerkt is, '?' voor onbekende
        of niet uniek bepaalde versies, en anders de expression-identificatie.
        """
        if self.IsJuridischUitgewerkt:
            return '-'
        if not self.IsTeruggetrokken:
            return self.WorkId + ': onbekend' if self.ExpressionId is None else self.ExpressionId
        if self.Uitgangssituatie is None:
            # Initiële versie
            return None
        if self.Uitgangssituatie[0].Momentopname.ExpressionId is None:
            # Onbekende versie of misschien ook wel geen eenduidige versie
            return self.WorkId + ': onbekend?'
        if len (self.Uitgangssituatie) > 1:
            if len (set (v.Momentopname.ExpressionId for v in self.Uitgangssituatie)) > 1:
                # Geen eenduidige versie
                return self.WorkId + ': ?'
        return self.Uitgangssituatie[0].Momentopname.ExpressionId

    def IsGepubliceerd (self, gemaaktOp : str, isConceptOfOntwerp : bool):
        """Markeert deze momentopname als gepubliceerd en maakt een nieuwe instantie die 
        die de acties in het interne versiebeheer in het creatieproces volgt. Het uitwisselen 
        van een revisie wordt in dit verband ook als een publicatie gezien.

        Argumenten:

        gemaaktOp string  Tijdstip voor de uitwisseling die voor de publicatie gebruikt wordt.
        isConceptOfOntwerp bool  Geeft aan of de publicatie een concept, ontwerp of revisie betreft in plaats van een
                                 bekendmaking van een vastgesteld besluit, mededeling uitspraak rechter of
                                 rectificatie van een van deze, of van een revisie van de de geconsolideerde regelgeving.
        """
        self.GemaaktOp = gemaaktOp
        self.VervlochtenMet = None
        self.OntvlochtenMet = None
        self._Branch.PubliekeInstrumentversies[self._WorkId] = self

        # Maak een nieuwe momentopname voor de volgende wijzigingen
        nieuweVersie = MomentopnameInstrument (self._Branch, self._WorkId)
        nieuweVersie.ExpressionId = self.ExpressionId
        nieuweVersie.IsJuridischUitgewerkt = self.IsJuridischUitgewerkt
        nieuweVersie.IsTeruggetrokken = self.IsTeruggetrokken
        nieuweVersie.Uitgangssituatie = self.Uitgangssituatie
        nieuweVersie.Versie = self.Versie
        self._Branch.InterneInstrumentversies[self._WorkId] = nieuweVersie

class MomentopnameVerwijzing:

    def __init__ (self, momentopname: MomentopnameInstrument):
        """Maak een verwijzing naar een momentopname aan

        Argumenten:

        momentopname MomentopnameInstrument  Momentopname waarnaar verwezen wordt
        """
        self.Momentopname = momentopname
        # Bewaar het versienummer als vingerafdruk van de inhoud van de momentopname
        self.Versie = momentopname.Versie

#----------------------------------------------------------------------
#
# MomentopnameTijdstempels: informatie over de tijdstempels voor een
#                           doel als gevolg van alle acties in het project.
#
#----------------------------------------------------------------------
class MomentopnameTijdstempels:

    def __init__(self, branch : Branch):
        """Maak een nieuwe momentopname voor de tijdstempels. Nadat de momentopname is
        gemaakt worden de waarden ervan steeds overschreven.

        Argumenten:

        branch Branch  Instantie van de branch waar de momentopname voor aangemaakt is
        """
        self._Branch = branch
        # De waarde van de juridischWerkendVanaf tijdstempel, of None als die niet gezet is.
        self.JuridischWerkendVanaf = None
        # De waarde van de geldigVanaf tijdstempel, of None als die niet gezet is.
        self.GeldigVanaf = None
        # Versie geeft een indicatie van het aantal wijzigingen van het instrument op de branch.
        # Wordt gebruikt om te detecteren of de inhoud van de momentopname is gewijzigd.
        self.Versie = 0

    def IsGepubliceerd (self):
        """Markeert deze momentopname als gepubliceerd en maakt een nieuwe instantie die 
        die de acties in het interne versiebeheer in het creatieproces volgt. Het uitwisselen 
        van een revisie wordt in dit verband ook als een publicatie gezien.
        """
        self._Branch.PubliekeTijdstempels = self
        # Maak een nieuwe momentopname voor de volgende wijzigingen
        nieuweVersie = MomentopnameTijdstempels (self._Branch)
        nieuweVersie.JuridischWerkendVanaf = self.JuridischWerkendVanaf
        nieuweVersie.GeldigVanaf = self.GeldigVanaf
        nieuweVersie.Versie = self.Versie
        self._Branch.InterneTijdstempels = nieuweVersie
