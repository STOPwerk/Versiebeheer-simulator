#======================================================================
#
# Maakt een overzicht van de uitwisseling tussen ketenpartners 
# als onderdeel van de webpagina met resultaten. Dit overzicht wordt
# gemaakt op basis van de projectacties
#
#======================================================================

from applicatie_scenario import Scenario
from weergave_stopmodule import Weergave_STOPModule
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

class Weergave_Project_Uitwisselingen:
    
    def VoegToe (generator: WebpaginaGenerator, scenario : Scenario):
        """Voeg een overzicht van de uitwisselingen toe die gedaan worden 
        in het kader van de projecten bij BG.

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        einde = generator.StartSectie ("STOP modules: uitwisselingen in de keten", True)
        einde_t = generator.StartToelichting ("Over het overzicht")
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        # Overzicht van de projectacties
        selector = Weergave_Uitwisselingselector (scenario)
        moduleMaker = Weergave_STOPModule (generator)
        for resultaat in scenario.Projectvoortgang.Projectacties:
            if len (resultaat.Uitgewisseld) > 0:
                generator.VoegHtmlToe ('<div ' + selector.AttributenToonVoor (resultaat._Projectactie.UitgevoerdOp) + '>')
                for module in resultaat.Uitgewisseld:
                    generator.VoegHtmlToe ('<p>Van: ' + module.Van + '<br/>Naar: ' + module.Naar + '</p>')
                    moduleMaker.VoegHtmlToe (module.Module.ModuleXml ())
                generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde)


