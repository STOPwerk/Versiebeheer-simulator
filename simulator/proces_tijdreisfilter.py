#======================================================================
#
# Toepassen van een tijdreisfilter op een volledig overzicht 
# van complete toestanden.
#
#======================================================================
#
# De bepaling van complete toestanden leidt tot een volledig
# overzicht van toestanden waarbij tijdreizen op vier tijdassen
# mogelijk is. Dat zal voor veel toepassingen teveel detail zijn.
# STOP staat het toe om een gefilterde versie van het overzicht
# uit te wisselen. De gefilterde versie kan op basis van de 
# volledige versie worden samengesteld door het kiezen van de
# informatie die opgenomen moet worden. Er is geen aparte
# toestandsbepaling voor nodig.
#
# STOP schrijft niet voor welke filters ondersteund moeten
# worden. In deze applicatie zijn een aantal filters beschikbaar
# ter illustratie van de mogelijkheden.
#
# De filtering bestaat uit twee delen: eerst wordt bepaald welke
# toestanden in het gefilterde resultaat opgenomen moeten worden:
# een lijst met indices van CompleteToestanden.Toestanden. Daarna
# kunnen die omgezet worden naar een CompleteToestanden waarin
# alleen nog de noodzakelijke informatie is overgehouden.
#
# De verschillende lijsten worden in deze applicatie gesorteerd
# zodat de uiteindelijke weergave onafhankelijk is van
# implementatiedetails. Dat is in een productie-waardige applicatie
# niet nodig.
#
#======================================================================

from unittest import result
from stop_completetoestanden import CompleteToestanden, Tijdreisfilter, Toestand

class Filtervoorschrift:

    def __init__ (self):
        """ Maak een nieuw resultaat voor de bepaling van de op te nemen toestanden"""
        # Tijdreisfilter dat de filtering beschrijft.
        self.Tijdreisfilter = Tijdreisfilter ()
        # Set met de unieke IDs van de toestanden die opgenomen moeten worden..
        self.ToestandIndex = set ()

class Filter_CompleteToestanden:

    def __init__ (self, completeToestanden: CompleteToestanden, gemaaktOp):
        """Maakt een nieuw filter aan.

        Argumenten:

        completeToestanden CompleteToestanden  Het volledige overzicht van complete toestanden
        gemaaktOp string  Tijdstip van de laatste uitwisseling die meegenomen moet worden. Alleen 
                          nodig voor weergave in deze applicatie.
        """
        self._CompleteToestanden = completeToestanden
        self._GemaaktOp = gemaaktOp

#======================================================================
#
# Bepalen van de toestanden die opgenomen moeten worden
#
#======================================================================

#----------------------------------------------------------------------
#
# 1 tijdstempel: JuridischWerkendVanaf
#
#----------------------------------------------------------------------
    def AlleenJuridischWerkendVanaf (self, alleenActueleToestanden : bool):
        """Filter de toestanden zodat alleen tijdreizen op juridischWerkendVanaf mogelijk is.

        Argumenten:

        alleenActueleToestanden bool  Geeft aan dat alleen toestanden die nu of in de toekomst geldig zijn opgenomen worden

        Geeft een Filtervoorschrift terug. 
        """
        resultaat = Filtervoorschrift ()
        resultaat.Tijdreisfilter.OntvangenOpAanwezig = False
        resultaat.Tijdreisfilter.BekendOpAanwezig = False
        resultaat.Tijdreisfilter.GeldigVanafAanwezig = False

        laatsteJWV = None
        for toestand in self._CompleteToestanden.Toestanden:
            if toestand.GemaaktOp <= self._GemaaktOp:
                # We hoeven niet op geldigVanaf te controleren, want toestanden met eerdere geldigVanaf staan 
                # later in de lijst met toestanden

                if not laatsteJWV is None and laatsteJWV <= toestand.JuridischWerkendVanaf:
                    # Deze toestand wordt nooit in een tijdreis gevonden
                    continue
                laatsteJWV = toestand.JuridischWerkendVanaf

                # Deze toestand moet meegenomen worden
                resultaat.ToestandIndex.add (toestand.UniekId)

                if alleenActueleToestanden and laatsteJWV <= self._CompleteToestanden.OntvangenOp:
                    # De overige toestanden worden niet gevonden of zijn historisch
                    break
        return resultaat

#----------------------------------------------------------------------
#
# 2 tijdstempels: JuridischWerkendVanaf + 1 andere
#
#----------------------------------------------------------------------
    def OntvangenOpJuridischWerkendVanaf (self, alleenLaatstOntvangen : bool):
        """Filter de toestanden zodat alleen tijdreizen op geldigheid mogelijk zijn.

        Argumenten:

        alleenLaatstOntvangen bool  Geeft aan dat alleen toestanden die ontvangen zijn op de laatste dag opgenomen worden

        Geeft een Filtervoorschrift terug.
        """
        resultaat = self._JuridischWerkendVanafPlus1 (lambda t: t.OntvangenOp, alleenLaatstOntvangen)
        resultaat.OntvangenOpAanwezig = True
        return resultaat

    def BekendOpJuridischWerkendVanaf (self):
        """Filter de toestanden zodat alleen tijdreizen op geldigheid mogelijk zijn.

        Geeft een Filtervoorschrift terug.
        """
        resultaat = self._JuridischWerkendVanafPlus1 (lambda t: t.BekendOp, False)
        resultaat.BekendOpAanwezig = True
        return resultaat

    def GeldigVanafJuridischWerkendVanaf (self):
        """Filter de toestanden zodat alleen tijdreizen op geldigheid mogelijk zijn.

        Geeft een Filtervoorschrift terug.
        """
        resultaat = self._JuridischWerkendVanafPlus1 (lambda t: t.GeldigVanaf, False)
        resultaat.GeldigVanafAanwezig = True
        return resultaat

    def _JuridischWerkendVanafPlus1 (self, geefTijdstempel, alleenLaatstOntvangen : bool):
        """Filter de toestanden zodat alleen tijdreizen op geldigheid mogelijk zijn.

        Argumenten:

        geefTijdstempel  Functie die de tweede tijd
        alleenActueleToestanden bool  Geeft aan dat alleen toestanden die ontvangen zijn op de laatste dag opgenomen worden

        Geeft een Filtervoorschrift terug. Daarin moet nog worden aangegeven wat het tweede tijdreisveld is
        """
        resultaat = Filtervoorschrift ()
        resultaat.Tijdreisfilter.OntvangenOpAanwezig = False
        resultaat.Tijdreisfilter.BekendOpAanwezig = False
        resultaat.Tijdreisfilter.GeldigVanafAanwezig = False

        laatsteOntvangenOp = None
        gedaan = Filter_CompleteToestanden._TijdreisParameterBereik ()
        for toestand in self._CompleteToestanden.Toestanden:
            if toestand.GemaaktOp <= self._GemaaktOp:

                if alleenLaatstOntvangen:
                    if laatsteOntvangenOp is None:
                        laatsteOntvangenOp = toestand.OntvangenOp
                    elif laatsteOntvangenOp != toestand.OntvangenOp:
                        break

                if gedaan.IsToestandBereisbaar (geefTijdstempel (toestand), toestand.JuridischWerkendVanaf):
                    # Deze toestand moet meegenomen worden
                    resultaat.ToestandIndex.add (toestand.UniekId)

        return resultaat

    #----------------------------------------------------------------------
    #
    # Bijhouden van het bereik aan tijdreisparameters die nog niet
    # bij een toestand uitkomen.
    #
    #----------------------------------------------------------------------
    class _TijdreisParameterBereik:

        def __init__(self):
            # Het bereik beschreven als lijst van blokken
            self._Bereik = [ ]

        def IsToestandBereisbaar (self, p1, p2):
            """Geef aan of er een tijdreis is die niet tot andere toestanden leidt maar tot deze toestand.
            Als dat zo is, wordt het nog te bereizen bereik verminderd met de tijdreizen die deze toestand bereiken.

            Argumenten:

            p1 string tijdreisparameter 1 van de toestand
            p2 string tijdreisparameter 2 van de toestand

            Geeft terug (of het bereik nog steeds tijdreisparameters bevat, of er blokken zijn met Parameter1Tot > p1 )
            """
            isBereisbaar = True
            nieuwBereik = []
            for blok in self._Bereik:
                if p1 < blok.Parameter1:
                    # Er zijn tijdreizen die bij de toestand uitkomen
                    if p2 < blok.Parameter2:
                        # Blok ligt helemaal binnen de toestand
                        pass
                    else:
                        # Blok en toestand overlappen
                        nieuwBereik.append (blok)
                elif p2 >= blok.Parameter2: # p1 >= blok.Parameter1
                    # Toestand ligt helemaal binnen het blok
                    isBereisbaar = False
                    nieuwBereik.append (blok)
                else: # p1 >= blok.Parameter1, p2 < blok.Parameter2
                    # Blok en toestand overlappen
                    nieuwBereik.append (blok)

            if isBereisbaar:
                nieuwBereik.append (Filter_CompleteToestanden._TijdreisParameterBereikBlok (p1, p2))
            self._Bereik = nieuwBereik
            return isBereisbaar

    class _TijdreisParameterBereikBlok:

        def __init__(self, jwv, gv, jwt = None, gt = None):
            # Startdatum parameter 1
            self.Parameter1 = jwv
            # Startdatum parameter 1
            self.Parameter2 = gv


#----------------------------------------------------------------------
#
# 3 tijdstempels: JuridischWerkendVanaf + 2 andere
#
#----------------------------------------------------------------------
    def JuridischWerkendVanafPlus2 (self, metOntvangenOp : bool, metBekendOp : bool, metGeldigVanaf: bool, alleenLaatstOntvangen = False):
        """Filter de toestanden zodat alleen tijdreizen op drie tijdstempels mogelijk zijn.

        Argumenten:

        metOntvangenOp bool  Geeft aan of ontvangenOp een van de tijdstempels is
        metBekendOp bool  Geeft aan of bekendOp een van de tijdstempels is
        metGeldigVanaf bool  Geeft aan of geldigVanaf een van de tijdstempels is
        alleenLaatstOntvangen bool  Geeft aan dat alleen toestanden die ontvangen zijn op de laatste dag opgenomen worden (mits metOntvangenOp True is)

        Geeft een Filtervoorschrift terug.
        """
        resultaat = Filtervoorschrift ()
        resultaat.Tijdreisfilter.OntvangenOpAanwezig = metOntvangenOp
        resultaat.Tijdreisfilter.BekendOpAanwezig = metBekendOp
        resultaat.Tijdreisfilter.GeldigVanafAanwezig = metGeldigVanaf
        alleenLaatstOntvangen = alleenLaatstOntvangen & metOntvangenOp

        geefTijdstempel = []
        if metOntvangenOp:
            geefTijdstempel.append (lambda t: t.OntvangenOp)
        if metBekendOp:
            geefTijdstempel.append (lambda t: t.BekendOp)
        geefTijdstempel.append (lambda t: t.JuridischWerkendVanaf)
        if metGeldigVanaf:
            geefTijdstempel.append (lambda t: t.GeldigVanaf)
        if len (geefTijdstempel) != 3:
            raise 'Filter_CompleteToestanden.OntvangenOpJuridischWerkendVanaf: gemaakt voor precies 3 tijdstempels, niet ' + str(len (geefTijdstempel))

        laatsteOntvangenOp = None
        gedaan = set()
        for toestand in self._CompleteToestanden.Toestanden:
            if toestand.GemaaktOp <= self._GemaaktOp:

                if alleenLaatstOntvangen:
                    if laatsteOntvangenOp is None:
                        laatsteOntvangenOp = toestand.OntvangenOp
                    elif laatsteOntvangenOp != toestand.OntvangenOp:
                        break

                # Controleer alleen op dubbel voorkomende tijdstempels
                key = ';'.join (geef(toestand) for geef in geefTijdstempel)
                if not key in gedaan:
                    # Deze toestand moet meegenomen worden
                    gedaan.add (key)
                    resultaat.ToestandIndex.add (toestand.UniekId)

        return resultaat

#----------------------------------------------------------------------
#
# 4 tijdstempels: JuridischWerkendVanaf + alle 3 andere
#
#----------------------------------------------------------------------
    def AlleToestanden (self, alleenLaatstOntvangen : bool):
        """Filter de toestanden zodat tijdreizen op alle vier tijdstempels mogelijk zijn.

        Argumenten:

        alleenLaatstOntvangen bool  Geeft aan dat alleen toestanden die ontvangen zijn op de laatste dag opgenomen worden (mits metOntvangenOp True is)

        Geeft een Filtervoorschrift terug.
        """
        resultaat = Filtervoorschrift ()
        resultaat.Tijdreisfilter.OntvangenOpAanwezig = True
        resultaat.Tijdreisfilter.BekendOpAanwezig = True
        resultaat.Tijdreisfilter.GeldigVanafAanwezig = True

        laatsteOntvangenOp = None
        for toestand in self._CompleteToestanden.Toestanden:
            if toestand.GemaaktOp <= self._GemaaktOp:

                if alleenLaatstOntvangen:
                    if laatsteOntvangenOp is None:
                        laatsteOntvangenOp = toestand.OntvangenOp
                    elif laatsteOntvangenOp != toestand.OntvangenOp:
                        break
                # Deze toestand moet meegenomen worden
                resultaat.ToestandIndex.add (toestand.UniekId)

        return resultaat


#----------------------------------------------------------------------
#
# 4 tijdstempels: JuridischWerkendVanaf + OntvangenOp - Ex Tunc
#
#----------------------------------------------------------------------
    def ExTunc (self, alleenLaatstOntvangen : bool):
        """Filter de toestanden zodat tijdreizen op JuridischWerkendVanaf + OntvangenOp
        mogelijk zijn, waarbij toestanden die niet meer geldig zijn niet meer aangepast
        worden.

        Argumenten:

        alleenLaatstOntvangen bool  Geeft aan dat alleen toestanden die ontvangen zijn op de laatste dag opgenomen worden (mits metOntvangenOp True is)

        Geeft een Filtervoorschrift terug.
        """
        resultaat = Filtervoorschrift ()
        resultaat.Tijdreisfilter.OntvangenOpAanwezig = True
        resultaat.Tijdreisfilter.BekendOpAanwezig = True
        resultaat.Tijdreisfilter.GeldigVanafAanwezig = True

        bepaalJWVHuidigeToestand = True # Bepaal per ontvangenOp datum wat de JWV van de huidige toestand is
        jwvHuidigeToestand = None
        laatsteOntvangenOp = None # Net zoals in Ex-Nunc tijdreis
        gedaan = Filter_CompleteToestanden._TijdreisParameterBereik () # Net zoals in Ex-Nunc tijdreis
        for idx, toestand in enumerate (self._CompleteToestanden.Toestanden):
            if toestand.GemaaktOp <= self._GemaaktOp:
                if alleenLaatstOntvangen:
                    # Net als bij Ex-Nunc: beperking tot de laatste OntvangenOp
                    if laatsteOntvangenOp is None:
                        laatsteOntvangenOp = toestand.OntvangenOp
                    elif laatsteOntvangenOp != toestand.OntvangenOp:
                        break
                else:
                    # Ex-Tunc: bij verandering van datum kan de huidige toestand anders worden
                    if laatsteOntvangenOp is None or laatsteOntvangenOp != toestand.OntvangenOp:
                        laatsteOntvangenOp = toestand.OntvangenOp
                        bepaalJWVHuidigeToestand = True

                if bepaalJWVHuidigeToestand:
                    bepaalJWVHuidigeToestand = False
                    jwvHuidigeToestand = None
                    # De jwv van de huidige toestand is de eerste jwv in de toestanden
                    # met index >= idx die kleiner dan of gelijk is aan toestand.OntvangenOp
                    bekijkIdx = idx
                    while bekijkIdx < len (self._CompleteToestanden.Toestanden):
                        bekijkToestand = self._CompleteToestanden.Toestanden[bekijkIdx]
                        if bekijkToestand.GemaaktOp <= self._GemaaktOp:
                            if bekijkToestand.JuridischWerkendVanaf <= laatsteOntvangenOp:
                                jwvHuidigeToestand = bekijkToestand.JuridischWerkendVanaf
                                break
                        bekijkIdx += 1

                if not jwvHuidigeToestand is None and toestand.JuridischWerkendVanaf < jwvHuidigeToestand:
                    # Ex-Tunc: dit is een historische toestand; weglaten
                    continue

                # Nu verder als bij Ex-Nunc
                if gedaan.IsToestandBereisbaar (toestand.OntvangenOp, toestand.JuridischWerkendVanaf):
                    # Deze toestand moet meegenomen worden
                    resultaat.ToestandIndex.add (toestand.UniekId)

        return resultaat

#======================================================================
#
# Maken van een CompleteToestanden module
#
#======================================================================

    def MaakModule (self, voorschrift : Filtervoorschrift):
        """Maak de COmpleteToestanden module passend bij het tijdreisfilter

        Argumenten:

        voorschrift Filtervoorschrift  Selectie van toestanden zoals eerder berekend

        Geeft de CompleteModule terug met alle indices e.d. pasgemaakt op het filter.
        """
        module = CompleteToestanden ()
        module.OntvangenOp = self._CompleteToestanden.OntvangenOp
        module.BekendOp = self._CompleteToestanden.BekendOp
        module.MaterieelUitgewerktOp = self._CompleteToestanden.MaterieelUitgewerktOp
        module.Tijdreisfilter = voorschrift.Tijdreisfilter
        module.ToestandIdentificatie = []
        module.ToestandInhoud = []

        vertaalIdentiteit = {} # key = oorspronkelijke index, value = nieuwe index
        vertaalInhoud = {} # key = oorspronkelijke index, value = nieuwe index

        for toestand in self._CompleteToestanden.Toestanden:
            if toestand.GemaaktOp <= self._GemaaktOp and toestand.UniekId in voorschrift.ToestandIndex:
                # Deze toestand moet meegenomen worden, maar met andere waarden
                nieuw = Toestand ()
                module.Toestanden.append (nieuw)

                # Kopieer de relevante tijdstempels
                if voorschrift.Tijdreisfilter.OntvangenOpAanwezig:
                    nieuw.OntvangenOp = toestand.OntvangenOp
                if voorschrift.Tijdreisfilter.BekendOpAanwezig:
                    nieuw.BekendOp = toestand.BekendOp
                nieuw.JuridischWerkendVanaf = toestand.JuridischWerkendVanaf
                if voorschrift.Tijdreisfilter.GeldigVanafAanwezig:
                    nieuw.GeldigVanaf = toestand.GeldigVanaf

                # Kopieer de identiteit; die krijgt (meestal) een nieuwe index
                idx = vertaalIdentiteit.get (toestand.Identificatie)
                if not idx is None:
                    vertaalIdentiteit[toestand.Identificatie] = len (module.ToestandIdentificatie)
                    module.ToestandIdentificatie.append (self._CompleteToestanden.ToestandIdentificatie[toestand.Identificatie])
                nieuw.Identificatie = idx

                # Kopieer de inhoud; die krijgt (meestal) een nieuwe index
                idx = vertaalInhoud.get (toestand.Inhoud)
                if not idx is None:
                    vertaalInhoud[toestand.Inhoud] = len (module.ToestandInhoud)
                    module.ToestandInhoud.append (self._CompleteToestanden.ToestandInhoud[toestand.Inhoud])
                nieuw.Inhoud = idx

        return module
