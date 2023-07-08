#======================================================================
#
# Maakt een overzicht van de uitwisseling tussen ketenpartners 
# als onderdeel van de webpagina met resultaten.
#
#======================================================================

from applicatie_scenario import Scenario
from weergave_data_stop_uitwisseling import STOPModuleUitwisseling
from weergave_stopmodule import Weergave_STOPModule
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

class Weergave_STOP_Uitwisselingen:
    
    def VoegToe (generator: WebpaginaGenerator, scenario : Scenario):
        """Voeg een overzicht van de STOP modules die uitwisseld worden
        tussen de verschillende systemen.

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar het overzicht voor gemaakt wordt
        """
        selector = Weergave_Uitwisselingselector (scenario)
        moduleMaker = Weergave_STOPModule (generator)

        def _ToonSectie (titel, inSelectie):
            einde = None
            for ontvangenOp, uitwisselingen in scenario.STOPUitwisselingen.Uitwisselingen.items ():
                heeftUitwisselingen = False
                for uitwisseling in uitwisselingen:
                    if inSelectie(uitwisseling):
                        if einde is None:
                            einde = generator.StartSectie (titel, True)
                        if not heeftUitwisselingen:
                            heeftUitwisselingen = True
                            generator.VoegHtmlToe ('<div ' + selector.AttributenToonVoor (ontvangenOp) + '>')
                        generator.VoegHtmlToe ('<p>' + uitwisseling.Module.WeergaveBeschrijving + '</p>')
                        moduleMaker.VoegHtmlToe (uitwisseling.Module.ModuleXml ())
                if heeftUitwisselingen:
                    generator.VoegHtmlToe ('</div>')
            if not einde is None:
                generator.VoegHtmlToe (einde)

        _ToonSectie ("Van bevoegd gezag naar LVBB", lambda u: u.Verzender == STOPModuleUitwisseling.Systeem_BevoegdGezag)
        _ToonSectie ("Van LVBB naar bevoegd gezag", lambda u: u.Ontvanger == STOPModuleUitwisseling.Systeem_BevoegdGezag)
        _ToonSectie ("Van LVBB naar afnemers van LVBB informatie", lambda u: u.Verzender == STOPModuleUitwisseling.Systeem_LVBB and u.Ontvanger != STOPModuleUitwisseling.Systeem_BevoegdGezag)


