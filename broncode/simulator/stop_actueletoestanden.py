#======================================================================
#
# In-memory representatie van de STOP ActueleToestanden module.
#
#======================================================================
#
# De actuele toestanden worden opgeslagen in een in-memory versie van
# de STOP module, via de ActueleToestanden klasse.
#
# De actuele toestanden worden gemaakt door de code in de
# MaakActueleToestanden klasse uit te voeren.
#
#======================================================================

from typing import List

from data_doel import Doel
from stop_toestand import Toestandidentificatie, NogTeConsolideren

#======================================================================
#
# ActueleToestanden module
#
#======================================================================
class ActueleToestanden:

    def __init__ (self, workId):
        """Maak een lege module aan
        
        workId string  Het work-ID zoals het bevoegd gezag dat gebruikt
        """
        # Datum waarop de informatie in de module voor het eerst bekend is geworden
        self.BekendOp = None
        # Datum waarop de informatie door de STOP-gebruikende applicatie
        # ontvangen is (maar het mag niet eerder zijn dan bekendOp).
        self.OntvangenOp = None
        # Datum waarop de regeling of informatieobject als materieel uitgewerkt wordt beschouwd.
        self.MaterieelUitgewerktOp = None
        # Toestanden van het geconsolideerde instrument, op volgorde van inwerkingtreding
        self.Toestanden : List[ToestandActueel] = []
        # Alleen voor weergave van de module met XML:
        self.WeergaveBeschrijving = """De actuele toestanden geven voor een regeling of informatieobject aan 
        wat de LVBB over de consolidatie ervan weet. De software van het bevoegd gezag kan nagaan of dat 
        overeenkomt met de voortgang van het consolidatieproces bij het bevoegd gezag. Deze module is
        gemaakt voor:<br><b>""" + workId + "</b>"


    def ModuleXml (self):
        """Geeft de XML van de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        xml = ['<ActueleToestanden xmlns="https://standaarden.overheid.nl/stop/imop/consolidatie/">',
               '\t<bekendOp>' + self.BekendOp + '</bekendOp>',
               '\t<ontvangenOp>' + self.OntvangenOp + '</ontvangenOp>']
        if self.MaterieelUitgewerktOp:
            xml.append ('\t<materieelUitgewerktOp>' + self.MaterieelUitgewerktOp + '</materieelUitgewerktOp>')
        for toestand in self.Toestanden:
            if not toestand.NietMeerActueel:
                xml.append ('')
                xml.extend (['\t' + x for x in toestand.ModuleXmlElement ()])
        xml.extend (['',
                     '</ActueleToestanden>'])
        return xml

#----------------------------------------------------------------------
# Toestand
#----------------------------------------------------------------------
class ToestandActueel(Toestandidentificatie, NogTeConsolideren):

    def __init__ (self):
        super ().__init__()
        # Eerste datum waarop de toestand juridisch in werking is
        self.JuridischWerkendVanaf = None
        # Eerste datum waarop de toestand juridisch niet meer in werking is,
        # of None als de juridische werking geen einddatum kent
        self.JuridischWerkendTot = None

        # De identificatie van de instrumentversie die de inhoud van de toestand geeft;
        # kan None zijn. 
        self.Instrumentversie = None

        # Doelen die tegelijk in werking treden maar die niet allemaal
        # dezelfde status voorschrijven voor de toestand. Er kan sprake
        # zijn van verschillende beoogde versies of combinatie van intrekking en versie(s).
        # Gesorteerd op de Identificatie van het doel
        self.TegensprekendeDoelen : List[TegensprekendDoel] = []

    def ModuleXmlElement (self):
        """Geeft de XML van dit element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave.
        """
        xml = ['<ToestandActueel>',
               '\t<FRBRExpression>' + self.ExpressionId + '</FRBRExpression>',
               '\t<juridischWerkendVanaf>' + self.JuridischWerkendVanaf + '</juridischWerkendVanaf>']
        if self.JuridischWerkendTot:
            xml.append ('\t<juridischWerkendTot>' + self.JuridischWerkendTot + '</juridischWerkendTot>')
        xml.extend (['\t' + x for x in self._ModuleXmlDoelen ()])
        if self.Instrumentversie:
            xml.append ('\t<instrumentVersie>' + self.Instrumentversie + '</instrumentVersie>')
        else:
            xml.append ('\t<nogTeConsolideren>')
            if len (self.TegensprekendeDoelen) > 0:
                for td in self.TegensprekendeDoelen: # volgorde is niet belangrijk
                    xml.extend (['\t\t' + x for x in td.ModuleXmlElement ()])
            xml.extend (['\t\t' + x for x in self._ModuleXmlAttributen ()])
            xml.append ('\t</nogTeConsolideren>')

        xml.append ('</ToestandActueel>')
        return xml

class TegensprekendDoel:

    def __init__ (self, doel : Doel, laatstBekend):
        # Het doel waarvoor nog uitwisselingen verwerkt moeten worden
        self.Doel = doel
        # De gemaaktOp van de meest recente uitwisseling die is meegenomen bij nog-te-verwerken conclusie 
        self.LaatstBekend = laatstBekend

    def ModuleXmlElement (self):
        """Geeft de XML uit deze klasse als onderdeel van een element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return ['<Tegensprekend>',
               '\t<tegensprekendDoel>' + self.Doel.Identificatie + '</tegensprekendDoel>',
               '\t<laatstBekend>' + self.LaatstBekend + '</laatstBekend>',
               '</Tegensprekend>']

