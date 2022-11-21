#======================================================================
#
# Simulator als web applicatie: startpunt voor Flask / vercel hosting
#
#----------------------------------------------------------------------
#
# Een Flask web applicatie die de invoer via een POST krijgt
# en de resultaatpagina als gevolg van de reguliere uitvoering
# van de simulator teruggeeft.
#
#======================================================================

from applicatie_web import WebApplicatie


#----------------------------------------------------------------------
# Flask app
#----------------------------------------------------------------------
from flask import Flask, request
app = Flask("STOPwerk Versiebeheer-simulator")
# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

#----------------------------------------------------------------------
#
# Routering
#
#----------------------------------------------------------------------
@app.route('/')
def index():
    return WebApplicatie.IndexPagine ()

@app.route('/invoer')
def invoer():
    return WebApplicatie.InvoerPagina ()

@app.route('/resultaat', methods = ['POST'])
def simuleer():
    return WebApplicatie.Simuleer (request)

#----------------------------------------------------------------------
#
# Flask server voor ontwikkeling
#
#----------------------------------------------------------------------
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
