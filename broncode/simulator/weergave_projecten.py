#======================================================================
#
# Maakt een overzicht van de projecten en projectacties als onderdeel
# van de webpagina met resultaten. Via dit overzicht is ook een
# projectactie te selecteren, en tevens een uitwisseling als een 
# projectactie tot een uitwisseling leidt.
#
#======================================================================

from applicatie_scenario import Scenario
from data_bg_procesverloop import Activiteitverloop
from weergave_webpagina import WebpaginaGenerator

class Weergave_Projecten:
    
    def VoegToe (generator: WebpaginaGenerator, scenario : Scenario):
        """Voeg een overzicht van de uitwisselingen toe

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        einde = generator.StartSectie ("<h3>Overzicht van projectacties</h3>", True)
        einde_t = generator.StartToelichting ("Over het overzicht")
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        # Overzicht van de projecten
        generator.VoegHtmlToe ('<p><table class="prj_overzicht"><tr><th>Project</th><th>Beschrijving</th></tr>')
        for project in scenario.Projecten:
            generator.VoegHtmlToe ('<tr><td>' + project.Code + '</td><td>' + project.Beschrijving + '</td></tr>')
        generator.VoegHtmlToe ('</table></p>')

        # Overzicht van de projectacties
        toonUitvoerder = False
        for resultaat in scenario.Projectvoortgang.Projectacties:
            if resultaat.UitgevoerdDoor != Activiteitverloop._Uitvoerder_BevoegdGezag:
                toonUitvoerder = True
                break
        generator.VoegHtmlToe ('<p><table class="prj_overzicht"><tr>')
        generator.VoegHtmlToe ('<th class="nw">Uitgevoerd op</th>')
        for project in scenario.Projecten:
            generator.VoegHtmlToe ('<th class="c">' + project.Code + '</th>')
        generator.VoegHtmlToe ('<th         >Actie</th>')
        if toonUitvoerder:
            generator.VoegHtmlToe ('<th>Door</th>')
        generator.VoegHtmlToe ('<th>Beschrijving</th></td></tr>')

        for resultaat in scenario.Projectvoortgang.Projectacties:
            actie = resultaat._Projectactie
            idx = scenario.Projecten.index (actie._Project)

            generator.VoegHtmlToe ('<tr data-pa="' + actie.UitgevoerdOp + '"')
            if actie._IsUitwisseling:
                generator.VoegHtmlToe (' class="uw"')
            generator.VoegHtmlToe ('><td>' + actie.UitgevoerdOp + '</td>')
            for jdx in range (0, len (scenario.Projecten)):
                generator.VoegHtmlToe ('<td class="c">' + ('&#x2714;' if idx == jdx else '') + '</td>')
            generator.VoegHtmlToe ('<td>' + actie.SoortActie + '</td>')
            if toonUitvoerder:
                generator.VoegHtmlToe ('<td>' + resultaat.UitgevoerdDoor + '</td>')
            generator.VoegHtmlToe ('<td>' + actie.Beschrijving)

            if len (resultaat.Data) > 0:
                einde_t = generator.StartToelichting ("Details", False)
                generator.VoegHtmlToe ('<table>')
                for naam, waarden in resultaat.Data:
                    generator.VoegHtmlToe ('<tr><td>' + naam + '</td><td>' + '<br/>'.join(str(w) for w in waarden) + '</td></tr>')
                generator.VoegHtmlToe ('</table>')
                generator.VoegHtmlToe (einde_t)

            generator.VoegHtmlToe ('</td></tr>')

        generator.VoegHtmlToe ('</table></p>')

        generator.VoegHtmlToe (einde)
        generator.LeesCssTemplate ('')
        generator.LeesJSTemplate ('')

