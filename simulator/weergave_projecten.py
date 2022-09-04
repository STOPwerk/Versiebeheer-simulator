#======================================================================
#
# Maakt een overzicht van de projecten en projectacties als onderdeel
# van de webpagina met resultaten. Via dit overzicht is ook een
# uitwisseling te selecteren, als de projectactie tot een uitwisseling
# leidt.
#
#======================================================================

from applicatie_scenario import Scenario
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

class Weergave_Projecten:
    
    def VoegToe (generator: WebpaginaGenerator, scenario : Scenario):
        """Voeg een overzicht van de uitwisselingen toe

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        einde = generator.StartSectie ("Overzicht van projectacties", True)
        einde_t = generator.StartToelichting ("Over het overzicht")
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        # Overzicht van de projecten
        generator.VoegHtmlToe ('<p><table class="prj_overzicht"><tr><th>Project</th><th>Beschrijving</th></tr>')
        for project in scenario.Projecten:
            generator.VoegHtmlToe ('<tr><td>' + project.Code + '</td><td>' + project.Beschrijving + '</td></tr>')
        generator.VoegHtmlToe ('</table></p>')

        # Overzicht van de projectacties
        generator.VoegHtmlToe ('<p><table class="prj_overzicht"><tr>')
        alleActies = []
        for idx, project in enumerate (scenario.Projecten):
            generator.VoegHtmlToe ('<th>' + project.Code + '</th>')
            for actie in project.Acties:
                alleActies.append ((idx, actie))
        generator.VoegHtmlToe ('<th>Actie</th><th colspan="2">Beschrijving</th></td></tr>')

        alleActies.sort (key = lambda a: a[1].UitgevoerdOp)
        for idx, actie in alleActies:

            beschrijving = [
                '<td colspan="2">' + actie.Beschrijving + '</td>',
                '<td class="nw">Uitgevoerd op:</td><td>' + actie.UitgevoerdOp + '</td>'
            ]

            tr = '<tr' + (' data-uw="' + actie.UitgevoerdOp + '"' if actie._IsUitwisseling else '')
            generator.VoegHtmlToe (tr + ' class="top">')
            for jdx in range (0, len (scenario.Projecten)):
                generator.VoegHtmlToe ('<td rowspan="' + str(len(beschrijving)-1) + '">' + ('&#x2714;' if idx == jdx else '') + '</td>')
            generator.VoegHtmlToe ('<td rowspan="' + str(len(beschrijving)-1) + '">' + actie.SoortActie + '</td>')

            for jdx, regel in enumerate (beschrijving):
                if jdx == len (beschrijving)-1:
                    generator.VoegHtmlToe (tr + ' class="bottom">')
                elif jdx > 0:
                    generator.VoegHtmlToe (tr + '>')
                generator.VoegHtmlToe (regel + '</tr>')

        generator.VoegHtmlToe ('</table></p>')

        generator.VoegHtmlToe (einde)
        generator.LeesCssTemplate ('')

