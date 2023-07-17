#======================================================================
#
# Simulatie
#
#----------------------------------------------------------------------
#
# Dit is de simulatie van het uitvoeren van versiebeheer door het bevoegd
# gezag, het ontvangen van consolidatie-informatie en het uitvoeren van
# de geautomatiseerde consolidatie door het ontvangende systeem.
#
# In dit proces zit niet het uitwisselen/bewaren van de informatie.
# Alle consolidatie-informatie is al ingelezen of wordt gemaakt via het
# interne in-memory datamodel, waarin ook de resultaten worden opgeslagen.
#
#======================================================================
from typing import List, Dict, Set, Tuple
from applicatie_meldingen import Meldingen

from applicatie_scenario import Scenario, BenoemdeUitwisseling
import applicatie_versie
from weergave_resultaat_data import WeergaveData
from proces_versiebeheerinformatie import WerkVersiebeheerinformatieBij
from proces_proefversies import MaakProefversies, Proefversie
from proces_completetoestanden import MaakCompleteToestanden
from proces_actueletoestanden import MaakActueleToestanden
from weergave_data_stop_uitwisseling import STOPModuleUitwisseling

#======================================================================
#
# Uitvoeren van de simulatie
#
#======================================================================
class Proces_Simulatie:

    def __init__ (self, scenario : Scenario):
        """Maak een nieuwe instantie voor het proces
        
        Argumenten:
        scenario Scenario  Invoer voor het consolidatie-scenario
        """
        self.Scenario = scenario

#----------------------------------------------------------------------
# Hoofdproces
#----------------------------------------------------------------------
    def VoerUit (self):
        """Voer de simulatie uit"""
        try:
            self.Scenario.Log.Informatie ('<a href="https://github.com/STOPwerk/Versiebeheer-simulator">Versiebeheer-simulator</a> ' + applicatie_versie.Applicatie_versie ())
            self.Scenario.Log.Informatie ("Voer de simulatie uit")
            self.Scenario.WeergaveData = WeergaveData (self.Scenario)

            publicatiebladNummer = 0
            for idx, consolidatieInformatie in enumerate (self.Scenario.Uitwisselingen):

                self.Scenario.STOPUitwisselingen.VoegToe (consolidatieInformatie.GemaaktOp, STOPModuleUitwisseling.Systeem_BevoegdGezag, STOPModuleUitwisseling.Systeem_LVBB, consolidatieInformatie)
                publicatie = None
                publicatiebron = None
                activiteit = None
                voerConsolidatieUit = consolidatieInformatie.VoerConsolidatieUit

                # Zit er een publicatie aan vast?
                if self.Scenario.Opties.IsRevisie (consolidatieInformatie.GemaaktOp):
                    publicatie = None
                    consolidatieInformatie.IsRevisie = True
                else:
                    publicatiebladNummer += 1
                    publicatie = 'pb{:03d}'.format (publicatiebladNummer)
                    if publicatiebron is None:
                        publicatiebron = 'Bekendmaking'

                # Verwerk de uitgewisselde consolidatie-informatie. Een productie-waardige (ontvangende) applicatie begint
                # hier met de verwerking na ontvangst van een uitwisseling
                self.Scenario.Log.Informatie ("Verwerk de consolidatie-informatie ontvangen op " + consolidatieInformatie.OntvangenOp + " (@" + consolidatieInformatie.GemaaktOp + ")")

                # Voeg de uitwisseling toe aan het interne versiebeheer-datamodel van het ontvangende systeem
                uitwisseling = WerkVersiebeheerinformatieBij.VoerUit (self.Scenario.Log, self.Scenario.Versiebeheerinformatie, publicatie, consolidatieInformatie)
                if not uitwisseling.IsValide:
                    return

                proefversies : Dict[str, List[Proefversie]] = {} # key = workId, value = lijst met proefversies
                if self.Scenario.Opties.Proefversies:
                    # In deze applicatie worden proefversies alleen gemaakt als er annotaties zijn gespecificeerd.
                    self.Scenario.Log.Informatie ("Bepaal de proefversies voor alle instrumentversies in de uitwisseling")
                    proefversies = MaakProefversies.VoerUit (self.Scenario.Log, self.Scenario.Versiebeheerinformatie, uitwisseling.Uitwisseling.Instrumentversies, self.Scenario.Annotaties, self.Scenario.STOPUitwisselingen.Uitwisselingen[consolidatieInformatie.GemaaktOp])

                if voerConsolidatieUit and (self.Scenario.Opties.ActueleToestanden or self.Scenario.Opties.CompleteToestanden):
                    # Doe de consolidatie alleen voor de geraakte instrumenten
                    for workId in sorted (uitwisseling.Instrumenten): # Sortering om zeker te zijn van iedere keer dezelfde volgorde van uitvoering
                        geconsolideerd = self.Scenario.GeconsolideerdeInstrument (workId)
                        geconsolideerd.MaakIdentificatie (self.Scenario.Log, self.Scenario.Versiebeheerinformatie)

                        if voerConsolidatieUit and (self.Scenario.Opties.ActueleToestanden or self.Scenario.Opties.CompleteToestanden):
                            # De LVBB zal de juridische verantwoording bijwerken als de uitwisseling tot een
                            # publicatie leidt. In deze applicatie wordt aangenomen dat elke uitwisseling tot
                            # een publicatie leidt. De juridische verantwoording is in deze applicatie alleen
                            # nodig om alternatieve weergaven te bepalen voor toestanden waarvan de inhoud
                            # onbekend is. Daarom wordt de juridische verantwoording alleen bijgewerkt als
                            # toestanden bepaald moeten worden.
                            self.Scenario.Log.Informatie ("Werk de juridische verantwoording bij voor " + workId)
                            geconsolideerd.JuridischeVerantwoording.VoegToe (uitwisseling.Verantwoording.get (workId))

                        if voerConsolidatieUit and self.Scenario.Opties.CompleteToestanden:
                            eersteBekendOp = uitwisseling.EersteBekendOp.get (workId)
                            if not eersteBekendOp is None: # is None bij alleen doorgifte MaterieelUitgewerkt
                                self.Scenario.Log.Informatie ("Bepaal de complete toestanden voor " + workId)
                                # In deze applicatie moeten de complete toestanden voor de actuele toestanden bepaald worden, want
                                # de meldingen over het bepalen van de (complete) toestanden worden bewaard bij het eerste voorkomen 
                                # van een toestand. In een productie-waardige applicatie kan ervoor gekozen worden alleen de actuele
                                # toestanden te ondersteunen en deze stap over te slaan.
                                MaakCompleteToestanden.VoerUit (self.Scenario.Log, geconsolideerd, uitwisseling.Uitwisseling.GemaaktOp, uitwisseling.Uitwisseling.OntvangenOp, eersteBekendOp)

                        if voerConsolidatieUit and self.Scenario.Opties.ActueleToestanden:
                            # De actuele toestanden zijn afleidbaar uit de complete toestanden. Een productie-waardige
                            # applicatie die tijdreizen ondersteunt zal deze bepaling daarom niet uitvoeren.
                            self.Scenario.Log.Informatie ("Bepaal de actuele toestanden voor " + workId)
                            MaakActueleToestanden.VoerUit (self.Scenario.Log, geconsolideerd, uitwisseling.Uitwisseling.GemaaktOp, uitwisseling.Uitwisseling.OntvangenOp, uitwisseling.Uitwisseling.BekendOp)

                # Werk de data bij die nodig is voor de weergave
                self.Scenario.WeergaveData.WerkBij (uitwisseling.Uitwisseling, uitwisseling.Instrumenten, uitwisseling.Doelen, proefversies, self.Scenario.STOPUitwisselingen.Uitwisselingen[consolidatieInformatie.GemaaktOp])

        except Exception as e:
            self.Scenario.Log.Fout ("Potverdorie, een fout in de simulatie die niet voorzien werd: " + str(e))
