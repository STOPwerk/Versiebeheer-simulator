#======================================================================
#
# In-memory representatie van de STOP CompleteToestanden module.
#
#======================================================================
#
# De complete toestanden worden opgeslagen in een in-memory versie van
# de STOP module, via de CompleteToestanden klasse.
#
#======================================================================

from stop_toestand import NogTeConsolideren

#----------------------------------------------------------------------
# CompleteToestanden module
#----------------------------------------------------------------------
class CompleteToestanden:

    def __init__(self):
        """Maak een lege module aan"""
        # Datum waarop de informatie in de module voor het eerst bekend is geworden
        self.BekendOp = None
        # Datum waarop de informatie door de STOP-gebruikende applicatie
        # ontvangen is (maar het mag niet eerder zijn dan bekendOp).
        self.OntvangenOp = None
        # Informatie over de manier waarop het overzicht is samengesteld
        # Instantie van TijdreisFilter
        self.Tijdreisfilter = None
        # Datum waarop de regeling of informatieobject als materieel uitgewerkt wordt beschouwd.
        self.MaterieelUitgewerktOp = None
        # Toestanden van het geconsolideerde instrument; volgorde is niet van belang
        # Lijst van instanties van ToestandIdentificatie
        self.ToestandIdentificatie = None
        # Inhoud van de toestanden zoals die op een bepaald moment in de tijd van toepassing is.
        # Volgorde is niet van belang
        # Lijst van instanties van ToestandCompleet
        self.ToestandInhoud = []
        # Tijdreisinformatie: koppeling van de identificatie, inhoud en tijdstempels voor een toestand
        # Aflopend gesorteerd op OntvangenOp, BekendOp, JuridischWerkendVanaf, GeldigVanaf
        self.Toestanden = []

    def ModuleXml (self):
        """Geeft de XML van de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<CompleteToestanden xmlns="https://standaarden.overheid.nl/stop/imop/consolidatie/">',
               '\t<bekendOp>' + self.BekendOp + '</bekendOp>',
               '\t<ontvangenOp>' + self.OntvangenOp + '</ontvangenOp>',
               '\t<heeftFilter>']
        xml.extend (['\t\t' + x for x in self.Tijdreisfilter.ModuleXmlElement ()])
        xml.append ('\t</heeftFilter>')

        if self.MaterieelUitgewerktOp:
            xml.append ('\t<materieelUitgewerktOp>' + self.MaterieelUitgewerktOp + '</materieelUitgewerktOp>')
        xml.extend (['',
                     '\t<bekendeToestanden>'])
        for idx, toestand in enumerate (self.ToestandIdentificatie):
            if idx > 0:
                xml.append ('')
            xml.extend (['\t\t' + x for x in toestand.IdentificatieXmlElement (idx)])
        xml.extend (['\t</bekendeToestanden>',
                     '',
                     '\t<toestanden>'])
        for idx, toestand in enumerate (self.ToestandInhoud):
            if idx > 0:
                xml.append ('')
            xml.extend (['\t\t' + x for x in toestand.ModuleXmlElement (idx)])
        xml.extend (['\t</toestanden>',
                     '',
                     '\t<tijdreisIndex>'])
        for toestand in self.Toestanden:
            xml.extend (['\t\t' + x for x in toestand.ModuleXmlElement ()])
        xml.extend (['\t</tijdreisIndex>',
                     '',
                     '</CompleteToestanden>'])
        return xml

#----------------------------------------------------------------------
# ToestandCompleet: inhoud van een toestand
#----------------------------------------------------------------------
class ToestandCompleet:

    def __init__(self):
        """Maak een lege toestandinhoud aan"""
        super().__init__ ()

        # De inhoud van een toestand kan een van de volgende drie vormen aannemen:

        # Als bepaald kan worden welke instrumentversie de inhoud van de toestand weergeeft:
        # de identificatie van de instrumentversie.
        # (Is None in de andere gevallen.) 
        self.Instrumentversie = None

        # Als niet bepaald kan worden welke instrumentversie de inhoud van de toestand weergeeft
        # omdat de consolidatie nog niet gecompleteerd is:
        # een of meer beschrijvingen van het gebruik van wel bekende instrumentversies en
        # welke uitwisselingen nog ontbreken/teveel zijn om tot de correcte inhoud 
        # van de toestand te komen.
        # Lijst met instanties van OnvolledigeVersie
        # (Is None in de andere gevallen.) 
        self.OnvolledigeVersies = None

        # Als de toestand de juridisch uitgewerkte staat van het instrument representeert:
        # geeft aan dat het instrument juridisch is uitgewerkt (is ingetrokken).
        # (Is False in de andere gevallen.) 
        self.IsJuridischUitgewerkt = False

    def ModuleXmlElement (self, index : int):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave
        
        Argumenten:

        index int  Index van de toestand zoals gebruikt in de tijdreistabel
        """
        xml = ['<ToestandCompleet>',
               '\t<id>' + str(index) + '</id>']
        if self.Instrumentversie:
            xml.append ('\t<instrumentVersie>' + self.Instrumentversie + '</instrumentVersie>')
        if not self.OnvolledigeVersies is None:
            xml.append ('\t<heeftOnvolledigeVersies>')
            for versie in self.OnvolledigeVersies:
                xml.extend (['\t\t' + x for x in versie.ModuleXmlElement ()])
            xml.append ('\t</heeftOnvolledigeVersies>')
        if self.IsJuridischUitgewerkt:
            xml.append ('\t<isJuridischUitgewerkt/>')
        xml.append ('<ToestandCompleet>')
        return xml

class OnvolledigeVersie(NogTeConsolideren):

    def __init__(self):
        super().__init__()
        # De identificatie van de instrumentversie die de inhoud van de toestand 
        # onvolledig weergeeft, 
        self.Instrumentversie = None

    def ModuleXmlElement (self):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<OnvolledigeVersie>',
               '\t<instrumentVersie>' + self.Instrumentversie + '</instrumentVersie>']
        xml.extend (['\t' + x for x in self._ModuleXmlAttributen ()])
        xml.append ('<OnvolledigeVersie>')
        return xml

#----------------------------------------------------------------------
# Tijdreisfilter specificeert
#----------------------------------------------------------------------
class Tijdreisfilter:

    def __init__(self):
        # Geeft aan dat de OntvangenOp datum in de tijdreisindex voorkomt
        self.OntvangenOpAanwezig = True
        # Geeft aan dat de BekendOp datum in de tijdreisindex voorkomt
        self.BekendOpAanwezig = True
        # Geeft aan dat de GeldigVanaf datum in de tijdreisindex voorkomt
        self.GeldigVanafAanwezig = True

    def ModuleXmlElement (self):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return ['<Tijdreisfilter>',
                '\t<ontvangenOpAanwezig>' + ('true' if self.OntvangenOpAanwezig else 'false') + '</ontvangenOpAanwezig>',
                '\t<bekendOpAanwezig>' + ('true' if self.BekendOpAanwezig else 'false') + '</bekendOpAanwezig>',
                '\t<GeldigVanafAanwezig>' + ('true' if self.GeldigVanafAanwezig else 'false') + '</geldigVanafAanwezig>',
                '</Tijdreisfilter>']

#----------------------------------------------------------------------
# Tijdstempels voor de toestanden
#----------------------------------------------------------------------
class Toestand:

    def __init__(self):
        super ().__init__()
        # OntvangenOp datum of None, afhankelijk van het filter
        self.OntvangenOp = None
        # BekendOp datum of None, afhankelijk van het filter
        self.BekendOp = None
        # JuridischWerkendVanaf datum
        self.JuridischWerkendVanaf = None
        # GeldigVanaf datum of None, afhankelijk van het filter
        self.GeldigVanaf = None
        # Index van de Toestandidentificatie in CompleteToestanden.Toestandidentificatie
        # Is None om aan te geven dat een instrument juridisch uitgewerkt is.
        self.Identificatie = None
        # Index van de ToestandCompleet in CompleteToestanden.ToestandInhoud
        self.Inhoud = None

    def ModuleXmlElement (self):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<Toestand>']
        if not self.OntvangenOp is None:
            xml.append ('\t<ontvangenOp>' + self.OntvangenOp + '</ontvangenOp>')
        if not self.BekendOp is None:
            xml.append ('\t<bekendOp>' + self.BekendOp + '</bekendOp>')
        xml.append ('\t<juridischWerkendVanaf>' + self.JuridischWerkendVanaf + '</juridischWerkendVanaf>')
        if not self.GeldigVanaf is None:
            xml.append ('\t<geldigVanaf>' + self.GeldigVanaf + '</geldigVanaf>')
        xml.extend (['\t<identificatie>' + str(self.Identificatie) + '</identificatie>',
                     '\t<inhoud>' + str(self.Inhoud) + '</inhoud>',
                     '</Toestand>'])
        return xml

#----------------------------------------------------------------------
# Tijdstempels voor intrekkingen
#----------------------------------------------------------------------
class JuridischUitgewerkt:

    def __init__(self, ontvangenOp : str, bekendOp : str, juridischUitgewerktOp : str):
        # OntvangenOp datum of None, afhankelijk van het filter
        self.OntvangenOp = ontvangenOp
        # BekendOp datum of None, afhankelijk van het filter
        self.BekendOp = bekendOp
        # JuridischWerkendVanaf datum, of None om aan te geven dat het instrument
        # niet (meer) juridisch uitgewerkt is.
        self.JuridischUitgewerktOp = juridischUitgewerktOp

    def ModuleXmlElement (self):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<JuridischUitgewerkt>']
        if not self.OntvangenOp is None:
            xml.append ('\t<ontvangenOp>' + self.OntvangenOp + '</ontvangenOp>')
        if not self.BekendOp is None:
            xml.append ('\t<bekendOp>' + self.BekendOp + '</bekendOp>')
        if not self.JuridischUitgewerktOp is None:
            xml.append ('\t<juridischUitgewerktOp>' + self.JuridischUitgewerktOp + '</juridischUitgewerktOp>')
        xml.append ('</JuridischUitgewerkt>')
        return xml
