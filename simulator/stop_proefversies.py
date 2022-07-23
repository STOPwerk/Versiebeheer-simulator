#======================================================================
#
# In-memory representatie van de STOP Proefversies module.
# De Proefversie elementen zijn als InstrumentversieHistorie te vinden
# in stop_instrumentversiehistorie.py.
#
#======================================================================

#----------------------------------------------------------------------
# Proefversies module
#----------------------------------------------------------------------
class Proefversies:

    def __init__(self):
        """Maak een lege module aan"""
        # Datum waarop de informatie in de module voor het eerst bekend is geworden
        self.BekendOp = None
        # Datum waarop de informatie door de STOP-gebruikende applicatie
        # ontvangen is (maar het mag niet eerder zijn dan bekendOp).
        self.OntvangenOp = None
        # De proefversies voor de uitgewisselde instrumentversies
        # Lijst van instanties van Proefversie elementen
        self.Proefversies = []

    def ModuleXml (self):
        """Geeft de XML van de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<Proefversies xmlns="https://standaarden.overheid.nl/stop/imop/consolidatie/">',
               '\t<bekendOp>' + self.BekendOp + '</bekendOp>',
               '\t<ontvangenOp>' + self.OntvangenOp + '</ontvangenOp>']
        for proefversie in self.Proefversies:
            xml.append ('')
            xml.extend ('\t' + x for x in proefversie.ModuleXmlElement ())
        xml.extend ('\t' + x if x else '' + x for x in self.ModuleXmlAttributen ())
        xml.extend (['',
                     '</Proefversies>'])
        return xml

    def ModuleXmlAttributen (self):
        """Voeg extra attributen toe"""

#----------------------------------------------------------------------
# Proefversie element
#----------------------------------------------------------------------
class Proefversie:

    def __init__ (self):
        """Maak een nieuwe proefversie aan"""
        super().__init__()
        # Identificatie van de versie van het niet-geconsolideerde instrument
        self.Instrumentversie = None
        # Doelen waarvoor de instrumentversie gemaakt is.
        # Lijst met instanties van Doel
        self.Doelen = []
        # Bronnen voor annotaties voor de proefversie.
        # Lijst van instanties van Annotatiebron
        self.Annotatiebronnen = []

    def ModuleXmlElement (self, tag = 'Proefversie'):
        '''Geeft de XML van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave.

        Argumenten:
        tag string Naam van het element in XML
        '''
        xml = ['<' + tag + '>',
               '\t<instrumentVersie>' + self.Instrumentversie + '</instrumentVersie>']
        for doel in self.Doelen: # volgorde is niet belangrijk
            xml.append ('\t<doel>' + str(doel) + '</doel>')
        xml.append ('\t<annotatiebronnen>')
        for bron in self.Annotatiebronnen:
            xml.extend ('\t\t' + x for x in bron.ModuleXmlElement ())
        xml.append ('\t</annotatiebronnen>')
        xml.append ('</' + tag + '>')
        return xml

#----------------------------------------------------------------------
# Informatie over een enkele annotatiebron
#----------------------------------------------------------------------
class Annotatiebron:

    def __init__ (self, doel):
        '''Geef aan uit welk deel van deze branch/doel annotaties voor de instrumentversie afkomstig zijn.

        Argumenten

        doel Doel  Doel (branch) waarvan annotaties bijdragen
        '''
        self.Doel = doel
        # Laatste gemaaktOp voor de branch die nog bijdraagt
        self.TotEnMet = None
        # De verwijzingen naar andere branches waarvan annotaties geërfd
        # kunnen worden.
        # Key = Lijst met instanties van MomentopnameVerwijzing
        self.AnnotatiesOvernemenVan = []

    def ModuleXmlElement (self):
        '''Geeft de XML van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave.
        '''
        xml = ['<Annotatiebron>',
               '\t<doel>' + str(self.Doel) + '</doel>',
               '\t<totEnMet>' + self.TotEnMet + '</totEnMet>']
        if len (self.AnnotatiesOvernemenVan) > 0:
            xml.append ('\t<annotatiesOvernemenVan>')
            for overname in self.AnnotatiesOvernemenVan:
                xml.extend ('\t\t' + x for x in overname.ModuleXmlElement ())
            xml.append ('\t</annotatiesOvernemenVan>')
        xml.append ('</Annotatiebron>')
        return xml

#----------------------------------------------------------------------
# Aamwijzing voor het overnemen van annotties uit een andere branch
#----------------------------------------------------------------------
class AnnotatiebronOvernme:

    def __init__ (self, vanaf, doel, gemaaktOp):
        """Maak een in-memory representatie van een momentopname aan

        Argumenten

        vanaf string Tijdstip dat het startpunt op de huidige branch is waarvoor annotaties overgenomen kunnen worden
        doel string  Doel (branch) waaruit de annotaties overgenomen kunnen worden
        gemaaktOp string  Tijdstip van de momentopname in de andere branch
        """
        self.Vanaf = vanaf
        self.Doel = doel
        self.GemaaktOp = gemaaktOp

    def ModuleXmlElement (self):
        '''Geeft de XML van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave.
        '''
        return ['<Overerving>',
                '\t<vanaf>' + self.Vanaf + '</vanaf>',
                '\t<doel>' + str(self.Doel) + '</doel>',
                '\t<gemaaktOp>' + self.GemaaktOp + '</gemaaktOp>',
                '</Overerving>']

