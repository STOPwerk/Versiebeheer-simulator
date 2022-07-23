#======================================================================
#
# Geautomatiseerde consolidatie
#
#----------------------------------------------------------------------
#
# Proces van het inlezen (/ontvangen) van consolidatie informatie in
# het interne datamodel, en het afleiden van de proefversies en
# geconsolideerde regelingen/informatieobjecten behorend bij de laatst
# aangeleverde consolidatie-informatie.
# 
# De resultaten worden in een webpagina bij het scenario bewaard
#
#======================================================================

from data_scenario import Scenario
from weergave_resultaat_data import WeergaveData
from proces_versiebeheerinformatie import WerkVersiebeheerinformatieBij
from proces_proefversies import MaakProefversies
from proces_completetoestanden import MaakCompleteToestanden
from proces_actueletoestanden import MaakActueleToestanden
from proces_actueleannotaties import MaakActueleToestandenMetAnnotaties

#======================================================================
#
# Uitvoeren van de geautomatiseerde consolidatie
#
#======================================================================
class Proces_Consolidatie:

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
        """Voer de geautomatiseerde consolidatie uit"""
        try:
            self.Scenario.Log.Informatie ("Voer de gaautomatiseerde consolidatie uit")
            self.Scenario.WeergaveData = WeergaveData (self.Scenario)

            for idx, consolidatieInformatie in enumerate (self.Scenario.ConsolidatieInformatie):
                publicatieblad = 'pb{:03d}'.format (idx)
                volgendeGemaaktOp = self.Scenario.ConsolidatieInformatie[idx+1].GemaaktOp if idx < len (self.Scenario.ConsolidatieInformatie) - 1 else None

                # Verwerk de uitgewisselde consolidatie-informatie. Een productie-waardige applicatie begint
                # hier met de verwerking na ontvangst van een uitwisseling
                self.Scenario.Log.Informatie ("Verwerk de consolidatie-informatie ontvangen op " + consolidatieInformatie.OntvangenOp + " (@" + consolidatieInformatie.GemaaktOp + ")")

                # In een productie-waardige applicatie die tijdreizen op bekendOp ondersteund zou de verwerking per bekendOp-datum
                # die in de consolidatie-informatie module gedaan kunnen worden, omdat de geraakte instrumenten daarvan afhankelijk zijn.
                # Dat is een optimalisatie: in deze applicatie wordt het niet zo gedaan en dat leidt tot dezelfde resultaten
                uitwisseling = WerkVersiebeheerinformatieBij.VoerUit (self.Scenario.Log, self.Scenario.Versiebeheerinformatie, publicatieblad, consolidatieInformatie)
                if not uitwisseling.IsValide:
                    return

                alleProefversies = {} # key = workId, value = lijst met proefversies
                if self.Scenario.Opties.Proefversies or self.Scenario.Opties.ActueleToestanden or self.Scenario.Opties.CompleteToestanden:
                    # Doe de consolidatie alleen voor de geraakte instrumenten
                    for workId in uitwisseling.InstrumentDoelen:
                        geconsolideerd = self.Scenario.GeconsolideerdeInstrument (workId)
                        geconsolideerd.MaakIdentificatie (self.Scenario.Log, self.Scenario.Versiebeheerinformatie)

                        if self.Scenario.Opties.ActueleToestanden or self.Scenario.Opties.CompleteToestanden:
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

                        if self.Scenario.Opties.CompleteToestanden:
                            self.Scenario.Log.Informatie ("Bepaal de complete toestanden voor " + workId)
                            # In deze applicatie moeten de complete toestanden voor de actuele toestanden bepaald worden, want
                            # de meldingen over het bepalen van de (complete) toestanden worden bewaard bij het eerste voorkomen 
                            # van een toestand. In een productie-waardige applicatie kan ervoor gekozen worden alleen de actuele
                            # toestanden te ondersteunen en deze stap over te slaan.
                            MaakCompleteToestanden.VoerUit (self.Scenario.Log, geconsolideerd, uitwisseling.Uitwisseling.GemaaktOp, uitwisseling.Uitwisseling.OntvangenOp, uitwisseling.EersteBekendOp[workId])

                        if self.Scenario.Opties.ActueleToestanden:
                            # De actuele toestanden zijn afleidbaar uit de complete toestanden. Een productie-waardige
                            # applicatie die tijdreizen ondersteunt zal deze bepaling daarom niet uitvoeren.
                            self.Scenario.Log.Informatie ("Bepaal de actuele toestanden voor " + workId)
                            MaakActueleToestanden.VoerUit (self.Scenario.Log, geconsolideerd, uitwisseling.Uitwisseling.GemaaktOp, uitwisseling.Uitwisseling.OntvangenOp, uitwisseling.Uitwisseling.BekendOp)

                            if len (self.Scenario.Annotaties) > 0:
                                MaakActueleToestandenMetAnnotaties.VoerUit (geconsolideerd, self.Scenario.Annotaties, uitwisseling.Uitwisseling.GemaaktOp, volgendeGemaaktOp)

                # Werk de data bij die nodig is voor de weergave
                self.Scenario.WeergaveData.WerkBij (uitwisseling.Uitwisseling, uitwisseling.InstrumentDoelen.keys(), uitwisseling.Doelen, alleProefversies)

        except Exception as e:
            self.Scenario.Log.Fout ("Potverdorie, een fout in de consolidatie die niet voorzien werd: " + str(e))
