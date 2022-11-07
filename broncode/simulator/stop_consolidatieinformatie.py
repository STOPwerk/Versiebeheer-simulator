#======================================================================
#
# In-memory representatie van de STOP ConsolidatieInformatie module.
#
# In Python wordt geen onderscheid gemaakt tussen regeling en
# informatieobject; de term "instrument" wordt voor beide gebruikt.
#
# In de applicatie wordt eerst een in-memory representatie van de
# inhoud van een XML bestand gemaakt, daarna worden alle ingelezen
# ConsolidatieInformatie instanties omgezet naar versiebeheerinformatie
# per instrument.
#
#======================================================================

import re
from typing import Dict, List

from data_doel import Doel
from stop_naamgeving import Naamgeving

#======================================================================
# ConsolidatieInformatie representeert de hele module
#======================================================================
class ConsolidatieInformatie:

#----------------------------------------------------------------------
# Aanmaken lege module
#----------------------------------------------------------------------
    def __init__ (self, log, pad):
        """Maak een lege module aan.
        
        Argumenten:
        log Meldingen verzameling van meldingen; alleen nodig voor het inlezen
        pad string Pad van het XML bestand; alleen nodig voor het inlezen
        """
        self._Log = log
        self._Pad = pad

        # Tijdstip van de momentopname voor alle elementen in de module
        self.GemaaktOp = None
        # Tijdstip waarop de informatie in de publicatie bekend is geworden
        # In deze applicatie wordt aangenomen dat het gelijk is aan de datum in
        # gemaaktOp als bekendOp niet aanwezig is in een element van de consolidatie informatie.
        self._BekendOp = None
        # Tijdstip waarop de informatie door de STOP-gebruikende applicatie
        # ontvangen is (maar het mag niet eerder zijn dan bekendOp)
        # In deze applicatie wordt aangenomen dat het gelijk is aan de datum in
        # gemaaktOp.
        self.OntvangenOp = None

        # Doorgeven van instrumentversies
        self.BeoogdeVersies : List[BeoogdeVersie] = []
        # Doorgeven van terugtrekkingen
        self.Terugtrekkingen : List[Terugtrekking] = []
        # Doorgeven van intrekkingen
        self.Intrekkingen : List[Intrekking] = []
        # Doorgeven van terugtrekkingen
        self.TerugtrekkingenIntrekking : List[TerugtrekkingIntrekking] = []
        # Doorgeven van tijdstempels
        self.Tijdstempels : List[Tijdstempel] = []
        # Doorgeven van terugtrekking tijdstempels
        self.TijdstempelTerugtrekkingen: List[TerugtrekkingTijdstempel] = []
        # Doorgeven van materieel uitgewerkte instrumentens
        self.MaterieelUitgewerkt: List[MaterieelUitgewerkt] = []
        # Geeft aan of er fouten zijn gesignaleerd bij het inlezen van de module
        self.IsValide = True

        # Geeft aan dat de consolidatie-informatie bij een revisie is gevoegd en niet bij een instrument dat gepubliceerd wordt.
        # Dit volgt uit de context van de uitwisseling, niet uit de STOP module.
        # In de simulator wordt het gezet vanuit de procesopties of vanuit de simulatie van de acties van het bevoegd gezag.
        self.IsRevisie = False

    def ModuleXml (self):
        """Geef de XML voor deze STOP module
        """
        xml = ['<ConsolidatieInformatie xmlns="' + ConsolidatieInformatie.DataNamespace + '">']
        xml.append ('\t<gemaaktOp>' + self.GemaaktOp + '</gemaaktOp>')
        perCollectie = {}
        for lijst in [self.BeoogdeVersies, self.Terugtrekkingen, self.Intrekkingen, self.TerugtrekkingenIntrekking, self.Tijdstempels, self.TijdstempelTerugtrekkingen, self.MaterieelUitgewerkt]:
            for ci in lijst:
                collectie = ci.ModuleXmlInCollectie ()
                if not collectie in perCollectie:
                    perCollectie[collectie] = []
                perCollectie[collectie].extend (['\t\t' + line for line in ci.ModuleXmlElement (False)])
        for collectie in sorted (perCollectie):
            if collectie:
                xml.append ('\t<' + collectie + '>')
            xml.extend (perCollectie[collectie])
            if collectie:
                xml.append ('\t</' + collectie + '>')
        xml.append ('</ConsolidatieInformatie>')
        return xml

#----------------------------------------------------------------------
# Inlezen van XML
#----------------------------------------------------------------------
    @staticmethod
    def IsConsolidatieInformatieBestand (xml):
        """Geeft aan of de XML een ConsolidatieInformatie module is.
        
        Argumenten:
        xml xml.etree.Element XML root element gelezen uit het bestand
        """
        return xml.tag == '{' + ConsolidatieInformatie.DataNamespace + '}ConsolidatieInformatie'

    @staticmethod
    def LeesXml (log, pad, xml):
        """Lees de inhoud van de module uit de XML.
        
        Argumenten:
        log Meldingen verzameling van meldingen
        pad string Pad van het XML bestand; alleen gebruikt voor meldingen
        xml xml.etree.Element XML root element gelezen uit het bestand
        
        Resultaat is een al dan niet valide ConsolidatieInformatie, 
        of None als het geen ConsolidatieInformatie module is
        """
        if not ConsolidatieInformatie.IsConsolidatieInformatieBestand (xml):
            return

        module = ConsolidatieInformatie (log, pad)
        module.GemaaktOp = module._LeesGemaaktOp (xml)
        if not module.GemaaktOp is None:
            module.OntvangenOp = module.GemaaktOp[0:10]
            module._BekendOp = module.GemaaktOp[0:10]

        def _VoegToe (lijst, element):
            if not element is None:
                lijst.append (element)
                bekendOp = element.BekendOp ()
                if not module._BekendOp is None and not bekendOp is None and bekendOp > module._BekendOp:
                    module._BekendOp = bekendOp

        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}BeoogdeRegeling'):
            _VoegToe (module.BeoogdeVersies, BeoogdeVersie.LeesXmlMetVersie (module, elt, True))
        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}BeoogdInformatieobject'):
            _VoegToe (module.BeoogdeVersies, BeoogdeVersie.LeesXmlMetVersie (module, elt, False))
        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}Intrekking'):
            _VoegToe (module.Intrekkingen, Intrekking.LeesXml (module, elt))
        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}TerugtrekkingRegeling'):
            _VoegToe (module.Terugtrekkingen, Terugtrekking.LeesXml (module, elt, True))
        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}TerugtrekkingInformatieobject'):
            _VoegToe (module.Terugtrekkingen, Terugtrekking.LeesXml (module, elt, False))
        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}TerugtrekkingIntrekking'):
            _VoegToe (module.TerugtrekkingenIntrekking, TerugtrekkingIntrekking.LeesXml (module, elt))
        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}Tijdstempel'):
            _VoegToe (module.Tijdstempels, Tijdstempel.LeesXml (module, elt))
        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}TerugtrekkingTijdstempel'):
            _VoegToe (module.TijdstempelTerugtrekkingen, TerugtrekkingTijdstempel.LeesXml (module, elt))
        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}MaterieelUitgewerkt'):
            _VoegToe (module.MaterieelUitgewerkt, MaterieelUitgewerkt.LeesXml (module, elt, False))
        for elt in xml.findall ('.//{' + ConsolidatieInformatie.DataNamespace + '}TerugtrekkingMaterieelUitgewerkt'):
            _VoegToe (module.MaterieelUitgewerkt, MaterieelUitgewerkt.LeesXml (module, elt, True))

        if not module._BekendOp is None and module._BekendOp > module.OntvangenOp:
            module._Log.Informatie ("Bestand '" + module._Pad + "': bekendOp ligt in de toekomst - dat is alleen toegestaan in deze applicatie")

        if module.IsValide:
            log.Detail ("Bestand '" + pad + "' bevat valide ConsolidatieInformatie")
        return module

#----------------------------------------------------------------------
# Hulpfuncties voor het inlezen van XML
#----------------------------------------------------------------------
    def _VindElement (self, containerElement, naam, moetBestaan = True):
        """Lees de waarde van het <naam> element dat als kind onder het containerElement hangt"""
        elt = containerElement.find ("data:" + naam, ConsolidatieInformatie._Namespaces)
        if elt is None:
            if moetBestaan:
                self._Log.Fout ("Bestand '" + self._Pad + "': " + naam + " ontbreekt")
                self.IsValide = False
            return
        return elt

    def _VindElementen (self, containerElement, naam, moetBestaan = True):
        """Lees de waarde van het <naam> element dat als kind onder het containerElement hangt"""
        elts = [x for x in containerElement.findall ("data:" + naam, ConsolidatieInformatie._Namespaces)]
        if len (elts) == 0:
            if moetBestaan:
                self._Log.Fout ("Bestand '" + self._Pad + "': " + naam + " ontbreekt")
                self.IsValide = False
            return
        return elts

    DataNamespace = 'https://standaarden.overheid.nl/stop/imop/data/'
    _Namespaces = { 'data': DataNamespace }

    def _LeesElement (self, containerElement, naam, moetBestaan = True):
        """Lees de waarde van het <naam> element dat als kind onder het containerElement hangt"""
        elt = self._VindElement (containerElement, naam, moetBestaan)
        if not elt is None:
            return elt.text

    def _LeesElementen (self, containerElement, containerNaam, naam, moetBestaan = True):
        """Lees de waarde van een sequentie van van <naam> element dat als kind onder 
        het <containerNaam> element van het containerElement hangt"""
        container = self._VindElement (containerElement, containerNaam, moetBestaan)
        if not container is None:
            return [elt.text for elt in container.findall ("data:" + naam, ConsolidatieInformatie._Namespaces)]

    def _LeesGemaaktOp (self, containerElement):
        """Lees de waarde van het gemaaktOp element dat als kind onder het containerElement hangt"""
        gemaaktOp = self._LeesElement (containerElement, "gemaaktOp")
        if gemaaktOp and ConsolidatieInformatie.ValideerGemaaktOp (self._Log, self._Pad, gemaaktOp):
            return gemaaktOp
        self.IsValide = False
        return None

    @staticmethod
    def ValideerGemaaktOp (log, pad, gemaaktOp, naam = 'gemaaktOp'):
        """Valideer de waarde van een gemaaktOp tijdstip

        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het bestand waar de gemaaktOp in voorkomt
        gemaaktOp string  Te valideren waarde
        naam string  Naam van de parameter die het tijdstip als waarde heeft

        Geeft de waarde terug als de waarde valide is, anders None
        """
        if gemaaktOp and ConsolidatieInformatie._GemaaktOpPatroon.match (gemaaktOp):
            return gemaaktOp
        log.Fout ("Bestand '" + pad + "': " + naam + " moet een UTC tijdstip zijn in plaats van '" + (gemaaktOp if gemaaktOp else 'null') + "'")
        return None

    _GemaaktOpPatroon = re.compile ('^[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$')

    @staticmethod
    def ValideerDatum (log, pad, naam, datum):
        """Valideer de waarde van een datum

        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het bestand waar de datum in voorkomt
        naam string  Naam van de parameter die de datum als waarde heeft
        datum string  Te valideren waarde

        Geeft de waarde terug als de waarde valide is, anders None
        """
        if datum:
            if ConsolidatieInformatie._DatumPatroon.match (datum):
                return datum
            log.Fout ("Bestand '" + pad + "': " + naam + " moet een datum zonder tijdinformatie zijn in plaats van '" + datum + "'")
        return None

    _DatumPatroon = re.compile ('^[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}$')

    def _LeesBekendOp (self, containerElement):
        """Lees de waarde van het gemaaktOp element dat als kind onder het containerElement hangt"""
        bekendOp = self._LeesElement (containerElement, "bekendOp", False)
        if bekendOp:
            if ConsolidatieInformatie.ValideerDatum (self._Log, self._Pad, "bekendOp", bekendOp):
                return bekendOp
            self.IsValide = False

#======================================================================
# Onderdelen van de ConsolidatieInformatie module
#======================================================================

#----------------------------------------------------------------------
# Momentopname (doel + gemaaktOp)
#----------------------------------------------------------------------
class Momentopname:

    def __init__ (self, doel : Doel, gemaaktOp : str):
        """Maak een nieuwe momentopname aan.
        
        Argumenten:
        
        doel Doel  Doel/branch waar de momentopname onderdeel van is
        gemaaktOp string  Tijdstip waarop de momentopname gemaakt is
        """
        self.Doel = doel
        self.GemaaktOp = gemaaktOp

    @staticmethod
    def LeesXml (module, xml):
        """Lees Basisversie/OntvlochtenVersie/VervlochtenVersie"""
        doel = Doel.DoelInstantie (module._LeesElement (xml, "doel"))
        gemaaktOp = module._LeesGemaaktOp (xml)
        return Momentopname (doel, gemaaktOp)

#----------------------------------------------------------------------
# Basisklasse voor alle consolidatie-informatie elementen
#----------------------------------------------------------------------
class VoorInstrumentEnTijdstempel:

    def __init__(self, consolidatieInformatie):
        self.ConsolidatieInformatie = consolidatieInformatie
        # Tijdstip waarop de informatie in de publicatie bekend is geworden
        self._BekendOp = None
        # eId in het besluit waar de regelingversie/wijziging/tijdstempel te vinden is
        self.eId = None

    def _LeesGemeenschappelijkeInformatie (self, module, xml):
        """Lees eId"""
        eId = module._VindElement (xml, "eId", False)
        if not eId is None:
            self.eId = eId.text
        return self


    def BekendOp (self):
        """Tijdstip waarop de informatie in een publicatie bekend is geworden"""
        if self._BekendOp:
            return self._BekendOp
        return self.ConsolidatieInformatie._BekendOp

    def OntvangenOp (self):
        """Tijdstip waarop de informatie in een publicatie ontvangen is; kan niet voor bekendOp liggen"""
        ontvangenOp = self.ConsolidatieInformatie.OntvangenOp
        if self._BekendOp and self._BekendOp > ontvangenOp:
            ontvangenOp = self._BekendOp
        return ontvangenOp

    def ModuleXmlElement (self, inclusiefImplicieteTijdstempels = True):
        """Geeft de XML van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave
        
        Argumenten:
        
        inclusiefImplicieteTijdstempels bool  Geeft aan of ontvangenOp/bekendOp altijd opgenomen moeten worden (als comment)
        """
        naam = self.ModuleXmlNaam ()
        xml = ["<" + naam + ">"]
        if inclusiefImplicieteTijdstempels:
            # Alleen voor weergave; is geen onderdeel van het STOP schema!
            xml.append ('\t<!-- ontvangenOp: ' + self.OntvangenOp() + ' -->')
        bekendOp = self.BekendOp ()
        if bekendOp >= self.ConsolidatieInformatie.OntvangenOp:
            if inclusiefImplicieteTijdstempels:
                # Alleen voor weergave
                # Alleen een bekendOp in het verleden zal door BG aan LVBB worden aangeleverd
                # Een bekendOp gelijk aan ontvangenOp of in de toekomst betreft een LVBB publicatie,
                # dan bepaalt LVBB de bekendOp datum o.b.v. de publicatiedatum.
                xml.append ('\t<!-- bekendOp: ' + bekendOp + ' -->')
        else:
            xml.append ('\t<bekendOp>' + bekendOp + '</bekendOp>')
        xml.extend ([*['\t' + x for x in self._ModuleXmlElement ()],
                    "</" + naam + ">"])
        return xml

#----------------------------------------------------------------------
# Basisklasse voor onderdelen gerelateerd aan een instrument
#----------------------------------------------------------------------
class VoorInstrument (VoorInstrumentEnTijdstempel):

    def __init__(self, consolidatieInformatie, workId, doelen):
        super ().__init__ (consolidatieInformatie)
        self.WorkId = workId
        # In deze simulator wordt doelen als array gebruikt ivm BeoogdeRegelgeving
        # ook al is er maar 1 doel voor een intrekking of terugtrekking. Het maakt
        # de code van de simulator eenvoudiger.
        if not doelen is None:
            if not isinstance (doelen, list):
                doelen = [doelen]
            doelen = [Doel.DoelInstantie (d) for d in doelen]
        self.Doelen : List[Doel] = doelen
        self.Basisversies : Dict[Doel,Momentopname] = {}

    def _LeesGemeenschappelijkeInformatie (self, module, xml, moetBestaan, alleenBasisversie):
        """Lees eId en gemaaktOpBasisVan"""
        super ()._LeesGemeenschappelijkeInformatie (module, xml)
        opBasisVan = module._VindElement (xml, "gemaaktOpBasisVan", moetBestaan)
        if not opBasisVan is None:
            elts = module._VindElementen (opBasisVan, "Basisversie", moetBestaan)
            if not elts is None:
                self.Basisversies = VoorInstrument._LeesMomentopnamen (module, elts, "Basisversie")
            if not alleenBasisversie:
                elts = module._VindElementen (opBasisVan, "OntvlochtenVersie", False)
                if not elts is None:
                    self.OntvlochtenVersies = VoorInstrument._LeesMomentopnamen (module, elts, "OntvlochtenVersie")
                elts = module._VindElementen (opBasisVan, "VervlochtenVersie", False)
                if not elts is None:
                    self.VervlochtenVersies = VoorInstrument._LeesMomentopnamen (module, elts, "VervlochtenVersie")
        self._BekendOp = module._LeesBekendOp (xml)
        return self

    @staticmethod
    def _LeesMomentopnamen (module, elts, collectie):
        resultaat = {}
        for elt in elts:
            momentopname = Momentopname.LeesXml (module, elt)
            if momentopname.Doel in resultaat:
                module._Log.Fout ("Bestand '" + module._Pad + "': doel " + str(momentopname.Doel) + " komt meerdere keren voor in " + collectie)
                module.IsValide = False
            else:
                resultaat[momentopname.Doel] = momentopname
        return resultaat

    def _ModuleXmlElement (self):
        """Geeft de XML van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return [*[x for x in self._ModuleXmlAttrinuten ()],
                *self._GemeenschappelijkeInformatieXml ()]

    def _DoelenXml (self, isEnkelvoudig):
        """Geeft de XML voor de doelen. In deze applicatie alleen nodig voor weergave."""
        if isEnkelvoudig:
            return ["<doel>" + str(self.Doelen[0]) + "</doel>"]
        else:
            return ["<doelen>",
                *["\t<doel>" + str(doel) + "</doel>" for doel in self.Doelen],
                "</doelen>"]

    def _GemeenschappelijkeInformatieXml (self):
        """Geeft de XML van de gemeenschappelijke informatie in het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave."""
        xml = []
        if len (self.Basisversies) > 0 or len (self.OntvlochtenVersies) > 0 or len (self.VervlochtenVersies) > 0:
            xml.append ("<gemaaktOpBasisVan>")
            for versie in sorted (self.Basisversies.values (), key = lambda x: x.GemaaktOp + str(x.Doel)):
                xml.append ("\t<Basisversie>")
                xml.append ("\t\t<doel>" + str(versie.Doel) + "</doel>")
                xml.append ("\t\t<gemaaktOp>" + versie.GemaaktOp + "</gemaaktOp>")
                xml.append ("\t</Basisversie>")
            if hasattr (self, 'VervlochtenVersies'):
                for versie in sorted (self.VervlochtenVersies.values (), key = lambda x: x.GemaaktOp + str(x.Doel)):
                    xml.append ("\t<VervlochtenVersie>")
                    xml.append ("\t\t<doel>" + str(versie.Doel) + "</doel>")
                    xml.append ("\t\t<gemaaktOp>" + versie.GemaaktOp + "</gemaaktOp>")
                    xml.append ("\t</VervlochtenVersie>")
            if hasattr (self, 'OntvlochtenVersies'):
                for versie in sorted (self.OntvlochtenVersies.values (), key = lambda x: x.GemaaktOp + str(x.Doel)):
                    xml.append ("\t<OntvlochtenVersie>")
                    xml.append ("\t\t<doel>" + str(versie.Doel) + "</doel>")
                    xml.append ("\t\t<gemaaktOp>" + versie.GemaaktOp + "</gemaaktOp>")
                    xml.append ("\t</OntvlochtenVersie>")
            xml.append ("</gemaaktOpBasisVan>")

        return xml

#----------------------------------------------------------------------
# BeoogdeRegeling / BeoogdInformatieobject
#----------------------------------------------------------------------
class BeoogdeVersie (VoorInstrument):

    def __init__ (self, consolidatieInformatie, doelen, workId, expressionId):
        super ().__init__ (consolidatieInformatie, workId, doelen)
        self.OntvlochtenVersies : Dict[Doel,Momentopname] = {}
        self.VervlochtenVersies : Dict[Doel,Momentopname] = {}
        self.ExpressionId = expressionId

    @staticmethod
    def LeesXmlMetVersie (module, xml, isRegeling):
        """Lees BeoogdeRegeling / BeoogdInformatieobject"""
        doelen = module._LeesElementen (xml, "doelen", "doel")
        expressionId = module._LeesElement (xml, "instrumentVersie", False)
        if not expressionId is None:
            if isRegeling:
                if not Naamgeving.IsRegeling (expressionId):
                    module._Log.Fout ("Bestand '" + module._Pad + "': expression identificatie '" + expressionId + "' past niet bij een regeling")
                    module.IsValide = False
                    return
            else:
                if not Naamgeving.IsInformatieobject (expressionId):
                    module._Log.Fout ("Bestand '" + module._Pad + "': expression identificatie '" + expressionId + "' past niet bij een informatieobject")
                    module.IsValide = False
                    return
            return BeoogdeVersie (module, doelen, Naamgeving.WorkVan (expressionId), expressionId)._LeesGemeenschappelijkeInformatie (module, xml, False, False)
        workId = module._LeesElement (xml, "instrument", False)
        if workId is None:
            module._Log.Fout ("Bestand '" + module._Pad + "': Instrument of Instrumentversie ontbreekt")
            module.IsValide = False
        else:
            if isRegeling:
                if not Naamgeving.IsRegeling (workId):
                    module._Log.Fout ("Bestand '" + module._Pad + "': work identificatie '" + workId + "' past niet bij een regeling")
                    module.IsValide = False
                    return
            else:
                if not Naamgeving.IsInformatieobject (workId):
                    module._Log.Fout ("Bestand '" + module._Pad + "': work identificatie '" + workId + "' past niet bij een informatieobject")
                    module.IsValide = False
                    return
            return BeoogdeVersie (module, doelen, workId, None)._LeesGemeenschappelijkeInformatie (module, xml, False, False)

    @staticmethod
    def LeesXmlZonderVersie (module, xml, isRegeling):
        """Lees ???"""
        doelen = module._LeesElementen (xml, "doelen", "doel")
        workId = module._LeesElement (xml, "instrument")
        if not workId is None:
            if not Naamgeving.IsRegeling (workId) and not Naamgeving.IsInformatieobject (workId):
                module._Log.Fout ("Bestand '" + module._Pad + "': work identificatie " + workId + " past niet bij een regeling of informatieobject")
                module.IsValide = False
                return
            return BeoogdeVersie (module, doelen, workId, None)._LeesGemeenschappelijkeInformatie (module, xml, True)

    def ModuleXmlInCollectie (self):
        """Geeft de naam van de collectie in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "BeoogdeRegelgeving"

    def ModuleXmlNaam (self):
        """Geeft de naam van het element in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "BeoogdeRegeling" if Naamgeving.IsRegeling (self.WorkId) else "BeoogdInformatieobject"

    def _ModuleXmlAttrinuten (self):
        """Geeft de XML van de attributen van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return [*[x for x in self._DoelenXml (False)],
                "<instrument>" + self.WorkId + "</instrument>" if self.ExpressionId is None else "<instrumentVersie>" + self.ExpressionId + "</instrumentVersie>"]

#----------------------------------------------------------------------
# Intrekking (Regeling / Informatieobject)
#----------------------------------------------------------------------
class Intrekking (VoorInstrument):

    def __init__ (self, consolidatieInformatie, doelen, workId):
        super ().__init__ (consolidatieInformatie, workId, doelen)

    @staticmethod
    def LeesXml (module, xml):
        """Lees Intrekking"""
        doelen = module._LeesElement (xml, "doel")
        workId = module._LeesElement (xml, "instrument")
        if not workId is None:
            if not Naamgeving.IsRegeling (workId) and not Naamgeving.IsInformatieobject (workId):
                module._Log.Fout ("Bestand '" + module._Pad + "': work identificatie " + workId + " past niet bij een regeling of informatieobject")
                module.IsValide = False
                return
            return Intrekking (module, doelen, workId)._LeesGemeenschappelijkeInformatie (module, xml, True, True)

    def ModuleXmlInCollectie (self):
        """Geeft de naam van de collectie in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "Intrekkingen"

    def ModuleXmlNaam (self):
        """Geeft de naam van het element in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "Intrekking"

    def _ModuleXmlAttrinuten (self):
        """Geeft de XML van de attributen van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return [*[x for x in self._DoelenXml (True)],
                "<instrument>" + self.WorkId + "</instrument>"]

#----------------------------------------------------------------------
# TerugtrekkingRegeling / TerugtrekkingInformatieobject
#----------------------------------------------------------------------
class Terugtrekking (VoorInstrument):

    def __init__ (self, consolidatieInformatie, doelen, workId):
        super ().__init__ (consolidatieInformatie, workId, doelen)

    @staticmethod
    def LeesXml (module, xml, isRegeling):
        """Lees TerugtrekkingRegeling/TerugtrekkingInformatieobject/TerugtrekkingIntrekking"""
        doelen = module._LeesElement (xml, "doel")
        workId = module._LeesElement (xml, "instrument")
        if not workId is None:
            if isRegeling:
                if not Naamgeving.IsRegeling (workId):
                    module._Log.Fout ("Bestand '" + module._Pad + "': work identificatie " + workId + " past niet bij een regeling")
                    module.IsValide = False
                    return
            else:
                if not Naamgeving.IsInformatieobject (workId):
                    module._Log.Fout ("Bestand '" + module._Pad + "': work identificatie " + workId + " past niet bij een informatieobject")
                    module.IsValide = False
                    return
            return Terugtrekking (module, doelen, workId)._LeesGemeenschappelijkeInformatie (module, xml, True, True)

    def ModuleXmlInCollectie (self):
        """Geeft de naam van de collectie in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "Terugtrekkingen"

    def ModuleXmlNaam (self):
        """Geeft de naam van het element in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "TerugtrekkingRegeling" if Naamgeving.IsRegeling (self.WorkId) else "TerugtrekkingInformatieobject"

    def _ModuleXmlAttrinuten (self):
        """Geeft de XML van de attributen van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return [*[x for x in self._DoelenXml (True)],
                "<instrument>" + self.WorkId + "</instrument>"]

#----------------------------------------------------------------------
# TerugtrekkingIntrekking
#----------------------------------------------------------------------
class TerugtrekkingIntrekking (VoorInstrument):

    def __init__ (self, consolidatieInformatie, doelen, workId):
        super ().__init__ (consolidatieInformatie, workId, doelen)

    @staticmethod
    def LeesXml (module, xml):
        """Lees TerugtrekkingRegeling/TerugtrekkingInformatieobject/TerugtrekkingIntrekking"""
        doelen = module._LeesElement (xml, "doel")
        workId = module._LeesElement (xml, "instrument")
        if not workId is None:
            if not Naamgeving.IsRegeling (workId) and not Naamgeving.IsInformatieobject (workId):
                module._Log.Fout ("Bestand '" + module._Pad + "': work identificatie " + workId + " past niet bij een regeling")
                module.IsValide = False
                return
            return TerugtrekkingIntrekking (module, doelen, workId)._LeesGemeenschappelijkeInformatie (module, xml, False, True)

    def ModuleXmlInCollectie (self):
        """Geeft de naam van de collectie in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "Terugtrekkingen"

    def ModuleXmlNaam (self):
        """Geeft de naam van het element in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "TerugtrekkingIntrekking"

    def _ModuleXmlAttrinuten (self):
        """Geeft de XML van de attributen van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return [*[x for x in self._DoelenXml (True)],
                "<instrument>" + self.WorkId + "</instrument>"]

#----------------------------------------------------------------------
# Basisklasse voor Tijdstempel / TerugtrekkingTijdstempel
#----------------------------------------------------------------------
class VoorTijdstempel(VoorInstrumentEnTijdstempel):

    def __init__(self, consolidatieInformatie):
        """Maak een lege tijdstempel aan"""
        super ().__init__ (consolidatieInformatie)
        self.Doel = None
        self.IsGeldigVanaf = None # In plaats van soortTijdstempel enumeratie
        # Tijdstip waarop de informatie in de publicatie bekend is geworden
        self._BekendOp = None

    def _LeesXml (self, module, xml):
        """Lees Tijdstempel/TerugtrekkingTijdstempel"""
        self.Doel = Doel.DoelInstantie (module._LeesElement (xml, "doel"))
        soort = module._LeesElement (xml, "soortTijdstempel")
        self.IsGeldigVanaf = None
        if not soort is None:
            if soort == "juridischWerkendVanaf":
                self.IsGeldigVanaf = False
            elif soort == "geldigVanaf":
                self.IsGeldigVanaf = True
            else:
                module._Log.Fout ("Bestand '" + module._Pad + "': onbekende soortTijdstempel '" + soort + "'")
                module.IsValide = False
        self._BekendOp = module._LeesBekendOp (xml)
        super ()._LeesGemeenschappelijkeInformatie (module, xml)

#----------------------------------------------------------------------
# Tijdstempel
#----------------------------------------------------------------------
class Tijdstempel(VoorTijdstempel):

    @staticmethod
    def LeesXml (module, xml):
        """Lees Tijdstempel"""
        tijdstempel = Tijdstempel (module)
        tijdstempel._LeesXml (module, xml)
        return tijdstempel


    def __init__ (self, consolidatieInformatie):
        super().__init__ (consolidatieInformatie)
        self.Datum = None

    def _LeesXml (self, module, xml):
        """Lees Tijdstempel"""
        super()._LeesXml (module, xml)
        datum = module._LeesElement (xml, "datum")
        if datum is None:
            return
        datum = datum[0:10]
        if not ConsolidatieInformatie._DatumPatroon.match (datum):
            module._Log.Fout ("Bestand '" + module._Pad + "': datum '" + datum + "' is onherkenbaar")
            module.IsValide = False
        else:
            self.Datum = datum

    def ModuleXmlInCollectie (self):
        """Geeft de naam van de collectie in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "Tijdstempels"

    def ModuleXmlNaam (self):
        """Geeft de naam van het element in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "Tijdstempel"

    def _ModuleXmlElement (self):
        """Geeft de XML van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return ["<doel>" + str(self.Doel) + "</doel>",
                "<soortTijdstempel>" + ("geldigVanaf" if self.IsGeldigVanaf else "juridischWerkendVanaf") + "</soortTijdstempel>",
                "<datum>" + self.Datum + "</datum>"]


#----------------------------------------------------------------------
# TerugtrekkingTijdstempel
#----------------------------------------------------------------------
class TerugtrekkingTijdstempel(VoorTijdstempel):

    @staticmethod
    def LeesXml (module, xml):
        """Lees TerugtrekkingTijdstempel"""
        terugtrekking = TerugtrekkingTijdstempel (module)
        terugtrekking._LeesXml (module, xml)
        return terugtrekking


    def __init__ (self, consolidatieInformatie):
        super().__init__ (consolidatieInformatie)

    def ModuleXmlInCollectie (self):
        """Geeft de naam van de collectie in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "Terugtrekkingen"

    def ModuleXmlNaam (self):
        """Geeft de naam van het element in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return "TerugtrekkingTijdstempel"

    def _ModuleXmlElement (self):
        """Geeft de XML van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave"""
        return ["<doel>" + str(self.Doel) + "</doel>",
                "<soortTijdstempel>" + ("geldigVanaf" if self.IsGeldigVanaf else "juridischWerkendVanaf") + "</soortTijdstempel>"]
        return xml

#----------------------------------------------------------------------
# MaterieelUitgewerkt
#----------------------------------------------------------------------
class MaterieelUitgewerkt:

    def __init__(self, consolidatieInformatie, workId):
        self.ConsolidatieInformatie = consolidatieInformatie
        self.WorkId = workId
        # Datum waarop het instrument materieel uitgewerkt is; is None voor terugtrekking.
        self.Datum = None

    def BekendOp (self):
        """Tijdstip waarop de informatie in een publicatie bekend is geworden"""
        return self.ConsolidatieInformatie._BekendOp

    def OntvangenOp (self):
        """Tijdstip waarop de informatie in een publicatie ontvangen is; kan niet voor bekendOp liggen"""
        return self.ConsolidatieInformatie.OntvangenOp

    @staticmethod
    def LeesXml (module, xml, isTerugtrekking):
        """Lees MaterieelUitgewerkt"""
        workId = module._LeesElement (xml, "instrument", True)
        if not workId is None:
            if not Naamgeving.IsRegeling (workId) and not Naamgeving.IsInformatieobject (workId):
                module._Log.Fout ("Bestand '" + module._Pad + "': work identificatie " + workId + " past niet bij een regeling of informatieobject")
                module.IsValide = False
        element = MaterieelUitgewerkt (module, workId)
        if not isTerugtrekking:
            datum = module._LeesElement (xml, "datum", True)
            if not datum is None:
                datum = datum[0:10]
                if not ConsolidatieInformatie._DatumPatroon.match (datum):
                    module._Log.Fout ("Bestand '" + module._Pad + "': datum '" + datum + "' is onherkenbaar")
                    module.IsValide = False
                else:
                    element.Datum = datum
        return element

    def ModuleXmlInCollectie (self):
        """Geeft de naam van de collectie in de STOP module waar dit element onderdeel van is.
        In deze applicatie alleen nodig voor weergave"""
        return 'Terugtrekkingen' if self.Datum is None else ''

    def ModuleXmlElement (self, inclusiefImplicieteTijdstempels = True):
        """Geeft de XML van het element in de STOP module, als lijst van regels.
        In deze applicatie alleen nodig voor weergave
        
        Argumenten:
        
        inclusiefImplicieteTijdstempels bool  Geeft aan of ontvangenOp/bekendOp altijd opgenomen moeten worden (als comment)
        """
        naam = 'TerugtrekkingMaterieelUitgewerkt' if self.Datum is None else 'MaterieelUitgewerkt'
        xml = ["<" + naam + ">"]
        if inclusiefImplicieteTijdstempels:
            # Alleen voor weergave; is geen onderdeel van het STOP schema!
            xml.extend (['\t<!-- ontvangenOp: ' + self.OntvangenOp() + ' -->'
                            '\t<bekendOp>' + self.BekendOp () + '</bekendOp>'])
        xml.append ("\t<instrument>" + self.WorkId + "</instrument>")
        if not self.Datum is None:
            xml.append ("\t<datum>" + self.Datum + "</datum>")
        xml.append ("</" + naam + ">")
        return xml

