#======================================================================
#
# Aanmaken van een weergave van proefversies en de daarbij behorende
# annotaties als onderdeel van de webpagina die alle beschikbare 
# resultaten laat zien van het consolidatie proces uit 
# proces_consolideren.
#
#======================================================================

from typing import List

from data_lv_annotatie import Annotatie
from data_lv_versiebeheerinformatie import Instrument
from weergave_data_proefversies import Proefversies, Proefversie, ProefversieAnnotatie
from weergave_resultaat_data import InstrumentData, InstrumentUitwisseling
from weergave_stopmodule import Weergave_STOPModule
from weergave_symbolen import Weergave_Symbolen
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_versiebeheer_diagram import DiagramGenerator, DiagramGeneratorOpties
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Weergave_Tijdreisfilter
#
#======================================================================
class Weergave_Proefversies ():

    @staticmethod
    def VoegToe (generator : WebpaginaGenerator, instrument : Instrument, instrumentData : InstrumentData):
        """Licht de bepaling van proefversies en van de bijbehorende annotaties toe
        
        Argumenten:
        generator WebpaginaGenerator  Generator voor de webpagina
        instrument Instrument Weer te geven versiebeheerinformatie
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        selector = Weergave_Uitwisselingselector (instrumentData.WeergaveData.Scenario)
        diagram_id = 'pv_' + str(generator.GeefUniekeIndex())

        einde = generator.StartSectie ('<h3>Proefversies en annotaties</h3>' if instrumentData.HeeftProefversiesMetAnnotaties else '<h3>Proefversies</h3>', True)

        einde_t = generator.StartToelichting ('Toelichting')
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        for uitwisseling in instrumentData.Uitwisselingen:
            generator.VoegHtmlToe ('<div ' + selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>')
            if uitwisseling.Proefversies is None:
                generator.VoegHtmlToe ('<p>De geselecteerde uitwisseling bevat geen versies voor dit instrument</p>')
            else:
                maker = Weergave_Proefversies (diagram_id, instrument, uitwisseling)
                generator.VoegHtmlToe (maker._MaakInstrumentversieOverzicht ())
                for proefversie in uitwisseling.Proefversies:
                    generator.VoegHtmlToe (maker._MaakProefversieDetail (generator, proefversie))
            generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde)

        generator.LeesCssTemplate ('')
        generator.VoegSlotScriptToe (generator.LeesJSTemplate ('', False).replace ('DIAGRAM_ID', diagram_id))

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
    def __init__ (self, diagram_id : str, instrument : Instrument, instrumentData : InstrumentUitwisseling):
        """Maak de generator aan
        
        Argumenten:
        diagram_id str  Unieke identificatie van dit fragment in de pagina
        instrument Instrument Weer te geven versiebeheerinformatie
        instrumentData InstrumentUitwisseling Weer te geven consolidatie informatie voor het instrument
        """
        self._DiagramId = diagram_id
        self._Instrument = instrument
        self._InstrumentData = instrumentData
        # Diagrammen gemaakt voor de proefversies
        # Key = proefversie, value = (opties, diagram)
        self._Diagrammen = {}

    def _Diagram (self, proefversie):
        """Maak het diagram aan voor de proefversie"""
        diagram = self._Diagrammen.get (proefversie)
        if not diagram is None:
            return diagram
        diagramOpties = _ProefversieDiagram (self._DiagramId + '_d_' + proefversie._UniekId, self._Instrument, self._InstrumentData, [a._Annotatie for a in proefversie.Annotaties])
        diagram = DiagramGenerator.VoerUit (diagramOpties)
        self._Diagrammen[proefversie] = ((diagramOpties, diagram))
        return (diagramOpties, diagram)

#----------------------------------------------------------------------
#
# Overzicht van instrumentversies
#
#----------------------------------------------------------------------
    def _MaakInstrumentversieOverzicht (self):
        """Maak een overzicht van de beschikbare proefversies voor dit en voor de andere instrumenten"""

        # Verzamel alle instrumentversies per doelgroep
        # key = doelen, value = (proefversie van die instrument, lijst van versies van overige instrumenten)
        doelgroepen = {}

        # Zoek de proefversies voor dit instrument op
        instrumentversies = set ()
        for proefversie in self._InstrumentData.Proefversies:
            doelen = '\n'.join (str(d) for d in proefversie.Doelen)
            doelgroepen[doelen] = (proefversie, [])
            instrumentversies.add (proefversie.Instrumentversie)

        # ... en voor de andere
        for instrumentversie in self._InstrumentData._Uitwisseling.Instrumentversies:
            if not instrumentversie.Instrumentversie in instrumentversies:
                doelen = '\n'.join (str(d) for d in instrumentversie.Doelen)
                info = doelgroepen.get (doelen)
                if info is None:
                    doelgroepen[doelen] = info = (None, [])
                info[1].append (instrumentversie)

        html = '<p>Er zijn proefversies beschikbaar voor:'
        html += '<table class="pv_overzicht"><tr><th>Doelen</th><th colspan="2">Instrumentversie</th><th colspan="2">Annotatie</th><th>Versie van</th></tr>'
        for doelen in sorted (doelgroepen.keys ()):
            info = doelgroepen[doelen]
            html += '<tr class="pv_toprow"><td rowspan="' + str((0 if info[0] is None else (1 if len (info[0].Annotaties) == 0 else len (info[0].Annotaties))) + len(info[1])) + '">' + doelen.replace ('\n', '<br/>') + '</td>'
            eindeRij = ''
            if not info[0] is None:
                aantalRijen = str(1 if len (info[0].Annotaties) == 0 else len (info[0].Annotaties))
                html += '<td rowspan="' + aantalRijen + '"><input type="radio" name="' + self._DiagramId + '_' + self._InstrumentData._UniekId + '" data-' + self._DiagramId + '_select="' + self._InstrumentData._Uitwisseling.GemaaktOp + ';' + info[0]._UniekId + '" id="' + self._DiagramId + '_' + info[0]._UniekId + '"></td>'
                html += '<td rowspan="' + aantalRijen + '"><label for="' + self._DiagramId + '_' + info[0]._UniekId + '">' + info[0].Instrumentversie + '</label></td>'

                diagramOpties, diagram = self._Diagram (info[0])
                for annotatie in info[0].Annotaties:
                    html += eindeRij + '<td><input type="radio" name="' + self._DiagramId + '_a_' + info[0]._UniekId + '" data-' + self._DiagramId + '_a_select="' + self._InstrumentData._Uitwisseling.GemaaktOp + ';'+ info[0]._UniekId + ';' + annotatie._Annotatie._UniekId + '" id="' + self._DiagramId + '_a_' + annotatie._UniekId + '"'
                    html += diagramOpties.MaakSelectieAttribuutVoorAnnotatie (info[0], annotatie) + '></td>'
                    html += '<td><label for="' + self._DiagramId + '_a_' + annotatie._UniekId + '">' + annotatie.Naam + '</label></td><td>'
                    if annotatie.Versie is None:
                        html += '-'
                    elif annotatie.Versie:
                        html += annotatie.Versie.GemaaktOp + '<span title="' + annotatie.Versie._Beschrijving + '">' + Weergave_Symbolen.Annotatie_Uitwisseling + '</span>'
                    else:
                        html += 'Onbekend'
                    html += '</td>'
                    eindeRij = '</tr><tr>\n'

                eindeRij = '</tr><tr>\n'
            for anderInstrument in info[1]:
                html += eindeRij + '<td></td><td>' + anderInstrument.Instrumentversie + '</td>'
                eindeRij = '</tr><tr>\n'
            html += '</tr>'

        html += '</table></p>\n'
        return html

#----------------------------------------------------------------------
#
# Informatie over een proefversie
#
#----------------------------------------------------------------------
    def _MaakProefversieDetail (self, generator : WebpaginaGenerator, proefversie : Proefversie):
        """Beschrijf de proefversie en de bepaling ervan"""

        diagramOpties, diagram = self._Diagram (proefversie)

        html = '<p data-' + self._DiagramId + '="' + self._InstrumentData._Uitwisseling.GemaaktOp + ';' + proefversie._UniekId + '" style="display: none;">'
        html += '<table><tr><td class="pv_kolom">'

        html += '<p><b>Bepaling van de proefversie</b> '
        html += '<input type="radio" name="' + self._DiagramId + '_a_' + proefversie._UniekId + '" data-' + self._DiagramId + '_a_select="' + self._InstrumentData._Uitwisseling.GemaaktOp + ';'+ proefversie._UniekId + ';0" id="' + self._DiagramId + '_a_' + proefversie._UniekId + '"' + diagramOpties.MaakSelectieAttribuutVoorProefversie (proefversie) + '>'
        html += '<label for="' + self._DiagramId + '_a_' + proefversie._UniekId + '">toon in diagram</label><br/>'
        html += '<table>' + ''.join (m.HtmlTabelRij (False) for m in proefversie._Uitleg) + '</table></p>'

        html += '<p><b>STOP module</b><br/>'
        html += Weergave_STOPModule.MaakHtml (Proefversies (self._InstrumentData._Uitwisseling.BekendOp, self._InstrumentData._Uitwisseling.OntvangenOp, proefversie).ModuleXml ())
        html += '</p>'

        html += '</td><td  class="pv_kolom">'

        html += '<div class="pv_diagram">'
        html += diagram.SVG
        html += '</div><table><tr><td>'
        html += diagram.DoelenHTML
        html += '</td><td>'
        html += '<table><tr><th colspan="2">Legenda</th></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Annotatie_Uitwisseling + '</td><td>Uitwisseling annotatieversie</td></tr>'
        html += '<tr><td class="vbd_ntc iv">&nbsp;</td><td>Proefversie/bron annotatieversie</td></tr>'
        html += '<tr><td class="vbd_ntc vw">&nbsp;</td><td>Betrokken</td></tr>'
        html += '<tr><td class="vbd_ntc ts">&nbsp;</td><td>Tegenstrijdige versies</td></tr>'
        html += '</table></td></tr></table>'
        diagram.VoegOndersteuningToe (generator)

        for annotatie in proefversie.Annotaties:
            html += '<div data-' + self._DiagramId + '_a="' + annotatie._Annotatie._UniekId + '" style="display: none;">'

            html += '<p><b>' + annotatie.Naam + '</b>:'
            if annotatie.Versie is None:
                html += 'geen versie uitgewisseld<br/>'
            elif annotatie.Versie:
                html += 'versie van ' + annotatie.Versie.GemaaktOp + '<br/>' + annotatie.Versie._Beschrijving
            else:
                html += 'versie kan niet (eenduidig) bepaald worden<br/>'
            html += '</p>'

            html += '<p><b>Bepaling van de versie van de annotatie</b><br/>'
            html += '<table>' + ''.join (m.HtmlTabelRij (False) for m in annotatie._Uitleg) + '</table></p>'
            html += '</div>'


        html += '</td></tr></table>'
        html += '</p>'
        return html

#======================================================================
#
# Maker van teksten en symbolen voor diagram elementen, en 
# context/opties voor het maken van het diagram, met als toepassing
# de proefversies / annotaties.
#
#======================================================================
class _ProefversieDiagram (DiagramGeneratorOpties):

    def __init__ (self, uniekId, instrument : Instrument, instrumentData : InstrumentUitwisseling, annotaties: List[Annotatie]):
        """Maak de tekstgenerator aan

        Argumenten:

        instrument InstrumentData Weer te geven versiebeheerinformatie
        instrumentData InstrumentUitwisseling Weer te geven consolidatie informatie voor het instrument
        annotaties Annotatie[]  De annotaties die bij een proefversie (kunnen) horen
        """
        super().__init__(uniekId, instrument, instrumentData.InstrumentData, False, instrumentData)
        self._ToonVervlechtingOntvlechting = False
        self._Annotaties = annotaties

    def MomentopnameSymbool (self, element):
        """Geef het symbool voor een element dat een of twee momentopnamen representeert

        Argumenten:
        element DiagramElement  Element waarvoor de toelichting gemaakt wordt

        Geeft een symbool of None
        """
        if not element.Kolom.Branch is None:
            for annotatie in self._Annotaties:
                for versie in annotatie.Versies:
                    if versie.GemaaktOp == element.Rij.GemaaktOp and element.Kolom.Branch.Doel in versie.Doelen:
                        return Weergave_Symbolen.Annotatie_Uitwisseling
        return None

    def MaakSelectieAttribuutVoorProefversie (self, proefversie : Proefversie):
        # Zet eerst alle elementen op niet van toepassing
        selectie = {}
        for elts in self._AlleElementen.values ():
            for elt in elts.values ():
                selectie[elt.Id] = 'nvt'

        for bron in proefversie.Annotatiebronnen:
            # Kleur alle bronnen in
            elts = self._AlleElementen.get (bron.Doel)
            if not elts is None:
                for gemaaktOp, elt in elts.items ():
                    if gemaaktOp <= bron.TotEnMet:
                        selectie[elt.Id] = 'vw'
                    if gemaaktOp == bron.TotEnMet and bron.Doel in proefversie.Doelen:
                        selectie[elt.Id] = 'iv'
        uniekId = proefversie._UniekId + '-0'
        return self._InputSelectieAttribuut (uniekId, selectie)


    def MaakSelectieAttribuutVoorAnnotatie (self, proefversie : Proefversie, annotatieVersie : ProefversieAnnotatie):
        # Zet eerst alle elementen op niet van toepassing
        selectie = {}
        for elts in self._AlleElementen.values ():
            for elt in elts.values ():
                selectie[elt.Id] = 'nvt'

        for doel, vanaf, totEnMet in annotatieVersie._Onderzocht:
            # Kleur alle bronnen in
            elts = self._AlleElementen.get (doel)
            if not elts is None:
                for gemaaktOp, elt in elts.items ():
                    if (vanaf is None or vanaf <= gemaaktOp) and gemaaktOp <= totEnMet:
                        selectie[elt.Id] = 'vw'

        for doel, vanaf in annotatieVersie._Tegenstrijdig:
            elts = self._AlleElementen.get (doel)
            if not elts is None:
                for gemaaktOp, elt in elts.items ():
                    if vanaf == gemaaktOp:
                        selectie[elt.Id] = 'ts'
                        break

        for doel, vanaf in annotatieVersie._Bronnen:
            elts = self._AlleElementen.get (doel)
            if not elts is None:
                for gemaaktOp, elt in elts.items ():
                    if vanaf == gemaaktOp:
                        if selectie[elt.Id][-2:] != 'iv':
                            if selectie[elt.Id] == 'vw':
                                selectie[elt.Id] = 'iv'
                            else:
                                selectie[elt.Id] += ' iv'
                        break

        uniekId = proefversie._UniekId + '-' + annotatieVersie._Annotatie._UniekId
        return self._InputSelectieAttribuut (uniekId, selectie)
