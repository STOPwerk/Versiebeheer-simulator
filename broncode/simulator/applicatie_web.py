#======================================================================
#
# Simulator als web applicatie
#
#----------------------------------------------------------------------
#
# Een Flask web applicatie die de invoer via een POST krijgt
# en de resultaatpagina als gevolg van de reguliere uitvoering
# van de simulator teruggeeft.
#
#======================================================================

from applicatie_meldingen import Meldingen
from applicatie_scenario import Scenario, ScenarioMappenIterator
from applicatie_uitvoeren import Uitvoering
from applicatie_web_scenario import ScenarioPostedDataIterator
from weergave_resultaat import ResultaatGenerator
from weergave_webpagina import WebpaginaGenerator

class WebApplicatie:

    FAVICON = "static/applicatie_web_favicon.png"

#======================================================================
#
# Indexpagina
#
#======================================================================
    @staticmethod
    def IndexPagina():
        """Startpagina"""
        generator = WebpaginaGenerator ("Simulator online", WebApplicatie.FAVICON)
        generator.LeesHtmlTemplate ('index')
        return generator.Html ()

    @staticmethod
    def InvoerPagina():
        """Invoerpagina"""
        generator = WebpaginaGenerator ("Simulator invoer", WebApplicatie.FAVICON)
        # Bron: https://bdwm.be/drag-and-drop-upload-files/
        generator.LeesHtmlTemplate ('invoer')
        generator.LeesCssTemplate ('invoer')
        generator.LeesJSTemplate ('invoer')
        return generator.Html ()

    @staticmethod
    def ProjectInvoerPagina():
        """Invoerpagina voor BG-projecten"""
        return WebApplicatie.ProjectInvoerPaginaVoorbeeld (None)

    @staticmethod
    def ProjectInvoerPaginaVoorbeeld(voorbeeldFilePad):
        """Invoerpagina voor BG-projecten, te vullen met een voorbeeld"""
        generator = WebpaginaGenerator ("Simulator @bevoegd gezag", WebApplicatie.FAVICON)
        einde = generator.StartSectie ("Toelichting", voorbeeldFilePad is None)
        generator.LeesHtmlTemplate ('project_invoer_help')
        generator.VoegHtmlToe (einde)
        if voorbeeldFilePad is None:
            generator.LeesHtmlTemplate ('project_invoer')
            generator.LeesJSTemplate ('project_invoer')
        else:
            generator.LeesHtmlTemplate ('project_invoer_voorbeeld')
            generator.VoegHtmlToe ('<textarea id="voorbeeld">')
            with open (voorbeeldFilePad, 'r', encoding='utf-8') as jsonFile:
                generator.VoegHtmlToe (jsonFile.read ())
            generator.VoegHtmlToe ('</textarea>')
            generator.LeesJSTemplate ('project_invoer_voorbeeld')
        generator.LeesCssTemplate ('project_invoer')
        generator.LeesJSTemplate ('project_invoer_bgproces', True, True)
        generator.GebruikSvgScript ()
        return generator.Html ()

    @staticmethod
    def Simuleer(request):
        """Voer de simulator uit"""
        generator = []
        def _MaakResultaatPagina (scenario : Scenario):
            if scenario.IsValide:
                generator.append (ResultaatGenerator.MaakPagina (scenario, WebApplicatie.FAVICON))
        applicatieLog = Meldingen (True)
        Scenario.VoorElkScenario (applicatieLog, ScenarioPostedDataIterator (applicatieLog, request.form, request.files), lambda s: Uitvoering.VoerUit (s, _MaakResultaatPagina))
        if len (generator) > 0:
            generator = generator[0]
        else:
            generator = WebpaginaGenerator ("Simulator resultaat", WebApplicatie.FAVICON)
            applicatieLog.MaakHtml (generator, 'request_meldingen', None)
        return generator.Html ()

    @staticmethod
    def SimuleerVoorbeeld(voorbeeldMapPad):
        """Voer de simulator uit voor een voorbeeld"""
        generator = []
        def _MaakResultaatPagina (scenario : Scenario):
            if scenario.IsValide:
                generator.append (ResultaatGenerator.MaakPagina (scenario, WebApplicatie.FAVICON))
        applicatieLog = Meldingen (True)
        Scenario.VoorElkScenario (applicatieLog, ScenarioMappenIterator (applicatieLog, [voorbeeldMapPad] , False), lambda s: Uitvoering.VoerUit (s, _MaakResultaatPagina))
        if len (generator) > 0:
            generator = generator[0]
        else:
            generator = WebpaginaGenerator ("Simulator resultaat", WebApplicatie.FAVICON)
            applicatieLog.MaakHtml (generator, 'request_meldingen', None)
        return generator.Html ()
