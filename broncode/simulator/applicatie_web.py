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
from applicatie_scenario import Scenario
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
        generator = WebpaginaGenerator ("Versiebeheer-simulator online", WebApplicatie.FAVICON)
        generator.LeesHtmlTemplate ('index')
        return generator.Html ()

    @staticmethod
    def InvoerPagine():
        """Invoerpagina"""
        generator = WebpaginaGenerator ("Versiebeheer-simulator invoer", WebApplicatie.FAVICON)
        # Bron: https://bdwm.be/drag-and-drop-upload-files/
        generator.LeesHtmlTemplate ('invoer')
        generator.LeesCssTemplate ('invoer')
        generator.LeesJSTemplate ('invoer')
        return generator.Html ()

    @staticmethod
    def Simuleer(request):
        """Voer de simulator uit"""
        generator = []
        applicatieLog = Meldingen (True)
        Scenario.VoorElkScenario (applicatieLog, ScenarioPostedDataIterator (applicatieLog, request.form, request.files), lambda s: Uitvoering.VoerUit (s, lambda s2: generator.append (ResultaatGenerator.MaakPagina (s2, WebApplicatie.FAVICON))))
        if len (generator) > 0:
            generator = generator[0]
        else:
            generator = WebpaginaGenerator ("Versiebeheer-simulator resultaat", WebApplicatie.FAVICON)
            applicatieLog.MaakHtml (generator, None)
        return generator.Html ()
