#======================================================================
#
# Data voor het aanmaken van een webpagina die alle beschikbare
# resultaten laat zien van het consolidatie proces uit 
# proces_consolidatie.py.
#
#----------------------------------------------------------------------
#
# Het consolidatieproces voert de consolidatie na elke uitwisseling
# uit. Daarbij wordt (conform ST) niet altijd bijgehouden welke
# informatie uit welke uitwisseling ontstaat. Om op de webpagina
# toch de resultaten per uitwisseling te kunnen tonen, wordt na elke
# uitwisseling een snapshot gemaakt met data voor de resultaatweergave
# van de data die later nog kan wijzigen.
#
#======================================================================
from typing import List, Dict, Set, Tuple

from data_doel import Doel
from data_proefversie import Proefversie
from data_versiebeheerinformatie import Uitwisseling
from proces_tijdreisfilter import Filter_CompleteToestanden, Filtervoorschrift
from stop_completetoestanden import CompleteToestanden, Toestand
from stop_proefversies import Proefversies
from weergave_data_toestanden import Toestand
from weergave_data_stop_uitwisseling import STOPModuleSnapshot, STOPModuleUitwisseling

#----------------------------------------------------------------------
#
# Collectie van alle data
#
#----------------------------------------------------------------------
class WeergaveData:
    def __init__ (self, scenario):
        """Maak een nieuwe instantie aan
        
        Argumenten:
        scenario Scenario  Het scenario waar de resultaten voor getoond worden
        """
        self.Scenario = scenario
        # Resultaten per instrument
        # key = workId
        self.InstrumentData : Dict[str,List[InstrumentData]] = {}
        # Bewaar voor elk doel de eerste datum juridischWerkendVanaf en
        # de eerste gemaaktOp van aanlevering, om een volgorde van de doelen
        # voor de illustraties en voor korte naamgeving te maken.
        # value = eerste gemaaktOp
        self._DoelEersteGemaaktOp : Dict[Doel,str] = {}
        # value = eerste juridischWerkendVanaf
        self._DoelEersteJuridischWerkendVanaf : Dict[Doel,str]= {}
        # Symbolen en namen van de doelen
        # Gesorteerde lijst met (doel, letter)
        self._DoelSymbool : List[Tuple[Doel,str]] = None
        # Uniek ID voor een toestand, zodat dezelfde toestand in alle weergaven herkend kan worden.
        # Laatst uitgegeven waarde
        self._LaatsteToestandUniekId = 0
        # Uniek ID voor een actuele toestand, als bepaald op basis van de informatie in de complete toestanden
        # key = toestandidentificatie, value = uniek ID (int)
        self._ActueleToestandUniekId : Dict[str,int] = {}
        # Uniek ID voor alle elementen die een uniek ID moeten krijgen zodat ze in de verschillende 
        # overzichten als hetzelfde herkend kunnen worden
        self._LaatsteUniekId = 0

    def UitwisselingNaam (self, gemaaktOp : str):
        """Geef de volledige naam van de uitwisseling
        
        Argumenten:
        
        gemaaktOp string  Tijdstip van uitwisseling
        """
        for uitwisseling in self.Scenario.Opties.Uitwisselingen:
            if uitwisseling.GemaaktOp == gemaaktOp:
                return gemaaktOp + ' (' + uitwisseling.Naam + ')'
        return gemaaktOp


    def WerkBij (self, uitwisseling : Uitwisseling, instrumentWorkId : Set[str], alleDoelen : Set[Doel], proefversies : Dict[str, List[Proefversie]], uitgewisseldeModules : List[STOPModuleUitwisseling]):
        """Werk de gegevens voor presentatie bij.

        Argumenten:
        uitwisseling Uitwisseling  De uitwisseling waarvoor de gegevens bijgewerkt moeten worden
        instrumentWorkId string[]  Work-id van de instrumenten die in deze uitwisseling geraakt zijn.
        alleDoelen string[]  Een set van alle doelen waarvoor informatie is aangeleverd
        proefversies {} key = work-ID van de instrumenten, value = lijst met proefversies
        uitgewisseldeModules STOPModuleUitwisseling[]  De lijst met STOP modules die op dit moment uitgewisseld worden
        """
        if self.Scenario.Opties.Applicatie_Resultaat:
            for branch in self.Scenario.Versiebeheerinformatie.Tijdstempels.values ():
                if len(branch.Momentopnamen) > 0:
                    if not branch.Doel in self._DoelEersteJuridischWerkendVanaf:
                        if not branch.Momentopnamen[-1].JuridischWerkendVanaf is None:
                            self._DoelEersteJuridischWerkendVanaf[branch.Doel] = branch.Momentopnamen[-1].JuridischWerkendVanaf
            for idx, doel in enumerate (alleDoelen):
                if not doel in self._DoelEersteGemaaktOp:
                    self._DoelEersteGemaaktOp[doel] = uitwisseling.GemaaktOp + "{:03d}".format (idx)

            # Informatie over instrumenten
            for workId in sorted (instrumentWorkId): # Volgorde ivm weergave op resultaatpagina
                data = self.InstrumentData.get (workId)
                if data is None:
                    self.InstrumentData[workId] = data = InstrumentData (self, workId)
                else:
                    data.Uitwisselingen[-1].VolgendeGemaaktOp = uitwisseling.GemaaktOp
                self._LaatsteUniekId += 1
                data.Uitwisselingen.append (InstrumentUitwisseling (str(self._LaatsteUniekId), data, uitwisseling, workId, proefversies.get (workId), uitgewisseldeModules))

            # Proefversie module
            if len (proefversies) > 0:
                module = Proefversies ()
                module.BekendOp = uitwisseling.BekendOp
                module.OntvangenOp = uitwisseling.OntvangenOp
                for workId in sorted (proefversies.keys ()):
                    module.Proefversies.extend (sorted (proefversies[workId], key = lambda p: p.Instrumentversie))
                uitgewisseldeModules.append (STOPModuleUitwisseling (
                    STOPModuleUitwisseling.Systeem_LVBB,
                    STOPModuleUitwisseling.Systeem_LVBBAfnemer,
                    module))

    def Branches (self, doelen : List[Doel]):
        """Geeft de volgorde waarin de doelen getoond moeten worden, en het symbool voor het tonen van het doel.

        Argumenten:

        doelen Doel[] Relevante doelen (lijst van instanties van Doel)

        Geeft een geordende lijst terug van (doel, symbool)
        """
        self._MaakDoelSymbool ()

        # Filter de doelen op de relevante doelen
        return [(doel, letter) for doel,letter in self._DoelSymbool if doel in doelen] 

    def DoelLetter (self, doel : Doel):
        """Geeft de letter die voor het doel gebruikt wordt in de weergave

        Argumenten:

        doel Doel  Identificatie van het doel
        """
        self._MaakDoelSymbool ()
        for d, letter in self._DoelSymbool:
            if d == doel:
                return letter

    def _MaakDoelSymbool (self):
        """Maak _DoelSymbool aan"""
        if self._DoelSymbool is None:
            # Sorteer de doelen eerst op eerste datum juridischWerkendVanaf, dan op datum eerste uitwisseling
            volgorde = []
            for doel, gemaaktOp in self._DoelEersteGemaaktOp.items ():
                jwv = self._DoelEersteJuridischWerkendVanaf.get (doel)
                volgorde.append (( doel, ('AAAA-AA-AA' if jwv is None else jwv) + gemaaktOp ))
            volgorde.sort (key = lambda key: key[1])

            # Ken letters toe aan de symbolen
            self._DoelSymbool = []
            for idx, doel in enumerate (volgorde):
                letter = ''
                id = idx
                while True:
                    frac = id % 26
                    letter = chr (ord('A') + frac) + letter
                    id = (id - frac) / 26
                    if id == 0:
                        break
                self._DoelSymbool.append ((doel[0], letter))

#----------------------------------------------------------------------
#
# Data voor een uitwisseling
#
#----------------------------------------------------------------------
class UitwisselingData:

    def __init__ (self, weergaveData : WeergaveData, uitwisseling : Uitwisseling, instrumentWorkId):
        """Maak een nieuwe instantie aan

        Argumenten:
        weergaveData WeergaveData  Eigenaar van de uitwisselingdata
        uitwisseling Uitwisseling  De uitwisseling waarvoor de gegevens bijgewerkt moeten worden
        instrumentWorkId string[]  Work-id van de instrumenten die in deze uitwisseling geraakt zijn.
        """
        self.WeergaveData = weergaveData
        self.GemaaktOp = uitwisseling.GemaaktOp
        self.Naam = None
        for u in self.WeergaveData.Scenario.Opties.Uitwisselingen:
            if u.GemaaktOp == self.GemaaktOp:
                self.Naam = u.Naam
                break
        self.InstrumentWorkId = instrumentWorkId

#----------------------------------------------------------------------
#
# Data voor een instrument
#
#----------------------------------------------------------------------
class InstrumentData:

    def __init__ (self, weergaveData : WeergaveData, workId):
        """Maak een nieuwe instantie aan

        Argumenten:
        weergaveData WeergaveData  Eigenaar van de uitwisselingdata
        workId string  Work-id van het instrument waarvoor de gegevens bewaard moeten worden
        """
        self.WeergaveData = weergaveData
        self.WorkId = workId
        # Geeft aan of er proefversies zijn gemaakt
        self.HeeftProefversies = False
        # Geeft aan of er actuele toestanden zijn gemaakt
        self.HeeftActueleToestanden = False
        # Geeft aan of er complete toestanden zijn gemaakt
        self.HeeftCompleteToestanden = False
        # De uitwisselingen voor dit instrument
        # Lijst met instanties van InstrumentUitwisseling
        self.Uitwisselingen = []

#----------------------------------------------------------------------
#
# Data voor een uitwisseling die een instrument raakt
#
#----------------------------------------------------------------------
class InstrumentUitwisseling:

    def __init__ (self, uniekId : str, instrumentData : InstrumentData, uitwisseling : Uitwisseling, workId, proefversies : List[Proefversie], uitgewisseldeModules : List[STOPModuleUitwisseling]):
        """Maak een nieuwe instantie aan

        Argumenten:
        uniekId string  Uniek ID voor deze uitwisseling
        instrumentData InstrumentData  De algemene data voor het instrument
        uitwisseling Uitwisseling  De uitwisseling waarvoor de gegevens bijgewerkt moeten worden
        workId string  Work-id van het instrument waarvoor de gegevens bewaard moeten worden
        proefversies Proefversie[] lijst met proefversies, of None als ze er niet zijn
        uitgewisseldeModules STOPModuleUitwisseling[]  De lijst met STOP modules die op dit moment uitgewisseld worden
        """
        self._UniekId = uniekId
        self._Uitwisseling = uitwisseling
        self.InstrumentData = instrumentData
        self.GemaaktOp = uitwisseling.GemaaktOp
        self.Naam = None
        for u in  self.InstrumentData.WeergaveData.Scenario.Opties.Uitwisselingen:
            if u.GemaaktOp == self.GemaaktOp:
                self.Naam = u.Naam
                break
        # Actuele toestanden resulterend na verwerking van de uitwisseling
        self.ActueleToestanden = None
        # Complete toestanden resulterend na verwerking van de uitwisseling
        self.CompleteToestanden = None
        # Geheugen voor de resultaten van de tijdreisfilters
        # Key = code voor tijdreis, value = instantie van Filtervoorschrift
        self._CompleteToestanden = None
        # GemaaktOp van de volgende uitwisseling
        self.VolgendeGemaaktOp = None

        consolidatie = self.InstrumentData.WeergaveData.Scenario.GeconsolideerdeInstrument (workId)

        # Proefversies voor het instrument
        # Lijst met instanties van Proefversie
        self.Proefversies = proefversies
        if not proefversies is None:
            for proefversie in proefversies:
                if not hasattr (proefversie, '._UniekId'):
                    instrumentData.HeeftProefversies = True
                    # Unieke ID voor proefversies en annotaties
                    self.InstrumentData.WeergaveData._LaatsteUniekId += 1
                    proefversie._UniekId = str(self.InstrumentData.WeergaveData._LaatsteUniekId)
                    for annotatie in proefversie.Annotaties.values ():
                        if not hasattr (annotatie, '._UniekId'):
                            self.InstrumentData.WeergaveData._LaatsteUniekId += 1
                            annotatie._UniekId = str(self.InstrumentData.WeergaveData._LaatsteUniekId)

        bewaarJuridischeVerantwoording = False

        if not consolidatie.CompleteToestanden is None and len (consolidatie.CompleteToestanden.Toestanden) > 0:
            instrumentData.HeeftCompleteToestanden = True

            # In deze applicatie wordt de selectie van toestanden voor weergave op basis van 
            # toestandeigenschappen gedaan. Het maken van een shallow kopie is voldoende.
            self.CompleteToestanden = CompleteToestanden ()
            self.CompleteToestanden.OntvangenOp = consolidatie.CompleteToestanden.OntvangenOp
            self.CompleteToestanden.BekendOp = consolidatie.CompleteToestanden.BekendOp
            self.CompleteToestanden.MaterieelUitgewerktOp = consolidatie.CompleteToestanden.MaterieelUitgewerktOp
            self.CompleteToestanden.ToestandIdentificatie = consolidatie.CompleteToestanden.ToestandIdentificatie
            self.CompleteToestanden.ToestandInhoud = consolidatie.CompleteToestanden.ToestandInhoud
            self.CompleteToestanden.Toestanden = consolidatie.CompleteToestanden.Toestanden
            bewaarJuridischeVerantwoording = True
            # Bewaar ook de relevante doelen
            self.DoelenCompleteToestanden = set()
            for identificatie in consolidatie.CompleteToestanden.ToestandIdentificatie:
                for doel in identificatie.Inwerkingtredingsdoelen:
                    self.DoelenCompleteToestanden.add (doel)

            # Deel unieke nummers uit
            voorIdentificatie = set() # Index van toestand identificatie waarvoor al een nieuw ActueleToestandUniekId is uitgedeeld
            for toestand in self.CompleteToestanden.Toestanden:
                if toestand.GemaaktOp != self.GemaaktOp:
                    break
                self.InstrumentData.WeergaveData._LaatsteUniekId += 1
                toestand._UniekId = self.InstrumentData.WeergaveData._LaatsteUniekId
                if not toestand.Identificatie in voorIdentificatie:
                    # Maak dit de corresponderende toestand voor de actuele toestanden
                    voorIdentificatie.add (toestand.Identificatie)
                    self.InstrumentData.WeergaveData._ActueleToestandUniekId[toestand.Identificatie] = toestand._UniekId
        else:
            self.InstrumentData.WeergaveData._ActueleToestandUniekId = {} # Als complete toestanden niet uitgerekend worden, dan weten we niet of twee actuele toestanden dezelfde inhoud hebben

        if not consolidatie.ActueleToestanden is None and len (consolidatie.ActueleToestanden.Toestanden) > 0:
            instrumentData.HeeftActueleToestanden = True
            self.ActueleToestanden = consolidatie.ActueleToestanden
            uitgewisseldeModules.append (STOPModuleUitwisseling (STOPModuleUitwisseling.Systeem_LVBB, STOPModuleUitwisseling.Systeem_BevoegdGezag, self.ActueleToestanden))
            bewaarJuridischeVerantwoording = True
            # Deel unieke nummers uit
            for toestand in self.ActueleToestanden.Toestanden:
                toestand._UniekId = self.InstrumentData.WeergaveData._ActueleToestandUniekId.get (toestand.Identificatie)
                if toestand._UniekId is None:
                    self.InstrumentData.WeergaveData._LaatsteUniekId += 1
                    toestand._UniekId = self.InstrumentData.WeergaveData._LaatsteUniekId

        if bewaarJuridischeVerantwoording:
            self.JuridischeVerantwoording = STOPModuleSnapshot (consolidatie.JuridischeVerantwoording)


    def ToestandTijdreisIndex (self, toestand : Toestand):
        """Geeft de index van een toestand om de toestand te kunnen verbergen voor tijdreisfilters.
        
        Argumenten:

        toestand Toestand  Toestand waarvoor de index bepaald moet wirden
        """
        self._PasTijdreisfiltersToe ()

        filterIndex = '|'
        for code, selectie in self._CompleteToestanden.items ():
            if not toestand._UniekId in selectie.ToestandIndex:
                # filterIndex geeft aan waar de toestand niet in voorkomt
                filterIndex += code + '|'

        return '' if len(filterIndex) == 1 else filterIndex

    def BeschikbareTijdreisfilters (self):
        """Geef de codes van de beschikbare tijdreisfilters"""
        self._PasTijdreisfiltersToe ()
        return self._CompleteToestanden.keys ()

    def GefilterdeCompleteToestanden (self, code = str(1 + 2 + 4 + 8)):
        """Geeft de (opgeschoonde) CompleteToestanden module voor het tijdreisfilter
        
        Argumenten:
        
        code string  Code van het tijdreisfilter
        """
        self._PasTijdreisfiltersToe ()
        filter = Filter_CompleteToestanden (self.CompleteToestanden, self.GemaaktOp)
        return filter.MaakModule (self._CompleteToestanden[code])

    def _PasTijdreisfiltersToe (self):
        """Pas de ondersteunde tijdreisfilters toe op de complete toestanden"""
        if not self._CompleteToestanden is None:
            return
        self._CompleteToestanden = {}

        ontvangenOp = 1
        bekendOp = 2
        juridischWerkendVanaf = 4
        geldigVanaf = 8
        laatstOntvangen = 16
        actueel = 32
        exTunc = 64
        exNunc =  0 # is de default
        filter = Filter_CompleteToestanden (self.CompleteToestanden, self.GemaaktOp)

        # De ondersteunde tijdreisfilters:
        self._CompleteToestanden[str(exNunc + juridischWerkendVanaf)] = filter.AlleenJuridischWerkendVanaf (False)
        self._CompleteToestanden[str(exNunc + juridischWerkendVanaf + actueel)] = filter.AlleenJuridischWerkendVanaf (True)

        self._CompleteToestanden[str(exNunc + ontvangenOp + juridischWerkendVanaf)] = filter.OntvangenOpJuridischWerkendVanaf (False)
        self._CompleteToestanden[str(exNunc + ontvangenOp + juridischWerkendVanaf + laatstOntvangen)] = filter.OntvangenOpJuridischWerkendVanaf (True)
        self._CompleteToestanden[str(exNunc + bekendOp + juridischWerkendVanaf)] = filter.BekendOpJuridischWerkendVanaf ()
        self._CompleteToestanden[str(exNunc + geldigVanaf + juridischWerkendVanaf)] = filter.GeldigVanafJuridischWerkendVanaf ()

        self._CompleteToestanden[str(exNunc + ontvangenOp + bekendOp + juridischWerkendVanaf)] = filter.JuridischWerkendVanafPlus2 (True, True, False)
        self._CompleteToestanden[str(exNunc + ontvangenOp + bekendOp + juridischWerkendVanaf + laatstOntvangen)] = filter.JuridischWerkendVanafPlus2 (True, True, False, True)
        self._CompleteToestanden[str(exNunc + ontvangenOp + geldigVanaf + juridischWerkendVanaf)] = filter.JuridischWerkendVanafPlus2 (True, False, True)
        self._CompleteToestanden[str(exNunc + ontvangenOp + geldigVanaf + juridischWerkendVanaf + laatstOntvangen)] = filter.JuridischWerkendVanafPlus2 (True, False, True, True)
        self._CompleteToestanden[str(exNunc + bekendOp + geldigVanaf + juridischWerkendVanaf)] = filter.JuridischWerkendVanafPlus2 (False, True, True)

        self._CompleteToestanden[str(exNunc + ontvangenOp + bekendOp + geldigVanaf + juridischWerkendVanaf)] = filter.AlleToestanden (False)
        self._CompleteToestanden[str(exNunc + ontvangenOp + bekendOp + geldigVanaf + juridischWerkendVanaf + laatstOntvangen)] = filter.AlleToestanden (True)

        self._CompleteToestanden[str(exTunc + ontvangenOp + juridischWerkendVanaf)] = filter.ExTunc (False)
        self._CompleteToestanden[str(exTunc + ontvangenOp + juridischWerkendVanaf + laatstOntvangen)] = filter.ExTunc (True)


