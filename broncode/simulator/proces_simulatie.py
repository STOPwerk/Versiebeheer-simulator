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

from pickle import NONE
from applicatie_scenario import Scenario
import applicatie_configuratie
from data_bg_project import ProjectActie
from data_bg_projectvoortgang import ProjectactieResultaat, UitgewisseldeSTOPModule
from weergave_data_bg_versiebeheer import VersiebeheerWeergave
from weergave_resultaat_data import WeergaveData
from proces_bg_consolidatieinformatie import ConsolidatieInformatieVerwerker
from proces_bg_procesbegeleiding import Procesbegeleiding
from proces_lv_versiebeheerinformatie import WerkVersiebeheerinformatieBij
from proces_lv_proefversies import MaakProefversies
from proces_lv_completetoestanden import MaakCompleteToestanden
from proces_lv_actueletoestanden import MaakActueleToestanden
from proces_lv_actueleannotaties import MaakActueleToestandenMetAnnotaties

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
            self.Scenario.Log.Informatie ('<a href="https://github.com/STOPwerk/Versiebeheer-simulator">Versiebeheer-simulator</a> ' + applicatie_configuratie.Applicatie_versie)
            self.Scenario.Log.Informatie ("Voer de simulatie uit")
            self.Scenario.WeergaveData = WeergaveData (self.Scenario)

            publicatiebladNummer = 0
            for idx, consolidatieInformatieBron in enumerate (self.Scenario.ConsolidatieInformatie):

                publicatieblad = None
                actieResultaat = None

                if not consolidatieInformatieBron.Module is None:
                    # Specificatie van consolidatie-informatie
                    consolidatieInformatie = consolidatieInformatieBron.Module
                    if self.Scenario.Opties.Versiebeheer:
                        # Verwerk dat in het versiebeheer van het bevoegd gezag
                        isValide, actieResultaat = ConsolidatieInformatieVerwerker.WerkBij (self.Scenario.Log, self.Scenario.Projectvoortgang, consolidatieInformatie, consolidatieInformatieBron.Actie)
                        if not isValide:
                            # Er is iets fout gegaan
                            return
                        # Bewaar een kopie van het interne versiebeheer voor weergave
                        actieResultaat._Versiebeheer = VersiebeheerWeergave (self.Scenario.Projectvoortgang.Versiebeheer)
                else:
                    # Project actie: voer de actie uit
                    isValide, consolidatieInformatie, actieResultaat = Procesbegeleiding.VoerUit (self.Scenario.Log, self.Scenario, consolidatieInformatieBron.Actie)
                    if not isValide:
                        # Er is iets fout gegaan
                        return
                    # Bewaar een kopie van het interne versiebeheer voor weergave
                    actieResultaat._Versiebeheer = VersiebeheerWeergave (self.Scenario.Projectvoortgang.Versiebeheer)
                    if consolidatieInformatie is None:
                        # Geen uitwisseling met ontvangende systemen/landelijke voorzieningen
                        continue

                # Verwerk de uitgewisselde consolidatie-informatie. Een productie-waardige (ontvangende) applicatie begint
                # hier met de verwerking na ontvangst van een uitwisseling
                self.Scenario.Log.Informatie ("Verwerk de consolidatie-informatie ontvangen op " + consolidatieInformatie.OntvangenOp + " (@" + consolidatieInformatie.GemaaktOp + ")")

                # Zit er een publicatie aan vast?
                if self.Scenario.Opties.IsRevisie (consolidatieInformatie.GemaaktOp):
                    publicatieblad = None
                    consolidatieInformatie.IsRevisie = True
                else:
                    publicatiebladNummer += 1
                    publicatieblad = 'pb{:03d}'.format (publicatiebladNummer)

                # Voeg de uitwisseling toe aan het interne versiebeheer-datamodel van het ontvangende systeem
                uitwisseling = WerkVersiebeheerinformatieBij.VoerUit (self.Scenario.Log, self.Scenario.Versiebeheerinformatie, publicatieblad, consolidatieInformatie)
                if not uitwisseling.IsValide:
                    return

                alleProefversies = {} # key = workId, value = lijst met proefversies
                if self.Scenario.Opties.Proefversies or self.Scenario.Opties.ActueleToestanden or self.Scenario.Opties.CompleteToestanden:
                    # Doe de consolidatie alleen voor de geraakte instrumenten
                    for workId in sorted (uitwisseling.Instrumenten): # Sortering om zeker te zijn van iedere keer dezelfde volgorde van uitvoering
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
                            eersteBekendOp = uitwisseling.EersteBekendOp.get (workId)
                            if not eersteBekendOp is None: # is None bij alleen doorgifte MaterieelUitgewerkt
                                self.Scenario.Log.Informatie ("Bepaal de complete toestanden voor " + workId)
                                # In deze applicatie moeten de complete toestanden voor de actuele toestanden bepaald worden, want
                                # de meldingen over het bepalen van de (complete) toestanden worden bewaard bij het eerste voorkomen 
                                # van een toestand. In een productie-waardige applicatie kan ervoor gekozen worden alleen de actuele
                                # toestanden te ondersteunen en deze stap over te slaan.
                                MaakCompleteToestanden.VoerUit (self.Scenario.Log, geconsolideerd, uitwisseling.Uitwisseling.GemaaktOp, uitwisseling.Uitwisseling.OntvangenOp, eersteBekendOp)

                        if self.Scenario.Opties.ActueleToestanden:
                            # De actuele toestanden zijn afleidbaar uit de complete toestanden. Een productie-waardige
                            # applicatie die tijdreizen ondersteunt zal deze bepaling daarom niet uitvoeren.
                            self.Scenario.Log.Informatie ("Bepaal de actuele toestanden voor " + workId)
                            MaakActueleToestanden.VoerUit (self.Scenario.Log, geconsolideerd, uitwisseling.Uitwisseling.GemaaktOp, uitwisseling.Uitwisseling.OntvangenOp, uitwisseling.Uitwisseling.BekendOp)
                            
                            if not actieResultaat is None:
                                actieResultaat.Uitgewisseld.append (UitgewisseldeSTOPModule (geconsolideerd.ActueleToestanden, ProjectactieResultaat._Uitvoerder_LVBB, ProjectactieResultaat._Uitvoerder_BevoegdGezag))

                            if len (self.Scenario.Annotaties) > 0:
                                # De volgendeGemaaktOp is in productie-waardige applicaties bij de verwerking op dit moment natuurlijk
                                # niet bekend. Het wordt hier gebruikt in de zin van: uitgewisseld tegelijk met of na de huidige uitwisseling,
                                # maar voor de volgende uitwisseling. In plaats van eerst de verwerking voor deze uitwisseling af te ronden en
                                # dan naar latere uitwisselingen van uitsluitend annotaties te kijken, wordt hier vooruit gekeken naar de
                                # annotatie-uitwisselingen. Dat is het voorrecht van een simulatie :-)
                                volgendeGemaaktOp = None
                                jdx = idx+1
                                while jdx < len (self.Scenario.ConsolidatieInformatie):
                                    bron = self.Scenario.ConsolidatieInformatie[jdx]
                                    if bron.Actie is None or bron.Actie.SoortActie in ProjectActie._SoortActie_MetUitwisseling:
                                        volgendeGemaaktOp = bron.GemaaktOp()
                                        break
                                    jdx += 1
                                MaakActueleToestandenMetAnnotaties.VoerUit (geconsolideerd, self.Scenario.Annotaties, uitwisseling.Uitwisseling.GemaaktOp, volgendeGemaaktOp)

                # Werk de data bij die nodig is voor de weergave
                self.Scenario.WeergaveData.WerkBij (uitwisseling.Uitwisseling, uitwisseling.Instrumenten, uitwisseling.Doelen, alleProefversies)

        except Exception as e:
            self.Scenario.Log.Fout ("Potverdorie, een fout in de simulatie die niet voorzien werd: " + str(e))
