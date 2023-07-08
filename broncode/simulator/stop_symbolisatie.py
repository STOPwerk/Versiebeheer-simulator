#======================================================================
#
# In-memory representatie van de STOP Symbolisatie module.
#
#======================================================================
#
# Dit is een uitgeklede versie van de STOP module. Voor de simulator
# is alleen van belang dat de module bestaat en voor welke
# GIO-versie een nieuwe versie van de module is uitgewisseld.
#
#======================================================================

from typing import Dict, List, Set, Tuple

import re

from stop_naamgeving import Naamgeving

#======================================================================
# Symbolisatie representeert de hele module
#======================================================================
class Symbolisatie:

#----------------------------------------------------------------------
# Modellering van de module
#----------------------------------------------------------------------
    def __init__ (self):
        """Maak een lege module aan."""
        # GIO-versie waar de symbolisatie bij hoort
        self.Instrumentversie : str = None
        # Geeft aan of er fouten zijn gesignaleerd bij het inlezen van de module
        self.IsValide = True

    def ModuleXml (self):
        """Geef de XML voor deze STOP module
        """
        xml = ['<FeatureTypeStyle xmlns="' + Symbolisatie.DataNamespace + '">']
        xml.append ('\t<-- Inhoud is in deze simulator niet gemodelleerd -->')
        xml.append ('</FeatureTypeStyle>')
        return xml

#----------------------------------------------------------------------
# Inlezen van XML
#----------------------------------------------------------------------
    @staticmethod
    def IsSymbolisatieBestand (xml):
        """Geeft aan of de XML een Symbolisatie module is.
        
        Argumenten:
        xml xml.etree.Element XML root element gelezen uit het bestand
        """
        return xml.tag == Symbolisatie.RootElement

    DataNamespace = 'http://www.opengis.net/se'
    RootElement = '{' + DataNamespace + '}FeatureTypeStyle'
    AnnotatieNaam = 'Symbolisatie'

    @staticmethod
    def LeesXml (log, pad, data):
        """Lees de inhoud van de module uit de XML.
        
        Argumenten:
        log Meldingen verzameling van meldingen
        pad string Pad van het XML bestand; alleen gebruikt voor meldingen
        data string XML (als tekst) gelezen uit het bestand
        
        Resultaat is een al dan niet valide Symbolisatie, 
        of None als het geen Symbolisatie module is
        """
        module = Symbolisatie ()
        
        match = Symbolisatie._Instrumentversie.search (data)
        if match is None:
            log.Fout ("Bestand '" + pad + "': geen instrumentversie gevonden")
            module.IsValide = False
        else:
            module.Instrumentversie = match.group(1)

            if not Naamgeving.IsInformatieobject (module.Instrumentversie) or not Naamgeving.IsExpression (module.Instrumentversie):
                log.Fout ("Bestand '" + pad + "': Symbolisatie hoort bij een GIO-versie, niet bij '" + module.Instrumentversie + "'")
                module.IsValide = False

        if module.IsValide:
            log.Detail ("Bestand '" + pad + "' bevat valide symbolisatie")
            # Alleen voor weergave ven de XML
            module.WeergaveBeschrijving = """De symbolisatie is een annotatie bij een GIO. Deze module is
            gemaakt voor:<br><b>""" + module.Instrumentversie + "</b>"
        return module

    _Instrumentversie = re.compile ('^\s*(\/join\/[^\s]*)', re.MULTILINE)
