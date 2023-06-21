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
from data_bg_versiebeheer import ConsolidatieInformatieVerwerker
from data_bg_procesverloop import Activiteitverloop, UitgewisseldeSTOPModule
from weergave_resultaat_data import WeergaveData
from proces_bg_proces import BGProces
from proces_lv_versiebeheerinformatie import WerkVersiebeheerinformatieBij
from proces_lv_proefversies import MaakProefversies, Proefversie
from proces_lv_completetoestanden import MaakCompleteToestanden
from proces_lv_actueletoestanden import MaakActueleToestanden

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
            for idx, gebeurtenis in enumerate (self.Scenario.Gebeurtenissen):

                publicatie = None
                publicatiebron = None
                activiteit = None
                voerConsolidatieUit = False

                if not gebeurtenis.Activiteit is None:
                    # BG activiteit: voer de actie uit
                    isValide, activiteit = gebeurtenis.Activiteit.VoerUit (self.Scenario.Log, self.Scenario, gebeurtenis)
                    if not isValide:
                        # Er is iets fout gegaan
                        return
                    publicatiebron = activiteit.Publicatiebron

                    if not gebeurtenis.Activiteit.UitwisselingNaam is None:
                        # Gebruik de actie als beschrijving indien aanwezig
                        uwHeeftBeschrijving = False
                        for uw in self.Scenario.Opties.Uitwisselingen:
                            if uw.GemaaktOp == gebeurtenis.Activiteit.UitgevoerdOp:
                                uwHeeftBeschrijving = True
                                uw.IsRevisie = not activiteit.IsPublicatie ()
                        if not uwHeeftBeschrijving:
                            benoemd = BenoemdeUitwisseling ()
                            benoemd.GemaaktOp = gebeurtenis.Activiteit.UitgevoerdOp 
                            benoemd.Naam = gebeurtenis.Activiteit.UitwisselingNaam
                            benoemd.Beschrijving = gebeurtenis.Activiteit.Beschrijving
                            benoemd.IsRevisie = gebeurtenis.Activiteit.SoortPublicatie is None
                            self.Scenario.Opties.Uitwisselingen.append (benoemd)

                if gebeurtenis.ConsolidatieInformatie is None:
                    # Geen uitwisseling met ontvangende systemen/landelijke voorzieningen
                    continue

                # Specificatie van consolidatie-informatie
                if self.Scenario.Opties.BGProces and gebeurtenis.Activiteit is None:
                    # Verwerk dat in het versiebeheer van het bevoegd gezag
                    isValide = ConsolidatieInformatieVerwerker.WerkBij (self.Scenario.Log, self.Scenario, gebeurtenis.ConsolidatieInformatie)
                    if not isValide:
                        # Er is iets fout gegaan
                        return

                voerConsolidatieUit = gebeurtenis.ConsolidatieInformatie.VoerConsolidatieUit
                if self.Scenario.Opties.BGProces and voerConsolidatieUit:
                    isValide = self.Scenario.BGVersiebeheerinformatie.WerkConsolidatieBij (self.Scenario.Log, Meldingen (False) if activiteit is None else activiteit.VersiebeheerVerslag, gebeurtenis.ConsolidatieInformatie.GemaaktOp)
                    if not isValide:
                        # Er is iets fout gegaan
                        return
                    if not activiteit is None:
                        activiteit.Consolidatie = self.Scenario.BGVersiebeheerinformatie.Consolidatie

                # Zit er een publicatie aan vast?
                if self.Scenario.Opties.IsRevisie (gebeurtenis.ConsolidatieInformatie.GemaaktOp):
                    publicatie = None
                    gebeurtenis.ConsolidatieInformatie.IsRevisie = True
                else:
                    publicatiebladNummer += 1
                    publicatie = 'pb{:03d}'.format (publicatiebladNummer)
                    if publicatiebron is None:
                        publicatiebron = 'Bekendmaking'
                if not activiteit is None:
                    activiteit.Publicatie = publicatie

                # Verwerk de uitgewisselde consolidatie-informatie. Een productie-waardige (ontvangende) applicatie begint
                # hier met de verwerking na ontvangst van een uitwisseling
                self.Scenario.Log.Informatie ("Verwerk de consolidatie-informatie ontvangen op " + gebeurtenis.ConsolidatieInformatie.OntvangenOp + " (@" + gebeurtenis.ConsolidatieInformatie.GemaaktOp + ")")

                # Voeg de uitwisseling toe aan het interne versiebeheer-datamodel van het ontvangende systeem
                uitwisseling = WerkVersiebeheerinformatieBij.VoerUit (self.Scenario.Log, self.Scenario.Versiebeheerinformatie, publicatie, gebeurtenis.ConsolidatieInformatie)
                if not uitwisseling.IsValide:
                    return

                alleProefversies : Dict[str, List[Proefversie]] = {} # key = workId, value = lijst met proefversies
                if self.Scenario.Opties.Proefversies or voerConsolidatieUit and (self.Scenario.Opties.ActueleToestanden or self.Scenario.Opties.CompleteToestanden):
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
                        
                        if self.Scenario.Opties.Proefversies:
                            # Voor een productie-waardige applicatie is het maken van een proefversie is alleen 
                            # nodig als andere systemen mee moeten liften met de resultaten uit deze applicatie
                            # om non-STOP annotaties te bepalen c.q. te valideren voor de uitgewisselde instrumentversies.
                            # In deze applicatie wordt het ook gebruikt voor STOP annotaties.
                            self.Scenario.Log.Informatie ("Bepaal de proefversies voor alle instrumentversies in de uitwisseling")
                            proefversies = MaakProefversies.VoerUit (uitwisseling.Uitwisseling, self.Scenario.Annotaties)
                            if len (proefversies) > 0:
                                geconsolideerd.Proefversies.extend (proefversies)
                                alleProefversies[workId] = proefversies

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
                            
                            if not activiteit is None:
                                activiteit.Uitgewisseld.append (UitgewisseldeSTOPModule (workId, geconsolideerd.ActueleToestanden, Activiteitverloop._Uitvoerder_LVBB, Activiteitverloop._Uitvoerder_BevoegdGezag))

                # Werk de data bij die nodig is voor de weergave
                self.Scenario.WeergaveData.WerkBij (uitwisseling.Uitwisseling, uitwisseling.Instrumenten, uitwisseling.Doelen, alleProefversies)

        except Exception as e:
            self.Scenario.Log.Fout ("Potverdorie, een fout in de simulatie die niet voorzien werd: " + str(e))
