#======================================================================
#
# Simulatie van het proces bij BG, waarbij productie-waardige
# software de eindgebruiker bij de hand neemt om een volgende stap
# te zetten in het opstellen/consolideren van regelgeving.
#
#======================================================================
#
# De implementatie van de activiteiten die het bevoegd gezag kan 
# uitvoeren staan elk in een eigen Python module. De Activiteit in
# deze module is de basisklasse voor elk van de activiteiten en
# dient als interface naar de rest van de simulator.
#
#======================================================================

from typing import Dict, List, Set, Tuple

from datetime import timedelta
from math import floor

from applicatie_meldingen import Meldingen
from data_bg_procesverloop import Activiteitverloop, Procesvoortgang, Projectstatus, Branch, UitgewisseldeSTOPModule
from data_bg_versiebeheer import Versiebeheerinformatie, Commit, ConsolidatieInformatieMaker
from stop_consolidatieinformatie import ConsolidatieInformatie

#======================================================================
#
# Basisklasse voor de specificatie en uitvoering van een BG-activiteit
#
#======================================================================
class Activiteit:

#----------------------------------------------------------------------
# Inlezen specificatie
#----------------------------------------------------------------------
    def LeesJson (self, log : Meldingen, pad : str) -> bool:
        """Lees de inhoud van de module uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        
        Resultaat van de methode geeft aan of het inlezen van de activiteit succesvol was
        """
        ok = True
        if "Tijdstip" in self._Data:
            self.UitgevoerdOp = self._LeesTijdstip (self._Data["Tijdstip"], False)
            del self._Data["Tijdstip"]
        else:
            log.Fout ("Tijdstip ontbreekt in een activiteit van " + ("'Overig'" if self.Project is None else "project '" + self.Project + "'") + " in '" + pad + "'")
            ok = False
            self.UitgevoerdOp = '???'

        if not self._LeesData (log, pad):
            ok = False
        return ok

    def _LeesTijdstip (self, data, isDatum: bool):
        """Interpreteer de data als een tijdstip relatief ten opzichte van de startdatum

        Argumenten:
        data  integer, float of string Aantal dagen sinds de startdatum. Het aaltal keer 0.01 in het getal wordt als uren op de dag gelezen.
                                       Als data None is, is het resultaat ook None

        Geeft de datum of het tijdstip als string terug
        """
        if data is None:
            return None
        dag = floor (float (data))
        uur = 0 if isDatum else round (100*(float (data) - dag))
        tijdstip = self._BGProcess._Startdatum + timedelta (days = 0 if dag < 0 else dag, hours = uur if uur < 24 else 24)
        return tijdstip.strftime ("%Y-%m-%d") if isDatum else tijdstip.strftime ("%Y-%m-%dT%H:%M:%SZ")

    def _LeesData (self, log, pad) -> bool:
        """Lees de specificatie van de activiteit uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        
        Resultaat van de methode geeft aan of het inlezen geslaagd is
        """
        raise Exception ("_LeesData niet geïmplementeerd")

#----------------------------------------------------------------------
# Initialisatie en overige eigenschappen
#----------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        # Specificatie van het proces
        self._BGProcess = None
        # Soort activiteit
        self._Soort : str = None
        # Specificatie van de activiteit voor zover niet bij het inlezen omgezets
        self._Data = None
        # Geeft aan dat de activiteit binnen een project uitgevoerd dient te worden
        self._ProjectVerplicht : bool = True
        # Tijdstip waarop de activiteit uitgevoerd is
        self.UitgevoerdOp : str = None
        # Project waarvoor de activiteit uitgevoerd wordt
        self.Project : str = None
        # Als de activiteit leidt tot een uitwisseling: de naam van de uitwisseling
        self.UitwisselingNaam : str = None
        # Beschrijving van de activiteit
        self.Beschrijving : str = None
        # Soort publicatie die volgt uit deze activiteit
        self.SoortPublicatie : str = None

#----------------------------------------------------------------------
# Uitvoering
#----------------------------------------------------------------------
    def VoerUit (self, log : Meldingen, scenario, gebeurtenis) -> Tuple[bool,Activiteitverloop]:
        """Voer de activiteit uit
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        scenario Scenario  Informatie over en uitkomsten van het scenario
        gebeurtenis Scenario.Gebeurtenis Gebeurtenis waarvan deze activiteit onderdeel is
        
        Resultaat van de methode geeft aan of de uitvoering geslaagd is, en geeft het resulterende Activiteitverloop
        """
        activiteitverloop = Activiteitverloop (self.UitgevoerdOp)
        context = Activiteit._VoerUitContext (log, scenario, activiteitverloop)
        
        if not self.Project is None:
            context.ProjectStatus = scenario.Procesvoortgang.Projecten.get (self.Project)
            if context.ProjectStatus is None:
                context.ProjectStatus = Projectstatus (self.Project, self.UitgevoerdOp)
                scenario.Procesvoortgang.Projecten[self.Project] = context.ProjectStatus
            context.Activiteitverloop.UitgevoerdDoor = context.ProjectStatus.UitgevoerdDoor
            context.Activiteitverloop.Projecten.add (self.Project)
        elif self._ProjectVerplicht:
            self._LogFout (context, "de activiteit moet als onderdeel van een project uitgevoerd worden")
            return
        self._VoerUit (context)
        if activiteitverloop.Naam is None:
            activiteitverloop.Naam = self._Soort
        gebeurtenis.ConsolidatieInformatie = context.ConsolidatieInformatieMaker.ConsolidatieInformatie ()
        if not gebeurtenis.ConsolidatieInformatie is None:
            activiteitverloop.Uitgewisseld.append (UitgewisseldeSTOPModule (None, gebeurtenis.ConsolidatieInformatie, Activiteitverloop._Uitvoerder_BevoegdGezag, Activiteitverloop._Uitvoerder_LVBB))
        if not context.ConsolidatieInformatieMaker.IsValide:
            context.Succes = False
        return (context.Succes, context.Activiteitverloop)

    class _VoerUitContext:
        def __init__(self, log : Meldingen, scenario, resultaat: Activiteitverloop):
            self.Log = log;
            self.Scenario = scenario
            self.Procesvoortgang : Procesvoortgang = scenario.Procesvoortgang
            self.Versiebeheer : Versiebeheerinformatie = scenario.BGVersiebeheerinformatie
            # Rapportage over de activiteit
            self.Activiteitverloop = resultaat
            self.Procesvoortgang.Activiteiten.append (resultaat)
            # Status van het project waartoe de activiteit behoort
            self.ProjectStatus : Projectstatus = None 
            # Maker voor de resulterende consolidatie-informatie
            self.ConsolidatieInformatieMaker = ConsolidatieInformatieMaker (log, resultaat.VersiebeheerVerslag, resultaat.UitgevoerdOp)
            # Geeft aan of de uitvoering succesvol was.
            self.Succes = True

        def MaakCommit (self, branch : Branch):
            """Maak een commit voor weergave in de resultaatpagina.

            Argumenten:

            branch Branch  Branch waarvoor de commit aangemaakt is
            gemaaktOp string  Tijdstip van wijziging van de branch
            """
            commit = Commit (self.Activiteitverloop.Commits, branch, self.Activiteitverloop.UitgevoerdOp)
            return commit


    def _VoerUit (self, context: _VoerUitContext):
        """Voer de activiteit uit

        Argumenten:

        context _VoerUitContext Status van de simulatie en en resultaat van de activiteit
        """
        raise Exception ("_VoerUit niet geïmplementeerd")

    def _LogFout (self, context: _VoerUitContext, tekst : str):
        context.Log.Fout (self._MaakMelding (tekst))
        context.Succes = False

    def _MaakMelding (self, tekst : str):
        return "BG activiteit " + self._Soort + " (" + self.UitgevoerdOp + "): " + tekst
