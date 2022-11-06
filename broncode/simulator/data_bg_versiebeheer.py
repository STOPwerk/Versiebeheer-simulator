#======================================================================
#
# Versiebeheer bij een bevoegd gezag.
#
#======================================================================
#
# De bevoegd gezag software zal moeten beschikken over een intern 
# versiebeheer dat tenminste een bepaalde hoeveelheid informatie
# bevat (of kan afleiden). Deze module bevat het datamodel voor
# het interne versiebeheer voor deze applicatie.
#
# Het datamodel kent geen historie; projectacties overschrijven
# oude informatie. In deze applicatie wordt er na elke projectactie
# wel een kloon gemaakt, maar dat is alleen voor de weergave van de
# resultaten en dus applicatie-specifiek. 
#
#======================================================================

from typing import Dict, List
from data_doel import Doel

#----------------------------------------------------------------------
#
# Versiebeheer: minimale informatie die in de bevoegd gezag software
#               bijgehouden moet worden c.q. afleidbaar moet zijn.
#
#----------------------------------------------------------------------
class Versiebeheer:

    def __init__ (self):
        """Maak een nieuwe instantie van het versiebeheer bij het bevoegd gezag.
        """
        # Informatie over alle doelen die door bevoegd gezag beheerd worden
        self.Branches : Dict[Doel,Branch] = {}
        # De consolidaties van elk bekend instrument
        # Key = work-id
        self.Consolidaties : Dict[str,Consolidatie] = {}
        # Alle gepubliceerde instrumentversies - deze versies hoeven niet
        # opnieuw uitgewisseld te worden (althans niet in deze simulator)
        self.PubliekeInstrumentversies = set ()

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
        # De lijst met momentopnamen (de meest recente van elke branch) die in deze instrumentversie
        # zijn verwerkt.
        self.MetBijdragenVan : List[MomentopnameVerwijzing] = []
        # De lijst met momentopnamen (de meest recente van elke branch) waarvan de wijzigingen
        # ooit wel maar nu niet meer in deze instrumentversie verwerkt zijn.
        self.ZonderBijdragenVan : List[MomentopnameVerwijzing] = []
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

#----------------------------------------------------------------------
#
# Consolidatie: consolidatie van een instrument.
#
#----------------------------------------------------------------------
class Consolidatie:

    def __init__(self, workId : str):
        """Maak een nieuwe consolidatie aan voor een instrument

        Argumenten:

        workId string  Work-identificatie van het instrument
        """
        self._WorkId = workId
        # Lijst met versies (toestanden) die nu of in de toekomst geldig zijn,
        # gesorteerd op oplopende juridischWerkendVanaf datum
        self.Versies : List[Consolidatieversie] = []

#----------------------------------------------------------------------
#
# Consolidatieversie: status van de consolidatie (van een instrument)
#                     op een bepaalde datum. BG-equivalent van een
#                     toestand.
#
#----------------------------------------------------------------------
class Consolidatieversie:

    def __init__(self, juridischWerkendVanaf : str):
        """Maak een nieuw overzicht aan van de status van de consolidatie
        voor een specifieke inwerkingtredingsdatum

        Argumenten:

        juridischWerkendVanaf  string  Datum waarop een nieuwe versie van een
                                       geconsolideerd instrument ontstaat.
        """
        self.JuridischWerkendVanaf = juridischWerkendVanaf
        # De doelen die aanleiding geven tot het ontstaan van deze consolidatie
        self.Inwerkingtredingsdoelen : List[Doel] = []
        # ExpressionId van de instrumentversie, indien bekend
        self.ExpressionId = None
        # Geeft aan of het instrument juridisch uitgewerkt is
        self.IsJuridischUitgewerkt = False
        # Geeft aan dat deze consolidatie ontstaat nadat het instrument al juridisch uitgewerkt is
        self.WijzigingNaIntrekking = False
        # Als er niet één versie voor het instrument wordt gespecificeerd, dan:
        # per versie de doelen die de versie 
        self.TegenstrijdigeVersies : Dict[str, List[Doel]] = {}
        # Als de consolidatie op een eerder moment wijzigt doordat een nieuwe instrumentversie
        # wordt opgegeven, dan moet deze consolidatie bijgewerkt worden.
        # De doelen van die eerdere consolidatie staan in:
        self.TeVervlechtenMet: List[Doel] = []
        # Als de consolidatie op een eerder moment komt te vervallen omdat er op dat moment
        # geen wijziging meer optreedt, dan moet deze consolidatie bijgewerkt worden.
        # De doelen van die eerdere consolidatie staan in:
        self.TeOntvlechtenMet: List[Doel] = []

