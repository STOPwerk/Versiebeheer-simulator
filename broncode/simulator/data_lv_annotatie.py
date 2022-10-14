#======================================================================
#
# In-memory representatie van een annotatie.
#
#======================================================================
#
# In deze applicatie wordt niet de inhoud maar de versie van de
# annotatie bijgehouden. Onderdeel van het scenario is een .json
# bestand met de naam van de annotatie (vrij te kiezen) en de
# gemaaktOp en doelen van de uitwisseling van de annotatie. Deze 
# applicatie brengt de annotatie niet onder in het versiebeheer, 
# maar zal aan de hand van de Proefversie de juiste annotatieversie 
# aan een instrumentversie koppelen, en aan de hand van de complete 
# toestanden een annotatie aan een geconsolideerd instrument.
#
# Het gebruik van de Proefversie om een annotatie aan een
# instrumentversie te koppelen wordt gedaan om te laten zien dat ook
# applicaties die niet over het volledige versiebeheer beschikken
# goed met annotaties kunnen omgaan. In een productie-waardige
# applicatie die over alle versiebeheerinformatie beschikt zal de
# annotatie in samenhang met de instrumentversies beheerd worden, en
# niet via een proefversie gekoppeld worden.
#
#======================================================================

from data_doel import Doel
from stop_consolidatieinformatie import ConsolidatieInformatie
from stop_naamgeving import Naamgeving

#======================================================================
# Specificatie van de uitwisseling van een annotatie
#======================================================================
class Annotatie:

#----------------------------------------------------------------------
# Aanmaken lege module
#----------------------------------------------------------------------
    def __init__ (self):
        """Maak een nieuw uitlevering-overzicht van een annotatie aan"""
        # Naam van de annotatie
        self.Naam = None
        # WorkId van het instrument waar de annotatie bijhoort
        self.WorkId = None
        # Geeft aan of een annotatie meedraait in het versiebeheer
        self.ViaVersiebeheer = None
        # De versies van de annotatie
        # Lijst van instanties van:
        # - AnnotatieMomentopname voor ViaVersiebeheer = True, gesorteerd op gemaaktOp (oplopend)
        # - AnnotatieUitwisseling voor ViaVersiebeheer = False, gesorteerd op ontvangenOp (oplopend)
        self.Versies = []
        # Geeft aan of er fouten zijn gesignaleerd bij het inlezen van de specificatie
        self._IsValide = True
        # Elke annotatie krijgt een nummer (voor weergave) op alfabetische volgorde van de naam
        # Het nummer wordt per work gegeven
        self._Nummer = None

#----------------------------------------------------------------------
# Inlezen specificatie
#----------------------------------------------------------------------
    @staticmethod
    def LeesJson (log, pad, data):
        """Lees de inhoud van de module uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        data string  JSON specificatie van de annotatie
        
        Resultaat van de methode is een Annotatie instantie, of None als de JSON 
        geen specificatie van de annotatie is
        """
        if not "Annotatie" in data:
            return None
        annotatie = Annotatie()

        annotatie.Naam = data["Annotatie"]
        if not isinstance (annotatie.Naam, str):
            log.Fout ("Bestand '" + pad + "': 'Annotatie' moet als waarde een string hebben")
            annotatie._IsValide = False

        if not "Instrument" in data or not isinstance (data["Instrument"], str):
            log.Fout ("Bestand '" + pad + "': 'Instrument' moet aanwezig zijn en als waarde een string hebben")
            annotatie._IsValide = False
        else:
            annotatie.WorkId = data["Instrument"]
            if (not Naamgeving.IsRegeling (annotatie.WorkId) and not Naamgeving.IsInformatieobject (annotatie.WorkId)) or Naamgeving.IsExpression (annotatie.WorkId):
                log.Fout ("Bestand '" + pad + "': 'Instrument' moet de work-identificatie van het instrument zijn")
                annotatie._IsValide = False

        uitwisselingen = None
        if "Uitwisselingen" in data:
            uitwisselingen = data["Uitwisselingen"]
        if not isinstance (uitwisselingen, list):
            log.Fout ("Bestand '" + pad + "': 'Uitwisselingen' moet array zijn")
            annotatie._IsValide = False
        elif len(uitwisselingen) == 0 :
            log.Fout ("Bestand '" + pad + "': 'Uitwisselingen' moet niet-leeg array zijn")
            annotatie._IsValide = False
        else:
            alleGemaaktOp = []
            for spec in uitwisselingen:
                if not isinstance (spec, dict):
                    log.Fout ("Bestand '" + pad + "': element van 'Uitwisselingen' moet een object zijn")
                    annotatie._IsValide = False
                else:
                    if annotatie.ViaVersiebeheer is None:
                        if "GemaaktOp" in spec:
                            annotatie.ViaVersiebeheer = True
                            if "UitgewisseldOp" in spec:
                                log.Fout ("Bestand '" + pad + "': 'GemaaktOp' en 'UitgewisseldOp' kunnen niet samen voorkomen")
                                annotatie._IsValide = False
                        elif "UitgewisseldOp" in spec:
                            annotatie.ViaVersiebeheer = False
                        else:
                            log.Fout ("Bestand '" + pad + "': 'GemaaktOp' of 'UitgewisseldOp' moet voor een uitwisseling opgegeven worden")
                            annotatie._IsValide = False
                            continue

                    if annotatie.ViaVersiebeheer:
                        if not "GemaaktOp" in spec:
                            log.Fout ("Bestand '" + pad + "': 'GemaaktOp' moet bij alle uitwisselingen voorkomen")
                            annotatie._IsValide = False
                            continue
                        else:
                            uitwisseling = AnnotatieMomentopname (annotatie)
                            uitwisseling.GemaaktOp = spec["GemaaktOp"]
                    else:
                        if not "UitgewisseldOp" in spec:
                            log.Fout ("Bestand '" + pad + "': 'UitgewisseldOp' moet bij alle uitwisselingen voorkomen")
                            annotatie._IsValide = False
                            continue
                        else:
                            uitwisseling = AnnotatieUitwisseling (annotatie)
                            uitwisseling.UitgewisseldOp = spec["UitgewisseldOp"]

                    if not uitwisseling.Tijdstip() is None:
                        if not isinstance (uitwisseling.Tijdstip(), str):
                            log.Fout ("Bestand '" + pad + "': tijdstip van uitwisseling moet als waarde een string hebben")
                            annotatie._IsValide = False
                        elif not ConsolidatieInformatie.ValideerGemaaktOp (log, pad, uitwisseling.Tijdstip()):
                            annotatie._IsValide = False
                        elif uitwisseling.Tijdstip() in alleGemaaktOp:
                            log.Fout ("Bestand '" + pad + "': tijdstip van uitwisseling '" +uitwisseling.Tijdstip() + "' komt meerdere keren voor")
                            annotatie._IsValide = False
                        else:
                            alleGemaaktOp.append (uitwisseling.Tijdstip())

                    if not "Doelen" in spec:
                        log.Fout ("Bestand '" + pad + "': 'Uitwisselingen' moet als elementen objecten met 'Doelen' en 'Beschrijving' hebben")
                        annotatie._IsValide = False
                    elif not isinstance (spec["Doelen"], list) or len (spec["Doelen"]) == 0:
                        log.Fout ("Bestand '" + pad + "': 'Doelen' moet als waarde een niet-leeg array van strings hebben")
                        annotatie._IsValide = False
                    else:
                        for doel in spec["Doelen"]:
                            if not isinstance (doel, str):
                                log.Fout ("Bestand '" + pad + "': doel moet als waarde een string hebben")
                                annotatie._IsValide = False
                            else:
                                d = Doel.DoelInstantie (doel)
                                if d in uitwisseling.Doelen:
                                    log.Waarschuwing ("Bestand '" + pad + "': doel '" + doel + "' komt meerdere keren voor in 'Doelen'")
                                else:
                                    uitwisseling.Doelen.append (d)

                    if not "Beschrijving" in spec:
                        log.Fout ("Bestand '" + pad + "': 'Uitwisselingen' moet als elementen objecten met 'Doelen' en 'Beschrijving' hebben")
                        annotatie._IsValide = False
                    elif not isinstance (spec["Beschrijving"], str):
                        log.Fout ("Bestand '" + pad + "': 'Beschrijving' moet als waarde een string hebben")
                        annotatie._IsValide = False
                    else:
                        uitwisseling._Beschrijving = spec["Beschrijving"]

                    annotatie.Versies.append (uitwisseling)

        if annotatie._IsValide:
            # Sorteer de uitwisselingen (alleen voor weergave/testen zodat ze altijd in dezelfde volgorde staan)
            annotatie.Versies.sort (key = lambda u: u.Tijdstip())
            for idx, uitwisseling in enumerate (annotatie.Versies):
                uitwisseling._Nummer = idx + 1

        return annotatie

#----------------------------------------------------------------------
# Specificatie van een annotatieversie
#----------------------------------------------------------------------
class AnnotatieVersie:

    def __init__ (self, annotatie):
        # De annotatie waar de uitwisseling bijhoort
        self._Annotatie = annotatie
        # Doelen waarvoor de versie van de annotatie is gemaakt
        # Lijst van instanties van Doel
        self.Doelen = []
        # Beschrijving van de annotatie (alleen voor weergave)
        self._Beschrijving = None
        # Elke annotatieversie krijgt een nummer (voor weergave) op volgorde van tijdstip
        # Het nummer wordt per annotatie gegeven
        self._Nummer = None

#----------------------------------------------------------------------
# Specificatie van de momentopname van een annotatieversie
#----------------------------------------------------------------------
class AnnotatieMomentopname (AnnotatieVersie):

    def __init__ (self, annotatie):
        super().__init__(annotatie)
        # Tijdstip van de momentopname
        self.GemaaktOp = None

    def Tijdstip (self):
        return self.GemaaktOp

#----------------------------------------------------------------------
# Specificatie van de uitwisseling van aan annotatieversie
#----------------------------------------------------------------------
class AnnotatieUitwisseling (AnnotatieVersie):

    def __init__ (self, annotatie):
        super().__init__(annotatie)
        # Tijdstip van de uitwisseling
        self.UitgewisseldOp = None

    def Tijdstip (self):
        return self.UitgewisseldOp
