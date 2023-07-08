#======================================================================
#
# In-memory representatie van de STOP Proefversies module.
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
        return []

    WeergaveBeschrijving = """De module met proefversies geeft een overzicht van de instrumentversies die voor het eerst zijn
    aangeleverd aan de LVBB."""

#----------------------------------------------------------------------
# Proefversie element
#----------------------------------------------------------------------
class Proefversie:

    def __init__ (self):
        """Maak een nieuwe proefversie aan"""
        super().__init__()
        # Identificatie van de versie van het niet-geconsolideerde instrument
        self.Instrumentversie = None
        # Basisversie is de voorgaande versie van de 
        self.Basisversie : Proefversie = None

    def ModuleXmlElement (self, tag = 'Proefversie'):
        '''Geeft de XML van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave.

        Argumenten:
        tag string Naam van het element in XML
        '''
        xml = ['<' + tag + '>',
               '\t<instrumentVersie>' + self.Instrumentversie + '</instrumentVersie>']
        if not self.Basisversie is None:
            xml.append ('\t<basisversie>' + self.Basisversie.Instrumentversie + '</basisversie>')
        xml.append ('</' + tag + '>')
        return xml
