#======================================================================
#
# In-memory representatie van de gemeenschappelijke delen van een
# beschrijving van een toestand uit de STOP modules ActueleToestanden
# en CompleteToestanden.
#
#======================================================================

from data_doel import Doel

#======================================================================
#
# Toestandidentificatie
#
#======================================================================
class Toestandidentificatie:

    def __init__ (self):
        super().__init__ ()
        # De identificatie van de toestand als versie van het geconsolideerde instrument
        self.ExpressionId = None

        # De doelen die de aanleiding van het bestaan dan deze toestand zijn
        # Lijst met instanties van Doel
        self.Inwerkingtredingsdoelen = []

    def IdentificatieXmlElement (self, index : int):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave.
        
        Argumenten:

        index int  Index van de toestand zoals gebruikt in de tijdreistabel
        """
        xml = ['<ToestandIdentificatie>',
               '\t<toestandId>' + str(index) + '</toestandId>',
               '\t<FRBRExpression>' + self.ExpressionId + '</FRBRExpression>']
        xml.extend (['\t' + x for x in self._ModuleXmlDoelen ()])
        xml.append ('</ToestandIdentificatie>')
        return xml

    def _ModuleXmlDoelen (self):
        """Geeft de XML uit deze klasse als onderdeel van een element in de STOP module, als lijst van regels.
        De ExpressionId wordt niet meegenomen ivm volgorde in de XML
        In deze applicatie alleen nodig voor weergave"""
        xml = []
        for doel in self.Inwerkingtredingsdoelen: # volgorde is niet belangrijk
            xml.append ('<inwerkingtredingsdoel>' + doel.Identificatie + '</inwerkingtredingsdoel>')
        return xml

#======================================================================
#
# NogTeConsolideren
#
#======================================================================
class NogTeConsolideren:

    def __init__ (self):
        super().__init__ ()

        # De doelen waarvoor er uitwisselingen hebben plaatsgevonden die nog verwerkt zijn
        # in de kandidaat-instrumentversie voor deze toestand
        # Lijst met instanties van NogTeVerwerken, (voor weergave:) gesorteerd op de Identificatie van het doel
        self.TeVerwerkenDoelen = []
        # De doelen waarvoor er die verwerkt zijn in de kandidaat-instrumentversie voor 
        # deze toestand maar geen onderdeel zijn van deze toestand
        # Lijst met instanties van NogTeOntvlechten, (voor weergave:) gesorteerd op de Identificatie van het doel
        self.TeOntvlechtenDoelen = []

    def _ModuleXmlAttributen (self):
        """Geeft de XML uit deze klasse als onderdeel van een element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = []
        for td in self.TeVerwerkenDoelen: # volgorde is niet belangrijk
            xml.extend (['\t' + x for x in td.ModuleXmlElement ()])
        for td in self.TeOntvlechtenDoelen: # volgorde is niet belangrijk
            xml.extend (['\t' + x for x in td.ModuleXmlElement ()])
        return xml

class NogTeVerwerken:

    def __init__ (self, doel : Doel, laatstBekend, laatstVerwerkt = None):
        # Het doel waarvoor nog uitwisselingen verwerkt moeten worden
        self.Doel = doel
        # De gemaaktOp van de meest recente uitwisseling die is meegenomen bij nog-te-verwerken conclusie 
        self.LaatstBekend = laatstBekend
        # De gemaaktOp van de meest recente uitwisseling die verwerkt is in de toestand of instrumentversie
        self.LaatstVerwerkt = laatstVerwerkt

    def ModuleXmlElement (self):
        """Geeft de XML uit deze klasse als onderdeel van een element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<NogTeVerwerken>',
               '\t<teVerwerkenDoel>' + self.Doel.Identificatie + '</teVerwerkenDoel>',
               '\t<laatstBekend>' + self.LaatstBekend + '</laatstBekend>']
        if not self.LaatstVerwerkt is None:
               xml.append ('\t<laatstVerwerkt>' + self.LaatstVerwerkt + '</laatstVerwerkt>')
        xml.append ('</NogTeVerwerken>')
        return xml

class NogTeOntvlechten:

    def __init__ (self, doel : Doel, laatstVerwerkt):
        # Het doel waarvoor nog uitwisselingen ontvlochten moeten worden
        self.Doel = doel
        # De gemaaktOp van de meest recente uitwisseling die verwerkt is in de toestand of instrumentversie
        self.LaatstVerwerkt = laatstVerwerkt

    def ModuleXmlElement (self):
        """Geeft de XML uit deze klasse als onderdeel van een element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return ['<NogTeOntvlechten>',
               '\t<teOntvlechtenDoel>' + self.Doel.Identificatie + '</teOntvlechtenDoel>',
               '\t<laatstVerwerkt>' + self.LaatstVerwerkt + '</laatstVerwerkt>',
               '</NogTeOntvlechten>']
