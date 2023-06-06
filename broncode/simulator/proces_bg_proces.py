#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# De activiteiten die het bevoegd gezag kan uitvoeren zijn geformuleerd
# als stappen in het proces van opstellen, uitwisselen en 
# consolideren van regelgeving. Productie-waardige software
# zou een eindgebruiker aan de hand nemen en aangeven welke versies
# van de regelgeving gemaakt moeten worden. In deze simulator
# uit zich dat in de argumenten voor een actie, en de validatie
# of een actie passend is gezien de staat van de regelgeving.
#
# BGProces in deze module valideert of een actie 
# uitgevoerd kan worden, en bepaalt daarna het effect van de actie 
# op (de simulatie van) het interne versiebeheer van het bevoegd
# gezag. Het laat ook zien welke aanvullende instructies aan BG 
# gegeven moeten worden om de activiteit uit te voeren.
#
# De systematiek is: de specificatie (typisch bg_proces.json) bevat
# de specificatie van een Activiteit. De klasse voor een specifieke
# Activiteit implementeert ook de uitvoering ervan. Die resulteert
# enerzijds in een Procesbegeleiding - een beschrijving van de
# activiteit plus instructies voor de uitvoering ervan - en anderzijds
# in het bijwerken van het BG-versiebeheer.
#
# Om de code inzichtelijker te maken is elke activiteit in een aparte
# Python module geplaatst. Deze module importeert alle activiteit-
# modules in de goede volgorde.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from datetime import datetime

from applicatie_meldingen import Meldingen
from data_validatie import Valideer
from proces_bg_activiteit import Activiteit
from proces_bg_activiteit_uitgangssituatie import Activiteit_Uitgangssituatie
from proces_bg_activiteit_download import Activiteit_Download
from proces_bg_activiteit_uitwisseling import Activiteit_Uitwisseling
from proces_bg_activiteit_wijzig import Activiteit_Wijzig
from proces_bg_activiteit_maakbranch import Activiteit_MaakBranch
from proces_bg_activiteit_bijwerken_uitgangssituatie import Activiteit_BijwerkenUitgangssituatie
from proces_bg_activiteit_publiceer import Activiteit_Publiceer
from proces_bg_activiteit_besluit import Activiteit_PubliceerBesluit

#======================================================================
#
# Representatie van de specificatie van het proces bij een BG
# (inclusief adviesbureaus).
#
#======================================================================

class BGProces:
#----------------------------------------------------------------------
# Inlezen specificatie
#----------------------------------------------------------------------
    @staticmethod
    def LeesJson (log : Meldingen, pad : str, data):
        """Lees de inhoud van de module uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        data string  JSON specificatie van het proces
        
        Resultaat van de methode is een BGProces instantie, of None als de JSON 
        geen specificatie van het BG proces is
        """
        if not "BGCode" in data:
            return None
        bgprocess = BGProces ()
        bgprocess.BGCode = data["BGCode"]
        if "Beschrijving" in data:
            bgprocess.Beschrijving = data["Beschrijving"]
        if "Startdatum" in data:
            if Valideer.Datum (data["Startdatum"]) is None:
                log.Fout ("Startdatum (" + data["Startdatum"] + ") is geen valide datum in '" + pad + "'")
                bgprocess._IsValide = False
            else:
                try:
                    bgprocess._Startdatum = datetime (int (data["Startdatum"][0:4]), int (data["Startdatum"][5:7]), int (data["Startdatum"][8:10]))
                except Exception as e:
                    log.Fout ("Startdatum is geen valide datum in '" + pad + "': " + str(e))
                    bgprocess._IsValide = False
        else:
            log.Fout ("Startdatum ontbreekt in '" + pad + "'")
            bgprocess._IsValide = False

        def _LeesActiviteit (project, data, activiteit : Activiteit = None):
            if activiteit is None:
                if not "Soort" in data:
                    log.Fout ("Soort ontbreekt in een activiteit van " + ("'Overig'" if project is None else "project '" + project + "'") + " in '" + pad + "'")
                    bgprocess._IsValide = False
                    return
                constructor = BGProces._Constructors.get (data["Soort"])
                if constructor is None:
                    log.Fout ("Onbekende Soort='" + data["Soort"] + "' voor een activiteit van " + ("'Overig'" if project is None else "project '" + project + "'") + " in '" + pad + "'")
                    bgprocess._IsValide = False
                    return
                activiteit = constructor ()
                activiteit._Soort = data["Soort"]
                del data["Soort"]
            activiteit._BGProcess = bgprocess
            activiteit._Data = data
            activiteit.Project = project
            if not activiteit.LeesJson (log, pad):
                bgprocess._IsValide = False
            if bgprocess._IsValide:
                bgprocess.Activiteiten.append (activiteit)

        if "Uitgangssituatie" in data:
            activiteit = Activiteit_Uitgangssituatie ()
            data["Uitgangssituatie"]["Tijdstip"] = 0
            _LeesActiviteit (None, data["Uitgangssituatie"], activiteit)

        if "Projecten" in data:
            for project, activiteiten in data["Projecten"].items ():
                bgprocess.Projecten.add (project)
                for activiteit in activiteiten:
                    _LeesActiviteit (project, activiteit)
        if "Overig" in data:
            for activiteit in data["Overig"]:
                _LeesActiviteit (None, activiteit)

        if bgprocess._IsValide:
            if len (bgprocess.Activiteiten) == 0:
                log.Waarschuwing ("Geen activiteiten gespecificeerd in '" + pad + "': " + str(e))
            else:
                bgprocess.Activiteiten.sort (key = lambda x: x.UitgevoerdOp)
        return bgprocess

    _Constructors = {
        "Maak branch": lambda : Activiteit_MaakBranch (),
        "Download": lambda : Activiteit_Download (),
        "Wijziging": lambda : Activiteit_Wijzig (),
        "Uitwisseling": lambda : Activiteit_Uitwisseling (),
        "Bijwerken uitgangssituatie": lambda : Activiteit_BijwerkenUitgangssituatie (),
        "Ontwerpbesluit": lambda : Activiteit_PubliceerBesluit (Activiteit_Publiceer._Soort_Ontwerpbesluit),
        "Vaststellingsbesluit": lambda : Activiteit_PubliceerBesluit (Activiteit_Publiceer._Soort_Vaststellingsbesluit)
    }

#----------------------------------------------------------------------
# Initialisatie en overige eigenschappen
#----------------------------------------------------------------------
    def __init__ (self):
        # Code te gebruiken bij het bepalen van de AKN/JOIN workId
        self.BGCode: str = None
        # Beschrijving van het scenario, als alternatief voor de beschrijving in 
        self.Beschrijving: str = None
        # Startdatum van het scenario; wordt overschreven door de specificatie
        self._Startdatum = datetime.now ()
        # De namen van de projecten in de specificatie
        self.Projecten : Set[str] = set()
        # Ingelezen activiteiten, gesorteerd op het tijdstip van uitvoering
        self.Activiteiten : List[Activiteit] = []
        # Geeft aan of de specificatie valide is
        self._IsValide = True

