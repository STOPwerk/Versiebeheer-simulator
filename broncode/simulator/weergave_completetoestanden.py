#======================================================================
#
# Aanmaken van een weergave van het CompleteToestanden overzicht als 
# onderdeel van de webpagina die alle beschikbare resultaten laat 
# zien van het consolidatie proces uit proces_consolideren.
#
#======================================================================

from weergave_resultaat_data import InstrumentData
from weergave_stopmodule import Weergave_STOPModule
from weergave_symbolen import Weergave_Symbolen
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Weergave_CompleteToestanden
#
#======================================================================
class Weergave_CompleteToestanden ():

    @staticmethod
    def VoegToe (generator : WebpaginaGenerator, instrumentData : InstrumentData):
        """Voeg de module voor complete toestanden met filterfunctionaliteit toe aan de pagina met resultaten.
        
        Argumenten:
        generator WebpaginaGenerator  Generator voor de webpagina
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        maker = Weergave_CompleteToestanden (generator.GeefUniekeIndex(), instrumentData)

        einde = generator.StartSectie ('<h3>Complete toestanden</h3>', True)

        einde_t = generator.StartToelichting ("Toelichting op het gebruik van de complete toestanden")
        generator.VoegHtmlToe (generator.LeesHtmlTemplate ('help', False).replace ('<!--SYMBOOL-->', Weergave_Symbolen.BenoemdeTijdreis))
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('<table><tr><td>')

        generator.VoegHtmlToe ('<table><tr><td>') # Toestanden en legenda onder elkaar
        generator.VoegHtmlToe (maker._MaakToestandenHtml ())
        generator.VoegHtmlToe ('</td></tr><tr><td>')

        einde_t = generator.StartToelichting ("Legenda")
        generator.VoegHtmlToe ('<table><tr><td>')
        generator.VoegHtmlToe (maker._MaakDoelenHtml ())
        generator.VoegHtmlToe ('</td><td>')
        generator.VoegHtmlToe (maker._MaakLegendaHtml ())
        generator.VoegHtmlToe ('</td></tr></table>')
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('</td></tr></table>')

        generator.VoegHtmlToe ('</td><td>') # Toelichtingen ernaast

        generator.VoegHtmlToe (maker._MaakToelichtingenHtml ())

        generator.VoegHtmlToe ('</td></tr></table>')

        generator.VoegHtmlToe (einde)
        generator.LeesCssTemplate ('')
        generator.VoegSlotScriptToe (generator.LeesJSTemplate ('', False).replace ('UNIEK_ID', maker._UniekId).replace ('WORK_ID', instrumentData.WorkId))

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
    def __init__ (self, uniek_id : int, instrumentData : InstrumentData):
        """Maak de weergave-maker aan.
        
        Argumenten:

        uniek_id int  Uniek nummer om kopieën van dit fragment in de pagina te onderscheiden
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        self._UniekId = 'ct_o_' + str(uniek_id)
        self._InstrumentData = instrumentData
        self._Selector = Weergave_Uitwisselingselector (instrumentData.WeergaveData.Scenario)

#----------------------------------------------------------------------
#
# Legenda
#
#----------------------------------------------------------------------
    def _MaakDoelenHtml (self):
        html = ''
        for uitwisseling in self._InstrumentData.Uitwisselingen:
            html += '<table' + self._Selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>\n'
            html += '<tr><th>Letter</th><th>Doel</th></tr>\n'
            if not uitwisseling.CompleteToestanden is None:
                for doel, branchId in self._InstrumentData.WeergaveData.Branches (uitwisseling.DoelenCompleteToestanden):
                    html += '<tr><td>' + branchId + '</td><td>' + str(doel) + '</td></tr>'
            html += '</table>'
        return html

    def _MaakLegendaHtml (self):
        
        html = '<table><tr><th colspan="2">Symbolen</th></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Toestand_BekendeInhoud + '</td><td>Bekende inhoud</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Toestand_OnbekendeInhoud + '</td><td>Onbekende inhoud</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Toestand_Uitgewerkt + '</td><td>Niet in werking</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.BenoemdeTijdreis + '</td><td>Toelichting beschikbaar</td></tr>'
        html += '<tr><td class="ct_o_t">#</td><td>In uitwisseling</td></tr>'
        html += '<tr><td class="ct_o_t uit">#</td><td>Uitgefilterd</td></tr>'
        html += '<tr><td class="ct_o_t geselecteerd">#</td><td>Geselecteerd</td></tr>'
        html += '</table>'
        return html

#----------------------------------------------------------------------
#
# Toestanden
#
#----------------------------------------------------------------------
    def _MaakToestandenHtml (self):
        html = ''
        for uitwisseling in self._InstrumentData.Uitwisselingen:
            if uitwisseling.CompleteToestanden is None:
                html += '<div ' + self._Selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>Het instrument is nog niet in werking</div>'
            else:
                html += '<table class="ct_o_toestanden"' + self._Selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>'
                html += '<tr><th data-' + self._UniekId + '_ts="o">ontvangenOp</th><th data-' + self._UniekId + '_ts="b">bekendOp</th><th>juridischWerkendVanaf</th><th data-' + self._UniekId + '_ts="g">geldigVanaf</th><th colspan="2">Identificatie</th><th colspan="2">Inhoud</th></tr>'

                for toestand in uitwisseling.CompleteToestanden.Toestanden:
                    if toestand.GemaaktOp <= uitwisseling.GemaaktOp and (toestand.OverschrevenOp is None or toestand.OverschrevenOp > uitwisseling.GemaaktOp):
                        identificatie = uitwisseling.CompleteToestanden.ToestandIdentificatie[toestand.Identificatie]
                        inhoud = uitwisseling.CompleteToestanden.ToestandInhoud[toestand.Inhoud]

                        html += ('<tr class="ct_o_t" data-' + self._UniekId + '_ti="{ti}" data-' + self._UniekId + '_tid="{tid}" data-' + self._UniekId + '_f="{tfi}"').format (ti=toestand.Identificatie, tid=toestand._UniekId, tfi=uitwisseling.ToestandTijdreisIndex(toestand)) + '>'
                        html += '<td data-' + self._UniekId + '_ts="o">' + toestand.OntvangenOp + '</td><td data-' + self._UniekId + '_ts="b">' + toestand.BekendOp + '</td><td>' + toestand.JuridischWerkendVanaf + '</td><td data-' + self._UniekId + '_ts="g">' + toestand.GeldigVanaf + '</td>'
                        html += '<td>#' + str(toestand.Identificatie) + '</td><td>' + ' '.join (letter for _, letter in self._InstrumentData.WeergaveData.Branches (identificatie.Inwerkingtredingsdoelen)) + '</td>'
                        html += '<td>#' + str(toestand.Inhoud) + '</td><td class="s">'
                        if inhoud.IsNietInWerking:
                            html += Weergave_Symbolen.Toestand_Uitgewerkt
                        else:
                            symbool = Weergave_Symbolen.ToestandBekendOfOnbekend (inhoud.Instrumentversie)
                            if symbool == Weergave_Symbolen.Toestand_BekendeInhoud:
                                html += '<span title="' + inhoud.Instrumentversie + '">' + symbool + '</span>'
                            else:
                                html += symbool
                        if toestand._Beschrijving:
                            html += Weergave_Symbolen.BenoemdeTijdreis
                        html += '</td></tr>\n'

                html += '</table>\n'

        return html

    def _MaakToelichtingenHtml (self):
        html = ''

        completeToestanden = self._InstrumentData.Uitwisselingen[-1].CompleteToestanden
        for toestand in completeToestanden.Toestanden:
            identificatie = completeToestanden.ToestandIdentificatie[toestand.Identificatie]
            inhoud = completeToestanden.ToestandInhoud[toestand.Inhoud]

            html += '<div data-' + self._UniekId + '_t="' + str(toestand._UniekId) + '" class="ct_o_toestand">\n'

            html += '<table>'
            html += '<tr><th colspan="3">Toestand</th></tr>'
            html += '<tr><td>ontvangenOp</td><td colspan="2">' + toestand.OntvangenOp + '</td></tr>'
            html += '<tr><td>bekendOp</td><td colspan="2">' + toestand.BekendOp + '</td></tr>'
            html += '<tr><td>juridischWerkendVanaf</td><td colspan="2">' + toestand.JuridischWerkendVanaf+ '</td></tr>'
            html += '<tr><td>geldigVanaf</td><td colspan="2">' + toestand.GeldigVanaf + '</td></tr>'
            html += '<tr><th colspan="3">Identificatie</th></tr>'
            html += '<tr><td>Expression identificatie</td><td colspan="2">' + identificatie.ExpressionId + '</td></tr>'
            if len (identificatie.Inwerkingtredingsdoelen) == 0:
                html += '<tr><td>Inwerkingtredingsdoelen</td><td colspan="2">-</td></tr>\n'
            else:
                html += '<tr><td rowspan="' + str(len (identificatie.Inwerkingtredingsdoelen)) + '">Inwerkingtredingsdoelen</td>' + '<tr>'.join ('<td>' + self._InstrumentData.WeergaveData.DoelLetter (doel) + '</td><td>' + str(doel) + '</td></tr>\n' for doel in identificatie.Inwerkingtredingsdoelen)
            html += '<tr><th colspan="3">Inhoud</th></tr>'
            if inhoud.IsNietInWerking:
                html += '<tr><td></td><td colspan="2">Het instrument is niet in werking</td></tr>'
            else:
                html += '<tr><td>Instrumentversie</td><td colspan="2">' + (inhoud.Instrumentversie if inhoud.Instrumentversie else 'Onbekend') + '</td></tr>'
            html += '</table>\n'

            if not toestand._Beschrijving is None:
                html += '<p>' + Weergave_Symbolen.BenoemdeTijdreis + ' ' + toestand._Beschrijving + '</p>'

            if not inhoud.OnvolledigeVersies is None:
                html += '<p>De inhoud van de toestand is op een alternatieve manier weer te geven:</p>\n'
                html += '<table><tr><th  colspan="3">Instrumentversie</th></tr><tr><td>&nbsp;&nbsp;&nbsp;</td><th colspan="2">... plus de inhoud van de publicatie</th></tr>'

                for versie in inhoud.OnvolledigeVersies:
                   html += '<tr><td colspan="3">' + versie.Instrumentversie + '</td></tr>'
                   if len (versie.TeVerwerkenPublicaties):
                       html += '<tr><td rowspan="' + str(len (versie.TeVerwerkenPublicaties)) + '"></td>'
                       html += '<td rowspan="' + str(len (versie.TeVerwerkenPublicaties)) + '">Verwerken:</td>'
                       html += '</tr><tr>'.join ('<td>' + p + '</td>' for p in sorted (versie.TeVerwerkenPublicaties)) 
                       html += '</tr>\n'
                   if len (versie.TeOntvlechtenPublicaties):
                       html += '<tr><td rowspan="' + str(len (versie.TeOntvlechtenPublicaties)) + '"></td>'
                       html += '<td rowspan="' + str(len (versie.TeOntvlechtenPublicaties)) + '">Ontvlechten:</td>' 
                       html += '</tr><tr>'.join ('<td>' + p + '</td>' for p in sorted (versie.TeOntvlechtenPublicaties))
                       html += '</tr>\n'
                   html += '</tr>\n'

                html += '</table>\n'

            html += '</div>\n'

        return html

