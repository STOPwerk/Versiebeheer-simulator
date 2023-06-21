#======================================================================
#
# In-memory representatie van de STOP Momentopname module.
#
#======================================================================
#
# De Momentopname module wordt gebruikt om versieinformatie voor een
# geconsolideerd instrument in de downloadfunctie mee te leveren, en
# bij de uitwisseling van alle instrumentversies voor een doel tussen
# advisbureau en bevoegd gezag.
#
#======================================================================

from typing import Dict, List
from data_doel import Doel

#======================================================================
#
# Momentopname module
#
#======================================================================
class Momentopname:

    def __init__ (self):
        """Maak een lege module aan"""
        # Doel als identificatie van de branch waarvoor de instrumentversies worden uitgewisseld
        self.Doel : Doel = None
        # Tijdstip waarop de momentopname is samengesteld
        self.GemaaktOp = None
        # De instrumentversies die in de module zijn opgenomen
        self.Instrumentversies : List[InstrumentversieInformatie] = []

    def ModuleXml (self):
        """Geeft de XML van de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<Momentopname xmlns="https://standaarden.overheid.nl/stop/imop/data/">',
               '\t<doel>' + str(self.Doel) + '</doel>',
               '\t<gemaaktOp>' + self.GemaaktOp + '</gemaaktOp>']
        if len(self.Instrumentversies) > 0:
            xml.append ('\t<bevatWijzigingenVoor>')
            for instrumentversie in self.Instrumentversies:
                xml.append ('')
                xml.extend (['\t\t' + x for x in instrumentversie.ModuleXmlElement ()])
            xml.extend (['',
                         '\t</bevatWijzigingenVoor>'])
        xml.append ('</Momentopname>')
        return xml

class InstrumentversieInformatie:

    def __init__ (self):
        """Maak een leeg element aan"""
        # Work-ID van het instrument
        self.WorkId = None
        # Doel van de basisversie voor dit instrument
        # Instantie van Doel
        self.Basisversie_Doel = None
        # Tijdstip waarop de momentopname van de basisversie is samengesteld
        self.Basisversie_GemaaktOp = None
        # Alleen voor weergave: instrumentversie.
        # Deze informatie is bij uitwisseling in een andere module te vinden
        self._ExpressionId = None

    def ModuleXmlElement (self):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<UitgewisseldInstrument>',
               '\t<!-- In de uitwisseling is aanwezig: ' + str(self._ExpressionId) + ' -->',
               '\t<FRBRWork>' + str(self.WorkId) + '</FRBRWork>']
        if not self.Basisversie_Doel is None:
            xml.extend (['\t<gemaaktOpBasisVan>',
                         '\t\t<Basisversie>',
                         '\t\t\t<doel>' + str(self.Basisversie_Doel) + '</doel>',
                         '\t\t\t<gemaaktOp>' + self.Basisversie_GemaaktOp + '</gemaaktOp>',
                         '\t\t</Basisversie>',
                         '\t</gemaaktOpBasisVan>'])
        xml.append ('</UitgewisseldInstrument>')
        return xml

#======================================================================
#
# Combinatie van alle Momentopname modules per gedownload instrument
#
#======================================================================

class DownloadserviceModules:

    def __init__ (self):
        """Maak een lege collectie van modules aan"""
        # Collectie van modules
        # Key = instrumentversie
        self.Modules : Dict[str,Momentopname] = {}

    def ModuleXml (self):
        """Geeft de XML van de STOP modules, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = []
        for instrumentversie in sorted (self.Modules.keys ()):
            if len (xml) > 0:
                xml.append ('')
            xml.append ('<!-- Module meegeleverd met de download van ' + instrumentversie + ' -->')
            xml.extend (self.Modules[instrumentversie].ModuleXml ())
        return xml
