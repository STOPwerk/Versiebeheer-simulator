#======================================================================
#
# In-memory representatie van de STOP JuridischeVerandwoording module.
#
#======================================================================
#
# De juridische verantwoording wordt in deze applicatie gebruikt om
# te laten zien hoe toestanden van een geconsolideerd instrument
# weergegeven kunnen worden als de inhoud/instrumentversie voor de
# toestand onbekend is, door een andere instrumentversie te laten zien
# en te verwijzen naar publicaties die nog in de versie verwerkt
# moeten worden.
#
# In deze applicatie is geen informatie over de publicaties aanwezig.
# De aanname is dat elke uitwisseling tot een publicatie leidt en dat
# in elke publicatie elke (bekende) instrumentversie te zien is die
# in de uitwisseling wordt meegegeven. Dat is in de echte wereld niet
# zo: sommige instrumentversie worden als revisie doorgegeven,
# verschijnen niet in de publicatie en dus ook niet in de juridische
# verantwoording.
#
#======================================================================

#======================================================================
#
# JuridischeVerantwoording module
#
#======================================================================
class JuridischeVerantwoording:

    def __init__(self):
        # Overzicht van de verantwoording voor het instrument
        # Key = doel, value = instantie van Verantwoording
        self.Verantwoording = {}

    def ModuleXml (self):
        """Geeft de XML van de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<JuridischeVerantwoording xmlns="https://standaarden.overheid.nl/stop/imop/consolidatie/">',
               '\t<!-- bekendOp en ontvangenOp zijn voor deze demonstratie niet relevant -->',
               '\t<VerantwoordingInstrument>',
               '\t\t<heeftVerantwoording>']
        for verantwoording in self.Verantwoording.values ():
            xml.append ('')
            xml.extend (['\t\t\t' + x for x in verantwoording.ModuleXmlElement ()])
        xml.extend (['',
                     '\t\t<heeftVerantwoording>',
                     '\t</VerantwoordingInstrument>'
                     '</JuridischeVerantwoording>'])
        return xml

#----------------------------------------------------------------------
# Voeg een publicatie toe. Deze functionaliteit zal er in een 
# productie-waardige applicatie totaal anders uitzien.
#----------------------------------------------------------------------
    def VoegToe (self, verantwoording):
        """Voeg een 'publicatie' toe
        
        Argumenten:
        verantwoording Verantwoording informatie afkomstig uit de verwerking van consolidatieinformatie modules.
        """
        if verantwoording is not None:
            for doel, doelverantwoording in verantwoording.Verantwoording.items ():
                v = self.Verantwoording.get (doel)
                if v is None:
                    self.Verantwoording[doel] = doelverantwoording
                else:
                    v.Publicaties.extend (doelverantwoording.Publicaties)

#----------------------------------------------------------------------
# Overzicht van de publicaties per doel
#----------------------------------------------------------------------
class Verantwoording:

    def __init__(self):
        # Doel waarvoor de 
        self.Doel = None
        # Overzicht van de publicaties
        # In deze applicatie is deze informatie niet beschikbaar, doe net alsof.
        # Lijst met instanties van Publicatie
        self.Publicaties = []

    def ModuleXmlElement (self):
        """Geeft de XML van de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<Verantwoording>',
               '\t<doel>' + str(self.Doel) + '</doel>',
               '\t<!-- Overige gegevens zijn voor deze demonstratie niet relevant -->',
               '\t<gepubliceerdIn>']
        for publicatie in self.Publicaties:
            xml.extend ('\t\t' + x for x in publicatie.ModuleXmlElement ())
        xml.extend (['',
                     '\t<gepubliceerdIn>',
                     '</Verantwoording>'])
        return xml


#----------------------------------------------------------------------
# Modellering van een publicatie
#----------------------------------------------------------------------
class Publicatie:

    def __init__(self):
        # Aanduiding van de publicatie
        self.GemaaktOp = None
        # Identificatie/nummer van de uitgave van het publicatieblad
        self.Publicatieblad = None
        # Inhoud van de publicaties
        # In deze applicatie is deze informatie niet beschikbaar, doe net alsof.
        self.VoorInstrument = False
        self.VoorTijdstempels = False

    def ModuleXmlElement (self):
        """Geeft de XML van de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<JuridischeBronpublicatie>',
                '\t<!-- De echte url en aanvullende informatie is niet beschikbaar -->',
                '\t<url>https://www.officielebekendmakingen.nl/' + self.Publicatieblad + '</url>',
                '\t<gemaaktOp>' + self.GemaaktOp + '</gemaaktOp>',
                '\t<bladwijzers>']
        if self.VoorInstrument:
            xml.extend (['\t<Bladwijzer>', 
                         '\t\t<relevantVoor>inhoud</relevantVoor>',
                         '\t\t<url>https://www.officielebekendmakingen.nl/' + self.Publicatieblad + '#eId_inhoud</url>',
                         '\t</Bladwijzer>'])
        if self.VoorTijdstempels:
            xml.extend (['\t<Bladwijzer>', 
                         '\t\t<relevantVoor>juridischeWerking</relevantVoor>',
                         '\t\t<url>https://www.officielebekendmakingen.nl/' + self.Publicatieblad + '#eId_tijdstempels</url>',
                         '\t</Bladwijzer>'])
        xml.extend (['\t/<bladwijzers>',
                     '</JuridischeBronpublicatie>'])
        return xml

    def UrlVoorInstrument (self):
        return 'https://www.officielebekendmakingen.nl/' + self.Publicatieblad + '#eId_inhoud'
