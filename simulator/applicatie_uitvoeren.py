#======================================================================
#
# Uitvoeren van het consolidatieproces
#
#----------------------------------------------------------------------
#
# Ondersteuning voor het uitvoeren van het consolideren door de
# applicatie. Gebruik de Uitvoering klasse op applicatieniveau 
# om voor elk gevonden scenario (= set van  invoerbestanden) 
# de consolidatie uit te voeren.
#
#======================================================================

import time

from data_scenario import Scenario
from proces_consolidatie import Proces_Consolidatie
from weergave_resultaat import ResultaatGenerator
from weergave_webpagina import WebpaginaGenerator


#======================================================================
#
# Uitvoeren van de consolidatie
#
#======================================================================
class Uitvoering:
    
    @staticmethod
    def VoerUit (scenario : Scenario):
        """Voeren de geautomatiseerde consolidatie uit
        
        Argumenten:
        scenario Scenario Invoer voor het consolidatiescenario

        Geeft terug of de uitvoering zonder problemen is verlopen
        """
        test = Uitvoering (scenario)
        return test._VoerUit ()

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, scenario : Scenario):
        """Maak een nieuwe instantie voor de uitvoering van het proces
        
        Argumenten:
        scenario Scenario Invoer voor het consolidatiescenario
        """
        self._Scenario = scenario
    
    def _VoerUit (self):
        """Voer de geautomatiseerde consolidatie uit
        Geeft terug of de uitvoering zonder problemen is verlopen
        """
        try:
            if self._Scenario.IsValide:
                proces = Proces_Consolidatie (self._Scenario)
                self._Scenario.ApplicatieLog.Detail ("Start van de geautomatiseerde consolidatie: " + self._Scenario.Pad)

                start = time.perf_counter ()
                proces.VoerUit ()
                tijd = time.perf_counter() - start

                if self._Scenario.Log.Waarschuwingen > 0:
                    if self._Scenario.Log.Fouten > 0:
                        self._Scenario.ApplicatieLog.Fout  ("Fouten bij uitvoering ({:.3f}s) van consolidatie".format(tijd) + ': <a href="' + WebpaginaGenerator.UrlVoorPad (self._Scenario.ResultaatPad) + '">' +  self._Scenario.ResultaatPad + '</a>')
                    else:
                        self._Scenario.ApplicatieLog.Waarschuwing  ("Waarschuwingen bij uitvoering ({:.3f}s) van consolidatie".format(tijd) + ': <a href="' + WebpaginaGenerator.UrlVoorPad (self._Scenario.ResultaatPad) + '">' +  self._Scenario.ResultaatPad + '</a>')
                else:
                    self._Scenario.ApplicatieLog.Informatie ("Consolidatie uitgevoerd ({:.3f}s)".format(tijd) + ': <a href="' + WebpaginaGenerator.UrlVoorPad (self._Scenario.ResultaatPad) + '">' +  self._Scenario.ResultaatPad + '</a>')

            else:
                self._Scenario.ApplicatieLog.Informatie ("Niet-valide invoer voor scenario in '" + self._Scenario.Pad + "'")

            ResultaatGenerator.MaakPagina (self._Scenario)

            return self._Scenario.IsValide and self._Scenario.Log.Fouten == 0

        except Exception as e:
            self._Scenario.ApplicatieLog.Fout ("Potverdorie, een fout in de uitvoering die niet voorzien werd: " + str(e))
