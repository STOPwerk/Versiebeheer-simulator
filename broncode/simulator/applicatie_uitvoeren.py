#======================================================================
#
# Uitvoeren van het simulatieproces
#
#----------------------------------------------------------------------
#
# Ondersteuning voor het uitvoeren van de simulatie. Gebruik de 
# Uitvoering klasse op applicatieniveau om voor elk gevonden scenario 
# (= set van  invoerbestanden) de simulatie uit te voeren.
#
#======================================================================

import time

from applicatie_scenario import Scenario
from proces_simulatie import Proces_Simulatie
from weergave_resultaat import ResultaatGenerator
from weergave_webpagina import WebpaginaGenerator


#======================================================================
#
# Uitvoeren van de simulatie
#
#======================================================================
class Uitvoering:
    
    @staticmethod
    def VoerUit (scenario : Scenario, maakResultaatGenerator = None):
        """Voer de simulatie uit
        
        Argumenten:
        scenario Scenario Invoer voor het consolidatiescenario
        maakResultaatGenerator lambda -> ResultaatGenerator Wordt aangeroepen om de resultaatpagina te genereren

        Geeft terug of de uitvoering zonder problemen is verlopen
        """
        test = Uitvoering (scenario)
        return test._VoerUit (maakResultaatGenerator)

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, scenario : Scenario):
        """Maak een nieuwe instantie voor de uitvoering van het proces
        
        Argumenten:
        scenario Scenario Invoer voor het consolidatiescenario
        """
        self._Scenario = scenario
    
    def _VoerUit (self, maakResultaatGenerator):
        """Voer de simulatie uit
        Geeft terug of de uitvoering zonder problemen is verlopen
        """
        try:
            if self._Scenario.IsValide:
                proces = Proces_Simulatie (self._Scenario)
                self._Scenario.ApplicatieLog.Detail ("Start van de simulatie: " + self._Scenario.Pad)

                start = time.perf_counter ()
                proces.VoerUit ()
                tijd = time.perf_counter() - start

                if self._Scenario.Log.Fouten > 0:
                    self._Scenario.ApplicatieLog.Fout  ("Fouten bij uitvoering ({:.3f}s) van simulatie".format(tijd))
                elif self._Scenario.Log.Waarschuwingen > 0:
                    self._Scenario.ApplicatieLog.Waarschuwing  ("Waarschuwingen bij uitvoering ({:.3f}s) van simulatie".format(tijd))
                else:
                    self._Scenario.ApplicatieLog.Informatie ("Consolidatie uitgevoerd ({:.3f}s)".format(tijd))

            else:
                self._Scenario.ApplicatieLog.Fout ("Scenario in '" + self._Scenario.Pad + "' niet uitgevoerd wegens invalide invoer")

            if maakResultaatGenerator is None:
                ResultaatGenerator.MaakPagina (self._Scenario)
                if not self._Scenario.ResultaatPad is None:
                    self._Scenario.ApplicatieLog.Informatie ('Voor een verslag zie: <a href="' + WebpaginaGenerator.UrlVoorPad (self._Scenario.ResultaatPad) + '">' +  self._Scenario.ResultaatPad + '</a>')
            else:
                maakResultaatGenerator (self._Scenario)
            return self._Scenario.IsValide and self._Scenario.Log.Fouten == 0

        except Exception as e:
            self._Scenario.ApplicatieLog.Fout ("Potverdorie, een fout in de uitvoering die niet voorzien werd: " + str(e))
