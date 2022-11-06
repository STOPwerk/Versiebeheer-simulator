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

import applicatie_configuratie
from applicatie_meldingen import Meldingen
from applicatie_scenario import Scenario, ScenarioMappenIterator
from applicatie_uitvoeren import Uitvoering
from applicatie_web_scenario import ScenarioPostedDataIterator
from weergave_resultaat import ResultaatGenerator
from weergave_webpagina import WebpaginaGenerator


#----------------------------------------------------------------------
# Flask app
#----------------------------------------------------------------------
from flask import Flask, request
app = Flask("STOPwerk Versiebeheer-simulator")
# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
FAVICON = "static/applicatie_web_favicon.png"

#======================================================================
#
# Indexpagina
#
#======================================================================
@app.route('/')
def index():
    """Startpagina"""
    generator = WebpaginaGenerator ("Versiebeheer-simulator online", FAVICON)
    html = generator.LeesHtmlTemplate ('index', False)
    html = html.replace ('@@@VERSIE@@@', applicatie_configuratie.Applicatie_versie)
    html = html.replace ('@@@STOP_Documentatie_Url@@@', applicatie_configuratie.STOP_Documentatie_Url)
    html = html.replace ('@@@STOP_Repository_Url@@@', applicatie_configuratie.STOP_Repository_Url)
    generator.VoegHtmlToe (html)
    return generator.Html ()

@app.route('/invoer')
def invoer():
    """Invoerpagina"""
    generator = WebpaginaGenerator ("Versiebeheer-simulator invoer", FAVICON)
    # Bron: https://bdwm.be/drag-and-drop-upload-files/
    generator.LeesHtmlTemplate ('invoer')
    generator.LeesCssTemplate ('invoer')
    generator.LeesJSTemplate ('invoer')
    return generator.Html ()

@app.route('/resultaat', methods = ['POST'])
def simuleer():
    """Voer de simulator uit"""
    generator = []
    applicatieLog = Meldingen (True)
    Scenario.VoorElkScenario (applicatieLog, ScenarioPostedDataIterator (applicatieLog, request.form, request.files), lambda s: Uitvoering.VoerUit (s, lambda s2: generator.append (ResultaatGenerator.MaakPagina (s2, FAVICON))))
    if len (generator) > 0:
        generator = generator[0]
    else:
        generator = WebpaginaGenerator ("Versiebeheer-simulator resultaat", FAVICON)
        applicatieLog.MaakHtml (generator, None)
    return generator.Html ()

#======================================================================
#
# Flask server voor ontwikkeling
#
#======================================================================
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
