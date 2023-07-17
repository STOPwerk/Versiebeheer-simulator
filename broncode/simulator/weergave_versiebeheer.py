#======================================================================
#
# Aanmaken van een diagram van het versiebeheer als onderdeel van
# de webpagina die alle beschikbare resultaten laat zien
# van het consolidatie proces uit proces_consolideren.
#
#======================================================================

from data_versiebeheerinformatie import Instrument
from nonstop_annotatie import NonSTOPAnnotatie
from stop_consolidatieinformatie import ConsolidatieInformatie
from stop_metadata import Metadata
from weergave_data_toestanden import ToestandActueel
from weergave_resultaat_data import InstrumentData
from weergave_stopmodule import Weergave_STOPModule
from weergave_versiebeheer_diagram import DiagramGenerator, DiagramGeneratorOpties
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Weergave_Versiebeheer
#
#----------------------------------------------------------------------
#
# Generator die het versiebeheer en de actuele toestanden voor een 
# instrument weergeeft.
#
#======================================================================
class Weergave_Versiebeheer ():

    @staticmethod
    def VoegToe (generator : WebpaginaGenerator, instrument : Instrument, instrumentData : InstrumentData):
        """Presenteer het overzicht van het versiebeheer en (indien beschikbaar) de actuele toestanden.
        
        Argumenten:
        generator WebpaginaGenerator  Generator voor de webpagina
        instrument Instrument Weer te geven versiebeheerinformatie
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        uniek_id = 'vbh_' + str (generator.GeefUniekeIndex ())
        einde = generator.StartSectie ('<h3>Versiebeheer en actuele toestanden</h3>' if instrumentData.HeeftActueleToestanden else '<h3>Versiebeheer</h3>', True, True)

        einde_t = generator.StartToelichting ('Toelichting op het gebruik van versiebeheer' + (' en actuele toestanden'if instrumentData.HeeftActueleToestanden else ''))
        generator.LeesHtmlTemplate ('help_versiebeheer')
        if instrumentData.HeeftActueleToestanden:
            generator.LeesHtmlTemplate ('help_toestanden')
        generator.VoegHtmlToe (einde_t)

        diagramOpties = _VersiebeheerDiagram (uniek_id, instrument, instrumentData)
        diagram = DiagramGenerator.VoerUit (diagramOpties)
        
        # Stel de pagina samen
        html = generator.LeesHtmlTemplate ("", False).replace ('UNIEK_ID', uniek_id)
        html = html.replace ('<!--DIAGRAM-->', diagram.SVG)
        html = html.replace ('<!--TOELICHTING-->', diagram.ToelichtingHTML)
        generator.VoegHtmlToe (html)

        einde_t = generator.StartToelichting ('Legenda')
        html = generator.LeesHtmlTemplate ("legenda", False)
        html = html.replace ('<!--DOELEN-->', diagram.DoelenHTML)
        html = html.replace ('<!--LEGENDA-->', diagram.LegendaHTML)
        generator.VoegHtmlToe (html)
        generator.VoegHtmlToe (einde_t)

        generator.VoegSlotScriptToe (generator.LeesJSTemplate ('', False).replace ('UNIEK_ID', uniek_id).replace ('WORK_ID', instrumentData.WorkId))
        diagram.VoegOndersteuningToe (generator)

        generator.VoegHtmlToe (einde)

#======================================================================
#
# Maker van teksten en symbolen voor diagram elementen, en 
# context/opties voor het maken van het diagram
#
#======================================================================
class _VersiebeheerDiagram (DiagramGeneratorOpties):

    def __init__ (self, uniek_id : str, instrument : Instrument, instrumentData : InstrumentData):
        """Maak de tekstgenerator aan

        Argumenten:

        uniek_id string  Uniek ID voor het fragment in de pagina
        instrument InstrumentData Weer te geven versiebeheerinformatie
        instrumentData InstrumentUitwisseling Weer te geven consolidatie informatie voor het instrument
        """
        super().__init__(uniek_id, instrument, instrumentData, True)

    def MomentopnameToelichting (self, element):
        """Geef de toelichting voor een element dat een of twee momentopnamen representeert

        Argumenten:
        element DiagramElement  Element waarvoor de toelichting gemaakt wordt
        """
        html = '<p><b>Doel ' + element.Kolom.BranchId + ' (' + str(element.Kolom.Branch.Doel) + '), gemaaktOp: ' + element.Rij.GemaaktOp + '</b><br/>\n'
        if element.Bron:
            if element.Bron.IsTeruggetrokken:
                html += 'Het instrument wordt niet meer gewijzigd voor dit doel<br/>\n'
            else:
                if element.Bron.IsIngetrokken:
                    html += 'Het instrument wordt ingetrokken<br/>\n'
                elif element.Bron.ExpressionId:
                    proefversie = self._Instrument.Proefversies.get (element.Bron.ExpressionId)
                    if not proefversie is None and len (proefversie.Annotaties) > 0:
                        html += '<table><tr><td colspan="2">Instrumentversie</td><td colspan="2">' + element.Bron.ExpressionId + '</td></tr>\n'
                        html += '<tr><td>&nbsp;</td><td><i>Annotatie</i></td><td colspan="2"><i>Van toepassing vanaf versie</i></td></tr>\n'
                        for rootElement in sorted (proefversie.Annotaties.keys ()):
                            annotatie = proefversie.Annotaties[rootElement]
                            if isinstance (annotatie, NonSTOPAnnotatie):
                                html += '<tr><td>&nbsp;</td><td colspan="2" class="nw">' + annotatie.AnnotatieNaam + '</td></tr>\n'
                                for nonStop in sorted (annotatie.Annotaties.keys ()):
                                    html += '<tr><td colspan="2">&nbsp;</td><td class="nw">' + nonStop + '</td><td>' + annotatie.Annotaties[nonStop] + '</td></tr>\n'
                            else:
                                html += '<tr><td>&nbsp;</td><td class="nw">' + annotatie.AnnotatieNaam + '</td><td colspan="2">' + annotatie.Instrumentversie + '</td></tr>\n'
                                if isinstance (annotatie, Metadata):
                                    html += '<tr><td colspan="2">&nbsp;</td><td>Citeertitel:</td><td>' + annotatie.Citeertitel + '</td></tr>\n'

                        html += '</table>'
                    else:
                        html += 'Instrumentversie: ' + element.Bron.ExpressionId + '<br/>\n'
                else:
                    html += 'Instrumentversie is niet opgesteld<br/>\n'
        if element.TijdstempelsBron:
            if element.TijdstempelsBron.JuridischWerkendVanaf:
                html += 'Juridisch werkend vanaf: ' + element.TijdstempelsBron.JuridischWerkendVanaf + '<br/>\n'
            if element.TijdstempelsBron.GeldigVanaf:
                html += 'Geldig vanaf: ' + element.TijdstempelsBron.GeldigVanaf + '<br/>\n'
        html += '</p><p>Relevant onderdeel van de consolidatie-informatie:\n'
        xml = ['<ConsolidatieInformatie xmlns="' + ConsolidatieInformatie.DataNamespace + '">']
        xml.append ('\t<gemaaktOp>' + element.Rij.GemaaktOp + '</gemaaktOp>')
        perCollectie = {}
        if not element.Bron is None and element.Bron.GemaaktOp == element.Rij.GemaaktOp:
            for ci in element.Bron._ConsolidatieInformatieElementen:
                collectie = ci.ModuleXmlInCollectie ()
                if not collectie in perCollectie:
                    perCollectie[collectie] = []
                perCollectie[collectie].extend (['\t\t' + line for line in ci.ModuleXmlElement ()])
        if not element.TijdstempelsBron is None and element.TijdstempelsBron.GemaaktOp == element.Rij.GemaaktOp:
            for ci in element.TijdstempelsBron._ConsolidatieInformatieElementen:
                collectie = ci.ModuleXmlInCollectie ()
                if not collectie in perCollectie:
                    perCollectie[collectie] = []
                perCollectie[collectie].extend (['\t\t' + line for line in ci.ModuleXmlElement ()])
        for collectie in sorted (perCollectie):
            if collectie:
                xml.append ('\t<' + collectie + '>')
            xml.extend (perCollectie[collectie])
            if collectie:
                xml.append ('\t</' + collectie + '>')
        xml.append ('</ConsolidatieInformatie>')
        html += Weergave_STOPModule.MaakHtml (xml) + '</p>'
        return html

    def ToestandToelichting (self, element, toestand : ToestandActueel):
        """Geef de toelichting voor een element dat een toestand representeert

        Argumenten:
        element DiagramElement  Element waarvoor de toelichting gemaakt wordt
        toestand ToestandInhoud  De toestand corresponderend met het element
        """
        html = '<p><b>Toestand: ' + toestand.ExpressionId + '</b><br/>\n'
        if toestand.NietMeerActueel:
            html = '<b>Toestand is niet meer actueel</b><br/>\n'
        html += 'Juridisch werkend vanaf ' + toestand.JuridischWerkendVanaf + (' tot ' + toestand.JuridischWerkendTot if toestand.JuridischWerkendTot else '') + '</p>\n'

        proefversie = self._Instrument.Proefversies.get (toestand.Instrumentversie) if toestand.Instrumentversie else None
        if not proefversie is None and len (proefversie.Annotaties) > 0:
            html += '<p><table><tr><td>Instrumentversie</td><td>' + toestand.Instrumentversie + '</td></tr><tr><td>Annotaties</td><td><table>\n'
            for rootElement in sorted (proefversie.Annotaties.keys ()):
                annotatie = proefversie.Annotaties[rootElement]
                if isinstance (annotatie, NonSTOPAnnotatie):
                    nonStopAnnotaties = sorted (annotatie.Annotaties.keys ())
                    html += '<tr><td rowspan="' + str(len(annotatie.Annotaties)) + '" class="nw">' + annotatie.AnnotatieNaam + '</td>'
                    startTR = ''
                    for nonStop in sorted (annotatie.Annotaties.keys ()):
                        html += startTR + '<td class="nw">' + nonStop + '</td></tr>\n'
                        startTR = '<tr>'
                elif isinstance (annotatie, Metadata):
                    html += '<tr><td colspan="2">' + annotatie.AnnotatieNaam + '</td></tr><tr><td class="ra">&nbsp;Citeertitel:</td><td>' + annotatie.Citeertitel + '</td></tr>\n'
                else:
                    html += '<td colspan="2" class="nw">' + annotatie.AnnotatieNaam + '</td></tr>\n'
            html += '</table></td></table></p>'
        else:
            html += '<p>Instrumentversie: ' + (toestand.Instrumentversie if toestand.Instrumentversie else 'onbekend') + '</p>\n'
        html += self.NogTeConsoliderenInformatie (toestand, toestand, str(element.Id))
        if toestand.Basisversiedoelen:
            html += '<div>(De <i>overige doelen die bijdragen</i> aan de toestand worden niet vermeld in de STOP module ActueleToestanden)</div>\n'

        # Selector om selectie van uitwisselingen te tonen
        html += '<p>'+ self.NogTeConsoliderenToggle (toestand, toestand, str(element.Id)) + ' Geef in het diagram de uitwisselingen aan die wel/niet bijdragen aan de toestand.</p>'

        return html
