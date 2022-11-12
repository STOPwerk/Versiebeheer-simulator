#======================================================================
#
# Simulatie van de consolidatie zoals de software van het bevoegd
# gezag die uit kan voeren op basis van het interne versiebeheer.
#
#======================================================================
#
# Het bevoegd gezag zal de consolidatie in het algemeen uit moeten
# voeren op basis van het interne versiebeheer, inclusief alle
# versies die nog niet gepubliceerd zijn. De eindgebruiker heeft dan
# de gelegenheid om problemen te verhelpen en een correcte consolidatie
# met de LVBB uit te wisselen.
#
#======================================================================

from typing import Dict
from data_bg_versiebeheer import Versiebeheer, Branch, InstrumentInformatie, Consolidatie, GeconsolideerdeVersie, Instrumentversie

class Consolideren:

    @staticmethod
    def VoerUit (versiebeheer : Versiebeheer, vandaag : str):
        """Voer de consolidatie uit op basis van het interen versiebeheer

        Argumenten:

        versiebeheer Versiebeheer het interne versiebeheer van het bevoegd gezag
        vandaag str datum of tijdstip van vandaag = heden
        """
        Consolideren ()._VoerUit (versiebeheer, vandaag[0:10])

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
    def __init__(self):
        """Maak de consolidatie-maker aan"""
        # Index om de consolidatie voor een branch te vinden die eerder in werking is getreden
        self._BranchConsolidatie : Dict[Branch,Consolidatie] = {}

    def _VoerUit (self, versiebeheer : Versiebeheer, vandaag : str):
        """Voer de consolidatie uit

        Argumenten:

        versiebeheer Versiebeheer het interne versiebeheer van het bevoegd gezag
        vandaag str datum of tijdstip van vandaag = heden
        """
        # Maak de consolidaties voor de verschillende inwerkingtredingsmomenten aan
        # De simulator maakt de consolidatie ook voor historische versies aan,
        # omdat er geen garantie is dat de nu geldende versie altijd volledig
        # geconsolideerd is. In productie-waardige software zal er een proces zijn
        # (met terugmelding naar eindgebruikers) voor het geval een consolidatie in de 
        # nabije toekomst niet compleet is. De status van de consolidatie van de 
        # nu geldende versie wordt dan op een andere manier bijgehouden. In dat geval 
        # volstaat het om alleen de consolidatie te bepalen van de nu en in de 
        # toekomst geldende regelgeving.
        consolidaties : Dict[str,Consolidatie] = {}
        jwvNuGeldendeRegelgeving = None
        for branch in versiebeheer.Branches.values ():
            if not branch.Tijdstempels.JuridischWerkendVanaf is None:
                consolidatie = consolidaties.get (branch.Tijdstempels.JuridischWerkendVanaf)
                if consolidatie is None:
                    consolidaties[branch.Tijdstempels.JuridischWerkendVanaf] = consolidatie = Consolidatie (branch.Tijdstempels.JuridischWerkendVanaf)
                    if jwvNuGeldendeRegelgeving is None or jwvNuGeldendeRegelgeving <= vandaag:
                        jwvNuGeldendeRegelgeving = vandaag
                consolidatie.Branches.append (branch)
        versiebeheer.Consolidatie = [consolidaties[jvw] for jvw in sorted (consolidaties.keys ())]

        # Bepaal de geconsolideerde versies en de status van de consolidatie
        vorigeConsolidatie : Consolidatie = None
        for consolidatie in versiebeheer.Consolidatie:
            # Nu of in de toekomst geldig?
            consolidatie.IsActueel = consolidatie.JuridischGeldigVanaf >= jwvNuGeldendeRegelgeving

            # Bepaal de instrumenten die nu bekend zijn
            instrumentenNu = set ()
            for branch in consolidatie.Branches:
                instrumentenNu.update (branch.Instrumentversies.keys ())
            vorigeVersies : Dict[str,GeconsolideerdeVersie] = {}
            alleInstrumenten = set (instrumentenNu)
            if not vorigeConsolidatie is None:
                vorigeVersies = vorigeConsolidatie.Instrumentversies
                alleInstrumenten.update (vorigeVersies.keys ())
            for workId in alleInstrumenten:
                if workId in instrumentenNu:
                    # Bepaal de geconsolideerde versie
                    consolidatie.Instrumentversies[workId] = versie = GeconsolideerdeVersie ()
                    if not self._BepaalInstrumentversie (vorigeVersies.get (workId), versie, { branch: branch.Instrumentversies.get (workId) for branch in consolidatie.Branches}):
                        consolidatie.Status = Consolidatie._Status_Incompleet
                else:
                    # Neem de vorige versie over
                    consolidatie.Instrumentversies[workId] = vorigeVersies[workId]


            # Uitstaande uitwisselingen?
            self._BepaalUitwisselingVereist (consolidatie)

            # Nog wijzigingen uit voorgaande branches verwijderen of verwerken?
            self._BepaalStatus (vorigeConsolidatie, consolidatie)

            # Voorbereiding voor volgende consolidatie
            for branch in consolidatie.Branches:
                self._BranchConsolidatie[branch] = consolidatie
            vorigeConsolidatie = consolidatie

    def _BepaalInstrumentversie (self, vorigeVersie : GeconsolideerdeVersie, consolidatie: GeconsolideerdeVersie, instrumentversies: Dict[Branch,InstrumentInformatie]) -> bool:
        """Bepaal de consolidatie van een instrument en geef terug of de consolidatie valide is"""
        # Is het instrument juridisch uitgewerkt?
        consolidatie.IsJuridischUitgewerkt = False if vorigeVersie is None else vorigeVersie.IsJuridischUitgewerkt
        for instrumentinfo in instrumentversies.values():
            if not instrumentinfo is None and instrumentinfo.Instrumentversie.IsJuridischUitgewerkt:
                consolidatie.IsJuridischUitgewerkt = True
        for instrumentinfo in instrumentversies.values():
            if not instrumentinfo is None and not instrumentinfo.Instrumentversie.IsJuridischUitgewerkt and instrumentinfo.IsGewijzigd:
                # Er is een instrumentversie opgegeven, maar het instrument bestaat niet meer
                consolidatie.WijzigingNaIntrekking = True
                # Niet geïnteresseerd in andere controles
                return False
        # Alle instrumentversies moeten nu hetzelfde zijn voor alle doelen
        consolidatie.TegenstrijdigeVersies = {}
        heeftTegenstrijdigeVersies = False
        for branch, instrumentinfo in instrumentversies.items ():
            if instrumentinfo is None or not instrumentinfo.IsGewijzigd:
                expressionId = '(geen instrumentversie gespecificeerd)'
                heeftTegenstrijdigeVersies = True # Dit is nooit goed
            elif instrumentinfo.Instrumentversie.ExpressionId is None:
                expressionId = '(onbekende instrumentversie)'
            else:
                consolidatie.ExpressionId = expressionId = instrumentinfo.Instrumentversie.ExpressionId
                consolidatie._Instrumentversie = instrumentinfo.Instrumentversie
            lijst = consolidatie.TegenstrijdigeVersies.get (expressionId)   
            if lijst is None:
                consolidatie.TegenstrijdigeVersies[expressionId] = lijst = []
            lijst.append (branch)
        heeftTegenstrijdigeVersies = heeftTegenstrijdigeVersies or len (consolidatie.TegenstrijdigeVersies) > 1
        if not heeftTegenstrijdigeVersies:
            consolidatie.TegenstrijdigeVersies = None
            return True
        else:
            consolidatie.ExpressionId = None
            consolidatie._Instrumentversie = None
            return False

    def _BepaalUitwisselingVereist (self, consolidatie: Consolidatie):
        """Ga na of er nog uitwisselingen te doen zijn"""
        for branch in consolidatie.Branches:
            if not branch.Tijdstempels.IsGelijkAan (branch.UitgewisseldeTijdstempels):
                if consolidatie.UitwisselingVereist is None:
                    consolidatie.UitwisselingVereist = []
                consolidatie.UitwisselingVereist.append (branch._Doel)
                continue
            for instrumentinfo in branch.Instrumentversies.values ():
                if not Instrumentversie.ZijnGelijk (instrumentinfo.Instrumentversie, instrumentinfo.UitgewisseldeVersie):
                    if consolidatie.UitwisselingVereist is None:
                        consolidatie.UitwisselingVereist = []
                    consolidatie.UitwisselingVereist.append (branch._Doel)
                    break

    def _BepaalStatus (self, vorigeConsolidatie: Consolidatie, consolidatie: Consolidatie):
        """Bepaal de status van de consolidatie"""
        teVervlechten = set () if vorigeConsolidatie else set (b._Doel for b in vorigeConsolidatie.Branches) # Zonder tegenbericht alle branches van de voorgaande consolidatie
        teOntvlechten = set ()
        for branch in consolidatie.Branches:
            if not branch.Uitgangssituatie_LaatstGewijzigdOp is None:
                for uitgangsBranch, laatstGewijzigd in branch.Uitgangssituatie_LaatstGewijzigdOp:
                    teVervlechten.remove (uitgangsBranch._Doel) # weghalen branch van voorgaande consolidatie
                    if uitgangsBranch in consolidatie.Branches:
                        # Evt fouten worden op instrumentniveau gedetecteerd
                        pass
                    elif not uitgangsBranch in self._BranchConsolidatie:
                        # Uitgangssituatie treedt niet of later in werking
                        teOntvlechten.add (uitgangsBranch._Doel)
                    elif uitgangsBranch.LaatstGewijzigdOp != laatstGewijzigd:
                        # Eerder uitgangspunt
                        teVervlechten.add (uitgangsBranch._Doel)

        if len (teVervlechten) > 0:
            consolidatie.TeVervlechtenMet = list (sorted (teVervlechten, key = lambda x: str(x)))
            consolidatie.Status = Consolidatie._Status_Incompleet
        if len (teOntvlechten) > 0:
            consolidatie.TeOntvlechtenMet = list (sorted (teOntvlechten, key = lambda x: str(x)))
            consolidatie.Status = Consolidatie._Status_Incompleet

        if not vorigeConsolidatie is None:
            if consolidatie.Status == Consolidatie._Status_Compleet and vorigeConsolidatie.IsActueel and vorigeConsolidatie.Status != Consolidatie._Status_Compleet:
                # De vorige consolidatie moet nog aangepast worden, en dan verandert deze ook nog
                consolidatie.Status = Consolidatie._Status_CompleetMaarEerdereNiet
        if not consolidatie.IsActueel:
            if consolidatie.Status != Consolidatie._Status_Compleet:
                consolidatie.Status = Consolidatie._Status_IncompleetHistorisch
