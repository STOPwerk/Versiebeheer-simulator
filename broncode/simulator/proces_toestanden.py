#======================================================================
#
# Gemeenschappelijke cpde voor de epaling van actuele en complete
# toestanden op basis van de uitgewisselde informatie.
#
#======================================================================
#
# De bepaling van actuele en complete toestanden delen een aantal
# operaties die in MaakToestanden zijn ondergebracht:
# - Selectie van de relevante delen uit het versiebeheer
# - Bepaling van de instrumentversie van een toestand
#
# De overige verwerkingstaken zijn in proces_actueletoestanden.py
# en proces_completetoestanden.py ondergebracht.
#
# De verschillende lijsten worden in deze applicatie gesorteerd
# zodat de uiteindelijke weergave onafhankelijk is van
# implementatiedetails. Dat is in een productie-waardige applicatie
# niet nodig.
#
#======================================================================

from typing import List, Dict, Tuple

from applicatie_meldingen import Melding
from data_consolidatie import GeconsolideerdInstrument
from data_doel import Doel
from data_versiebeheerinformatie import Branch, MomentopnameInstrument, MomentopnameTijdstempels, BranchBijdrage
from proces_branchescumulatief import AccumuleerBranchInformatie
from stop_actueletoestanden import TegensprekendDoel
from stop_toestand import Toestandidentificatie, NogTeConsolideren, NogTeVerwerken, NogTeOntvlechten
from weergave_data_toestanden import ConsolidatieprocesInformatie
from weergave_toestandbepaling import Weergave_Toestandbepaling

#======================================================================
#
# Aanmaken van toestanden na een uitwisseling, per instrument
#
#======================================================================
class MaakToestanden:

    def __init__ (self, consolidatie : GeconsolideerdInstrument, gemaaktOp, ontvangenOp, bekendOp):
        """Maak een nieuwe instantie.
        
        consolidatie GeconsolideerdInstrument  Informatie over het geconsolideerde instrument
        gemaaktOp string Tijdstip waarop de uitwisseling gemaakt is
        ontvangenOp string De datum waarop de uitwisseling ontvangen is waarvoor de consolidatie opnieuw gedaan wordt.
        bekendOp string  Maximale waarde van de bekendOp tijdstempels die meedoen in de consolidatie,
                         of None als alle versiebeheerinformatie meegenomen wordt.
        """
        self._Consolidatie = consolidatie
        # De gemaaktOp tijdstempel
        self._GemaaktOp = gemaaktOp
        # De bekendOp tijdstempel
        self._BekendOp = bekendOp
        # De ontvangenOp tijdstempel
        self._OntvangenOp = ontvangenOp

#======================================================================
#
# Hulpmethoden om selecties uit de versiebeheerinformatie te maken
#
#----------------------------------------------------------------------
#
# Een deel van de code komt in meerdere hulpmethoden voor. De code
# kan efficiënter geschreven worden door de hulpmethoden in elkaar
# te schuiven. Er is toch voor verschillende methoden gekozen om
# in de aanroepende code duidelijker te maken welke informatie 
# precies gevraagd wordt.
#
#======================================================================

#----------------------------------------------------------------------
#
# Bepaal alle tijdstempels van momentopnamen die bijdragen aan een 
# nieuwe versie van een instrument, en die dus leiden tot een toestand
#
#----------------------------------------------------------------------
    def TijdstempelMomentopnamen (self) -> List[Tuple[Doel,MomentopnameTijdstempels]]:
        """Geef alle momentopneman voor de tijdstempels die leiden tot een toestand van het geconsolideerde instrument.
        Het resultaat is een lijst van momentopnamen, gesorteerd op (1) oplopende JuridischWerkendVanaf, (2) GeldigVanaf
        """
        if not hasattr (self, '_Tijdstempels'):
            # Cache de resultaten
            self._Tijdstempels = []

            initieelDoelInWerking = False
            # Onderzoek alle doelen
            for branch in self._Consolidatie.Instrument.Branches.values ():

                # Zijn er tijdstempels bekend?
                tijdstempelBranch = self._Consolidatie.Instrument._Versiebeheerinformatie.Tijdstempels.get (branch.Doel)
                if tijdstempelBranch is None:
                    # Er zijn nooit tijdstempels voor de branch uitgewisseld, deze branch doet niet mee
                    continue

                # Is deze branch in werking?
                tijdstempelMomentopname = None
                for tijdstempel in reversed (tijdstempelBranch.Momentopnamen):
                    if tijdstempel.BekendOp <= self._BekendOp:
                        # Dit is de meest recente momentopname van de tijdstempels, die dus meegenomen moet worden
                        # Is er een tijdstempel bekend?
                        if not tijdstempel.JuridischWerkendVanaf is None:
                            # Ja, branch doet mee
                            tijdstempelMomentopname = tijdstempel
                        break
                if tijdstempelMomentopname is None:
                    continue

                # Draagt de branch bij aan een toestand?
                for momentopname in reversed (branch.Momentopnamen):
                    if momentopname.BekendOp <= self._BekendOp:
                        # Dit is de meest recente momentopname van het instrument, die dus meegenomen moet worden
                        if not momentopname.IsIngetrokken and not momentopname.IsTeruggetrokken:
                            # De momentopname correspondeert met een nieuwe versie voor het instrument
                            # De branch draagt dus bij aan toestanden
                            self._Tijdstempels.append ((branch.Doel, tijdstempelMomentopname))

                            if branch.Doel in self._Consolidatie.Instrument.InitieleDoelen:
                                initieelDoelInWerking = True
                    break

            if not initieelDoelInWerking:
                # Als de initiële versie niet in werking is, dan geen enkele toestand van het instrument
                self._Tijdstempels = []
            else:
                # Sorteer de tijdstempels
                self._Tijdstempels.sort (key = lambda mo: mo[1].JuridischWerkendVanaf + (mo[1].JuridischWerkendVanaf if mo[1].GeldigVanaf is None else mo[1].GeldigVanaf))

        return self._Tijdstempels

#----------------------------------------------------------------------
#
# Bepaal de datum dat het instrument juridisch uitgewerkt is, en
# de doelen die voor die datum zorgen
#
#----------------------------------------------------------------------
    def JuridischUitgewerktOp (self) -> Tuple[str, List[Doel]]:
        """Geef de datum dat het instrument (voor het eerst) ingetrokken wordt, en alle doelen die corresponderen met 
        die datum van intrekking. Als het instrument niet ingetrokken is, dan is de datum None en lijst None.
        """
        if not hasattr (self, '_JuridischUitgewerktOp'):
            # Cache de resultaten
            self._JuridischUitgewerktOp = None
            self._IntrekkingsDoelen = None
            # Onderzoek alle doelen
            for branch in self._Consolidatie.Instrument.Branches.values ():

                # Zijn er tijdstempels bekend?
                tijdstempelBranch = self._Consolidatie.Instrument._Versiebeheerinformatie.Tijdstempels.get (branch.Doel)
                if tijdstempelBranch is None:
                    # Er zijn nooit tijdstempels voor de branch uitgewisseld, deze branch doet niet mee
                    continue

                # Is deze branch in werking?
                juridischWerkendVanaf = None
                for tijdstempel in reversed (tijdstempelBranch.Momentopnamen):
                    if tijdstempel.BekendOp <= self._BekendOp:
                        # Dit is de meest recente momentopname van de tijdstempels, die dus meegenomen moet worden
                        juridischWerkendVanaf = tijdstempel.JuridischWerkendVanaf
                        break
                if juridischWerkendVanaf is None:
                    continue

                # Draagt de branch bij aan een toestand?
                for momentopname in reversed (branch.Momentopnamen):
                    if momentopname.BekendOp <= self._BekendOp:
                        # Dit is de meest recente momentopname van het instrument, die dus meegenomen moet worden
                        if momentopname.IsIngetrokken:
                            # De momentopname correspondeert met een intrekking van het instrument
                            # Bepaal de eerste datum waarop het instrument ingetrokken is en de bijbehorende doelen
                            # Juridisch bestaat het instrument na de eerste intrekking niet meer.
                            if self._JuridischUitgewerktOp is None or juridischWerkendVanaf < self._JuridischUitgewerktOp:
                                self._JuridischUitgewerktOp = juridischWerkendVanaf
                                self._IntrekkingsDoelen = [branch.Doel]
                            elif  juridischWerkendVanaf == self._JuridischUitgewerktOp:
                                self._IntrekkingsDoelen.append (branch.Doel)
                    break

            # Sorteer de doelen
            if not self._IntrekkingsDoelen is None:
                self._IntrekkingsDoelen.sort (key = lambda d: d.Identificatie)

        return (self._JuridischUitgewerktOp, self._IntrekkingsDoelen)

#----------------------------------------------------------------------
#
# Bepaal alle momentopnamen die leiden tot een intrekking van 
# het instrument
#
#----------------------------------------------------------------------
    class _MomentopnameIntrekking:
        def __init__ (self, intrekking : MomentopnameInstrument, tijdstempels : MomentopnameTijdstempels):
            self.Branch = intrekking.Branch
            self.GemaaktOp = intrekking.GemaaktOp
            self.BekendOp = intrekking.BekendOp
            if tijdstempels.BekendOp > intrekking.BekendOp:
                self.BekendOp = tijdstempels.BekendOp
            self.JuridischWerkendVanaf = tijdstempels.JuridischWerkendVanaf

    def Intrekkingstijdstempels (self) -> List[_MomentopnameIntrekking]:
        """Geef alle momentopneman die corresponderen met een intrekking van het instrument.
        Als die er niet zijn wordt een lege lijst teruggegeven.
        """
        if not hasattr (self, '_IntrekkingTijdstempels'):
            # Cache de resultaten
            self._IntrekkingTijdstempels = []
            # Onderzoek alle doelen
            for branch in self._Consolidatie.Instrument.Branches.values ():

                # Zijn er tijdstempels bekend?
                tijdstempelBranch = self._Consolidatie.Instrument._Versiebeheerinformatie.Tijdstempels.get (branch.Doel)
                if tijdstempelBranch is None:
                    # Er zijn nooit tijdstempels voor de branch uitgewisseld, deze branch doet niet mee
                    continue

                # Is deze branch in werking?
                tijdstempelMomentopname = None
                for tijdstempel in reversed (tijdstempelBranch.Momentopnamen):
                    if tijdstempel.BekendOp <= self._BekendOp:
                        # Dit is de meest recente momentopname van de tijdstempels, die dus meegenomen moet worden
                        # Is er een tijdstempel bekend?
                        if not tijdstempel.JuridischWerkendVanaf is None:
                            # Ja, branch doet mee
                            tijdstempelMomentopname = tijdstempel
                        break
                if tijdstempelMomentopname is None:
                    continue

                # Draagt de branch bij aan een toestand?
                for momentopname in reversed (branch.Momentopnamen):
                    if momentopname.BekendOp <= self._BekendOp:
                        # Dit is de meest recente momentopname van het instrument, die dus meegenomen moet worden
                        if momentopname.IsIngetrokken:
                            # De momentopname correspondeert met een intrekking van het instrument
                            self._IntrekkingTijdstempels.append (MaakToestanden._MomentopnameIntrekking (momentopname, tijdstempelMomentopname))
                    break

        return self._IntrekkingTijdstempels

#----------------------------------------------------------------------
#
# Bepaal de meest recente momentopname voor het instrument die 
# bijdraagt aan toestand door een instrumentversie te specificeren,
# al is het een onbekende versie
#
#----------------------------------------------------------------------
    def LaatsteMomentopname (self, doel : Doel) -> MomentopnameInstrument:
        """Geef de laatste momentopname voor het doel dat bijdraagt aan een toestand van het geconsolideerde instrument

        Argumenten:

        doel Doel  Doel dat voorkomt als een van de inwerkingtredingsdoelen van een toestand
        """
        if not hasattr (self, '_ToestandBranches'):
            # Cache de resultaten
            # Key = doel, value = momentopname
            self._ToestandBranches = {}
            # Onderzoek alle doelen
            for branch in self._Consolidatie.Instrument.Branches.values ():

                # Zijn er tijdstempels bekend?
                tijdstempelBranch = self._Consolidatie.Instrument._Versiebeheerinformatie.Tijdstempels.get (branch.Doel)
                if tijdstempelBranch is None:
                    # Er zijn nooit tijdstempels voor de branch uitgewisseld, deze branch doet niet mee
                    continue

                # Is deze branch in werking?
                juridischWerkendVanaf = None
                for tijdstempel in reversed (tijdstempelBranch.Momentopnamen):
                    if tijdstempel.BekendOp <= self._BekendOp:
                        # Dit is de meest recente momentopname van de tijdstempels, die dus meegenomen moet worden
                        juridischWerkendVanaf = tijdstempel.JuridischWerkendVanaf
                        break
                if juridischWerkendVanaf is None:
                    continue

                # Draagt de branch bij aan een toestand?
                for momentopname in reversed (branch.Momentopnamen):
                    if momentopname.BekendOp <= self._BekendOp:
                        # Dit is de meest recente momentopname van het instrument, die dus meegenomen moet worden
                        if not momentopname.IsIngetrokken and not momentopname.IsTeruggetrokken:
                            # De momentopname correspondeert met een nieuwe versie voor het instrument
                            # De branch draagt dus bij aan toestanden
                            self._ToestandBranches[branch.Doel] = momentopname
                    break

        return self._ToestandBranches.get (doel)

#----------------------------------------------------------------------
#
# Bepaal de meest recente momentopname voor het instrument voor een branch
# die ooit bijdroeg aan het instrument maar nu niet meer. Als de branch
# niet meer voorkomt in een toestand maar wel nog in de (kandidaat-)
# instrumentversie, dan zal dat wel komen omdat de instrumentversie is 
# opgesteld toen de branch nog wel bijdroeg. Dan moeten de resterende 
# momentopnamen verwerkt worden om de branch uit de instrumentversie 
# te halen. In alle andere gevallen is de branch altijd al onterecht
# opgenomen in de instrumentversie en moet de branch ontvlochten worden.
#
#----------------------------------------------------------------------
    def EersteMomentopnameDieNietMeerBijdraagt (self, doel : Doel) -> MomentopnameInstrument:
        """Geef de laatste momentopname voor het doel dat niet bijdraagt aan een toestand van het geconsolideerde instrument,
        als de branch tenminste ooit wel heeft bijgedragen aan een toestand.
        Dit is bijvoorbeeld het geval bij vernietiging van een besluit door de rechter.

        Argumenten:

        doel Doel  Doel dat voorkomt als een van de inwerkingtredingsdoelen van een toestand

        Geeft de momentopname terug, of None als er geen passende momentopname gevonden kan worden.
        """
        if not hasattr (self, '_ExToestandBranches'):
            # Cache de resultaten
            # Key = doel, value = momentopname
            self._ExToestandBranches = {}
            # Onderzoek alle doelen
            for branch in self._Consolidatie.Instrument.Branches.values ():

                # Draagt de branch bij aan een toestand?
                laatsteBijdrage = None
                eersteNietBijdrage = None
                for momentopname in reversed (branch.Momentopnamen):
                    if momentopname.BekendOp <= self._BekendOp:
                        if momentopname.IsIngetrokken or momentopname.IsTeruggetrokken:
                            # De branch draagt nu niet meer bij
                            eersteNietBijdrage = momentopname
                        else:
                            # De momentopname correspondeert met een nieuwe versie voor het instrument
                            # De branch draagt dus bij aan toestanden (of heeft dat ooit gedaan)
                            laatsteBijdrage = momentopname
                            break

                if laatsteBijdrage is None or eersteNietBijdrage is None:
                    # Branch heeft nooit bijgedragen of doet dat nu nog steeds
                    continue

                # Zijn/waren er tijdstempels bekend ten tijde van de bijdrage?
                tijdstempelBranch = self._Consolidatie.Instrument._Versiebeheerinformatie.Tijdstempels.get (branch.Doel)
                if tijdstempelBranch is None:
                    # Er zijn nooit tijdstempels voor de branch uitgewisseld, deze branch doet niet mee
                    continue

                # Is deze branch in werking?
                for tijdstempel in reversed (tijdstempelBranch.Momentopnamen):
                    if tijdstempel.BekendOp <= eersteNietBijdrage.BekendOp and tijdstempel.GemaaktOp < eersteNietBijdrage.GemaaktOp and not tijdstempel.JuridischWerkendVanaf is None:
                        # Dit is een tijdstempel die de laatsteBijdrage laat bijdragen aan een toestand
                        self._ExToestandBranches[branch.Doel] = eersteNietBijdrage
                        break

        return self._ExToestandBranches.get (doel)


#======================================================================
#
# Bepaal de inhoud van een toestand
#
#======================================================================
    def _BepaalInhoud (self, resultaat : ConsolidatieprocesInformatie, toestand : Toestandidentificatie, basisversiedoelen):
        """Voer een analyse uit op de versiebeheerinformatie om te achterhalen welke 
        (kandidaat-)instrumentversie bij de toestand past. Valideer dat in deze versie
        ook alle uitgewisselde informatie uit het versiebeheer verwerkt is, en ook niet teveel.

        Deze methode wordt gebruikt voor zowel de bepaling van actuele als complete toestanden.
        Het verschil zit erin dat voor complete toestanden de bepaling afgebroken kan worden
        zodra duidelijk

        Argumenten:

        resultaat ConsolidatieprocesInformatie  Instantie waar de resultaten van de bepaling aan toegevoegd worden
        toestand Toestandidentificatie  Informatie over de doelen die de aanleiding voor de toestand zijn.
        basisversiedoelen Doel[] De overige doelen die in de toestand verwerkt zijn

        Geeft een instantie van ConsolidatieprocesInformatie terug met daarin de uitkomst van
        de bepaling van de inhoud van de toestand.
        """
        consolidatieStap = Weergave_Toestandbepaling.Validatie_GeenToestandNaIntrekking
        def _MaakMelding (tekst, ernst = None, stap = None):
            """Voeg een melding toe aan het resultaat; alleen nodig voor de weergave in deze applicatie"""
            melding = Melding(ernst if ernst else Melding.Ernst_Informatie, tekst)
            melding._Stap = stap if stap else consolidatieStap
            resultaat._Uitleg.append (melding)

        # Bepaal de kandidaat-instrumentversies
        consolidatieStap = Weergave_Toestandbepaling.BepaalKandidaatInstrumentversie
        kandidaatVersies = {} # Alle kandidaat-instrumentversies; key = instrumentversie, value = lijst van TegensprekendDoel voor een van de doelen uit een momentopname
        aantalMomentopnamen = 0 # Aantal verschillende momentopnamen die aan de toestand bijdragen

        momentopnameOnbekendeVersie = set () # momentopnamen (doel + gemaaktOp) die al verwerkt is
        aantalMomentopnamen = 0
        for doel in toestand.Inwerkingtredingsdoelen:
            momentopname = self.LaatsteMomentopname(doel)
            if momentopname.GemaaktOp + str(doel) in momentopnameOnbekendeVersie:
                # Deze is al eerder verwerkt
                continue
            aantalMomentopnamen += 1
            for d in momentopname.Doelen:
                momentopnameOnbekendeVersie.add (momentopname.GemaaktOp + str(d))

            versie = momentopname.ExpressionId
            if not versie is None:
                lijst = kandidaatVersies.get (versie)
                if lijst is None:
                    _MaakMelding ('Kandidaat-instrumentversie gevonden: ' + versie)
                    kandidaatVersies[versie] = lijst = []
                lijst.append (TegensprekendDoel (doel, momentopname.GemaaktOp))
            else:
                # Als er twee keer een onbekende versie uitgewisseld is voor de toestand.
                # dan weten we niet of dat dezelfde is. Tel daarom elke onbekende versie 
                # als een aparte versie, behalve als ze uit dezelfde momentopname komen

                # Gebruik nummer als key, zodat we nog steeds het aantal verschillende versies kunnen tellen
                kandidaatVersies['(onbekend)'] = [TegensprekendDoel (doel, momentopname.GemaaktOp)]
                _MaakMelding ('Geen instrumentversie bekend voor ' + ('' if len (momentopname.Doelen) == 1 else 'o.a. ') + 'doel ' + str(doel), Melding.Ernst_Waarschuwing)

                # In een productie-waardige applicatie kan nu de inhoudbepaling voor een complete toestand afgebroken worden
                # want de instrumentversie zal niet bekend zijn. In deze applicatie wordt wel de bepaling doorgezet
                # om bij de weergave precies volledig aan te geven wat er met de toestand aan de hand is.

                # Zoek de laatste momentopname op waarvoor wel een instrumentversie is opgegeven
                for d in momentopname.Doelen:
                    rapporteer = NogTeVerwerken (d, momentopname.GemaaktOp)
                    for m in reversed (self._Consolidatie.Instrument.Branches[d].Momentopnamen):
                        if m.GemaaktOp < momentopname.GemaaktOp and m.BekendOp <= self._BekendOp:
                            # Dit is een eerdere momentopname
                            if m.IsTeruggetrokken or m.IsIngetrokken:
                                # Kan dit voorkomen? Nooit een expressionId gespecificeerd na intrekking/terugtrekking
                                break
                            rapporteer.LaatstVerwerkt = m.GemaaktOp
                            if not m.ExpressionId:
                                # Instrumentversie gespecificeerd
                                break
                    # if rapporteer.LaatstVerwerkt is None: # Kan niet voorkomen, nieuwe branch starten met een onbekende instrumentversie is niet toegestaan, afgevangen bij uitwisseling
                    _MaakMelding ('Instrumentversie voor doel ' + str(d) + ' is onbekend, geen consolidatie uitgevoerd na uitwisseling ' + rapporteer.LaatstVerwerkt, Melding.Ernst_Waarschuwing, Weergave_Toestandbepaling.Validatie_LaatsteUitwisselingVoorAlleDoelen)
                    resultaat.TeVerwerkenDoelen.append (rapporteer)

        # Kan de kandidaatversie eenduidig aangewezen worden?
        consolidatieStap = Weergave_Toestandbepaling.Validatie_DezelfdeVersieVoorAlleDoelen
        if len (kandidaatVersies) > 1:
            _MaakMelding ('Er zijn meerdere kandidaat-versies; niet alle inwerkingtredingsdoelen hebben dezelfde instrumentversie', Melding.Ernst_Fout)
            for lijst in kandidaatVersies.values ():
                resultaat.TegensprekendeDoelen.extend (lijst)
        elif aantalMomentopnamen > 1:
            _MaakMelding ('Dezelfde kandidaatversie is in meerdere momentopnamen aangeleverd in plaats van één momentopnamen met meerdere doelen', Melding.Ernst_Fout)
            for lijst in kandidaatVersies.values ():
                resultaat.TegensprekendeDoelen.extend (lijst)
        else:
            _MaakMelding ('Alle inwerkingtredingsdoelen hebben dezelfde beoogde instrumentversie')
            resultaat.KandidaatInstrumentversie = resultaat.Instrumentversie = list (kandidaatVersies.keys ())[0]
        resultaat.TegensprekendeDoelen.sort (key = lambda x: x.Doel.Identificatie)

        # Zoek uit welk deel van het versiebeheer meegenomen is als alle laatste uitwisselingen voor de inwerkingtredingsdoelen
        # meegenomen worden.
        branchesCumulatief = AccumuleerBranchInformatie.VoorToestand (self._Consolidatie.Instrument, toestand.Inwerkingtredingsdoelen)
        self._MaakNogTeConsolideren (resultaat, toestand, basisversiedoelen, branchesCumulatief, resultaat._Uitleg)

#----------------------------------------------------------------------
#
# Bepaal het deel van het versiebeheer dat nog niet of onterecht deel
# is van de toestand/instrumentversie
#
#----------------------------------------------------------------------

    def _MaakNogTeConsolideren (self, resultaat: NogTeConsolideren, toestand : Toestandidentificatie, basisversiedoelen : List[Doel], branchesCumulatief: Dict[Doel,BranchBijdrage], meldingen = None):
        """Bepaal het deel van het versiebeheer dat nog niet of onterecht deel is van de toestand/instrumentversie

        Argumenten:

        resultaat NogTeConsolideren  Instantie waar de uitkomst in opgeslagen moet worden
        toestand Toestandidentificatie  Informatie over de doelen die de aanleiding voor de toestand zijn.
        basisversiedoelen Doel[] De overige doelen die in de toestand verwerkt zijn
        momentopname MomentopnameInstrument Momentopname waaruit de instrumentversie afkomstig is, of die de inhoud van toestand representeert
        meldingen Melding[]  Verzameling van meldingen voor uitleg over het proces

        Geeft een instantie van ConsolidatieprocesInformatie terug met daarin de uitkomst van
        de bepaling van de inhoud van de toestand.
        """
        resultaat.Basisversiedoelen = basisversiedoelen # Voor weergave

        # Zoek nu uit welk deel van het versiebeheer nog niet verwerkt is
        consolidatieStap = Weergave_Toestandbepaling.Validatie_LaatsteUitwisselingVoorAlleDoelen
        def _MaakMelding (tekst, ernst = None, stap = None):
            """Voeg een melding toe aan het resultaat; alleen nodig voor de weergave in deze applicatie"""
            if not meldingen is None:
                melding = Melding(ernst if ernst else Melding.Ernst_Informatie, tekst)
                melding._Stap = stap if stap else consolidatieStap
                meldingen.append (melding)

        # Ga na dat alle toestand-doelen volledig bijdragen
        toestandDoelen = [*basisversiedoelen, *toestand.Inwerkingtredingsdoelen]
        for doel in toestandDoelen:
            verwerkt = branchesCumulatief.get (doel)
            if verwerkt is None:
                # Branch niet verwerkt, had wel gemoeten
                resultaat.TeVerwerkenDoelen.append (NogTeVerwerken (doel, self.LaatsteMomentopname(doel).GemaaktOp))
                resultaat.Instrumentversie = None
                _MaakMelding ('Doel ' + str(doel) + ' is helemaal niet verwerkt in de kandidaat-instrumentversie voor de toestand', Melding.Ernst_Fout)
            elif not verwerkt.IsOntvlochten is None and verwerkt.IsOntvlochten:
                # Branch is ontvlochten maar dat had niet gemoeten
                resultaat.TeVerwerkenDoelen.append (NogTeVerwerken (doel, self.LaatsteMomentopname(doel).GemaaktOp))
                resultaat.Instrumentversie = None
                _MaakMelding ('De kandidaat-instrumentversie voor de toestand is onterecht ontvlochten met doel ' + str(doel) + ' (@' + verwerkt.LaatstVerwerkt + ')', Melding.Ernst_Fout)
            elif verwerkt.LaatstVerwerkt < self.LaatsteMomentopname(doel).GemaaktOp:
                # De bijdrage is een eerdere uitwisseling dan de laatst beschikbare
                resultaat.TeVerwerkenDoelen.append (NogTeVerwerken (doel, self.LaatsteMomentopname(doel).GemaaktOp, verwerkt.LaatstVerwerkt))
                resultaat.Instrumentversie = None
                _MaakMelding ('Laatste uitwisseling (' + self.LaatsteMomentopname(doel).GemaaktOp + ') voor doel ' + str(doel) + ' is recenter dan de bijdrage (' + verwerkt.LaatstVerwerkt + ') aan de kandidaat-instrumentversie voor de toestand', Melding.Ernst_Fout)
            elif verwerkt.IsOntvlochten is None:
                # Branch is wel en niet ontvlochten. Dit hoeft niet als NogTeConsolideren gemeld te worden,
                # want het kan alleen het resultaat zijn van het samenkomen van verschillende doelen in de toestand.
                # Bij aanlevering van de gemeenschappelijke instrumentversie wordt gevalideerd dat dit opgelost is.
                _MaakMelding ('Doel ' + str(doel) + ' is zowel vervlochten als ontvlochten in basisversie(s) van de toestand; status moet (nogmaals) expliciet aangegeven worden bij verdere consolidatie')
            else:
                _MaakMelding ('Laatste uitwisseling (' + self.LaatsteMomentopname(doel).GemaaktOp + ') voor basisversiedoel ' + str(doel) + ' draagt bij aan de kandidaat-instrumentversie voor de toestand')

        # Kijk of er doelen in de toestand-/instrumentversie verwerkt zijn die niet in de toestand zitten
        consolidatieStap = Weergave_Toestandbepaling.Validatie_GeenAnderDoelVerwerktInInstrumentversie
        ietsGemeld = False
        for doel, verwerkt in branchesCumulatief.items ():
            if not doel in toestandDoelen:
                ietsGemeld = True
                if verwerkt.IsOntvlochten is None:
                    # Branch is wel en niet ontvlochten. Dit hoeft niet als NogTeConsolideren gemeld te worden,
                    # want het kan alleen het resultaat zijn van het samenkomen van verschillende doelen in de toestand.
                    # Bij aanlevering van de gemeenschappelijke instrumentversie wordt gevalideerd dat dit opgelost is.
                    _MaakMelding ('Doel ' + str(doel) + ' is zowel vervlochten als ontvlochten in basisversie(s) van de toestand; status moet (nogmaals) expliciet aangegeven worden bij verdere consolidatie')
                elif verwerkt.IsOntvlochten:
                    _MaakMelding ('Doel ' + str(doel) + ' draagt niet bij aan de toestand en de kandidaat-instrumentversie voor de toestand zijn hiermee ontvlochten')
                else:
                    # Dit doel zitten niet in de toestand maar wel in de toestand/instrumentversie
                    ntv = self.EersteMomentopnameDieNietMeerBijdraagt (doel)
                    if not ntv is None:
                        # Het doel draagt nu niet meer bij aan een toestand en vroeger blijkbaar wel.
                        resultaat.TeVerwerkenDoelen.append (NogTeVerwerken (doel, ntv.GemaaktOp, verwerkt.LaatstVerwerkt))
                        resultaat.Instrumentversie = None
                        _MaakMelding ('Laatste uitwisseling (' + ntv.GemaaktOp + ') voor doel ' + str(doel) + ' (dat niet bijdraagt aan de toestand) is recenter dan de bijdrage (' + verwerkt.LaatstVerwerkt + ') aan de kandidaat-instrumentversie voor de toestand. Consolidatie van de uitwisselingen bestaat uit het ontvlechten van dit doel.', Melding.Ernst_Fout)
                    else:
                        # Verwerking van de recentere uitwisselingen leidt niet tot het verwijderen van de bijdrage. Verwijder daarom alle 
                        resultaat.TeOntvlechtenDoelen.append (NogTeOntvlechten (doel, verwerkt.LaatstVerwerkt))
                        resultaat.Instrumentversie = None
                        _MaakMelding ('Bijdragen van doel ' + str(doel) + ' tot ' + verwerkt.LaatstVerwerkt + ' dragen bij aan de kandidaat-instrumentversie voor de toestand, maar het doel draagt niet bij aan de toestand', Melding.Ernst_Fout)

        if not ietsGemeld:
            _MaakMelding ('Er zijn geen doelen die wel bijdragen aan de kandidaat-instrumentversie maar niet aan de toestand')

        resultaat.TeVerwerkenDoelen.sort (key = lambda x: x.Doel.Identificatie)
        resultaat.TeOntvlechtenDoelen.sort (key = lambda x: x.Doel.Identificatie)
