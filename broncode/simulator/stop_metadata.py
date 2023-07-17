#======================================================================
#
# In-memory representatie van een STOP RegelingMetadata module.
#
#======================================================================
#
# Dit is een uitgeklede versie van de STOP module. Voor de simulator
# is alleen van belang dat de module bestaat en voor welke
# regelingversie een nieuwe versie van de module is uitgewisseld.
# Het enige kenmerk dat gemodelleerd wordt is de citeertitel
#
#======================================================================

from typing import Dict, List, Set, Tuple

import re
from webbrowser import Opera

from stop_naamgeving import Naamgeving

#======================================================================
#
# Metadata representeert een module met metadata voor een regeling,
# informatieobject of besluit met daarin de citeertitel als enig
# gemodelleerd kenmerk.
#
#======================================================================
class Metadata:

#----------------------------------------------------------------------
# Modellering van de module
#----------------------------------------------------------------------
    def __init__ (self):
        """Maak een lege module aan."""
        # Instrumentversie waar de metadata bij hoort
        self.Instrumentversie : str = None
        # Citeertitel zoals opgegeven in de metadata
        self.Citeertitel : str = None 
        # Geeft aan of er fouten zijn gesignaleerd bij het inlezen van de module
        self.IsValide = True

    def ModuleXml (self):
        """Geef de XML voor deze STOP module
        """
        xml = ['<' + self._RootElementNaam + ' xmlns="' + Metadata.DataNamespace + '">']
        xml.append ('\t<-- Alleen de Citeertitel is gemodelleerd in deze simulator -->')
        xml.append ('\t<Citeertitel>' + self.Citeertitel.replace ('<', '&lt;').replace ('>', '&gt;') + '</Citeertitel>')
        xml.append ('</' + self._RootElementNaam + '>')
        return xml

    DataNamespace = 'https://standaarden.overheid.nl/stop/imop/data/'
    AnnotatieNaam = 'Metadata'

#----------------------------------------------------------------------
# Inlezen van XML
#----------------------------------------------------------------------
    def _LeesXml (self, log, pad, xml, data, isValideWorkId):
        """Lees de inhoud van de module uit de XML.
        
        Argumenten:
        log Meldingen verzameling van meldingen
        pad string Pad van het XML bestand; alleen gebruikt voor meldingen
        xml xml.etree.Element XML root element gelezen uit het bestand
        data string XML (als tekst) gelezen uit het bestand
        isValideWorkId lambda  methode die vaststelt of het workID goed is
        """
        match = self._Instrumentversie.search (data)
        if match is None:
            log.Fout ("Bestand '" + pad + "': geen instrumentversie gevonden")
            self.IsValide = False
        else:
            self.Instrumentversie = match.group(1)

            if not isValideWorkId (self.Instrumentversie) or not Naamgeving.IsExpression (self.Instrumentversie):
                log.Fout ("Bestand '" + pad + "': " + self._RootElementNaam + " heeft een versie-identificatie die niet bij het instrument hoort: '" + self.Instrumentversie + "'")
                self.IsValide = False

        for elt in xml.findall ('.//{' + Metadata.DataNamespace + '}Citeertitel'):
            self.Citeertitel = elt.text
        if self.Citeertitel is None:
            log.Fout ("Bestand '" + pad + "': Citeertitel is verplicht in " + self._RootElementNaam)
            self.IsValide = False

        if self.IsValide:
            log.Detail ("Bestand '" + pad + "' bevat valide " + self._RootElementNaam)
        return self

#======================================================================
#
# RegelingMetadata representeert een module met metadata voor een 
# regeling
#
#======================================================================
class RegelingMetadata (Metadata):

#----------------------------------------------------------------------
# Modellering van de module
#----------------------------------------------------------------------
    def __init__ (self):
        super ().__init__()

#----------------------------------------------------------------------
# Inlezen van XML
#----------------------------------------------------------------------
    @staticmethod
    def IsRegelingMetadataBestand (xml):
        """Geeft aan of de XML een RegelingMetadata module is.
        
        Argumenten:
        xml xml.etree.Element XML root element gelezen uit het bestand
        """
        return xml.tag == RegelingMetadata.RootElement

    _RootElementNaam = 'RegelingMetadata'
    RootElement = '{' + Metadata.DataNamespace + '}' + _RootElementNaam

    @staticmethod
    def LeesXml (log, pad, xml, data):
        """Lees de inhoud van de module uit de XML.
        
        Argumenten:
        log Meldingen verzameling van meldingen
        pad string Pad van het XML bestand; alleen gebruikt voor meldingen
        xml xml.etree.Element XML root element gelezen uit het bestand
        data string XML (als tekst) gelezen uit het bestand
        
        Resultaat is een al dan niet valide RegelingMetadata, 
        of None als het geen RegelingMetadata module is
        """
        module = RegelingMetadata ()
        module._LeesXml (log, pad, xml, data, Naamgeving.IsRegeling)
        module.WeergaveBeschrijving = """De metadata is een annotatie bij een regelingversie. Deze module is
        gemaakt voor:<br><b>""" + module.Instrumentversie + "</b>"
        return module

    _Instrumentversie = re.compile ('^\s*(\/akn\/[^\s]*)', re.MULTILINE)


#======================================================================
#
# InformatieobjectMetadata representeert een module met metadata voor een 
# regeling
#
#======================================================================
class InformatieobjectMetadata (Metadata):

#----------------------------------------------------------------------
# Modellering van de module
#----------------------------------------------------------------------
    def __init__ (self):
        super ().__init__()

#----------------------------------------------------------------------
# Inlezen van XML
#----------------------------------------------------------------------
    @staticmethod
    def IsInformatieobjectMetadataBestand (xml):
        """Geeft aan of de XML een InformatieobjectMetadata module is.
        
        Argumenten:
        xml xml.etree.Element XML root element gelezen uit het bestand
        """
        return xml.tag == InformatieobjectMetadata.RootElement

    _RootElementNaam = 'InformatieobjectMetadata'
    RootElement = '{' + Metadata.DataNamespace + '}' + _RootElementNaam

    @staticmethod
    def LeesXml (log, pad, xml, data):
        """Lees de inhoud van de module uit de XML.
        
        Argumenten:
        log Meldingen verzameling van meldingen
        pad string Pad van het XML bestand; alleen gebruikt voor meldingen
        xml xml.etree.Element XML root element gelezen uit het bestand
        data string XML (als tekst) gelezen uit het bestand
        
        Resultaat is een al dan niet valide InformatieobjectMetadata, 
        of None als het geen InformatieobjectMetadata module is
        """
        module = InformatieobjectMetadata ()
        module._LeesXml (log, pad, xml, data, Naamgeving.IsInformatieobject)
        module.WeergaveBeschrijving = """De metadata is een annotatie bij een informatieobjectversie. Deze module is
        gemaakt voor:<br><b>""" + module.Instrumentversie + "</b>"
        return module

    _Instrumentversie = re.compile ('^\s*(\/join\/[^\s]*)', re.MULTILINE)
