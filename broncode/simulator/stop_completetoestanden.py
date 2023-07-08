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
               '\t<ontvangenOp>' + self.OntvangenOp + '</ontvangenOp>']
        xml.extend (['\t' + x for x in self.Tijdreisfilter.ModuleXmlElement ()])

        if self.MaterieelUitgewerktOp:
            xml.append ('\t<materieelUitgewerktOp>' + self.MaterieelUitgewerktOp + '</materieelUitgewerktOp>')
        if len (self.ToestandIdentificatie) > 0:
            xml.append ('')
            for idx, toestand in enumerate (self.ToestandIdentificatie):
                xml.extend (['\t' + x for x in toestand.IdentificatieXmlElement (idx)])
        if len (self.ToestandInhoud) > 0:
            xml.append ('')
            for idx, toestand in enumerate (self.ToestandInhoud):
                xml.extend (['\t' + x for x in toestand.ModuleXmlElement (idx)])
        if len (self.Toestanden) > 0:
            xml.extend (['',
                        '\t<Tijdreisindex>'])
            for idx, toestand in enumerate (self.Toestanden):
                xml.extend (['\t\t' + x for x in toestand.ModuleXmlElement ()])
            xml.append ('\t</Tijdreisindex>')
        xml.extend (['',
                     '</CompleteToestanden>'])
        return xml

    WeergaveBeschrijving = "Het overzicht van de geconsolideerde instrument geeft de tijdreisbare geldigheidsinformatie van de (on)bekende versies van het instrument zoals die aan de LVBB zijn aangeleverd."

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
        self.IsNietInWerking = False

    def ModuleXmlElement (self, index : int):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave
        
        Argumenten:

        index int  Index van de toestand zoals gebruikt in de tijdreistabel
        """
        xml = ['<ToestandInhoud>',
               '\t<inhoudId>' + str(index) + '</inhoudId>']
        if self.Instrumentversie:
            xml.append ('\t<instrumentVersie>' + self.Instrumentversie + '</instrumentVersie>')
        if not self.OnvolledigeVersies is None:
            xml.append ('\t<isTePresenterenAls>')
            for versie in self.OnvolledigeVersies:
                xml.extend (['\t\t' + x for x in versie.ModuleXmlElement ()])
            xml.append ('\t</isTePresenterenAls>')
        if self.IsNietInWerking:
            xml.append ('\t<isNietInWerking/>')
        xml.append ('</ToestandInhoud>')
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
               '\t<instrumentVersie>' + self.Instrumentversie + '</instrumentVersie>',
               '\t<nogTeConsolideren>']
        xml.extend (['\t\t' + x for x in self._ModuleXmlAttributen ()])
        xml.extend (['\t</nogTeConsolideren>',
                     '</OnvolledigeVersie>'])
        return xml

#----------------------------------------------------------------------
# Tijdreisfilter specificeert
#----------------------------------------------------------------------
class Tijdreisfilter:

    def __init__(self):
        # Geeft aan welke tijdreis gebruikt is voor het samenstellen van het overzicht
        self.SoortTijdreis = None
        # Geeft aan dat de OntvangenOp datum in de tijdreisindex voorkomt
        self.OntvangenOpAanwezig = True
        # Geeft aan dat de BekendOp datum in de tijdreisindex voorkomt
        self.BekendOpAanwezig = True
        # Geeft aan dat de GeldigVanaf datum in de tijdreisindex voorkomt
        self.GeldigVanafAanwezig = True

    _SoortTijdreis_ActueleToestanden = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_at'
    _SoortTijdreis_AlleenJuridischWerkendVanaf = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_jwv'
    _SoortTijdreis_BekendOpGeldigVanafJuridischWerkendVanaf = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_b_gv_jwv'
    _SoortTijdreis_BekendOpJuridischWerkendVanaf = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_b_jwv'
    _SoortTijdreis_GeldigVanafJuridischWerkendVanaf = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_gv_jwv'
    _SoortTijdreis_OntvangenOpBekendOpJuridischWerkendVanaf = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_o_b_jwv'
    _SoortTijdreis_OntvangenOpBekendOpJuridischWerkendVanaf_Update = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_o_b_jwv_u'
    _SoortTijdreis_OntvangenOpGeldigVanafJuridischWerkendVanaf = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_o_gv_jwv'
    _SoortTijdreis_OntvangenOpGeldigVanafJuridischWerkendVanaf_Update = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_o_gv_jwv_u'
    _SoortTijdreis_OntvangenOpJuridischWerkendVanaf = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_o_jwv'
    _SoortTijdreis_OntvangenOpJuridischWerkendVanaf_Update = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_o_jwv_u'
    _SoortTijdreis_ExTunc = 'http://omgevingswet/tijdreis/extunc'
    _SoortTijdreis_ExTunc_Update = 'http://omgevingswet/tijdreis/extunc/update'
    _SoortTijdreis_CompleteToestanden = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_ct'
    _SoortTijdreis_CompleteToestanden_Update = 'https://identifier.overheid.nl/tooi/def/thes/kern/c_nntb_ct_u'

    def ModuleXmlElement (self):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return ['<Tijdreisfilter>',
                '\t<soortTijdreis>' + (self.SoortTijdreis if self.SoortTijdreis else 'https://tijdre.is/42') + '</soortTijdreis>',
                '\t<ontvangenOpAanwezig>' + ('true' if self.OntvangenOpAanwezig else 'false') + '</ontvangenOpAanwezig>',
                '\t<bekendOpAanwezig>' + ('true' if self.BekendOpAanwezig else 'false') + '</bekendOpAanwezig>',
                '\t<geldigVanafAanwezig>' + ('true' if self.GeldigVanafAanwezig else 'false') + '</geldigVanafAanwezig>',
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
        xml = ['<Tijdreistupel>']
        if not self.OntvangenOp is None:
            xml.append ('\t<ontvangenOp>' + self.OntvangenOp + '</ontvangenOp>')
        if not self.BekendOp is None:
            xml.append ('\t<bekendOp>' + self.BekendOp + '</bekendOp>')
        xml.append ('\t<juridischWerkendVanaf>' + self.JuridischWerkendVanaf + '</juridischWerkendVanaf>')
        if not self.GeldigVanaf is None:
            xml.append ('\t<geldigVanaf>' + self.GeldigVanaf + '</geldigVanaf>')
        xml.extend (['\t<toestandId>' + str(self.Identificatie) + '</toestandId>',
                     '\t<inhoudId>' + str(self.Inhoud) + '</inhoudId>',
                     '</Tijdreistupel>'])
        return xml
