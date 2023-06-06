#======================================================================
#
# Maakt een overzicht van de uitwisseling tussen ketenpartners 
# als onderdeel van de webpagina met resultaten. Dit overzicht wordt
# gemaakt op basis van de projectacties
#
#======================================================================

from applicatie_scenario import Scenario
from weergave_stopmodule import Weergave_STOPModule
from weergave_webpagina import WebpaginaGenerator

class Weergave_BG_Uitwisselingen:
    
    def VoegToe (generator: WebpaginaGenerator, scenario : Scenario):
        """Voeg een overzicht van de uitwisselingen toe die gedaan worden 
        in het kader van de activiteiten van BG en adviesbureaus.

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        einde = generator.StartSectie ("STOP modules: uitwisselingen in de keten", True)
        einde_t = generator.StartToelichting ("Over het overzicht")
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        # Overzicht van de projectacties
        moduleMaker = Weergave_STOPModule (generator)
        for activiteit in scenario.Procesvoortgang.Activiteiten:
            if len (activiteit.Uitgewisseld) > 0:
                # Lift mee op de activiteitselectie bij de proces-weergave
                generator.VoegHtmlToe ('<div class="activiteit_uitvoering_status" data-bga="' + activiteit.UitgevoerdOp + '">')
                for module in activiteit.Uitgewisseld:
                    generator.VoegHtmlToe ('<p>Van: ' + module.Van + '<br/>Naar: ' + module.Naar + ('' if module.Instrument is None else '<br/>Voor: ' + module.Instrument ) + '</p>')
                    moduleMaker.VoegHtmlToe (module.Module.ModuleXml ())
                generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde)


