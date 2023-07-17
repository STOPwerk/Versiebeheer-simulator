#======================================================================
#
# In-memory representatie van een non-STOP annotatie module.
#
#======================================================================
#
# Dit is een fantasie-versie van de module met non-STOP annotaties.
# Voor de simulator is alleen van belang dat de module bestaat,
# voor welke GIO-versie een nieuwe versie van de module is uitgewisseld
# en welke annotatie-IDs erin zitten. Wat de non-STOP annotaties
# inhouden is voor de simulator niet van belang.
#
#======================================================================

from typing import Dict, List, Set, Tuple

import re
from webbrowser import Opera

from stop_naamgeving import Naamgeving

#======================================================================
# NonSTOPAnnotatie representeert een module met meerdere non-STOP
# annotaties
#======================================================================
class NonSTOPAnnotatie:

#----------------------------------------------------------------------
# Modellering van de module
#----------------------------------------------------------------------
    def __init__ (self):
        """Maak een lege module aan."""
        # Regelingversie waar de non-stop annotaties bij horen
        self.Instrumentversie : str = None
        # Mutaties die in de module zijn gedefinieerd
        # key = annotatienaam, value = voegtoe/wijzig (True) / verwijder (False)
        self._Mutaties : Dict[str,bool] = {}
        # Uitwerking van de mutatie van de module
        # key = annotatienaam, value = Instrumentversie van laatste wijziging
        self.Annotaties : Dict[str,str] = None 
        # Geeft aan of er fouten zijn gesignaleerd bij het inlezen van de module
        self.IsValide = True


    def ModuleXml (self):
        """Geef de XML voor deze STOP module
        """
        xml = ['<NonSTOPAnnotaties xmlns="' + NonSTOPAnnotatie.DataNamespace + '">']
        xml.append ('\t<-- Simulatie van annotatiemutaties uit een andere standaard dan STOP -->')
        xml.append ('\t<mutaties>')
        for naam, operatie in self._Mutaties.items ():
            xml.append ('\t<Annotatie>')
            xml.append ('\t\t<naam>' + naam.replace ('<', '&lt;').replace ('>', '&gt;') + '</naam>')
            xml.append ('\t\t<wijzigactie>' + ('nieuw' if operatie else 'verwijder') + '</wijzigactie>')
            xml.append ('\t</Annotatie>')
        xml.append ('\t</mutaties>')
        xml.append ('</NonSTOPAnnotaties>')
        return xml

    def VoerMutatieUit (self, basisversie: 'NonSTOPAnnotatie'):
        """Voer de mutatie uit die in de module is gespecificeerd
        
        basisversie NonSTOPAnnotatie  Voorgaande versie van de volledige set non-STOP annotaties"""
        self.Annotaties = {} if basisversie is None else basisversie.Annotaties.copy ()
        for naam, operatie in self._Mutaties.items ():
            if operatie:
                self.Annotaties[naam] = self.Instrumentversie
            else:
                del self.Annotaties[naam]

#----------------------------------------------------------------------
# Inlezen van XML
#----------------------------------------------------------------------
    @staticmethod
    def IsNonSTOPAnnotatieBestand (xml):
        """Geeft aan of de XML een NonSTOPAnnotatie module is.
        
        Argumenten:
        xml xml.etree.Element XML root element gelezen uit het bestand
        """
        return xml.tag == NonSTOPAnnotatie.RootElement

    DataNamespace = 'urn:non.stop'
    RootElement = '{' + DataNamespace + '}NonSTOPAnnotaties'
    AnnotatieNaam = 'Non-STOP annotaties'

    @staticmethod
    def LeesXml (log, pad, xml, data):
        """Lees de inhoud van de module uit de XML.
        
        Argumenten:
        log Meldingen verzameling van meldingen
        pad string Pad van het XML bestand; alleen gebruikt voor meldingen
        xml xml.etree.Element XML root element gelezen uit het bestand
        data string XML (als tekst) gelezen uit het bestand
        
        Resultaat is een al dan niet valide NonSTOPAnnotatie, 
        of None als het geen NonSTOPAnnotatie module is
        """
        module = NonSTOPAnnotatie ()
        
        match = NonSTOPAnnotatie._Instrumentversie.search (data)
        if match is None:
            log.Fout ("Bestand '" + pad + "': geen instrumentversie gevonden")
            module.IsValide = False
        else:
            module.Instrumentversie = match.group(1)

            if not Naamgeving.IsRegeling (module.Instrumentversie) or not Naamgeving.IsExpression (module.Instrumentversie):
                log.Fout ("Bestand '" + pad + "': NonSTOPAnnotatie hoort bij een regelingversie, niet bij '" + module.Instrumentversie + "'")
                module.IsValide = False

        for elt in xml.findall ('.//{' + NonSTOPAnnotatie.DataNamespace + '}Annotatie'):
            naamElt = elt.find ('{' + NonSTOPAnnotatie.DataNamespace + '}naam')
            mutatieElt = elt.find ('{' + NonSTOPAnnotatie.DataNamespace + '}wijzigactie')
            if naamElt is None or mutatieElt is None or not (mutatieElt.text == 'nieuw' or mutatieElt.text == 'verwijder'):
                log.Fout ("Bestand '" + pad + "': Annotatie moet een valide naam en mutatie attribuut hebben")
                module.IsValide = False
            else:
                module._Mutaties[naamElt.text] = mutatieElt.text == 'nieuw'

        if module.IsValide:
            log.Detail ("Bestand '" + pad + "' bevat valide non-STOP annotaties")
            # Alleen voor weergave van de XML
            module.WeergaveBeschrijving = """De non-STOP module simuleert de doorgifte van annotaties 
            bij een regelingversie die niet in STOP gemodelleerd zijn. Deze module is
            gemaakt voor:<br><b>""" + module.Instrumentversie + "</b>"
        return module

    _Instrumentversie = re.compile ('^\s*(\/akn\/[^\s]*)', re.MULTILINE)
