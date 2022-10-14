#======================================================================
#
# Maakt een overzicht van de uitwisselingen # als onderdeel van de 
# webpagina met resultaten. Via dit overzicht is ook een uitwisseling
# te selecteren.
#
#======================================================================

from applicatie_scenario import Scenario
from weergave_stopmodule import Weergave_STOPModule
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

class Weergave_ConsolidatieInformatie:
    
    def VoegToe (generator: WebpaginaGenerator, scenario : Scenario):
        """Voeg een overzicht van de uitwisselingen toe

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        einde = generator.StartSectie ("STOP-module: ConsolidatieInformatie")
        einde_t = generator.StartToelichting ("Over de module")
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        selector = Weergave_Uitwisselingselector (scenario)
        moduleMaker = Weergave_STOPModule (generator)
        for idx, uitwisseling in enumerate (scenario.Versiebeheerinformatie.Uitwisselingen):
            volgendeGemaaktOp = None if idx == len (scenario.Versiebeheerinformatie.Uitwisselingen)-1 else scenario.Versiebeheerinformatie.Uitwisselingen[idx+1].GemaaktOp
            generator.VoegHtmlToe ('<div ' + selector.AttributenToonIn (uitwisseling.GemaaktOp, volgendeGemaaktOp) + '>')
            moduleMaker.VoegHtmlToe (uitwisseling._ConsolidatieInformatie.ModuleXml ())
            generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde)
