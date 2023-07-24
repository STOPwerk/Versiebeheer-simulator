#======================================================================
#
# Opties voor het simulatieproces (invoer)
#
#----------------------------------------------------------------------
#
# De opties kunnen in een json bestand als onderdeel van het scenario
# gespecificeerd worden.
#
#======================================================================

from typing import Dict, List

from stop_consolidatieinformatie import ConsolidatieInformatie

#======================================================================
#
# Opties voor het (gedeeltelijk) uitvoeren van het consolidatieproces
#
#======================================================================
class ProcesOpties:

    def __init__ (self, defaultSelectie = None):
        """Maak default opties aan voor het uitvoeren van het proces"""
        # Geeft aan dat de actuele toestanden berekend moeten worden
        self.ActueleToestanden = True if defaultSelectie is None else defaultSelectie
        # Geeft aan dat de complete toestanden berekend moeten worden
        self.CompleteToestanden = True if defaultSelectie is None else defaultSelectie
        # Geeft aan dat de webpagina met resultaten gemaakt wordt
        self.Applicatie_Resultaat = True
        # Titel (tekst) van het scenario
        self.Titel = None
        # Beschrijving (html) van het scenario
        self.Beschrijving = None
        # Benoemde uitwisselingen in het scenario
        self.Uitwisselingen : List[BenoemdeUitwisseling] = []
        # Benoemde tijdreizen in het scenario
        # Key = work-ID
        self.Tijdreizen : Dict[str,List[BenoemdeTijdreis]] = {}
        # Geeft aan dat de map een scenario voor de simulator bevat
        self.SimulatorScenario = True
        # Geeft aan dat de proefversies berekend moeten worden
        # Proefversies worden alleen berekend als annotaties onderdeel zijn van het scenario
        # self.Proefversies = False
        # Geeft aan of er fouten zijn gesignaleerd bij het inlezen van de specificatie
        self.IsValide = True

    def IsRevisie (self, gemaaktOp):
        """Geeft aan of een uitwisseling een revisie is of een uitwisseling tussen BG en adviesbureau"""
        for uitwisseling in self.Uitwisselingen:
            if uitwisseling.GemaaktOp == gemaaktOp:
                return uitwisseling.IsRevisie
        return False

#----------------------------------------------------------------------
# Inlezen specificatie
#----------------------------------------------------------------------
    @staticmethod
    def LeesJson (log, pad, data):
        """Lees de opties uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        data string  JSON specificatie van de Procesopties
        
        Resultaat van de methode is een ProcesOpties instantie, of None als de JSON 
        geen specificatie van de ProcesOpties is
        """
        gevonden = "Procesopties" in data
        opties = ProcesOpties (data["Procesopties"] if gevonden else None)
        for optie in opties.__dict__:
            if optie in data:
                if hasattr (opties, optie):
                    gevonden = True
                    if optie == 'Titel':
                        if not isinstance (data[optie], str):
                            log.Fout ("Bestand '" + pad + "': '" + optie + "' moet als waarde een string hebben")
                            opties.IsValide = False
                            continue
                        opties.Titel = data[optie]

                    elif optie == 'Beschrijving':
                        if not isinstance (data[optie], str):
                            log.Fout ("Bestand '" + pad + "': '" + optie + "' moet als waarde een string hebben")
                            opties.IsValide = False
                            continue
                        opties.Beschrijving = data[optie]

                    elif optie == 'Uitwisselingen':
                        if not isinstance (data[optie], list):
                            log.Fout ("Bestand '" + pad + "': '" + optie + "' moet als waarde een array van objecten hebben")
                            opties.IsValide = False
                            continue
                        for item in data[optie]:
                            uitwisseling = BenoemdeUitwisseling.LeesJson (log, pad, item)
                            if not uitwisseling is None:
                                opties.Uitwisselingen.append (uitwisseling)
                            else:
                                opties.IsValide = False

                    elif optie == 'Tijdreizen':
                        if not isinstance (data[optie], dict):
                            log.Fout ("Bestand '" + pad + "': '" + optie + "' moet als waarde een ander object hebben")
                            opties.IsValide = False
                            continue

                        for workId, lijst in data[optie].items():
                            if not isinstance (lijst, list):
                                log.Fout ("Bestand '" + pad + "': '" + workId + "' in '" + optie + "' moet als waarde een array van objecten hebben")
                                opties.IsValide = False
                                continue
                            opties.Tijdreizen[workId] = reizen = []
                            for item in lijst:
                                tijdreis = BenoemdeTijdreis.LeesJson (log, pad, item)
                                if not tijdreis is None:
                                    reizen.append (tijdreis)
                                else:
                                    opties.IsValide = False
                    else:
                        if not isinstance (data[optie], bool):
                            log.Fout ("Bestand '" + pad + "': '" + optie + "' moet als waarde true of false hebben")
                            opties.IsValide = False
                            continue
                        setattr (opties, optie, data[optie])
        if gevonden:
            return opties

#----------------------------------------------------------------------
# Benoemde uitwisseling
#----------------------------------------------------------------------
class BenoemdeUitwisseling:

    def __init__ (self):
        # Korte naam van de uitwisseling
        self.Naam = None
        # Tijdstip van de uitwisseling
        self.GemaaktOp = None
        # Beschrijving van de uitwisseling
        self.Beschrijving = None
        # Geeft aan dat het om een revisie gaat
        self.IsRevisie = False

    @staticmethod
    def LeesJson (log, pad, data):
        """Lees de instantie uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        data {}  JSON specificatie van de uitwisseling
        
        Resultaat van de methode is een BenoemdeUitwisseling of None
        """
        uitwisseling = BenoemdeUitwisseling ()
        if not isinstance (data, dict):
            log.Fout ("Bestand '" + pad + "': 'Uitwisselingen' moet als waarde een array van objecten hebben")
            return

        isValide = True
        if not "naam" in data or not isinstance (data["naam"], str):
            log.Fout ("Bestand '" + pad + "': elk object in 'Uitwisselingen' moet een 'naam' (string) hebben")
            isValide = False
        else:
            uitwisseling.Naam = data["naam"]

        if not "gemaaktOp" in data or not isinstance (data["gemaaktOp"], str):
            log.Fout ("Bestand '" + pad + "': elk object in 'Uitwisselingen' moet een 'gemaaktOp' (string) hebben")
            isValide = False
        else:
            uitwisseling.GemaaktOp = data["gemaaktOp"]
            if not ConsolidatieInformatie.ValideerGemaaktOp (log, pad, uitwisseling.GemaaktOp):
                isValide = False

        if "beschrijving" in data:
            if not isinstance (data["beschrijving"], str):
                log.Fout ("Bestand '" + pad + "': de 'beschrijving' in 'Uitwisselingen' moet een string zijn")
                isValide = False
            else:
                uitwisseling.Beschrijving = data["beschrijving"]

        if "revisie" in data:
            if not isinstance (data["revisie"], bool):
                log.Fout ("Bestand '" + pad + "': de 'revisie' in 'Uitwisselingen' moet een boolean zijn")
                isValide = False
            else:
                uitwisseling.IsRevisie = data["revisie"]

        if isValide:
            return uitwisseling

#----------------------------------------------------------------------
# Benoemde tijdreis
#----------------------------------------------------------------------
class BenoemdeTijdreis:

    def __init__ (self):
        # Tijdreisparameter: ontvangenOp
        self.ontvangenOp = None
        # Tijdreisparameter: bekendOp
        self.bekendOp = None
        # Tijdreisparameter: juridischWerkendOp
        self.juridischWerkendOp = None
        # Tijdreisparameter: geldigOp
        self.geldigOp = None
        # Beschrijving van de tijdreis
        self.Beschrijving = None

    @staticmethod
    def LeesJson (log, pad, data):
        """Lees de instantie uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        data {}  JSON specificatie van de tijdreis
        
        Resultaat van de methode is een BenoemdeTijdreis of None
        """
        tijdreis = BenoemdeTijdreis ()
        if not isinstance (data, dict):
            log.Fout ("Bestand '" + pad + "': 'Tijdreizen' moet als waarde een array van objecten hebben")
            return

        isValide = True
        for naam in ["ontvangenOp", "bekendOp", "juridischWerkendOp", "geldigOp"]:
            if not naam in data or not isinstance (data[naam], str):
                log.Fout ("Bestand '" + pad + "': elk object in 'Tijdreizen' moet een " + naam + " (string) hebben")
                isValide = False
            else:
                setattr (tijdreis, naam, data[naam])
                if not ConsolidatieInformatie.ValideerDatum (log, pad, naam, data[naam]):
                    isValide = False
        
        if "beschrijving" in data:
            if not isinstance (data["beschrijving"], str):
                log.Fout ("Bestand '" + pad + "': de beschrijving in 'Tijdreizen' moet een string zijn")
                isValide = False
            else:
                tijdreis.Beschrijving = data["beschrijving"]
        else:
            log.Fout ("Bestand '" + pad + "': elke tijdreis in 'Tijdreizen' moet een beschrijving hebben")
            isValide = False

        if isValide:
            return tijdreis
                    
