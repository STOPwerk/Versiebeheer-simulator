#======================================================================
#
# Maakt een overzicht van de uitwisselingen als onderdeel van de 
# webpagina met resultaten. Via dit overzicht is ook een uitwisseling
# te selecteren.
#
#======================================================================

from applicatie_scenario import Scenario
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

class Weergave_Uitwisselingen:
    
    def VoegToe (generator: WebpaginaGenerator, scenario : Scenario):
        """Voeg een overzicht van de uitwisselingen toe

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        einde = generator.StartSectie ("<h3>Overzicht van uitwisselingen en publicaties</h3>", True)
        einde_t = generator.StartToelichting ("Over het overzicht")
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('<p><table class="uw_overzicht"><tr><th>Naam</th><th>gemaaktOp</th><th>Publicatieblad</th><th>Beschrijving</th></tr>')

        benoemdeUitwisselingen = { u.GemaaktOp: u for u in scenario.Opties.Uitwisselingen }
        for uitwisseling in scenario.Versiebeheerinformatie.Uitwisselingen:
            benoemd = benoemdeUitwisselingen.get (uitwisseling.GemaaktOp)

            generator.VoegHtmlToe ('<tr data-uw="' + uitwisseling.GemaaktOp + '">')
            if benoemd is None:
                generator.VoegHtmlToe ('<td></td>')
            else:
                generator.VoegHtmlToe ('<td>' + benoemd.Naam + '</td>')
            generator.VoegHtmlToe ('<td class="nw">' + uitwisseling.GemaaktOp + '</td><td class="nw">' + ('-' if uitwisseling._Publicatieblad is None else uitwisseling._Publicatieblad) + '</td>')
            if benoemd is None:
                generator.VoegHtmlToe ('<td></td>')
            else:
                generator.VoegHtmlToe ('<td>' + ('' if benoemd.Beschrijving is None else benoemd.Beschrijving) + '</td>')
            generator.VoegHtmlToe ('</tr>')

        generator.VoegHtmlToe ('</table></p>')

        generator.VoegHtmlToe (einde)
        generator.LeesCssTemplate ('')
