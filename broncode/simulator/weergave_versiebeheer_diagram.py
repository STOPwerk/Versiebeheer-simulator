
#======================================================================
#
# Aanmaken van een diagram van het versiebeheer als onderdeel van
# de webpagina die alle beschikbare resultaten laat zien
# van het consolidatie proces uit proces_consolideren.
#
#======================================================================

from data_lv_versiebeheerinformatie import Instrument
from weergave_data_toestanden import ToestandActueel
from weergave_resultaat_data import InstrumentData, InstrumentUitwisseling
from weergave_symbolen import Weergave_Symbolen
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Maker van teksten en symbolen voor diagram elementen, en 
# context/opties voor het maken van het diagram
#
#======================================================================
class DiagramGeneratorOpties:

    def __init__ (self, diagramId : str, instrument : Instrument, instrumentData : InstrumentData, toonActueleToestanden : bool, voorUitwisseling : InstrumentUitwisseling = None, bekendOp = None):
        """Maak de tekstgenerator aan

        Argumenten:

        diagramId string  Korte unieke string die gebruikt wordt als klasse voor elementen en als dataset naam voor toelichting-elementen
        instrument InstrumentData Weer te geven versiebeheerinformatie
        instrumentData InstrumentUitwisseling Weer te geven consolidatie informatie voor het instrument
        toonActueleToestanden bool  Geeft aan of de actuele toestanden ook getoond moeten worden
        voorUitwisseling InstrumentUitwisseling Geeft aan dat het diagram voor een specifieke uitwisseling gemaakt moet worden. Als dit niet is opgegeven, dan wordt het voor alle uitwisselingen gemaakt.
        bekendOp string  Uiterste datum waarop de informatie in de uitwisselingen bekend moeten zijn
        """
        self._Instrument = instrument
        self._InstrumentData = instrumentData
        self._ToonActueleToestanden = toonActueleToestanden
        self._VoorUitwisseling = voorUitwisseling
        self._BekendOp = bekendOp
        self._DiagramId = diagramId
        # Moeten de vervlechting/ontvlechtingsrelaties getoond worden?
        self._ToonVervlechtingOntvlechting = True
        # Alle elementen; wordt gezet vanuit de diagram generator
        self._AlleElementen = None

    def MomentopnameSymbool (self, element):
        """Geef het symbool voor een element dat een of twee momentopnamen representeert

        Argumenten:
        element DiagramElement  Element waarvoor de toelichting gemaakt wordt

        Geeft een symbool of None
        """
        symbool = ''
        if not element.Bron is None and element.Bron.GemaaktOp == element.Rij.GemaaktOp:
            symbool += element.Bron._Symbool
        if not element.TijdstempelsBron is None and element.TijdstempelsBron.GemaaktOp == element.Rij.GemaaktOp:
            symbool += element.TijdstempelsBron._Symbool
        if symbool:
            return symbool

    def MomentopnameToelichting (self, element):
        """Geef de toelichting voor een element dat een of twee momentopnamen representeert,
        of None om geen toelichting te tonen

        Argumenten:
        element DiagramElement  Element waarvoor de toelichting gemaakt wordt
        """
        return None

    def ToestandSymbool (self, toestand : ToestandActueel):
        """Geef het symbool voor een element dat een toestand representeert

        Argumenten:
        toestand ToestandInhoud  De toestand corresponderend met het element
        """
        return Weergave_Symbolen.ToestandSymbool (toestand)

    def ToestandToelichting (self, element, toestand : ToestandActueel):
        """Geef de toelichting voor een element dat een toestand representeert,
        of None om geen toelichting te tonen

        Argumenten:
        element DiagramElement  Element waarvoor de toelichting gemaakt wordt
        toestand ToestandInhoud  De toestand corresponderend met het element
        """
        return None

    def NogTeConsoliderenInformatie (self, identificatie, inhoud, uniekId):
        """Maak de HTML voor een tabel met een overzicht van betrokken doelen en nog uit te voeren consolidatie activiteiten.
        De tekst in dit overzicht kan samen met elementen in het diagram uitgelicht worden.

        Argumenten:

        identificatie ActueleToestand of ToestandIdentificatie Informatie over het resultaat van de consolidatie
        inhoud ActueleToestand, ToestancCompleet of OnvolledigeVersie  Informatie over het resultaat van de consolidatie
        uniekId string ID van het element corresponderend met de toestand in het diagram, of anders een uniek ID.
        instrumentversie string Instrumentversie waarvoor het diagram getekend wordt.
        """
        selector = ' data-' + self._DiagramId + '_ntc="' + uniekId + '" '

        html = '<table>'
        if hasattr (inhoud, '_InstrumentversieDoelen') and not inhoud._InstrumentversieDoelen is None:
            html += '<tr><td ' + selector + 'class="iv">Instrumentversie</td><td colspan="2">' + inhoud.Instrumentversie + '</td></tr>\n'
        html += '<tr><td rowspan="' + str(len (identificatie.Inwerkingtredingsdoelen)) + '"' + selector + 'class="vw">Inwerkingtredingsdoelen</td>' + '<tr>'.join (('<td>' + self._InstrumentData.WeergaveData.DoelLetter (doel) + '</td><td>' + str(doel) + '</td></tr>\n') for doel in identificatie.Inwerkingtredingsdoelen)
        if inhoud.Basisversiedoelen:
            html += '<tr><td rowspan="' + str(len (inhoud.Basisversiedoelen)) + '"' + selector + 'class="vw">Overige doelen die bijdragen</td>' + '<tr>'.join (('<td>' + self._InstrumentData.WeergaveData.DoelLetter (doel) + '</td><td>' + str(doel) + '</td></tr>\n') for doel in inhoud.Basisversiedoelen)
        if hasattr (inhoud, 'TegensprekendeDoelen') and inhoud.TegensprekendeDoelen:
            html += '<tr><td rowspan="' + str(len (inhoud.TegensprekendeDoelen)) + '"' + selector + 'class="ts">TegensprekendeDoelen</td>' + '<tr>'.join (('<td>' + self._InstrumentData.WeergaveData.DoelLetter (td.Doel) + '</td><td>' + str(td.Doel) + '<br/>&nbsp;&nbsp;&nbsp;&nbsp;Laatst bekend: ' + td.LaatstBekend + '</td></tr>\n') for td in inhoud.TegensprekendeDoelen)
        if inhoud.TeVerwerkenDoelen:
            html += '<tr><td rowspan="' + str(len (inhoud.TeVerwerkenDoelen)) + '"' + selector + 'class="tv">TeVerwerkenDoelen</td>' + '<tr>'.join (('<td>' + self._InstrumentData.WeergaveData.DoelLetter (tvd.Doel) + '</td><td>' + str(tvd.Doel) + '<br/>&nbsp;&nbsp;&nbsp;&nbsp;Laatst bekend: ' + tvd.LaatstBekend + '<br/>&nbsp;&nbsp;&nbsp;&nbsp;Laatst verwerkt: ' + ('-' if tvd.LaatstVerwerkt is None else tvd.LaatstVerwerkt) + '</td></tr>\n') for tvd in inhoud.TeVerwerkenDoelen)
        if inhoud.TeOntvlechtenDoelen:
            html += '<tr><td rowspan="' + str(len (inhoud.TeOntvlechtenDoelen)) + '"' + selector + 'class="to">TeOntvlechtenDoelen</td>' + '<tr>'.join (('<td>' + self._InstrumentData.WeergaveData.DoelLetter (tod.Doel) + '</td><td>' + str(tod.Doel) + '<br/>&nbsp;&nbsp;&nbsp;&nbsp;Laatst verwerkt' + tod.LaatstVerwerkt + '</td></tr>\n') for tod in inhoud.TeOntvlechtenDoelen)
        html += '</table>\n'

        return html

    def NogTeConsoliderenToggle (self, identificatie, inhoud, uniekId, asRadio = False):
        """Maak de HTML voor een checkbox om de nog te consolideren informatie en elementen in het diagram uit te lichten.

        Argumenten (moeten gelijk zijn aan de argumenten voor _NogTeConsoliderenInformatie):

        identificatie ActueleToestand of ToestandIdentificatie Informatie over het resultaat van de consolidatie
        inhoud ActueleToestand, ToestancCompleet of OnvolledigeVersie  Informatie over het resultaat van de consolidatie
        uniekId string ID van het element corresponderend met de toestand in het diagram, of anders een uniek ID.
        asRadio bool  Maak een radio control ipv een checkbox
        """
        # Selector om selectie van uitwisselingen te tonen
        html = '<input type="'
        if asRadio:
            html += 'radio" name="' + self._DiagramId + '_tv" value="' + uniekId + '"'
        else:
            html += 'checkbox"'
        if hasattr (identificatie, 'Identificatie'):
            html += ' data-ti="' + str(identificatie.Identificatie) + '"'

        # Zoek op om welke elementen het gaat
        selectie = {} # key = elementId, value = extra klasse
        for doel, elts in self._AlleElementen.items ():
            # Alle elementen krijgen een vw als ze in een toestand-branch zitten of een nvt anders.
            c = 'vw' if doel in identificatie.Inwerkingtredingsdoelen or doel in inhoud.Basisversiedoelen else 'nvt'
            for gemaaktOp, elt in elts.items ():
                selectie[elt.Id] = c
        for tv in inhoud.TeVerwerkenDoelen:
            # Te verwerken: < tv.LaatstVerwerkt zijn verwerkt (ook voor doelen die niet in de toestand zitten), <= LaatstBekend zijn te verwerken
            for gemaaktOp, elt in self._AlleElementen[tv.Doel].items ():
                if not tv.LaatstVerwerkt is None and gemaaktOp <= tv.LaatstVerwerkt:
                    selectie[elt.Id] = 'vw'
                elif gemaaktOp <= tv.LaatstBekend:
                    selectie[elt.Id] = 'tv'
        for to in inhoud.TeOntvlechtenDoelen:
            # Te ontvlechten: alle tot en met LaatstVerwerkt ontvlechten
            for gemaaktOp, elt in self._AlleElementen[to.Doel].items ():
                if gemaaktOp <= to.LaatstVerwerkt:
                    selectie[elt.Id] = 'to'
        if hasattr (inhoud, 'TegensprekendeDoelen'):
            for td in inhoud.TegensprekendeDoelen:
                # Markeer tegenspraak met een andere kleur
                selectie[self._AlleElementen[td.Doel][td.LaatstBekend].Id] = 'ts'
        if hasattr (inhoud, '_InstrumentversieDoelen') and not inhoud._InstrumentversieDoelen is None:
            # Markeer de instrumentversie
            for iv in inhoud._InstrumentversieDoelen:
                # Te ontvlechten: alle tot en met LaatstVerwerkt ontvlechten
                for gemaaktOp, elt in self._AlleElementen[iv].items ():
                    if gemaaktOp == inhoud._InstrumentversieGemaaktOp:
                        c = selectie.get (elt.Id)
                        ok = True
                        if c is None or c == 'vw':
                            selectie[elt.Id] = 'iv'
                        else:
                            selectie[elt.Id] = c + ' iv'

        html += self._InputSelectieAttribuut (uniekId, selectie)
        html += '/>'

        return html

    def _InputSelectieAttribuut (self, uniekId, selectie):
        html = ' data-' + self._DiagramId + '_tv="' + uniekId + ';'
        html += ';'.join ((ct + '=' + ','.join (str(i) for i,c in selectie.items() if c == ct)) for ct in ['nvt','vw','ts','tv','to','iv','to iv','ts iv'])
        html += '" class="' + self._DiagramId + '_tv"'
        return html


#======================================================================
#
# DiagramGenerator
#
#======================================================================
#
# Basisklasse voor een generator van de bijdrage aan de webpagina.
# DiagramGenerator kan het diagram maken, de UX en containers voor
# de detailinformatie. Afgeleide klassen moeten de detailinformatie
# samenstellen.
#
#======================================================================

#----------------------------------------------------------------------
# Uitkomst van het maken van het diagram
#----------------------------------------------------------------------
class Diagram:

    def __init__(self, diagramId):
        """Resultaten van DiagramGenerator.VoerUit methode 
        
        Argumenten:

        diagramId string  Korte unieke string die gebruikt wordt als klasse voor elementen en als dataset naam voor toelichting-elementen
        """
        self._DiagramId = diagramId
        # De relevante doelen voor dit instrument
        self.RelevanteDoelen = None
        # De SVG van het diagram
        self.SVG = ''
        # De HTML met de toelichting op de elementen
        self.ToelichtingHTML = ''
        # De HTML met een overzicht van de doelen
        self.DoelenHTML = ''
        # De HTML met een overzicht van de symbolen
        self.LegendaHTML = ''

    def VoegOndersteuningToe (self, generator : WebpaginaGenerator):
        """Voeg de ondersteunende artefacten toe aan de pagina
        
        Argumenten:
        
        generator WebpaginaGenerator  Generator voor de resultaatpagina
        """
        generator.GebruikSvgScript ()
        generator.LeesCssTemplate ('')
        generator.VoegSlotScriptToe (generator.LeesJSTemplate ('', False).replace ("DIAGRAM_ID", self._DiagramId))

class DiagramGenerator:

#----------------------------------------------------------------------
#
# Startpunt voor het maken van het diagram
#
#----------------------------------------------------------------------
    @staticmethod
    def VoerUit (opties: DiagramGeneratorOpties):
        """Stel het diagram samen

        Argumenten:

        opties DiagramGeneratorOpties  Opties voor de weergave van het diagram

        Geeft een Diagram met het resultaat terug.
        """
        toonActueleToestanden = opties._InstrumentData.HeeftActueleToestanden if opties._ToonActueleToestanden else False

        resultaat = Diagram (opties._DiagramId)
        resultaat.RelevanteDoelen = opties._InstrumentData.WeergaveData.Branches ([doel for doel in opties._Instrument.Branches])

        # Maak de SVG/HTML foor de diagrammen
        elementId = 0
        svgBreedte = 0
        svgHoogte = 0
        svgElementen = ''
        selector = Weergave_Uitwisselingselector (opties._InstrumentData.WeergaveData.Scenario)
        # Maak de diagrammen en bepaal de grootte
        diagrammen = {}
        momentopnameUniekId = {} # uniek ID voor momentopnamen, om ze te herkennen over uitwisselingen heen, key = object, value = id
        for uitwisseling in (opties._InstrumentData.Uitwisselingen if opties._VoorUitwisseling is None else [opties._VoorUitwisseling]) :
            diagram = DiagramGenerator (opties, uitwisseling, toonActueleToestanden, resultaat.RelevanteDoelen, momentopnameUniekId)
            diagrammen[uitwisseling] = diagram
            elementId = diagram._MaakDiagramElementen (elementId)
            diagram._BepaalPosities (0)
            if diagram.Breedte > svgBreedte:
                svgBreedte = diagram.Breedte
            if diagram.DiagramHoogte > svgHoogte:
                svgHoogte = diagram.DiagramHoogte

        # Teken de diagrammen
        for uitwisseling, diagram in diagrammen.items ():
            diagram._BepaalPosities (svgHoogte)
            diagram._MaakDiagram ()
            diagram._VoegToelichtingenToe ()
            interval = selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) if opties._VoorUitwisseling is None else ''
            svgElementen += '<g' + interval + '>' + diagram.SVG + '</g>\n'
            resultaat.DoelenHTML += '<div' + interval + '>' + diagram.DoelenHTML + '</div>\n'
            resultaat.LegendaHTML += '<div' + interval + '>' + diagram.LegendaHTML + '</div>\n'
            resultaat.ToelichtingHTML += '<div' + interval + '>' + diagram.ToelichtingHTML + '</div>\n'

        resultaat.SVG = '<svg id="' + opties._DiagramId + '_svg" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: 100%; height: 100%;" viewBox="0 0 ' + str(svgBreedte) + ' ' + str(svgHoogte) + ' " version="1.1">\n' + svgElementen + 'Deze browser ondersteunt geen SVG\n</svg>'
        return resultaat
    
#----------------------------------------------------------------------
#
# Implementatie van het maken van 1 diagram
#
#----------------------------------------------------------------------
    def __init__ (self, opties : DiagramGeneratorOpties, instrumentData : InstrumentUitwisseling, toonActueleToestanden : bool, relevanteDoelen, momentopnameUniekId : dict):
        """Maak de generator aan
        
        Argumenten:
        opties DiagramGeneratorOpties  Opties voor de diagram generatie
        toonActueleToestanden bool  Geeft aan of de actuele toestanden ook getoond moeten worden
        relevanteDoelen (string,string)[] Lijst met relevante doelen en de letter om de doelen mee aan te duiden
        momentopnameUniekId {} Uniek ID voor momentopnamen, om ze te herkennen over uitwisselingen heen
        """
        self._Opties = opties
        self._InstrumentData = instrumentData
        self._ToonActueleToestanden = toonActueleToestanden and not self._InstrumentData.ActueleToestanden is None
        self._RelevanteDoelen = relevanteDoelen
        self.__MomentopnameUniekId = momentopnameUniekId
        # Selectie uit self._RelevanteDoelen van doelen waarvoor informatie aanwezig is
        self._ActieveDoelen = []
        # Geeft aan of er toestanden te zien zijn in het diagram
        self._HeeftActueleToestanden = False
        # De kolommen van het diagram
        # Lijst van instanties van DiagramKolom
        self._Kolommen = []
        # De rijen van het diagram
        # Lijst van instanties van DiagramRij
        self._Rijen = []
        # De SVG code van de diagramelementen
        self.SVG = None
        # Breedte in svg-eenheden van dit diagram
        self.Breedte = 0
        # Hoogte in svg-eenheden van dit diagram
        self.DiagramHoogte = 0
        # Totale hoogte in svg-eenheden van het hele diagram
        self.Hoogte = 0
        # De HTML met de toelichtingen
        self.ToelichtingHTML = ''
        # De HTML met een overzicht van de doelen
        self.DoelenHTML = ''

    def _MomentopnameUniekId (self, momentopnameInstrument, momentopnameTijdstempel):
        """Geef het unieke ID geassocieerd met een momentopname"""
        key = momentopnameInstrument if not momentopnameInstrument is None else momentopnameTijdstempel
        id = self.__MomentopnameUniekId.get (key)
        if id is None:
            self.__MomentopnameUniekId[key] = id = len (self.__MomentopnameUniekId)
        return id

#----------------------------------------------------------------------
# Bepalen inhoud van het diagram
#----------------------------------------------------------------------
    def _MaakDiagramElementen (self, elementId : int):
        """Maak alle elementen voor het diagram
        
        Argumenten:
        toonActueleToestanden bool  Geeft aan of de actuele toestanden ook getoond moeten worden
        elementId int  Eerste index van de elementen in het diagram

        Geeft het laatst gebruikte elementId terug.
        """

        # Maak de toestand elementen aan voor het diagram, nog zonder rij
        toestandVoorDoel = {} # key = doel, value = DiagramElement
        toestandenKolom = None
        if self._ToonActueleToestanden:
            toestandenKolom = DiagramKolom (self._Kolommen)
            if hasattr (self._InstrumentData, 'ActueleToestanden'):
                for toestand in self._InstrumentData.ActueleToestanden.Toestanden:
                    # Maak element voor toestand
                    element = DiagramElement (toestand).InKolom (toestandenKolom)
                    for doel in toestand.Inwerkingtredingsdoelen:
                        toestandVoorDoel[doel] = element
                    self._HeeftActueleToestanden = True

        # Maak de elementen voor de versiebeheerinformatie
        rijPerGemaaktOp = {} # key = gemaaktOp, value = instantie van DiagramRij
        self._Opties._AlleElementen = {} # key = doel, value = {} met key = gemaaktOp, value = instantie van DiagramElement
        for doel, branchId in self._RelevanteDoelen:
            # Reserveer altijd een kolom voor deze branch
            branchKolom = DiagramKolom (self._Kolommen)

            branch = self._Opties._Instrument.Branches.get (doel)
            if branch is None or len (branch.Momentopnamen) == 0 or branch.Momentopnamen[0].GemaaktOp > self._InstrumentData.GemaaktOp:
                continue
            # Vul de kolom
            branchKolom.Branch = branch
            branchKolom.BranchId = branchId
            self._ActieveDoelen.append ((doel, branchId))

            # Maak een lijst van alle relevante momentopnamen en maak de elementen ervoor aan
            momentopnamen = { m.GemaaktOp: (m, None) for m in branch.Momentopnamen if m.GemaaktOp <= self._InstrumentData.GemaaktOp and (self._Opties._BekendOp is None or m.BekendOp <= self._Opties._BekendOp) } # value = (voor instrument, voor tijdstempel)
            tijdstempels = self._Opties._Instrument._Versiebeheerinformatie.Tijdstempels.get (doel)
            if tijdstempels:
                for m in tijdstempels.Momentopnamen:
                    if m.GemaaktOp <= self._InstrumentData.GemaaktOp and (self._Opties._BekendOp is None or m.BekendOp <= self._Opties._BekendOp):
                        m_instrument = momentopnamen.get (m.GemaaktOp)
                        momentopnamen[m.GemaaktOp] = (None if m_instrument is None else m_instrument[0], m)

            self._Opties._AlleElementen[doel] = {}
            laatsteElement = None
            for gemaaktOp in sorted (momentopnamen.keys ()):
                momentopnameInstrument, momentopnameTijdstempel = momentopnamen[gemaaktOp]

                # Maak element voor momentopname
                rij = rijPerGemaaktOp.get (gemaaktOp)
                if rij is None:
                    rijPerGemaaktOp[gemaaktOp] = rij = DiagramRij (gemaaktOp)
                element = DiagramElement (momentopnameInstrument).InKolom (branchKolom).InRij (rij)
                element.TijdstempelsBron = momentopnameTijdstempel
                self._Opties._AlleElementen[doel][gemaaktOp] = laatsteElement = element
                element.Label = self._Opties.MomentopnameSymbool (element)
                element.Toelichting = self._Opties.MomentopnameToelichting (element)

            toestandElement = toestandVoorDoel.get (doel)
            if not toestandElement is None:
                # Laatste element draagt bij aan de toestand
                laatsteElement.NaarToestand = toestandElement
                # Zet de toestand op de laatste rij die bijdraagt
                if toestandElement.Rij is None or toestandElement.Rij.GemaaktOp < gemaaktOp:
                    toestandElement.Rij = rij # Nog niet in Rij.Elementen opnemen

        # Ruim lege kolommen aan het einde op
        idx = len (self._Kolommen)-1
        while idx > (1 if self._ToonActueleToestanden else 0):
            if len (self._Kolommen[idx].Elementen) > 0:
                break
            self._Kolommen.pop ()
            idx -= 1

        # Neem de relaties tussen de elementen over
        for doel in self._Opties._AlleElementen:
            for element in self._Opties._AlleElementen[doel].values ():
                if not element.Bron is None:
                    for momentopname in element.Bron.Basisversies.values ():
                        if not momentopname.Branch.Doel in element.Bron.Doelen:
                            anderElement = self._Opties._AlleElementen[momentopname.Branch.Doel][momentopname.GemaaktOp]
                            if anderElement.Rij == element.Rij:
                                anderElement._NaarElementBinnenUitwisseling.append (element)
                            element.Basisversies.append (anderElement)

                    for momentopname in element.Bron.OntvlochtenMet.values ():
                        anderElement = self._Opties._AlleElementen[momentopname.Branch.Doel][momentopname.GemaaktOp]
                        if anderElement.Rij == element.Rij:
                            anderElement._NaarElementBinnenUitwisseling.append (element)
                        element.OntvlochtenMet.append (anderElement)

                    for momentopname in element.Bron.VervlochtenMet.values ():
                        anderElement = self._Opties._AlleElementen[momentopname.Branch.Doel][momentopname.GemaaktOp]
                        if anderElement.Rij == element.Rij:
                            anderElement._NaarElementBinnenUitwisseling.append (element)
                        element.VervlochtenMet.append (anderElement)

        # Sorteer de rijen en elementen daarin
        self._Rijen = [rijPerGemaaktOp[g] for g in sorted (rijPerGemaaktOp.keys())]
        idx = 0
        for rij in self._Rijen:
            rij.Index = idx
            idx += 1
            rij.Elementen.sort (key = lambda e: e.Kolom.Index)

            # Verbind de elementen met hetzelfde consolidatie-informatie-element, tenzij ze 
            # teruggetrokken zijn.
            for i, element in enumerate (rij.Elementen):
                if not element.Bron is None and not element.Bron.IsTeruggetrokken:
                    ciElement = element.Bron._ConsolidatieInformatieElementen[0]
                    verbonden = [element]
                    naarElementen = [*element._NaarElementBinnenUitwisseling]
                    tussenliggend = []
                    for j in range (i+1, len (rij.Elementen)):
                        anderElement = rij.Elementen[j]
                        if ciElement == anderElement.Bron._ConsolidatieInformatieElementen[0]:
                            verbonden.append (anderElement)
                            naarElementen.extend (anderElement._NaarElementBinnenUitwisseling)
                            element.AantalKolommen = anderElement.Kolom.Index - element.Kolom.Index + 1
                            for k in range (i+1, j):
                                if not rij.Elementen[k].Bron.IsTeruggetrokken:
                                    tussenliggend.append (rij.Elementen[k])
                    if element.AantalKolommen > 1:
                        for anderElement in verbonden:
                            anderElement._Verbonden = verbonden
                            anderElement._NaarElementBinnenUitwisseling = naarElementen
                            anderElement._Tussenliggend = tussenliggend

            # Schuif elementen omhoog om ruimte te maken voor relaties tussen elementen binnen dezelfde rij
            def SchuifGerelateerdeElementenOmhoog (element):
                omhoogschuiven = []
                for anderElement in element._NaarElementBinnenUitwisseling:
                    if not anderElement.Bron.IsTeruggetrokken:
                        if anderElement.Baan <= element.Baan:
                            # Zorg dat dit (verbonden?) element hoger komt te liggen
                            omhoogschuiven.extend (anderElement._Verbonden)
                            tussenliggend.extend (anderElement._Tussenliggend)
                if omhoogschuiven:
                    # Schuif de elementen op en ook de gerelateerde elementen
                    for elt in omhoogschuiven:
                        elt.Baan = element.Baan + 1
                    for elt in omhoogschuiven:
                        SchuifGerelateerdeElementenOmhoog (elt)
            for element in rij.Elementen:
                if not element.Bron is None and not element.Bron.IsTeruggetrokken:
                    SchuifGerelateerdeElementenOmhoog (element)

            # Als er een baan is waarbij verbonden elementen over tussenliggende elementen
            # heen liggen, splits dat niveau dan op en schuif de verbonden elementen omhoog
            for element in rij.Elementen:
                if len (element._Verbonden) > 1 and element._Verbonden[0] == element:
                    for t in element._Tussenliggend:
                        if t.Baan == element.Baan:
                            # Schuif de hoger gelegen elementen omhoog
                            for anderElement in rij.Elementen:
                                if anderElement.Baan > element.Baan:
                                    anderElement.Baan += 1
                            # Schuif de verbonden elementen omhoog
                            baan = element.Baan + 1
                            for anderElement in element._Verbonden:
                                anderElement.Baan = baan
                            break

            # Tel het aantal banen
            for element in rij.Elementen:
                if rij.AantalBanen <= element.Baan:
                    rij.AantalBanen = element.Baan + 1
            rij.AantalMOBanen = rij.AantalBanen

        if toestandenKolom:
            # Zorg ervoor dat de toestanden op volgorde van inwerkingtreding staan
            laatsteRijIndex = -1
            ingevoegdeRij = None
            for toestand in sorted (toestandenKolom.Elementen, key = lambda t:t.Bron.JuridischWerkendVanaf):
                if toestand.Rij.Index < laatsteRijIndex:
                    # Maak een extra rij voor deze toestand
                    if ingevoegdeRij is None:
                        laatsteRijIndex += 1
                        for rij in self._Rijen:
                            if rij.Index >= laatsteRijIndex:
                                rij.Index += 1
                        ingevoegdeRij = DiagramRij ("-")
                        ingevoegdeRij.Index = laatsteRijIndex
                        self._Rijen.insert (laatsteRijIndex, ingevoegdeRij)
                    toestand.Rij = ingevoegdeRij
                else:
                    laatsteRijIndex = toestand.Rij.Index
                    ingevoegdeRij = None
                # Plaats de toestanden in banen boven de andere elementen en maak de toelichting
                toestand.Baan = toestand.Rij.AantalBanen
                toestand.Rij.AantalBanen += 1
                toestand.Rij.Elementen.insert (0, toestand)

        # Sorteer de elementen in de kolommen en geef alle elementen een uniek ID
        for kolom in self._Kolommen:
            kolom.Elementen.sort (key = lambda e: e.Rij.Index * 1000 + e.Baan)
            for element in kolom.Elementen:
                elementId += 1
                element.Id = elementId

        if toestandenKolom:
            # Maak nu pas de toelichting, nadat alle andere elementen zijn gemaakt en van een ID zijn voorzien
            for element in toestandenKolom.Elementen:
                element.Label = self._Opties.ToestandSymbool (element.Bron)
                element.Toelichting = self._Opties.ToestandToelichting (element, element.Bron)

        return elementId

    _SvgElementBreedte = 45 # Breedte van een toestand/momentopname rechthoek in diagram-eenheden
    _SvgHalveElementBreedte = int(_SvgElementBreedte/2)
    _SvgElementHoogte = 30 # Hoogte van een toestand/momentopname rechthoek in diagram-eenheden
    _SvgHalveElementHoogte = int (_SvgElementHoogte/2)
    _SvgDatumBreedte = 50 # Breedte van de tekst met de juridischWerkendVanaf datum bij toestanden
    _SvgTijdstipBreedte = 100 # Breedte van de tekst met de gemaaktOp datum bij momentopnamen

#----------------------------------------------------------------------
# Bepaal de posities
#----------------------------------------------------------------------
    def _BepaalPosities (self, diagramHoogte):
        """Bepaal de positie van de elementen

        Argumenten:

        diagramHoogte int Totale hoogte van het diagram
        """
        self.Breedte = DiagramGenerator._SvgDatumBreedte if self._HeeftActueleToestanden else 0
        for idx, kolom in enumerate (self._Kolommen):
            self.Breedte += DiagramGenerator._SvgHalveElementBreedte
            kolom._X = self.Breedte + DiagramGenerator._SvgHalveElementBreedte
            for element in kolom.Elementen:
                element._X = self.Breedte

            self.Breedte += DiagramGenerator._SvgElementBreedte
            if idx == 0 and self._HeeftActueleToestanden:
                self.Breedte += DiagramGenerator._SvgHalveElementBreedte
        self.Breedte += DiagramGenerator._SvgHalveElementBreedte + DiagramGenerator._SvgTijdstipBreedte

        self.DiagramHoogte = DiagramGenerator._SvgElementHoogte
        for rij in self._Rijen:
            self.DiagramHoogte += DiagramGenerator._SvgHalveElementHoogte
            rij._Y0 = self.DiagramHoogte
            rij._Y1 = rij._Y0 + rij.AantalMOBanen * (DiagramGenerator._SvgElementHoogte + DiagramGenerator._SvgHalveElementHoogte) - DiagramGenerator._SvgHalveElementHoogte
            for element in rij.Elementen:
                # Top-left corner
                element._Y = rij._Y0 + DiagramGenerator._SvgElementHoogte + element.Baan * (DiagramGenerator._SvgElementHoogte + DiagramGenerator._SvgHalveElementHoogte)
            self.DiagramHoogte += rij.AantalBanen * (DiagramGenerator._SvgElementHoogte + DiagramGenerator._SvgHalveElementHoogte)
        self.DiagramHoogte += DiagramGenerator._SvgElementHoogte # Stippellijnen

        self.Hoogte = diagramHoogte
        for rij in self._Rijen:
            rij._Y0 = self.Hoogte - rij._Y0 # svg-Y neemt toe naar beneden
            rij._Y1 = self.Hoogte - rij._Y1 # svg-Y neemt toe naar beneden
            for element in rij.Elementen:
                element._Y = self.Hoogte - element._Y

#----------------------------------------------------------------------
# Maak het diagram in SVG
#----------------------------------------------------------------------
    def _MaakDiagram (self):
        """Maak de svg van het diagram en voeg dat toe aan het template

        Argumenten:

        diagramHoogte int Totale hoogte van het diagram
        """

        # Teken de elementen
        self.SVG = ''
        svgLabel = '<text x="{x}" y="{y}" dominant-baseline="middle" text-anchor="middle" class="vbd_l_{t}" data-' + self._Opties._DiagramId + '_e="{id}"{extra}>{tekst}</text>\n'
        for idx, kolom in enumerate (self._Kolommen):
            isActueleToestanden = idx == 0 and self._HeeftActueleToestanden
            
            if not kolom.BranchId is None:
                # Label voor de branch
                self.SVG += '<text x="' + str(kolom._X) + '" y="' + str(self.Hoogte-DiagramGenerator._SvgHalveElementHoogte) + '" dominant-baseline="middle" text-anchor="middle" class="vbd_txt">' + kolom.BranchId + '</text>'
            # Elementen in de kolom
            svgFragment = '<rect x="{x}" y="{y}" width="' + str(DiagramGenerator._SvgElementBreedte) + '" height="' + str(DiagramGenerator._SvgElementHoogte) + '" rx="3" ry="3" class="vbd_{t}" data-' + self._Opties._DiagramId + '_e="{id}"{extra}></rect>\n'
            for elt in kolom.Elementen:
                if len (elt._Verbonden) > 1 and elt._Verbonden[0] == elt:
                    # Teken de verbinding
                    self.SVG += '<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" ry="3" class="vbd_mov"></rect>\n'.format (x = elt._X, y = elt._Y, w = elt._Verbonden[-1]._X + DiagramGenerator._SvgElementBreedte - elt._X, h = DiagramGenerator._SvgElementHoogte)
                # Teken het element
                extra = ' data-' + self._Opties._DiagramId + '_ti="' + str(elt.Bron.Identificatie) + '" data-' + self._Opties._DiagramId + '_tid="' + str(elt.Bron.UniekId) + '"' if isActueleToestanden else ' data-' + self._Opties._DiagramId + '_mo="' + str(self._MomentopnameUniekId(elt.Bron, elt.TijdstempelsBron)) + '"'
                elementType = ('mot' if (elt.Bron.IsTeruggetrokken if elt.Bron else elt.TijdstempelsBron.JuridischWerkendVanaf is None) else 'mo') if not isActueleToestanden else 'th ' + self._Opties._DiagramId + '_th' if elt.Bron.NietMeerActueel else 't'
                if not elt.Toelichting is None:
                    elementType += ' vbd_i'
                if isActueleToestanden:
                    self.SVG += svgLabel.format (id= elt.Id, x = DiagramGenerator._SvgDatumBreedte/2, y = elt._Y + DiagramGenerator._SvgHalveElementHoogte, tekst = elt.Bron.JuridischWerkendVanaf, t = elementType, extra = extra)
                self.SVG += svgFragment.format (id= elt.Id, x = elt._X, y = elt._Y, t = elementType, extra = extra)
                if not elt.Label is None:
                    self.SVG += svgLabel.format (id= elt.Id, x = elt._X + DiagramGenerator._SvgHalveElementBreedte, y = elt._Y + DiagramGenerator._SvgHalveElementHoogte, tekst = elt.Label, t = elementType, extra = extra)

        # Teken de gemaaktOp datums
        svgFragment = '<path d="M ' + str(self.Breedte - DiagramGenerator._SvgTijdstipBreedte) + ' {y0} L ' + str(self.Breedte - DiagramGenerator._SvgTijdstipBreedte) + ' {y1}" class="vbd_line_uw"/>\n<text x="' + str(self.Breedte) + '" y="{y}" dominant-baseline="middle" text-anchor="end" class="vbd_txt">{tekst}<title>{tijd}</title></text>\n'
        for rij in self._Rijen:
            self.SVG += svgFragment.format (y0 = rij._Y0, y1 = rij._Y1, y = (rij._Y0 + rij._Y1) / 2, tekst = rij.GemaaktOp[0:10] + "..", tijd = rij.GemaaktOp)

        # Teken de branch lijnen
        for idx, kolom in enumerate (self._Kolommen):
            isActueleToestanden = idx == 0 and self._HeeftActueleToestanden
            svgFragment = '<path d="M ' + str(kolom._X) + ' {y0} L ' + str(kolom._X) + ' {y1}" class="vbd_line_{c}"/>\n'
            y0 = None
            teken = False
            for elt in kolom.Elementen:
                y1 = elt._Y
                if teken:
                    # Verbinding tussen elementen
                    self.SVG += svgFragment.format (y0 = y0, y1 = y1 + DiagramGenerator._SvgElementHoogte, c = lineType)
                y0 = y1
                lineType = 'b' if not isActueleToestanden else 'th ' + self._Opties._DiagramId + '_th' if elt.Bron.NietMeerActueel else 't'
                teken = isActueleToestanden or not (elt.Bron.IsTeruggetrokken if elt.Bron else elt.TijdstempelsBron.JuridischWerkendVanaf is None)
            if teken:
                self.SVG += svgFragment.format (y0 = y0, y1 = y0 - 3*DiagramGenerator._SvgHalveElementHoogte, c = 's' + lineType)

        # Teken de basisversies
        relatie_pt_yp = 7 # punt van de punt tov lijn
        relatie_pt_xp = 4.5 # punt van de punt tov lijn
        relatie_pt_y0 = 5 # punt ter hoogte van lijn
        svgFragment = '<path d="M {xb} {yb} L {xe} {yb} L {xe} {ye}" class="vbd_line_basis"/>\n'
        svgPunt = '<path d="M {xe} {ye} L {xep_1} {yep1} L {xe} {yep0} L {xep1} {yep1} Z" class="vbd_line_basis_p"/>\n'
        for kolom in self._Kolommen:
            for elt in kolom.Elementen:
                if len (elt.Basisversies) > 0:
                    xe = elt._X + DiagramGenerator._SvgHalveElementBreedte
                    ye = elt._Y + DiagramGenerator._SvgElementHoogte
                    for bronElt in elt.Basisversies:
                        # Lijn
                        xb = bronElt._X + (DiagramGenerator._SvgElementBreedte if bronElt._X < xe else 0)
                        yb = bronElt._Y + DiagramGenerator._SvgHalveElementHoogte
                        self.SVG += svgFragment.format (xe = xe, ye = ye, xb = xb, yb = yb)
                    # Punt
                    self.SVG += svgPunt.format (xe = xe, xep_1 = xe-relatie_pt_xp, xep1 = xe+relatie_pt_xp, ye = ye, yep1 = ye+relatie_pt_yp, yep0 = ye+relatie_pt_y0)

        if self._Opties._ToonVervlechtingOntvlechting:
            # Teken de VervlochtenVersie relaties
            svgFragment = '<path d="M {xb} {yb} L {xt} {yb} L {xt} {yt} L {xe} {yt} L {xe} {yt} L {xe} {ye}" class="vbd_line_vv"/>\n'
            svgPunt = '<path d="M {xe} {ye} L {xep_1} {yep1} L {xe} {yep0} L {xep1} {yep1} Z" class="vbd_line_vv_p"/>\n'
            dyb = int ((2 * DiagramGenerator._SvgHalveElementHoogte) / 3)
            dxe = int ((2 * DiagramGenerator._SvgHalveElementBreedte) / 3)
            dxt = int ((2 * DiagramGenerator._SvgElementBreedte) / 5)
            dyt = int ((2 * DiagramGenerator._SvgElementHoogte) / 3)
            for kolom in self._Kolommen:
                for elt in kolom.Elementen:
                    if len (elt.VervlochtenMet) > 0:
                        ye = elt._Y + DiagramGenerator._SvgElementHoogte
                        yt = ye + dyt # y voor de tussenpunten in de routering van de lijn
                        for bronElt in elt.VervlochtenMet:
                            # Lijn
                            xb = bronElt._X + (DiagramGenerator._SvgElementBreedte if bronElt._X < elt._X else 0)
                            yb = bronElt._Y + dyb
                            xt = xb + dxt * (1 if bronElt._X < elt._X else -1) # x voor de tussenpunten in de routering van de lijn
                            xe = elt._X + (dxe if bronElt._X < elt._X else DiagramGenerator._SvgElementBreedte - dxe)
                            self.SVG += svgFragment.format (xe = xe, ye = ye, xb = xb, yb = yb, xt = xt, yt = yt)
                        # Punt
                        self.SVG += svgPunt.format (xe = xe, xep_1 = xe-relatie_pt_xp, xep1 = xe+relatie_pt_xp, ye = ye, yep1 = ye+relatie_pt_yp, yep0 = ye+relatie_pt_y0)

            # Teken de OntvlochtenVersie relaties
            svgFragment = '<path d="M {xb} {yb} L {xt} {yb} L {xt} {yt} L {xe} {yt} L {xe} {yt} L {xe} {ye}" class="vbd_line_ov"/>\n'
            svgPunt = '<path d="M {xe} {ye} L {xep_1} {yep1} L {xe} {yep0} L {xep1} {yep1} Z" class="vbd_line_ov_p"/>\n'
            svgLabel = '<text x="{x}" y="{y}" dominant-baseline="middle" text-anchor="middle" class="vbd_line_ov_x">X</text>\n'
            dyb = int (DiagramGenerator._SvgHalveElementHoogte / 3)
            dxe = int (DiagramGenerator._SvgHalveElementBreedte / 3)
            dxt = int (DiagramGenerator._SvgElementBreedte / 5)
            dyt = int (DiagramGenerator._SvgElementHoogte / 3)
            for kolom in self._Kolommen:
                for elt in kolom.Elementen:
                    if len (elt.OntvlochtenMet) > 0:
                        ye = elt._Y + DiagramGenerator._SvgElementHoogte
                        yt = ye + dyt # y voor de tussenpunten in de routering van de lijn
                        for bronElt in elt.OntvlochtenMet:
                            # Lijn
                            xb = bronElt._X + (DiagramGenerator._SvgElementBreedte if bronElt._X < elt._X else 0)
                            yb = bronElt._Y + dyb
                            xt = xb + dxt * (1 if bronElt._X < elt._X else -1) # x voor de tussenpunten in de routering van de lijn
                            xe = elt._X + (dxe if bronElt._X < elt._X else DiagramGenerator._SvgElementBreedte - dxe)
                            self.SVG += svgFragment.format (xe = xe, ye = ye, xb = xb, yb = yb, xt = xt, yt = yt)
                        # X
                        self.SVG += svgLabel.format (x = xe, y = yt)
                        # Punt
                        self.SVG += svgPunt.format (xe = xe, xep_1 = xe-relatie_pt_xp, xep1 = xe+relatie_pt_xp, ye = ye, yep1 = ye+relatie_pt_yp, yep0 = ye+relatie_pt_y0)

        # Teken de branch-toestand lijnen
        b_t_punt_xp = 7 # punt van de punt tov lijn
        b_t_punt_yp = 4.5 # punt van de punt tov lijn
        b_t_punt_x0 = 5 # punt ter hoogte van lijn
        svgFragment = '<path d="M {xe} {ye} Q {xe} {yc} {xt} {yt}" class="vbd_line_b_{t}"/>\n'
        svgPunt = '<path d="M {xt} {yt} L {xtp1} {ytp1} L {xtp0} {yt} L {xtp1} {ytp_1} Z" class="vbd_line_p_b_{t}"/>\n'
        for kolom in self._Kolommen:
            if not kolom.Branch is None and len(kolom.Elementen) > 0:
                elt = kolom.Elementen[-1]
                if not elt.NaarToestand is None:
                    xt = elt.NaarToestand._X + DiagramGenerator._SvgElementBreedte
                    yt = elt.NaarToestand._Y + DiagramGenerator._SvgHalveElementHoogte
                    lineType = 'th ' + self._Opties._DiagramId + '_th' if elt.NaarToestand.Bron.NietMeerActueel else 't'
                    # Lijn
                    yc = elt._Y - (elt._Y - elt.NaarToestand._Y) + DiagramGenerator._SvgHalveElementHoogte
                    self.SVG += svgFragment.format (xe = elt._X, ye = elt._Y, yc = yc, xt = xt, yt = yt, t = lineType)
                    # Punt
                    self.SVG += svgPunt.format (xt = xt, xtp1=xt+b_t_punt_xp, xtp0=xt+b_t_punt_x0, yt = yt, ytp_1 = yt-b_t_punt_yp, ytp1 = yt+b_t_punt_yp, t = lineType)

#----------------------------------------------------------------------
# Voeg de toelichtingen toe
#----------------------------------------------------------------------
    def _VoegToelichtingenToe (self):
        """Completeer de overzichten van doelen en van de informatieblokken"""
        
        self.DoelenHTML = '<table><tr><th>Letter</th><th>Doel</th></tr>\n'
        for doel, branchId in self._ActieveDoelen:
            self.DoelenHTML += '<tr><td>' + branchId + '</td><td>' + str(doel) + '</td></tr>'
        if self._HeeftActueleToestanden:
            self.DoelenHTML += '<tr><td colspan="2">De linkerkolom toont de actuele toestanden, en</td></tr>\n'
            self.DoelenHTML += '<tr><td colspan="2"><input type="checkbox" class="' + self._Opties._DiagramId + '_toon_th"/> de niet meer geldende toestanden in grijs.</td></tr>\n'
        self.DoelenHTML += '</table>'

        self.LegendaHTML = '<table><tr>' + ('<th class="vbd_th_t">&nbsp;</th><th>Toestanden</th>' if self._HeeftActueleToestanden else '') + '<th class="vbd_th_mo">&nbsp;</th><th>Momentopnamen</th></tr>'
        self.LegendaHTML += '<tr>' + ('<td>' + Weergave_Symbolen.Toestand_BekendeInhoud + '</td><td>Bekende inhoud</td>' if self._HeeftActueleToestanden else '') + '<td>' + Weergave_Symbolen.Instrument_Versie + '</td><td>Beoogde instrumentversie</td></tr>'
        self.LegendaHTML += '<tr>' + ('<td>' + Weergave_Symbolen.Toestand_OnbekendeInhoud + '</td><td>Onbekende inhoud</td>' if self._HeeftActueleToestanden else '') + '<td>' + Weergave_Symbolen.Instrument_OnbekendeVersie + '</td><td>Nieuwe instrumentversie is onbekend</td></tr>'
        self.LegendaHTML += '<tr>' + ('<td>' + Weergave_Symbolen.Toestand_MeerdereVersies + '</td><td>Meerdere versies</td>' if self._HeeftActueleToestanden else '') + '<td>' + Weergave_Symbolen.Instrument_Intrekking + '</td><td>Intrekking</td></tr>'
        self.LegendaHTML += '<tr>' + ('<td></td><td></td>' if self._HeeftActueleToestanden else '') + '<td>' + Weergave_Symbolen.Tijdstempel_Waarde + '</td><td>Tijdstempel(s)</td></tr>'
        self.LegendaHTML += '<tr>' + ('<td></td><td></td>' if self._HeeftActueleToestanden else '') + '<td>' + Weergave_Symbolen.Instrument_Terugtrekking + '</td><td>Instrument wijzigt niet meer</td></tr>'
        self.LegendaHTML += '<tr>' + ('<td></td><td></td>' if self._HeeftActueleToestanden else '') + '<td>' + Weergave_Symbolen.Tijdstempel_Terugtrekking + '</td><td>Tijdstempels geschrapt</td></tr>'
        self.LegendaHTML += '</table>'

        self.ToelichtingHTML = ''
        for idx, kolom in enumerate (self._Kolommen):
            for elt in kolom.Elementen:
                if elt.Toelichting:
                    if idx == 0 and self._HeeftActueleToestanden:
                        # Globaal ID van de toestand (identificatie en versie)
                        extradata = ' data-' + self._Opties._DiagramId + '_tid="' + str(elt.Bron.UniekId) + '" data-' + self._Opties._DiagramId + '_ti="' + str(elt.Bron.Identificatie) + '"'
                    else:
                        # Lokaal ID van de momentopname
                        extradata = ' data-' + self._Opties._DiagramId + '_mo="' + str(self._MomentopnameUniekId (elt.Bron, elt.TijdstempelsBron)) + '"'
                    self.ToelichtingHTML += '<div data-' + self._Opties._DiagramId + '_t="' + str(elt.Id) + '"' + extradata + ' class="vbd_tl">' + elt.Toelichting + '</div>\n'

#----------------------------------------------------------------------
# Elementen van het diagram: kolommen, rijen en elementen
#----------------------------------------------------------------------
class DiagramKolom:

    def __init__ (self, kolommen):
        """Maak een lege kolom voor het diagram aan

        Argumenten:

        kolommen DiagramKolom[]  Lijst met eerder aangemaakte kolommen
        """
        # Branch die in deze kolom wordt weergegeven; None voor actuele toestanden en voor lege kolommen
        self.Branch = None
        # Uniek ID te gebruiken voor het doel in het diagram
        self.BranchId = None
        # Index van de kolom; 0 = eerste kolom
        self.Index = len (kolommen)
        # De elementen in deze kolom, gesorteerd op oplopende rij
        self.Elementen = []
        # Horizontale positie in de SVG (bij samenstellen van de SVG)
        self._X = None
        kolommen.append (self)

class DiagramRij:

    def __init__(self, gemaaktOp):
        """Maak een lege rij voor het diagram

        Argumenten:
        gemaaktOp string  Het tijdstip van de uitwisseling die in de rij getoond wordt
        """
        self.GemaaktOp = gemaaktOp
        # Index van de rij; 0 = onderste rij
        self.Index = None
        # De elementen in deze rij, gesorteerd op oplopende kolom
        self.Elementen = []
        # Het aantal horizontale banen waarin de rij opgedeeld moet worden zodat verbanden 
        # tussen de elementen netjes getekend kunnen worden
        self.AantalBanen = 1
        # Het aantal horizontale banen waarin de momentopnamen zitten
        self.AantalMOBanen = 1
        # Boven- en ondergrens in y van het gebied waar elementen afgebeeld zijn
        self._Y0 = 0
        self._Y1 = 0

class DiagramElement:

    def __init__(self, bron):
        """Maak een leeg element rij voor het diagram

        Argumenten:
        bron ToestandActueel of Momentopname
        """
        self.Bron = bron
        # Bron van de tijdstempels, als die in deze momentopname wijzigen
        self.TijdstempelsBron = None
        # Uniek nummer voor het element
        self.Id = None
        # Toelichting op het element
        self.Toelichting = None
        # Kolom het element is deel van
        self.Kolom = None
        # Rij het element is deel van
        self.Rij = None
        # Index van de baan binnen de rij; 0 is de onderste
        self.Baan = 0
        # Het aantal kolommen waarvan de elementen met dezelfde Baan verbonden
        # moeten worden omdat het om dezelfde instrumentversie gaat
        self.AantalKolommen = 1
        # Label dat in het element getekend moet worden
        self.Label = None
        # Geeft aan welke elementen de basisversies zijn. Hierbij worden de branches
        # die ook in de doelen staan niet meegenomen.
        # (De basisversies binnen een branch worden anders getekend)
        # Lijst met instanties van DiagramElement
        self.Basisversies = []
        # Geeft aan met welke elementen uit een andere branch deze momentopname ontvlochten is
        # Lijst met instanties van DiagramElement
        self.OntvlochtenMet = []
        # Geeft aan met welke elementen uit een andere branch deze momentopname vervlochten is
        # Lijst met instanties van DiagramElement
        self.VervlochtenMet = []
        # Geeft aan met welke toestand de momentopname verbonden moet worden
        # Instantie van DiagramElement
        self.NaarToestand = None
        # Geeft de elementen binnen dezelfde uitwisseling (gemaaktOp) naar dit element verwijzen
        # via een Basisversie / OntvlochtenMet / VervlochtenMet
        self._NaarElementBinnenUitwisseling = []
        # Geeft elementen binnen een rij die horizontaal verbonden moeten worden
        self._Verbonden = [self]
        # Geeft elementen binnen een rij tussen de elementen die horizontaal verbonden moeten worden
        self._Tussenliggend = []
        # Horizontale positie van de linkerbovenhoek in de SVG (bij samenstellen van de SVG)
        self._X = None
        # Verticale positie van de linkerbovenhoek in de SVG (bij samenstellen van de SVG)
        self._Y = None

    def InKolom (self, kolom):
        """Voeg het element aan een kolom toe
        
        Argumenten:
        kolom DiagramKolom  Kolom waar het element deel van uitmaakt

        Geeft dit element terug
        """
        self.Kolom = kolom
        kolom.Elementen.append (self)
        return self

    def InRij (self, rij):
        """Voeg het element aan een kolom toe
        
        Argumenten:
        rij DiagramRij Rijwaar het element deel van uitmaakt

        Geeft dit element terug
        """
        self.Rij = rij
        rij.Elementen.append (self)
        return self
