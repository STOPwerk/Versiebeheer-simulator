#======================================================================
#
# Bepaling van de complete toestanden op basis van de uitgewisselde
# informatie.
#
#======================================================================
#
# De bepaling van complete toestanden maakt gebruik van een aantal
# operaties die in proces_lv_toestanden.py zijn ondergebracht:
# - Selectie van de relevante delen uit het versiebeheer
# - Bepaling van de instrumentversie van een toestand
#
# In MaakCompleteToestanden zijn ondergebrachtL
# - Bepaling welke toestanden er zijn
# - Bepaling alternatieve versies voor weergave
#
# In deze applicatie worden alle complete toestanden steeds opnieuw
# uitgerekend na elke uitwisseling. Optimalisatie door sommige
# toestanden ongewijzigd te laten vereist dat van tevoren voorspeld
# kan worden welke toestanden geraakt worden door een uitwisseling.
# Dat is complex en foutgevoelig vanwege de terugwerking naar 
# het (verre) verleden van sommige operaties.
#
# De verschillende lijsten worden in deze applicatie gesorteerd
# zodat de uiteindelijke weergave onafhankelijk is van
# implementatiedetails. Dat is in een productie-waardige applicatie
# niet nodig.
#
#======================================================================

from applicatie_meldingen import Melding
from data_lv_consolidatie import GeconsolideerdInstrument
from proces_lv_toestanden import MaakToestanden
from weergave_data_toestanden import  ToestandCompleet, OnvolledigeVersie, Toestand, Toestandidentificatie
from weergave_toestandbepaling import Weergave_Toestandbepaling

#======================================================================
#
# Aanmaken van complete toestanden na een uitwisseling, per instrument
#
#======================================================================
# Het daadwerkelijk bepalen van toestanden voor een
# (ontvangenOp,bekendOp) wordt door _MaakToestanden gedaan.
#=====================================================================
class MaakCompleteToestanden:

    @staticmethod
    def VoerUit (log, consolidatie : GeconsolideerdInstrument, gemaaktOp, ontvangenOp, eersteBekendOp):
        """Maak een nieuwe versie van de actuele toestanden.
        
        log Meldingen Verzameling meldingen over de voortgang van het consolidatieproces
        consolidatie GeconsolideerdInstrument  Informatie over het geconsolideerde instrument
        gemaaktOp string Tijdstip waarop de uitwisseling gemaakt is
        ontvangenOp string De datum waarop de uitwisseling ontvangen is waarvoor de consolidatie opnieuw gedaan wordt.
        eersteBekendOp string De eerste datum waarop (een deel van) de consolidatie informatie uit de uitwisseling bekend is geworden.
        """
        maker = MaakCompleteToestanden (log, consolidatie, gemaaktOp, ontvangenOp)
        maker._VoerUit (eersteBekendOp)

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, log, consolidatie : GeconsolideerdInstrument, gemaaktOp, ontvangenOp):
        """Maak een nieuwe instantie.

        Argumenten:
        
        log Meldingen Verzameling meldingen over de voortgang van het consolidatieproces
        consolidatie GeconsolideerdInstrument  Informatie over het geconsolideerde instrument
        gemaaktOp string Tijdstip waarop de uitwisseling gemaakt is
        ontvangenOp string De datum waarop de uitwisseling ontvangen is waarvoor de consolidatie opnieuw gedaan wordt.
        """
        self._Log = log
        self._Consolidatie = consolidatie
        # De gemaaktOp tijdstempel
        self._GemaaktOp = gemaaktOp
        # De ontvangenOp tijdstempel
        self._OntvangenOp = ontvangenOp
        # De toestanden die bepaald zijn voor deze uitwisseling
        self._NuBepaaldeToestanden = []
        self._Consolidatie.CompleteToestanden.OntvangenOp = self._OntvangenOp

    def _VoerUit (self, eersteBekendOp):
        """Werk de CompleteToestanden bij
        
        Argumenten:

        eersteBekendOp string De eerste datum waarop (een deel van) de consolidatie informatie uit de uitwisseling bekend is geworden.
        """
        # Bepaal welke toestanden er zijn, op volgorde van bekendOp
        # Begin bij de eerste bekendOp waarvoor er iets gewijzigd is voor dit instrument
        for bekendOp in sorted (self._Consolidatie.Instrument.BekendOp):
            if bekendOp >= eersteBekendOp:
                self._Log.Detail ('Bepaal de toestanden voor de informatie bekend op ' + bekendOp)
                self._NuBepaaldeToestanden = _MaakToestanden.VoerUit (self._Consolidatie, self._GemaaktOp, self._OntvangenOp, bekendOp)
        
                # Werk de tijdreisindex bij
                self._VoegToeAanTijdreisIndex (bekendOp)

    class _BepaaldeToestand:
        def __init__ (self, identificatie : Toestandidentificatie, gemaaktOp, ontvangenOp, bekendOp, jwv, gv):
            # Identificatie van de toestand
            self.Identificatie = identificatie
            self.Identificatie._GemaaktOp = gemaaktOp
            # Inhoud van de toestand; instantie van ToestandCompleet
            self.Inhoud = ToestandCompleet ()
            self.Inhoud._GemaaktOp = gemaaktOp
            self.Inhoud._BekendOp = bekendOp
            # Toestand 
            self.Toestand = Toestand ()
            self.Toestand.OntvangenOp = ontvangenOp
            self.Toestand.BekendOp = bekendOp
            self.Toestand.JuridischWerkendVanaf = jwv
            self.Toestand.GeldigVanaf = gv
            self.Toestand.GemaaktOp = gemaaktOp

#----------------------------------------------------------------------
#
# Voeg de toestanden toe aan CompleteToestanden.Toestanden
#
#----------------------------------------------------------------------
    def _VoegToeAanTijdreisIndex (self, bekendOpNieuweToestanden):
        """Voeg de toestand toe aan de tijdreisindex van CompleteToestanden

        Argumenten:

        toestand _BepaaldeToestand  De toestand die toegevoegd moet worden
        bekendOpNieuweToestanden string  De bekendOp tijdstempel voor alle nieuwe toestanden
        """
        # Maak de tijdreisindex elementen voor de nieuwe toestanden
        # De laatst bepaalde toestand eerst, want de tijdreisindex is geordend op aflopende
        # ontvangenOp en bekendOp (daarom moet de nieuwe tijdreisindex vooraan ingevoegd worden in CompleteToestanden.Toestanden),
        # juridischWerkendVanaf en geldigVanaf (de omgekeerde volgorde van de toestanden)
        tijdreisIndex = [toestand.Toestand for toestand in reversed (self._NuBepaaldeToestanden)]

        self._Consolidatie.CompleteToestanden.BekendOp = bekendOpNieuweToestanden
        completeToestanden = self._Consolidatie.CompleteToestanden.Toestanden

        def _VoegMeldingToe (toestand, melding):
            toestand._Uitleg.append (Melding (Melding.Ernst_Detail, 'Toestand (' + toestand.OntvangenOp + ',' + toestand.BekendOp + ',' + toestand.JuridischWerkendVanaf + ',' + toestand.GeldigVanaf + '): ' + melding))

        #--------------------------------------------------------------
        #
        # Over de tijdreisindex
        #
        #--------------------------------------------------------------
        # Om een tijdreis uit te voeren op CompleteToestanden.Toestanden wordt gezocht naar de eerste
        # toestand t met t.OntvangenOp <= ontvangenOp, t.BekendOp <= bekendOp, t.JuridischWerkendVanaf <= juridischWerkendVanaf, t.GeldigVanaf <= geldigVanaf.
        #
        # In principe worden alle toestanden uit tijdreisIndex geplaatst in CompleteToestanden.Toestanden voorafgaand aan de toestanden
        # in CompleteToestanden.Toestanden. Maar niet elke nieuwe toestand uit tijdreisIndex hoeft toegevoegd te worden. Als er al een toestand is in
        # CompleteToestanden.Toestanden met dezelfde Identificatie/Inhoud, en elke tijdreis die de nieuwe toestand vindt zal ook de bestaande toestand
        # vinden, dan voegt het toevoegen van de nieuwe toestand geen nieuw resultaat toe voor welke tijdreis dan ook, en kan dus weggelaten worden.
        #
        # Het toevoegen van toestanden aan CompleteToestanden wordt gedaan vanaf de laatste toestand in tijdreisIndex, dus de eerste in self._NuBepaaldeToestanden
        # Dit is de oudste toestand en heeft de grootste kans niet toegevoegd te hoeven worden, want veranderingen zullen typisch in de recente toestanden plaatsvinden.
        # Als een oude toestand wel toegevoegd moet worden, is de kans groot dat recentere toestanden (eerder in tijdreisIndex) ook toegevoegd moeten worden.
        # Immers een tijdreis die de recente toestand vindt zal typisch een grotere juridischWerkendVanaf/geldigVanaf hebben dan de toegevoegde oudere toestand,
        # en dus zou een tijdreis die de recentere toestand vindt bij weglating van de recente toestand de toegevoegde oudere toestand vinden.

        def _OnderzoekWeglatenToestand (nieuweToestand : Toestand, nieuweToestandIndex : int):
            """Onderzoek of een toestand uit tijdreisIndex toegevoegd moet worden aan CompleteToestanden.Toestanden.

            Argumenten:

            nieuweToestand _BepaaldeToestand  De nieuwe toestand die onderzocht moet worden
            nieuweToestandIndex int  Index van de nieuwe toestand in tijdreisIndex

            Geeft terug (of de toestand toegevoegd moet worden, aantal toestandsvergelijkingen, aantal tijdreizen)
            """
            #----------------------------------------------------------
            #
            # Altijd toevoegen als er geen andere gelijke toestand is
            #
            #----------------------------------------------------------
            bestaandeToestandIndex = 0
            bestaandeToestand = None
            aantalToestandsvergelijkingen = 0 # Voor melding over proces
            aantalTijdreizen = 0 # Voor melding over proces
            while bestaandeToestandIndex < len (completeToestanden):
                aantalToestandsvergelijkingen += 1
                kandidaat = completeToestanden[bestaandeToestandIndex]
                # Is de toestand gelijk (inhoud en identificatie)?
                if kandidaat.Identificatie == nieuweToestand.Identificatie and kandidaat.Inhoud == nieuweToestand.Inhoud:
                    if kandidaat.JuridischWerkendVanaf != nieuweToestand.JuridischWerkendVanaf or kandidaat.GeldigVanaf != nieuweToestand.GeldigVanaf:
                        # Als de JWV/GV parameters ongelijk zijn, dan zijn er tijdreizen die wel de nieuwe en niet de bestaande toestand vinden.
                        # Het is daarom niet verkeerd om de nieuwe toestand toe te voegen. Maar het is denkbaar dat verderop nog een gelijke toestand
                        # bestaat waarvan de tijdstempels wel gelijk zijn. Zet het onderzoek daarom voort
                        pass
                    elif kandidaat.BekendOp > bekendOpNieuweToestanden:
                        # Er zijn tijdreizen (met bekendOp < kandidaat.BekendOp) die wel de nieuwe toestand maar niet de bestaande toestand vinden.
                        # Het is daarom niet verkeerd om de nieuwe toestand toe te voegen. Maar het is denkbaar dat verderop nog een gelijke toestand
                        # bestaat die wel al eerder bekend was. Zet het onderzoek daarom voort.
                        pass
                    else:
                        # Elke tijdreis die de nieuwe toestand zou kunnen vinden (afhankelijk van de toestanden voorafgaand aan de nieuwe toestand) is:
                        # (ontvangen >= self._OntvangenOp, bekendOp >= nieuw.BekendOp, JWV >= nieuw.JuridischWerkendVanaf, GV >= nieuw.geldigVanaf)
                        # Elke tijdreis die de bestaande toestand zou kunnen vinden (idem) is:
                        # (ontvangen >= bestaand.OntvangenOp < self._Ontvangen, bekendOp >= nieuw.BekendOp, JWV >= nieuw.JuridischWerkendVanaf, GV >= nieuw.geldigVanaf)
                        # Oftewel: elke tijdreis die de nieuwe toestand vindt, kan ook de bestaande toestand vinden.
                        bestaandeToestand = kandidaat
                        break
                bestaandeToestandIndex += 1
            if bestaandeToestand is None:
                # Geen gelijke toestand gevonden, dus toevoegen
                _VoegMeldingToe (nieuweToestand, 'wordt toegevoegd omdat er geen andere toestand met gelijke identificatie, inhoud, juridischWerkendVanaf en geldigVanaf is')
                return True, aantalToestandsvergelijkingen, aantalTijdreizen

            #----------------------------------------------------------
            #
            # Onderzoeken of een nieuwe toestand weggelaten mag worden
            #
            #----------------------------------------------------------
            # Er is dus een bestaande toestand met dezelfde inhoud, identificatie en JWV/GV tijdstempels,
            # waarbij de bestaande toestand gelijk of eerder bekend is dan de nieuwe toestand.
            # Stel dat alle toestanden uit tijdreisIndex toegevoegd zouden worden aan CompleteToestanden.Toestanden,
            # dan zou dat eruit zien als:
            #
            # tijdreisIndex:
            #     ... (A) toestanden met een latere JWV of GV dan de nieuweToestand
            #
            #     nieuweToestand
            #
            #     .... toestanden die al weggelaten/toegevoegd zijn en dus genegeerd kunnen worden
            #
            # CompleteToestanden.Toestanden:
            #
            #     ... (B) toestanden met een latere ontvangenOp, bekendOp en/of een latere JWV of GV dan de bestaande toestand,
            #
            #     bestaandeToestand
            #
            #     ... (C) toestanden die nooit gevonden worden voor een tijdreis die de bestaandeToestand en dus nieuweToestand oplevert.
            #
            # De nieuwe toestand hoeft niet toegevoegd te worden als elke tijdreis die een bestaande toestand uit
            # (B) kan vinden en die tevens de nieuweToestand kan vinden, altijd ook een nieuwe toestand uit (A) kan vinden.
            #
            # De tijdreis voor een toestand uit B is:
            # (ontvangen >= toestand.OntvangenOp <= self._Ontvangen, bekendOp >= toestand.BekendOp, JWV >= toestand.JuridischWerkendVanaf, GV >= toestand.geldigVanaf)
            # De tijdreis voor de nieuweToestand is:
            # (ontvangen >= self._Ontvangen, bekendOp >= bekendOpNieuweToestanden, JWV >= nieuw.JuridischWerkendVanaf, GV >= nieuw.geldigVanaf)
            #
            # De tijdreis die beide vindt heeft ontvangen >= self._Ontvangen en dat geldt voor alle toestanden uit (A), dus bij het bepalen of 
            # een tijdreis voor een toestand uit (B) een toestand uit (A) vindt hoeven we niet naar de ontvangenOp datum te kijken. 
            #
            # De tijdreis die beide vindt heeft bekendOp >= max (toestand.BekendOp, bekendOpNieuweToestanden) en dat geldt voor alle toestanden uit (A), dus bij het bepalen of 
            # een tijdreis voor een toestand uit (B) een toestand uit (A) vindt hoeven we niet naar de bekendOp datum te kijken.

            # Begin bij de toestand net voor de bestaande toestand, deze zal in het algemeen het grootste JWV/GV bereik hebben   
            _VoegMeldingToe (nieuweToestand, 'kan misschien weggelaten worden omdat toestand #' + str(bestaandeToestandIndex) + ' al gelijke identificatie, inhoud, juridischWerkendVanaf en geldigVanaf heeft')
            while bestaandeToestandIndex > 0:
                bestaandeToestandIndex -= 1
                toestandB = completeToestanden[bestaandeToestandIndex]
                tijdreisparameterbereik = MaakCompleteToestanden._TijdreisParameterBereik (toestandB.JuridischWerkendVanaf, toestandB.GeldigVanaf)
                isNietLeeg = True

                # Begin daarna met de toestand voor de nieuwe toestand, die in het algemeen het grootste JWV/GV bereik hebben
                toestandAindex = nieuweToestandIndex-1
                while toestandAindex >= 0:
                    aantalTijdreizen += 1
                    isNietLeeg, alleBlokkenOnderJWV = tijdreisparameterbereik.Verwijder (tijdreisIndex[toestandAindex].JuridischWerkendVanaf, tijdreisIndex[toestandAindex].GeldigVanaf)
                    if alleBlokkenOnderJWV:
                        # Gezien de ordening van de nieuwe toestanden hebben alle overige toestanden een grotere JWV
                        break
                    if not isNietLeeg:
                        # Leger wordt het niet
                        break
                    toestandAindex -= 1
                if isNietLeeg:
                    # De tijdreis voor deze toestand B komt bij de nieuweToestand uit in plaats van bij toestand B
                    # De nieuweToestand moet dus toegevoegd worden
                    _VoegMeldingToe (nieuweToestand, 'kan niet weggelaten worden omdat er tijdreizen zijn die bij deze toestand uitkomen: ' + tijdreisparameterbereik.Beschrijf())
                    return True, aantalToestandsvergelijkingen, aantalTijdreizen
            # Als er hier komen, dan komen alle tijdreizen voor toestand B elders uit en hieft deze toestand niet toegevoegd te worden
            return False, aantalToestandsvergelijkingen, aantalTijdreizen

        #--------------------------------------------------------------
        #
        # Toevoegen van de toestanden
        #
        #--------------------------------------------------------------
        # De JuridischWerkendVanaf en GeldigVanaf van de eerste toestand die uit tijdreisIndex wordt toegevoegd aan CompleteToestanden.Toestanden
        # Toestanden met JVW >= eerstToegevoegdeToestand_JuridischWerkendVanaf en GV >= eerstToegevoegdeToestand_GeldigVanaf moeten altijd
        # aan CompleteToestanden.Toestanden worden toegevoegd, omdat anders een tijdreis op (self._OntvangenOp, self._BekendOp, JWV, GV)
        # bij de eerst-toegevoegde toestand uitkomt.
        eerstToegevoegdeToestand_JuridischWerkendVanaf = None
        eerstToegevoegdeToestand_GeldigVanaf = None
        aantalToegevoegd = 0 # Voor melding over proces
        aantalToestandsvergelijkingen = 0 # Voor melding over proces
        aantalTijdreizen = 0 # Voor melding over proces

        nieuweToestandIndex = len (tijdreisIndex)
        while nieuweToestandIndex > 0:
            nieuweToestandIndex -= 1
            nieuweToestand = tijdreisIndex[nieuweToestandIndex]

            voegToe = True
            if eerstToegevoegdeToestand_JuridischWerkendVanaf is None or nieuweToestand.JuridischWerkendVanaf < eerstToegevoegdeToestand_JuridischWerkendVanaf or nieuweToestand.GeldigVanaf < eerstToegevoegdeToestand_GeldigVanaf:
                voegToe, n1, n2 = _OnderzoekWeglatenToestand (nieuweToestand, nieuweToestandIndex)
                aantalToestandsvergelijkingen += n1
                aantalTijdreizen += n2
            else:
                _VoegMeldingToe (nieuweToestand, 'kan niet weggelaten worden omdat tijdreizen voor deze testand anders bij een zojuist toegevoegde toestand zouden komen')

            if voegToe:
                for bestaandeToestand in completeToestanden:
                    # Verwijder een bestaande toestand als die exact dezelfde tijdreisparameters heeft
                    if bestaandeToestand.OntvangenOp < nieuweToestand.OntvangenOp:
                        break
                    if bestaandeToestand.GemaaktOp < nieuweToestand.GemaaktOp and bestaandeToestand.BekendOp == nieuweToestand.BekendOp and bestaandeToestand.JuridischWerkendVanaf == nieuweToestand.JuridischWerkendVanaf and bestaandeToestand.GeldigVanaf == nieuweToestand.GeldigVanaf:
                        bestaandeToestand.OverschrevenOp = nieuweToestand.GemaaktOp # In deze applicatie behouden we de toestand voor weergave
                        break
                aantalToegevoegd += 1
                nieuweToestand._Beschrijving = self._Consolidatie.Tijdreis (nieuweToestand) # Alleen voor weergave
                completeToestanden.insert (0, nieuweToestand)
                if eerstToegevoegdeToestand_JuridischWerkendVanaf is None:
                    eerstToegevoegdeToestand_JuridischWerkendVanaf = nieuweToestand.JuridischWerkendVanaf
                    eerstToegevoegdeToestand_GeldigVanaf = nieuweToestand.GeldigVanaf

            self._Log.Meldingen.extend (nieuweToestand._Uitleg)

        self._Log.Detail ('Complete toestanden: ' + str(len (tijdreisIndex)) + ' bepaald, ' + str (aantalToegevoegd) + ' toegevoegd, ' + str(len (tijdreisIndex)-aantalToegevoegd) + ' al aanwezig')
        self._Log.Detail ('Voor de bepaling zijn ' + str(aantalToestandsvergelijkingen) + ' toestanden met elkaar vergeleken en ' + str (aantalTijdreizen) + ' tijdreizen gemaakt')

    #------------------------------------------------------------------
    #
    # Bijhouden van het bereik aan tijdreisparameters waarvan nog niet
    # is vastgesteld dat die niet de nieuwe toestand gaat vinden.
    #
    #------------------------------------------------------------------
    class _TijdreisParameterBereik:

        def __init__(self, jwv, gv):
            # Het bereik beschreven als lijst van blokken
            self._Bereik = [ MaakCompleteToestanden._TijdreisParameterBereikBlok (jwv, gv)  ]

        def Verwijder (self, juridischWerkendVanaf, geldigVanaf):
            """Verwijder een andere toestand uit het bereik

            Argumenten:

            juridischWerkendVanaf string JWV van de toestand
            geldigVanaf string GV van de toestand

            Geeft terug (of het bereik nog steeds tijdreisparameters bevat, of er blokken zijn met JuridischWerkendTot > juridischWerkendVanaf )
            """
            nieuwBereik = []
            bereikOnderJWV = True # Geeft aan of alle blokken blok.JuridischWerkendTot <= juridischWerkendVanaf hebben
            for blok in self._Bereik:
                if not blok.JuridischWerkendTot is None and blok.JuridischWerkendTot <= juridischWerkendVanaf:
                    # Dit blokje moet behouden blijven
                    nieuwBereik.append (blok)
                    continue
                bereikOnderJWV = False
                if not blok.GeldigTot is None and blok.GeldigTot <= geldigVanaf:
                    # Dit blokje moet behouden blijven
                    nieuwBereik.append (blok)
                    continue

                if blok.JuridischWerkendVanaf >= juridischWerkendVanaf:
                    if blok.GeldigVanaf >= geldigVanaf:
                        # Dit blokje kan weg
                        pass
                    else:
                        # Dit blokje moet gedeeltelijk behouden blijven
                        blok.GeldigTot = geldigVanaf
                        nieuwBereik.append (blok)
                elif blok.GeldigVanaf >= geldigVanaf:
                    # Dit blokje moet gedeeltelijk behouden blijven
                    blok.JuridischWerkendTot = juridischWerkendVanaf
                    nieuwBereik.append (blok)
                else:
                    # Dit blokje moet opgeknipt worden
                    nieuwBereik.append (MaakCompleteToestanden._TijdreisParameterBereikBlok (juridischWerkendVanaf, blok.GeldigVanaf, blok.JuridischWerkendTot, geldigVanaf) )
                    blok.JuridischWerkendTot = juridischWerkendVanaf
                    nieuwBereik.append (blok)

            self._Bereik = nieuwBereik
            return (len (nieuwBereik) > 0, bereikOnderJWV)

        def Beschrijf (self):
            """Beschijf het bereik voor gebruik in een melding"""
            return '[jwv,gv] = ' + ' + '.join (b._Beschrijf () for b in self._Bereik)

    class _TijdreisParameterBereikBlok:

        def __init__(self, jwv, gv, jwt = None, gt = None):
            # Startdatum JWV
            self.JuridischWerkendVanaf = jwv
            # Einddatum JWV, None voor het einde der tijden
            self.JuridischWerkendTot = jwt
            # Startdatum GV
            self.GeldigVanaf = gv
            # Einddatum GV, None voor het einde der tijden
            self.GeldigTot = gt

        def _Beschrijf (self):
            """Beschijf het bereik voor gebruik in een melding"""
            return '[' + self.JuridischWerkendVanaf + '..' + ('' if self.JuridischWerkendTot is None else self.JuridischWerkendTot) + ',' + self.GeldigVanaf + '..' + ('' if self.GeldigTot is None else self.GeldigTot) + ']'

#======================================================================
#
# Aanmaken van complete toestanden, per instrument en per bekendOp.
#
#======================================================================
class _MaakToestanden (MaakToestanden):

    @staticmethod
    def VoerUit (consolidatie : GeconsolideerdInstrument, gemaaktOp, ontvangenOp, bekendOp):
        """Maak een nieuwe versie van de actuele toestanden.
        
        consolidatie GeconsolideerdInstrument  Informatie over het geconsolideerde instrument
        gemaaktOp string Tijdstip waarop de uitwisseling gemaakt is
        ontvangenOp string De datum waarop de uitwisseling ontvangen is waarvoor de consolidatie opnieuw gedaan wordt.
        bekendOp string De datum waarop consolidatie informatie uit de uitwisseling bekend is geworden.

        Geeft een lijst met instanties van MaakCompleteToestanden._BepaaldeToestand terug
        """
        maker = _MaakToestanden (consolidatie, gemaaktOp, ontvangenOp, bekendOp)
        maker._VoerUit ()
        return maker._NuBepaaldeToestanden

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, consolidatie : GeconsolideerdInstrument, gemaaktOp, ontvangenOp, bekendOp):
        """Maak een nieuwe instantie.
        
        consolidatie GeconsolideerdInstrument  Informatie over het geconsolideerde instrument
        gemaaktOp string Tijdstip waarop de uitwisseling gemaakt is
        ontvangenOp string De datum waarop de uitwisseling ontvangen is waarvoor de consolidatie opnieuw gedaan wordt.
        bekendOp string  Maximale waarde van de bekendOp tijdstempels die meedoen in de consolidatie,
                         of None als alle versiebeheerinformatie meegenomen wordt.
        """
        super().__init__ (consolidatie, gemaaktOp, ontvangenOp, bekendOp)
        # De toestanden die bepaald zijn voor deze uitwisseling
        self._NuBepaaldeToestanden = []

    def _VoerUit (self):
        """Bepaal de toestanden"""

        # Bepaal welke toestanden er zijn
        self._BepaalToestanden ()
        
        for toestand in self._NuBepaaldeToestanden:
            # Bepaal de inhoud van de toestand
            if not toestand.Inhoud.IsNietInWerking:
                self._BepaalInhoud (toestand.Inhoud._Consolidatieproces, toestand.Identificatie, toestand.Inhoud.Basisversiedoelen)
                toestand.Inhoud.Instrumentversie = toestand.Inhoud._Consolidatieproces.Instrumentversie

                if toestand.Inhoud.Instrumentversie is None:
                    # Bepaal welke onvolledige versies geschikt zijn om de inhoud weer te geven
                    self._BepaalOnvolledigeVersies (toestand)

            toestand.Toestand.Inhoud = self._Consolidatie.CompleteToestanden.ToestandInhoudIndex (toestand.Inhoud)

#----------------------------------------------------------------------
#
# Bepaal de toestanden
#
#----------------------------------------------------------------------
    def _BepaalToestanden (self):
        """Bepaal de toestanden na deze uitwisseling
        
        Geeft een lijst met instanties van _BepaaldeToestand terug, gesorteerd op (1) juridischWerkendVanaf en (2) geldigVanaf 
        """

        # De CompleteToestanden instantie wordt niet opnieuw gemaakt maar aangevuld
        # Alle toestanden worden wel opnieuw bepaald. De ongewijzigde toestanden worden
        # aan het einde automatisch genegeerd en niet opnieuw aan de instantie toegevoegd.
        completeToestanden = self._Consolidatie.CompleteToestanden
        if completeToestanden.BekendOp is None or completeToestanden.BekendOp < self._BekendOp:
            completeToestanden.BekendOp = self._BekendOp
        if completeToestanden.OntvangenOp is None or completeToestanden.OntvangenOp < self._OntvangenOp:
            completeToestanden.OntvangenOp = self._OntvangenOp

        meldingen = [] # Alleen voor weergave: cumulatieve meldingen zodat elke toestand de historie tot en met de creatie van de toestand krijgt
        def _MaakMelding (tekst, ernst = None):
            """Alleen voor weergave: maak een melding aan"""
            melding = Melding(Melding.Ernst_Informatie if ernst is None else ernst, tekst)
            melding._Stap = Weergave_Toestandbepaling.BepaalToestanden
            meldingen.append (melding)
        _MaakMelding ('Bepaal alle toestanden voor ontvangenOp = ' + self._OntvangenOp + ' en bekendOp = ' + self._BekendOp) 

        #
        # JWV = juridischWerkendVanaf
        # GV = geldigVanaf
        #

        # Bepaal welke toestanden er zijn
        self._NuBepaaldeToestanden = [] # Lijst met alle in deze methode bepaalde toestanden (instantie van _BepaaldeToestand)
        geldendeToestanden = [] # Lijst met toestanden die op het moment van JWV geldig zijn, op volgorde van geldigVanaf (instantie van _BepaaldeToestand)
        voorgaandeGeldigeToestand = -1 # Index in geldendeToestanden van de toestand met de grootste geldigVanaf kleiner dan die van de huidige toestand

        def _MaakToestandExpressionId (voorgaandeGeldigeToestand):
            """Het maken van de ExpressionId wordt uitgesteld totdat zeker is dat alle inwerkingtredingsdoelen verzameld zijn"""
            toestand = geldendeToestanden[voorgaandeGeldigeToestand]
            if toestand.Toestand.Identificatie is None:
                toestand.Identificatie.Inwerkingtredingsdoelen.sort (key = lambda x: x.Identificatie)
                toestand.Toestand.Identificatie = self._Consolidatie.MaakToestandExpressionId (toestand.Identificatie, toestand.Toestand.JuridischWerkendVanaf, toestand.Toestand.GeldigVanaf, meldingen)
                toestand.Identificatie._Uitleg = [*meldingen]

        def _MaakTussenliggendeToestanden (geldigVanaf, voorgaandeGeldigeToestand : int):
            """Kijk of er tussen de zojuist bepaalde toestand en een nieuwe toestand met dezelfde JWV maar een latere geldigVanaf
            aanvullende toestanden gemaakt moeten worden. Die aanvullende toestanden corresponderen met toestanden
            met eerdere JVW maar met een GV tussen die van de zojuist bepaalde toestand en geldigVanaf in (dus kleiner dan en niet gelijk aan geldigVanaf).

            Argumenten:
            geldigVanaf string  De geldigVanaf datum voor een volgende toestand, of None als er geen volgende toestand meer is
            voorgaandeGeldigeToestand int  Index in geldendeToestanden van de toestand met een geldigVanaf kleiner dan de geldigVanaf parameter

            Geeft de bijgewerkte waarde van voorgaandeGeldigeToestand terug
            """
            # Ligt er een toestand tussen de vorig geldende (langs de GV-tijdas) en de komende?
            while voorgaandeGeldigeToestand < len (geldendeToestanden)-1 and (geldigVanaf is None or geldendeToestanden[voorgaandeGeldigeToestand+1].Toestand.GeldigVanaf < geldigVanaf):
                # Jawel
                _MaakToestandExpressionId (voorgaandeGeldigeToestand)
                voorgaandeToestand = geldendeToestanden[voorgaandeGeldigeToestand]
                volgendeToestand = geldendeToestanden[voorgaandeGeldigeToestand+1]
                _MaakMelding ("Zojuist gemaakte toestand overlapt met een toestand met eerdere juridischWerkendVanaf " + volgendeToestand.Toestand.JuridischWerkendVanaf + ' en geldigVanaf ' + volgendeToestand.Toestand.GeldigVanaf)
                _MaakMelding ("Voor de overlap wordt een nieuwe toestand gemaakt met juridischWerkendVanaf " + voorgaandeToestand.Toestand.JuridischWerkendVanaf + ' en geldigVanaf ' + volgendeToestand.Toestand.GeldigVanaf)
                # Maak hiervoor een nieuwe toestand
                tussenliggendeToestand = MaakCompleteToestanden._BepaaldeToestand (Toestandidentificatie(), self._GemaaktOp, self._OntvangenOp, self._BekendOp, voorgaandeToestand.Toestand.JuridischWerkendVanaf, volgendeToestand.Toestand.GeldigVanaf)
                self._NuBepaaldeToestanden.append (tussenliggendeToestand)

                # De IWTdoelen zijn gelijk aan die van de zojuist bepaalde toestand
                tussenliggendeToestand.Identificatie.Inwerkingtredingsdoelen.extend (voorgaandeToestand.Identificatie.Inwerkingtredingsdoelen)

                # De basisversiedoelen zijn de doelen van de toestand met eerdere JVW
                tussenliggendeToestand.Inhoud.Basisversiedoelen.extend (volgendeToestand.Inhoud.Basisversiedoelen)
                tussenliggendeToestand.Inhoud.Basisversiedoelen.extend (volgendeToestand.Identificatie.Inwerkingtredingsdoelen)
                tussenliggendeToestand.Inhoud.Basisversiedoelen.sort (key = lambda x: x.Identificatie)

                # Vervang de oude "volgendeToestand" door de nieuwe toestand
                voorgaandeGeldigeToestand += 1
                geldendeToestanden[voorgaandeGeldigeToestand] = tussenliggendeToestand
                _MaakToestandExpressionId (voorgaandeGeldigeToestand)

            return voorgaandeGeldigeToestand

        # Bepaal alle toestanden (opnieuw). De volgorde is: kleinste JWV eerst, en binnen toestanden met dezelfde JVW de kleinste GV eerst.
        # Dit komt overeen met de juridische spelregels: latere toestanden overschrijven eerdere toestanden.
        juridischUitgewerktOp, intrekkingsdoelen = self.JuridischUitgewerktOp ()
        for _, tijdstempel in self.TijdstempelMomentopnamen ():

            if not juridischUitgewerktOp is None and tijdstempel.JuridischWerkendVanaf >= juridischUitgewerktOp:
                # Na een intrekking bestaat het instrument niet meer, wat er ook verder nog aan wijzigingen klaar staat.
                _MaakMelding ('Geen toestanden gemaakt voor juridischWerkendVanaf &ge; ' + tijdstempel.JuridischWerkendVanaf + ' omdat het instrument is ingetrokken per ' + juridischUitgewerktOp) 
                break

            geldigVanaf = tijdstempel.JuridischWerkendVanaf if tijdstempel.GeldigVanaf is None else tijdstempel.GeldigVanaf

            # Hoe verhoudt de nieuwe toestand zich tot de vorig geldende toestand (langs de GV-tijdas)?
            voorgaandeToestandMetDezelfdeJWV = None # Wijst naar de vorig geldende toestand als dat een toestand met dezelfde JWV is, anders None
            if voorgaandeGeldigeToestand >= 0 and voorgaandeGeldigeToestand < len (geldendeToestanden):
                # Er is een voorgaande toestand
                # Zijn de tijdstempels hetzelfde als voor de nieuwe toestand?
                if tijdstempel.JuridischWerkendVanaf != geldendeToestanden[voorgaandeGeldigeToestand].Toestand.JuridischWerkendVanaf:
                    # Nee, maak een nieuwe toestand
                    _MaakMelding ('Nieuwe toestand voor juridischWerkendVanaf ' + tijdstempel.JuridischWerkendVanaf + ' en geldigVanaf ' + geldigVanaf) 
                    _MaakToestandExpressionId (voorgaandeGeldigeToestand)
                    _MaakTussenliggendeToestanden (None, voorgaandeGeldigeToestand)
                else:
                    # Ja, verwerk eerst toestanden met tussenliggende geldigVanaf en eerdere JWV, tot geldigVanaf
                    voorgaandeGeldigeToestand = _MaakTussenliggendeToestanden (geldigVanaf, voorgaandeGeldigeToestand) 
                    voorgaandeToestandMetDezelfdeJWV = geldendeToestanden[voorgaandeGeldigeToestand]
                    if voorgaandeGeldigeToestand < len (geldendeToestanden) and geldigVanaf == voorgaandeToestandMetDezelfdeJWV.Toestand.GeldigVanaf:
                        _MaakMelding ('Doel ' + str(tijdstempel.Branch.Doel) + ' is een extra inwerkingtredingsdoel van de nieuwe toestand') 
                        voorgaandeToestandMetDezelfdeJWV.Identificatie.Inwerkingtredingsdoelen.append (tijdstempel.Branch.Doel)
                        continue
                    else:
                        # Maak een nieuwe toestand voor dezelfde jWV
                        _MaakMelding ('Nieuwe toestand voor dezelfde juridischWerkendVanaf ' + tijdstempel.JuridischWerkendVanaf + ' en latere geldigVanaf ' + geldigVanaf) 
                        _MaakToestandExpressionId (voorgaandeGeldigeToestand)
            else:
                _MaakMelding ('Eerste toestand, voor juridischWerkendVanaf ' + tijdstempel.JuridischWerkendVanaf + ' en geldigVanaf ' + geldigVanaf) 

            # Maak een nieuwe toestand
            nieuweToestand = MaakCompleteToestanden._BepaaldeToestand (Toestandidentificatie(), self._GemaaktOp, self._OntvangenOp, self._BekendOp, tijdstempel.JuridischWerkendVanaf, geldigVanaf)
            nieuweToestand.Identificatie.Inwerkingtredingsdoelen.append (tijdstempel.Branch.Doel)
            self._NuBepaaldeToestanden.append (nieuweToestand)

            if voorgaandeToestandMetDezelfdeJWV is None:
                _MaakMelding ('Doel ' + str(tijdstempel.Branch.Doel) + ' is het inwerkingtredingsdoel van de nieuwe toestand')

                # Begin aan een nieuwe reeks toestanden met dezelfde JWV
                # Zoek eerst de geldende toestand met een geldigVanaf kleiner dan of gelijk aan geldigVanaf, daar komen de basisversiedoelen vandaan
                voorgaandeGeldigeToestand = len (geldendeToestanden) - 1
                while voorgaandeGeldigeToestand >= 0 and geldendeToestanden[voorgaandeGeldigeToestand].Toestand.GeldigVanaf > geldigVanaf:
                    voorgaandeGeldigeToestand -= 1
                if voorgaandeGeldigeToestand < 0 and len (self._NuBepaaldeToestanden) > 1:
                    # Juridisch misschien een probleem, technisch niet (althans niet in deze applicatie)
                    _MaakMelding ('De toestand heeft een geldigVanaf die voor de eerste geldigheid van het instrument ligt', Melding.Ernst_Waarschuwing) 

                if voorgaandeGeldigeToestand >= 0:
                    nieuweToestand.Inhoud.Basisversiedoelen.extend (geldendeToestanden[voorgaandeGeldigeToestand].Inhoud.Basisversiedoelen)
                    nieuweToestand.Inhoud.Basisversiedoelen.extend (geldendeToestanden[voorgaandeGeldigeToestand].Identificatie.Inwerkingtredingsdoelen)
                    nieuweToestand.Inhoud.Basisversiedoelen.sort (key = lambda x: x.Identificatie)
                    if geldendeToestanden[voorgaandeGeldigeToestand].Toestand.GeldigVanaf == geldigVanaf:
                        _MaakMelding ('Neem de basisversiedoelen over van de toestand met juridischWerkendVanaf ' + geldendeToestanden[voorgaandeGeldigeToestand].Toestand.JuridischWerkendVanaf + ' en dezelfde geldigVanaf als deze toestand') 
                        # De nieuwe toestand vervangt de voorgaande als geldende toestand
                        geldendeToestanden[voorgaandeGeldigeToestand] = nieuweToestand
                    else:
                        _MaakMelding ('Neem de basisversiedoelen over van de toestand met juridischWerkendVanaf ' + geldendeToestanden[voorgaandeGeldigeToestand].Toestand.JuridischWerkendVanaf + ' en geldigVanaf ' + geldendeToestanden[voorgaandeGeldigeToestand].Toestand.GeldigVanaf) 
                        # Voeg de nieuwe toestand toe na de voorgaande toestand
                        voorgaandeGeldigeToestand += 1
                        geldendeToestanden.insert (voorgaandeGeldigeToestand, nieuweToestand)
                else:
                    # Dit wordt de eerste geldige toestand
                    voorgaandeGeldigeToestand = 0
                    geldendeToestanden.insert (voorgaandeGeldigeToestand, nieuweToestand)

            else:
                # Vorige toestand met dezelfde JWV, dus ook de inwerkingtredingsdoelen van die toestand overnemen
                nieuweToestand.Identificatie.Inwerkingtredingsdoelen.extend (voorgaandeToestandMetDezelfdeJWV.Identificatie.Inwerkingtredingsdoelen)
                _MaakMelding ('Doel ' + str(tijdstempel.Branch.Doel) + ' is een extra inwerkingtredingsdoel van de nieuwe toestand, naast de inwerkingtredingsdoel(en)') 

                if geldendeToestanden[voorgaandeGeldigeToestand].Toestand.GeldigVanaf == geldigVanaf:
                    # De nieuwe toestand vervangt een toestand met eerdere JWV als geldende toestand
                    _MaakMelding ('Neem de basisversiedoelen over van de toestand met juridischWerkendVanaf ' + geldendeToestanden[voorgaandeGeldigeToestand].Toestand.JuridischWerkendVanaf + ' en dezelfde geldigVanaf als deze toestand') 
                    nieuweToestand.Inhoud.Basisversiedoelen.extend (geldendeToestanden[voorgaandeGeldigeToestand].Inhoud.Basisversiedoelen)
                    nieuweToestand.Inhoud.Basisversiedoelen.extend (geldendeToestanden[voorgaandeGeldigeToestand].Identificatie.Inwerkingtredingsdoelen)
                    nieuweToestand.Inhoud.Basisversiedoelen.sort (key = lambda x: x.Identificatie)
                    geldendeToestanden[voorgaandeGeldigeToestand] = nieuweToestand
                else:
                    _MaakMelding ('Neem de basisversiedoelen over van de toestand met dezelfde juridischWerkendVanaf als deze toestand en geldigVanaf ' + voorgaandeToestandMetDezelfdeJWV.Toestand.GeldigVanaf) 
                    nieuweToestand.Inhoud.Basisversiedoelen.extend (voorgaandeToestandMetDezelfdeJWV.Inhoud.Basisversiedoelen)
                    # Voeg de nieuwe toestand toe na de voorgaande toestand
                    voorgaandeGeldigeToestand += 1
                    geldendeToestanden.insert (voorgaandeGeldigeToestand, nieuweToestand)

        if voorgaandeGeldigeToestand >= 0 and voorgaandeGeldigeToestand < len (geldendeToestanden):
            # Maak tot slot de toestanden voor de overlap van toestanden met grotere geldigVanaf met de laatst aangemaakte toestand
            _MaakToestandExpressionId (voorgaandeGeldigeToestand)
            _MaakTussenliggendeToestanden (None, voorgaandeGeldigeToestand)

        if not juridischUitgewerktOp is None:
            # Maak een nieuwe toestand voor de ingetrokken staat van het instrument
            nieuweToestand = MaakCompleteToestanden._BepaaldeToestand (Toestandidentificatie(), self._GemaaktOp, self._OntvangenOp, self._BekendOp, juridischUitgewerktOp, juridischUitgewerktOp)
            nieuweToestand.Identificatie.Inwerkingtredingsdoelen.extend (intrekkingsdoelen)
            nieuweToestand.Inhoud.IsNietInWerking = True
            geldendeToestanden = [nieuweToestand]
            _MaakToestandExpressionId (0)
            self._NuBepaaldeToestanden.append (nieuweToestand)

#----------------------------------------------------------------------
#
# Bepaal alternatieve versies om de inhoud van een toestand te tonen
#
#----------------------------------------------------------------------
    def _BepaalOnvolledigeVersies(self, toestand: MaakCompleteToestanden._BepaaldeToestand):
        """Vind de instrumentversies die wel bekend wijn en bepaal in hoeverre ze afwijken van de versie die voor de toestand nodig is

        Argumenten:

        toestand _BepaaldeToestand  De toestand waarvoor de versies bepaald moeten worden
        """
        if not toestand.Inhoud.Instrumentversie is None:
            return
        toestand.Inhoud.OnvolledigeVersies = []

        # Onderzoek de versies voor alle toestanden die in werking treden tussen de geldigVanaf en de juridischWerkendVanaf
        # van de toestand. Dit zijn versies die vermoedelijk met niet al te veel publicaties aangevuld kunnen worden.

        # Zoek per doel naar de laatst doorgegeven instrumentversie
        onvolledigeVersies = set() # Gevonden instrumentversies
        for doel, tijdstempel in reversed (self.TijdstempelMomentopnamen ()):
            isLaatsteIteratie = False
            if tijdstempel.JuridischWerkendVanaf > toestand.Toestand.JuridischWerkendVanaf:
                # Toestanden die later in werking treden zijn nooit interessant
                continue
            if tijdstempel.JuridischWerkendVanaf < toestand.Toestand.GeldigVanaf:
                # Toestanden die op of na de geldigheid van de toestand in werking treden zijn interessant
                # Andere hooguit 1 keer
                isLaatsteIteratie = True
                waarom = 'Deze instrumentversie treedt in werking (vanaf ' + tijdstempel.JuridischWerkendVanaf + ') net voordat de toestand geldig is (vandaf ' + toestand.Toestand.GeldigVanaf + ')'
            else:
                waarom = 'Deze instrumentversie heeft juridische werking (vanaf ' + tijdstempel.JuridischWerkendVanaf + ') als de toestand geldig is (vanaf ' + toestand.Toestand.GeldigVanaf + ')'

            branch = self._Consolidatie.Instrument.Branches.get (doel)
            if not branch is None:
                for momentopname in reversed (branch.Momentopnamen):
                    if momentopname.GemaaktOp <= self._GemaaktOp and momentopname.BekendOp<= self._BekendOp:
                        if not momentopname.ExpressionId is None:
                            if not momentopname.ExpressionId in onvolledigeVersies:
                                onvolledigeVersies.add (momentopname.ExpressionId)

                                melding = Melding (Melding.Ernst_Informatie, 'Onderzoek als onvolledige versie de bekende instrumentversie ' + momentopname.ExpressionId)
                                melding._Stap = Weergave_Toestandbepaling.BepaalAlternatieveVersies 
                                toestand.Inhoud._Consolidatieproces._Uitleg.append (melding)
                                melding = Melding (Melding.Ernst_Informatie, waarom)
                                melding._Stap = Weergave_Toestandbepaling.BepaalAlternatieveVersies 
                                toestand.Inhoud._Consolidatieproces._Uitleg.append (melding)

                                versie = OnvolledigeVersie ()
                                self._MaakNogTeConsolideren (versie, toestand.Identificatie, toestand.Inhoud.Basisversiedoelen, momentopname.BranchesCumulatief, versie._Uitleg)
                                versie.Instrumentversie = momentopname.ExpressionId
                                versie._InstrumentversieDoelen = momentopname.Doelen
                                versie._InstrumentversieGemaaktOp = momentopname.GemaaktOp
                                toestand.Inhoud.OnvolledigeVersies.append (versie)

                                melding = Melding (Melding.Ernst_Informatie, 'Bepaal welke publicaties nodig zijn om de consolidatie af te ronden' + momentopname.ExpressionId)
                                melding._Stap = Weergave_Toestandbepaling.BepaalAanvullendePublicaties 
                                versie._Uitleg.append (melding)
                                self._BepaalAanvullendePublicaties (versie)
                                melding = Melding (Melding.Ernst_Informatie, str(len (versie.TeVerwerkenPublicaties) + len (versie.TeOntvlechtenPublicaties)) + ' publicaties gevonden' + momentopname.ExpressionId)
                                melding._Stap = Weergave_Toestandbepaling.BepaalAanvullendePublicaties 
                                versie._Uitleg.append (melding)
                            break
            if isLaatsteIteratie:
                break

        # Sorteer de versies
        toestand.Inhoud.OnvolledigeVersies.sort (key = lambda x: "{to:06d}{tv:06d}".format(to=len(x.TeOntvlechtenDoelen), tv=len(x.TeVerwerkenDoelen)) + x.Instrumentversie)

    def _BepaalAanvullendePublicaties (self, versie : OnvolledigeVersie):
        """Zoek de publicaties op die gebruikt moeten worden om de ontbrekende uitwisselingen te kunnen verwerken

        Argumenten:

        versie OnvolledigeVersie  Bekende instrumentversie waar de publicaties bijgezocht moeten worden
        """
        for teVerwerken in versie.TeVerwerkenDoelen:
            verantwoording = self._Consolidatie.JuridischeVerantwoording.Verantwoording[teVerwerken.Doel]
            for publicatie in verantwoording.Publicaties:
                if publicatie.VoorInstrument:
                    if (teVerwerken.LaatstVerwerkt is None or teVerwerken.LaatstVerwerkt < publicatie.GemaaktOp) and publicatie.GemaaktOp <= teVerwerken.LaatstBekend:
                        melding = Melding (Melding.Ernst_Informatie, 'Te verwerken publicatie voor (' + teVerwerken.Doel.Identificatie + ',@' + publicatie.GemaaktOp + '): ' + publicatie.UrlVoorInstrument ())
                        melding._Stap = Weergave_Toestandbepaling.BepaalAanvullendePublicaties 
                        versie._Uitleg.append (melding)
                        versie.TeVerwerkenPublicaties.add (publicatie.UrlVoorInstrument ())

        for teontvlechten in versie.TeOntvlechtenDoelen:
            verantwoording = self._Consolidatie.JuridischeVerantwoording.Verantwoording[teontvlechten.Doel]
            for publicatie in verantwoording.Publicaties:
                if publicatie.VoorInstrument:
                    if publicatie.GemaaktOp <= teontvlechten.LaatstVerwerkt:
                        melding = Melding (Melding.Ernst_Informatie, 'Te ontvlechten publicatie voor (' + teontvlechten.Doel.Identificatie + ',@' + publicatie.GemaaktOp + '): ' + publicatie.UrlVoorInstrument ())
                        melding._Stap = Weergave_Toestandbepaling.BepaalAanvullendePublicaties 
                        versie._Uitleg.append (melding)
                        versie.TeOntvlechtenPublicaties.add (publicatie.UrlVoorInstrument ())

