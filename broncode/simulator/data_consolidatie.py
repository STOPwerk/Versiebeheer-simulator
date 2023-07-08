#======================================================================
#
# Informatie over een geconsolideerd instrument
#
#======================================================================
#
# In Python wordt geen onderscheid gemaakt tussen regeling en
# informatieobject; de term "instrument" wordt voor beide gebruikt.
#
# Deze module bevat een in-memory datamodel om alle informatie over een
# geconsolideerd instrument op te slaan, en functionaliteit die op
# verschillende plaatsen binnen de applicatie gebruikt wordt om
# toestanden te bepalen.
#
#======================================================================

from applicatie_meldingen import Melding
from data_toestanden import CompleteToestanden
from stop_completetoestanden import Toestand
from stop_consolidatieidentificatie import ConsolidatieIdentificatie
from stop_juridischeverantwoording import JuridischeVerantwoording
from stop_toestand import Toestandidentificatie
from weergave_toestandbepaling import Weergave_Toestandbepaling

#======================================================================
#
# Datamodel voor het geconsolideerde instrument
#
#======================================================================
class GeconsolideerdInstrument:

    def __init__(self, scenario, instrument):
        """Maak de informatie voor het geconsolideerde instrument aan

        Argumenten:
        scenario Scenario  Scenario dat het geconsolideerde instrument aanmaakt
        instrument Instrument  Het niet=geconsolideerde instrument
        """
        self._Scenario = scenario
        self.Instrument = instrument
        # Identificatie van het geconsolideerde instrument
        # Instantie van ConsolidatieIdentificatie
        self.ConsolidatieIdentificatie = None
        # De actuele toestanden voor het geconsolideerde instrument
        self.ActueleToestanden = None
        # De juridische verantwoording voor de consolidatie
        # Instantie van JuridischeVerantwoording
        self.JuridischeVerantwoording = JuridischeVerantwoording ()
        # Toestanden van het geconsolideerde instrument; volgorde is niet van belang.
        # Dit is de lijst die het uitgangspunt moet zijn voor CompleteToestanden.ToestandIdentificatie
        # Lijst van instanties van ToestandIdentificatie
        self.ToestandIdentificatie = scenario._ToestandIdentificatie
        # Geheugen voor de MaakToestandExpressionId methode
        self._ToestandIdentificaties = {}
        # Er is maar één instantie van de CompleteToestanden die steeds aangeuld wordt.
        # Filteren op de uitwisseling kan via de extra gemaaktOp tijdstempel in de toestanden.
        if scenario.Opties.CompleteToestanden:
            self.CompleteToestanden = CompleteToestanden (self.ToestandIdentificatie)
        else:
            self.CompleteToestanden = None
        # Beschrijvingen van de tijdreizen - alleen nodig voor weergave
        self._Tijdreizen = {}
        if scenario.Opties:
            tijdreizen = scenario.Opties.Tijdreizen.get (instrument.WorkId)
            if not tijdreizen is None:
                for tijdreis in tijdreizen:
                    self._Tijdreizen[tijdreis.ontvangenOp + ':' + tijdreis.bekendOp  + ':' + tijdreis.juridischWerkendOp  + ':' + tijdreis.geldigOp] = tijdreis.Beschrijving

#----------------------------------------------------------------------
# Naamgeving van het geconsolideerde work (volgens AKN / STOP)
#----------------------------------------------------------------------
    def MaakIdentificatie (self, log, versiebeheerinformatie):
        """Bepaal (indien nodig) de work-identificatie van het geconsolideerd instrument
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        versiebeheerinformatie Versiebeheerinformatie Alle versiebeheerinformatie
        """
        if self.ConsolidatieIdentificatie is None:
            eersteDatum = None
            for doel in self.Instrument.Branches:
                # Kijk of er een inwerkingtreding is voor deze branch
                branch = versiebeheerinformatie.Tijdstempels.get (doel)
                if not branch is None:
                    for momentopname in branch.Momentopnamen:
                        if not momentopname.JuridischWerkendVanaf is None:
                            # Als er meer zijn, neem de eerste datum
                            if eersteDatum is None or eersteDatum > momentopname.JuridischWerkendVanaf:
                                eersteDatum = momentopname.JuridischWerkendVanaf
                            break
            if not eersteDatum is None:
                self.ConsolidatieIdentificatie = ConsolidatieIdentificatie (self._Scenario, self.Instrument.WorkId, eersteDatum)
                log.Detail ("Instrument " + self.Instrument.WorkId + " heeft consolidatie " + self.ConsolidatieIdentificatie.WorkId)

#----------------------------------------------------------------------
# Naamgeving van toestanden (volgens AKN / STOP)
#----------------------------------------------------------------------
    def MaakToestandExpressionId (self, toestand : Toestandidentificatie, juridischWerkendVanaf, geldigVanaf, meldingen = None):
        """Maak de expression-ID voor een toestand, en voegt de toestand toe aan 

        Argumenten:
        toestand Toestandidentificatie  Toestand waarvoor de expression-id bepaald moet worden
        juridischWerkendVanaf string  Datum waarop de toestand (voor het eerst) in werking zal treden
        geldigVanaf string  Datum waarop de toestand (voor het eerst) geldig wordt; 
                            mag None zijn als het gelijk is aan juridischWerkendVanaf
        meldingen Melding[] Optioneel: lijst met meldingen om informatie over de constructie van de expressionId
                            aan toe te voegen - uitsluitend nodig voor de weergave.

        Geeft de index in ToestandIdentificatie terug
        """
        # AKN schrijft als datums in de expression voor: <datum_g> [ ";" <datum_iwt> ] 
        datums = juridischWerkendVanaf
        if not geldigVanaf is None and geldigVanaf != juridischWerkendVanaf:
            datums = geldigVanaf + ";" + datums

        # _ToestandIdentificaties: key = datums
        bekendeToestanden = self._ToestandIdentificaties.get (datums)
        if bekendeToestanden is None:
            self._ToestandIdentificaties[datums] = bekendeToestanden = {}

        # Elke combinatie van toestanden wordt als een aparte toestand beschouwd
        # Gebruik de index van de doelen als key voor bekendeToestanden, en het versienummer als value
        # De Inwerkingtredingsdoelen worden bij de constructie van de toestanden altijd op dezelfde
        # manier gesorteerd.
        doelen = ';'.join (str(d.Index) for d in sorted (toestand.Inwerkingtredingsdoelen, key = lambda d: d.Index))
        info = bekendeToestanden.get (doelen)
        if info is None:
            index = len (self.ToestandIdentificatie)
            versie = len (bekendeToestanden) + 1
            self.ToestandIdentificatie.append (toestand)
            # Stel de expression samen
            toestand.ExpressionId = self.ConsolidatieIdentificatie.WorkId + "/nld@" + datums
            if versie > 1:
                toestand.ExpressionId += ";" + str(versie)
            bekendeToestanden[doelen] = (index, toestand.ExpressionId, versie) # versie alleen voor weergave
        else:
            index = info[0]
            toestand.ExpressionId = info[1]
            versie = info[2]

        if not meldingen is None:
            if versie > 1:
                melding = 'Er zijn al toestanden met dezelfde tijdstempels maar met andere inwerkingtredingsdoelen, dit is nummer ' + str(versie) + ': '
            else:
                melding = 'Dit is de eerste toestand met deze tijdstempels: '
            melding = Melding (Melding.Ernst_Informatie, melding + toestand.ExpressionId)
            melding._Stap = Weergave_Toestandbepaling.BepaalToestanden
            meldingen.append (melding)

        return index

#----------------------------------------------------------------------
# Alleen voor weergave: beschrijving van de tijdreizen
#----------------------------------------------------------------------
    def Tijdreis (self, toestand : Toestand):
        """Zoek de tijdreis op voor de toestand. Alleen de eerste die voldoet wordt teruggegeven.
        
        Argumenten:

        toestand Toestand Toestand 
        """
        return self._Tijdreizen.get (toestand.OntvangenOp + ':' + toestand.BekendOp  + ':' + toestand.JuridischWerkendVanaf  + ':' + toestand.GeldigVanaf)

