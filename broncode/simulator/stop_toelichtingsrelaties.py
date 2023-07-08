#======================================================================
#
# In-memory representatie van de STOP Toelichtingsrelaties module.
#
#======================================================================
#
# Dit is een uitgeklede versie van de STOP module. Voor de simulator
# is alleen van belang dat de module bestaat en voor welke
# regelingversie een nieuwe versie van de module is uitgewisseld.
#
#======================================================================

from typing import Dict, List, Set, Tuple

import re

from stop_naamgeving import Naamgeving

#======================================================================
# Toelichtingsrelaties representeert de hele module
#======================================================================
class Toelichtingsrelaties:

#----------------------------------------------------------------------
# Modellering van de module
#----------------------------------------------------------------------
    def __init__ (self):
        """Maak een lege module aan."""
        # Regelingversie waar de symbolisatie bij hoort
        self.Instrumentversie : str = None
        # Geeft aan of er fouten zijn gesignaleerd bij het inlezen van de module
        self.IsValide = True

    def ModuleXml (self):
        """Geef de XML voor deze STOP module
        """
        xml = ['<Toelichtingsrelaties xmlns="' + Toelichtingsrelaties.DataNamespace + '">']
        xml.append ('\t<-- Inhoud is in deze simulator niet gemodelleerd -->')
        xml.append ('</Toelichtingsrelaties>')
        return xml

#----------------------------------------------------------------------
# Inlezen van XML
#----------------------------------------------------------------------
    @staticmethod
    def IsToelichtingsrelatiesBestand (xml):
        """Geeft aan of de XML een Toelichtingsrelaties module is.
        
        Argumenten:
        xml xml.etree.Element XML root element gelezen uit het bestand
        """
        return xml.tag == Toelichtingsrelaties.RootElement

    DataNamespace = 'https://standaarden.overheid.nl/stop/imop/data/'
    RootElement = '{' + DataNamespace + '}Toelichtingsrelaties'
    AnnotatieNaam = 'Toelichtingsrelaties'

    @staticmethod
    def LeesXml (log, pad, data):
        """Lees de inhoud van de module uit de XML.
        
        Argumenten:
        log Meldingen verzameling van meldingen
        pad string Pad van het XML bestand; alleen gebruikt voor meldingen
        data string XML (als tekst) gelezen uit het bestand
        
        Resultaat is een al dan niet valide Toelichtingsrelaties, 
        of None als het geen Toelichtingsrelaties module is
        """
        module = Toelichtingsrelaties ()
        
        match = Toelichtingsrelaties._Instrumentversie.search (data)
        if match is None:
            log.Fout ("Bestand '" + pad + "': geen instrumentversie gevonden")
            module.IsValide = False
        else:
            module.Instrumentversie = match.group(1)

            if not Naamgeving.IsRegeling (module.Instrumentversie) or not Naamgeving.IsExpression (module.Instrumentversie):
                log.Fout ("Bestand '" + pad + "': Toelichtingsrelaties hoort bij een regelingversie, niet bij '" + module.Instrumentversie + "'")
                module.IsValide = False

        if module.IsValide:
            log.Detail ("Bestand '" + pad + "' bevat valide Toelichtingsrelaties")
            # Alleen voor weergave ven de XML
            module.WeergaveBeschrijving = """De Toelichtingsrelaties geven de relatie aan tussen
            een artikelsgewijze toelichting en de tekst van de regeling waar de toelichting over gaat. Deze module is
            gemaakt voor:<br><b>""" + module.Instrumentversie + "</b>"
        return module

    _Instrumentversie = re.compile ('^\s*(\/akn\/[^\s]*)', re.MULTILINE)
