#======================================================================
#
# Aanmaken van een weergave van een overzicht van de complete 
# toestanden als onderdeel van de webpagina die alle beschikbare 
# resultaten laat zien van het consolidatie proces uit 
# proces_consolideren. De eindsituatie wordt getoond, en via
# tijdreizen kan getoond worden wat het effect van een tijdreis
# op de lijst van toestanden is.
#
#======================================================================

from data_versiebeheerinformatie import Instrument
from weergave_resultaat_data import InstrumentData, InstrumentUitwisseling
from weergave_symbolen import Weergave_Symbolen
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Weergave_Tijdreizen
#
#======================================================================
class Weergave_Tijdreizen ():

    @staticmethod
    def VoegToe (generator : WebpaginaGenerator, instrument : Instrument, instrumentData : InstrumentData):
        """Voeg de complete toestanden met tijdreisfunctionaliteit toe aan de pagina met resultaten.
        
        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        instrument Instrument  Informatie over het instrument uit het versiebeheer.
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        einde = generator.StartSectie ('<h3>Tijdreizen</h3>', True)

        einde_t = generator.StartToelichting ('Toelichting op tijdreizen')
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        maker = Weergave_Tijdreizen (generator.GeefUniekeIndex(), instrument, instrumentData)
        generator.VoegHtmlToe ('<table><tr><td>') 
        generator.VoegHtmlToe ('<table><tr><td>') # Toestanden en legenda
        
        generator.VoegHtmlToe (maker._MaakToestandenOverzicht())

        generator.VoegHtmlToe ('</td></tr><tr><td>') # Legenda en doelen
        
        einde_t = generator.StartToelichting ('Legenda')
        generator.VoegHtmlToe ('<table><tr><td>') 
        generator.VoegHtmlToe (maker._MaakDoelenOverzicht ())
        generator.VoegHtmlToe ('</td><td>') 
        generator.VoegHtmlToe (maker._MaakLegenda ())
        generator.VoegHtmlToe ('</td></tr></table>')
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('</td></tr></table></td>') # Einde toestanden en legenda, start diagrammen

        generator.VoegHtmlToe (maker._MaakDiagrammen(generator.LeesHtmlTemplate ('', False).replace ('UNIEK_ID', maker._UniekId)))
        generator.VoegHtmlToe ('</tr></table>')

        generator.VoegHtmlToe (einde)
        generator.LeesCssTemplate ('')
        generator.VoegSlotScriptToe (generator.LeesJSTemplate ('', False).replace ('UNIEK_ID', maker._UniekId).replace ('WORK_ID', instrumentData.WorkId))

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
    def __init__ (self, uniek_id : int, instrument : Instrument, instrumentData : InstrumentData):
        """Maak de maker aan.
        
        Argumenten:

        uniek_id int  Uniek nummer om kopieën van dit fragment in de pagina te onderscheiden
        instrument Instrument  Informatie over het instrument uit het versiebeheer.
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        self._UniekId = 'ct_tr_' + str(uniek_id)
        self._Instrument = instrument
        self._InstrumentData = instrumentData
        self._CompleteToestanden = self._InstrumentData.Uitwisselingen[-1].CompleteToestanden
        self._Selector = Weergave_Uitwisselingselector (self._InstrumentData.WeergaveData.Scenario)
        # Gebruik een index om de elementen uit het ontvangenOp/bekendOp diagram te selecteren
        # Elk van die elementen heeft een unieke ontvangenOp/bekendOp combinatie
        beschikbaarheidCombinaties = { t.OntvangenOp + ':' + t.BekendOp : (t.OntvangenOp, t.BekendOp) for t in self._CompleteToestanden.Toestanden }
        self._BeschikbaarheidCombi = { }
        idx = 0
        for key in beschikbaarheidCombinaties:
            idx += 1
            self._BeschikbaarheidCombi[key] = str(idx)

        # Gebruik een index array om de elementen uit het JWV/GV diagram te relateren aan het ontvangenOp/bekendOp diagram
        # De gegevens van meerdere beschikbaarheidsperioden moeten gecombineerd worden
        self._BeschikbaarheidTotaal = {}
        for key, ob in beschikbaarheidCombinaties.items ():
            gecombineerd = []
            for key2, ob2 in beschikbaarheidCombinaties.items ():
                if ob2[0] <= ob[0] and ob2[1] <= ob[1]:
                    gecombineerd.append (self._BeschikbaarheidCombi[key2])
            self._BeschikbaarheidTotaal[key] = '|' + '|'.join (gecombineerd) + '|'

#----------------------------------------------------------------------
#
# HTML generatie
#
#----------------------------------------------------------------------
    def _MaakDoelenOverzicht (self):
        html = '<table><tr><th>Letter</th><th>Doel</th></tr>\n'
        for doel, branchId in self._InstrumentData.WeergaveData.Branches ([doel for doel in self._Instrument.Branches]):
            html += '<tr><td>' + branchId + '</td><td>' + str(doel) + '</td></tr>'
        html += '</table>'
        return html

    def _MaakLegenda (self):
        html = '<table><tr><th colspan="2">Symbolen</th></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Toestand_BekendeInhoud + '</td><td>Bekende inhoud</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Toestand_OnbekendeInhoud + '</td><td>Onbekende inhoud</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Toestand_Uitgewerkt + '</td><td>Juridisch uitgewerkt</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.BenoemdeTijdreis + '</td><td>Toelichting</td></tr>'
        html += '<tr><td class="ct_tr_t uw">#</td><td>Bepaald in deze uitwisseling</td></tr>'
        html += '<tr><td class="ct_tr_t">#</td><td>Eerder bepaald</td></tr>'
        html += '<tr><td class="ct_tr_tk">#</td><td>Nog niet van toepassing</td></tr>'
        html += '<tr><td class="ct_tr_t geselecteerd">#</td><td>Geselecteerde tijdreis</td></tr>'
        html += '<tr><td>' + Weergave_Tijdreizen._BeschikbaarheidVoorGeldigheid + '</td><td>Beschikbaarheid voor geldigheidsoverzicht</td></tr>'
        html += '</table>'
        return html

    def _MaakDiagrammen (self, html):
        html = html.replace ("<!--TIJDREIZEN_OB-->", self._MaakBeschikbaarheidDiagram ())
        html = html.replace ("<!--TIJDREIZEN_JG-->", self._MaakGeldigheidDiagram ())

        return html

    def _MaakToestandenOverzicht (self):
        """Maak de tijdreistabel met de stand voor na specifieke uitwisseling
        """
        toestandenHtml = '<table class="ct_tr_toestanden"><tr><th>ontvangenOp</th><th>bekendOp</th><th>juridischWerkendVanaf</th><th>geldigVanaf</th><th colspan="2">Identificatie</th><th colspan="2">Inhoud</th></tr>'
        allegemaaktOp = list (sorted (set ([t.GemaaktOp for t in  self._CompleteToestanden.Toestanden])))
        for toestand in self._CompleteToestanden.Toestanden:
            identificatie = self._CompleteToestanden.ToestandIdentificatie[toestand.Identificatie]
            inhoud = self._CompleteToestanden.ToestandInhoud[toestand.Inhoud]

            toestandHtml = '<tr {attr}>'
            toestandHtml += '<td>' + toestand.OntvangenOp + '</td><td>' + toestand.BekendOp + '</td><td>' + toestand.JuridischWerkendVanaf + '</td><td>' + toestand.GeldigVanaf + '</td>'
            toestandHtml += '<td>#' + str(toestand.Identificatie) + '</td><td>' + ' '.join (letter for _, letter in self._InstrumentData.WeergaveData.Branches (identificatie.Inwerkingtredingsdoelen)) + '</td>'
            toestandHtml += '<td>#' + str(toestand.Inhoud) + '</td><td class="s">'
            if inhoud.IsNietInWerking:
                toestandHtml += Weergave_Symbolen.Toestand_Uitgewerkt
            else:
                symbool = Weergave_Symbolen.ToestandBekendOfOnbekend (inhoud.Instrumentversie)
                if symbool == Weergave_Symbolen.Toestand_BekendeInhoud:
                    toestandHtml += '<span title="' + inhoud.Instrumentversie + '">' + symbool + '</span>'
                else:
                    toestandHtml += symbool
            if toestand._Beschrijving:
                toestandHtml += '<span title="' + toestand._Beschrijving + '">' + Weergave_Symbolen.BenoemdeTijdreis + '</span>'
            toestandHtml += '</td></tr>'

            idxGemaaktOp = allegemaaktOp.index (toestand.GemaaktOp)
            if idxGemaaktOp > 0:
                # Maak de regel voor eerdere uitwisselingen:
                toestandenHtml += toestandHtml.format (attr = 'class="ct_tr_tk"' + self._Selector.AttributenToonIn (allegemaaktOp[0], toestand.GemaaktOp))
            idAttr = ' data-{id}_ti="{ti}" data-{id}_tid="{tid}" data-{id}_ob_t="{ob}"'.format (id=self._UniekId, ti=toestand.Identificatie, tid=toestand._UniekId, ob=self._BeschikbaarheidCombi[toestand.OntvangenOp + ':' + toestand.BekendOp])
            if idxGemaaktOp < len (allegemaaktOp) - 1:
                toestandenHtml += toestandHtml.format (attr = 'class="ct_tr_t uw"' + idAttr + self._Selector.AttributenToonIn (toestand.GemaaktOp, allegemaaktOp[idxGemaaktOp+1]))
                if toestand.OverschrevenOp is None:
                    toestandenHtml += toestandHtml.format (attr = 'class="ct_tr_t"' + idAttr + self._Selector.AttributenToonIn (allegemaaktOp[idxGemaaktOp+1], None))
                else:
                    if toestand.OverschrevenOp > allegemaaktOp[idxGemaaktOp+1]:
                        toestandenHtml += toestandHtml.format (attr = 'class="ct_tr_t"' + idAttr + self._Selector.AttributenToonIn (allegemaaktOp[idxGemaaktOp+1], toestand.OverschrevenOp))
                    toestandenHtml += toestandHtml.format (attr = 'class="ct_tr_to"' + self._Selector.AttributenToonIn (toestand.OverschrevenOp, None))
            else:
                toestandenHtml += toestandHtml.format (attr = 'class="ct_tr_t uw"' + idAttr + self._Selector.AttributenToonIn (toestand.GemaaktOp, None))

        toestandenHtml += '</table>'
        return toestandenHtml

    def _MaakBeschikbaarheidDiagram (self):
        # Bepaal de rijen voor ontvangenOp
        ontvangenOp_Y = { t.OntvangenOp : 0 for t in  self._CompleteToestanden.Toestanden}
        svgHoogte = ((2 * len(ontvangenOp_Y) + 1) * Weergave_Tijdreizen._SvgRijHoogte) / 2
        y = Weergave_Tijdreizen._SvgRijHoogte / 2
        for ontvangenOp in sorted (ontvangenOp_Y.keys ()):
            ontvangenOp_Y[ontvangenOp] = svgHoogte - y
            y += Weergave_Tijdreizen._SvgRijHoogte

        # Bepaal de kolommen voor bekendOp
        bekendOp_X = { t.BekendOp : 0 for t in  self._CompleteToestanden.Toestanden}
        svgBreedte = ((2 * len(bekendOp_X) + 1) * Weergave_Tijdreizen._SvgKolomBreedte) / 2
        x = Weergave_Tijdreizen._SvgKolomBreedte / 2
        for bekendOp in sorted (bekendOp_X.keys ()):
            bekendOp_X[bekendOp] = x
            x +=  Weergave_Tijdreizen._SvgKolomBreedte

        svg = '<svg id="' + self._UniekId + '_ob_svg" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: 100%; height: 100%;" viewBox="0 0 ' + str(svgBreedte) + ' ' + str(svgHoogte) + ' " version="1.1">\n'

        svgFragment = '<rect x="{x}" y="0" width="{w}" height="{y}" class="ct_tr_dr{t}" data-' + self._UniekId + '_ob_e="{ob}" data-' + self._UniekId + '_obt="{obt}"><title>ontvangenOp={o}, bekendOp={b}</title></rect>\n'
        svgFragment += '<path d="M {x} {y} L {x} 0" class="ct_tr_dl{t}"/>\n'
        svgFragment += '<path d="M {x} {y} L ' + str(svgBreedte) + ' {y}" class="ct_tr_dl{t}"/>\n'
        svgFragment += '<text x="{xt}" y="{yt}" class="ct_tr_dt_obt" data-' + self._UniekId + '_obt_g="{obt}">' + Weergave_Tijdreizen._BeschikbaarheidVoorGeldigheid + '</text>\n'
        for uitwisseling in self._InstrumentData.Uitwisselingen:
            getoond = set()
            bijdragen = []
            for toestand in self._CompleteToestanden.Toestanden:
                if toestand.GemaaktOp > uitwisseling.GemaaktOp or (not toestand.OverschrevenOp is None and toestand.OverschrevenOp <= uitwisseling.GemaaktOp):
                    continue
                ob = toestand.OntvangenOp + ':' + toestand.BekendOp
                if ob in getoond:
                    continue
                getoond.add (ob)
                obt = self._BeschikbaarheidTotaal[ob]
                ob = self._BeschikbaarheidCombi[ob]

                x = bekendOp_X[toestand.BekendOp]
                y = ontvangenOp_Y[toestand.OntvangenOp]
                xt = x + (Weergave_Tijdreizen._SvgKolomBreedte/2)
                yt = y - (Weergave_Tijdreizen._SvgRijHoogte/4)
                bijdragen.append (svgFragment.format (x=x, y=y, w=svgBreedte-x, xt=xt, yt=yt, ob=ob, obt=obt, o=toestand.OntvangenOp, b=toestand.BekendOp, t = ' uw' if toestand.GemaaktOp == uitwisseling.GemaaktOp else ''))

            svg += '<g ' + self._Selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>\n'
            svg += ''.join (reversed (bijdragen))
            svg += '</g>'

        svg += 'Deze browser ondersteunt geen SVG\n</svg>'
        return svg

    def _MaakGeldigheidDiagram (self):
        # Bepaal de rijen voor juridischWerkendOp
        juridischWerkendVanaf_Y = { t.JuridischWerkendVanaf : 0 for t in  self._CompleteToestanden.Toestanden}
        svgHoogte = ((2 * len(juridischWerkendVanaf_Y) + 1) * Weergave_Tijdreizen._SvgRijHoogte) / 2
        startY = svgHoogte - Weergave_Tijdreizen._SvgRijHoogte / 2
        y = startY
        for jwv in sorted (juridischWerkendVanaf_Y.keys ()):
            juridischWerkendVanaf_Y[jwv] = y
            y -= Weergave_Tijdreizen._SvgRijHoogte

        # Bepaal de kolommen voor geldigOp
        geldigVanaf_X = { t.GeldigVanaf : 0 for t in  self._CompleteToestanden.Toestanden}
        svgBreedte = ((2 * len(geldigVanaf_X) + 3) * Weergave_Tijdreizen._SvgKolomBreedte) / 2
        startX = Weergave_Tijdreizen._SvgKolomBreedte / 2
        x = startX
        for bekendOp in sorted (geldigVanaf_X.keys ()):
            geldigVanaf_X[bekendOp] = x
            x +=  Weergave_Tijdreizen._SvgKolomBreedte

        svg = '<svg id="' + self._UniekId + '_jg_svg" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: 100%; height: 100%;" viewBox="0 0 ' + str(svgBreedte) + ' ' + str(svgHoogte) + ' " version="1.1">\n'

        svgFragment = '<rect x="{x}" y="0" width="{w}" height="{y}" class="ct_tr_dr{t}" data-' + self._UniekId + '_ob_g={ob} data-' + self._UniekId + '_tid={tid} data-' + self._UniekId + '_ti={ti}><title>juridischWerkendVanaf={j}, geldigVanaf={g}</title></rect>\n'
        svgFragment += '<path d="M {x} {y} L {x} 0" class="ct_tr_dl{t}" data-' + self._UniekId + '_ob_g="{ob}"/>\n'
        svgFragment += '<path d="M {x} {y} L ' + str(svgBreedte) + ' {y}" class="ct_tr_dl{t}" data-' + self._UniekId + '_ob_g="{ob}"/>\n'
        svgFragment += '<text x="{xt}" y="{yt}" class="ct_tr_dt" data-' + self._UniekId + '_ob_g={ob} data-' + self._UniekId + '_tid={tid} data-' + self._UniekId + '_ti={ti}>{inhoud}</text>\n'

        svgFragment_Uitgewerkt = '<rect x="' + str(startX) + '" y="0" width="' + str(svgBreedte-startX) + '" height="{y}" class="ct_tr_du{t}" data-' + self._UniekId + '_ob_g={ob} data-' + self._UniekId + '_tid={tid} data-' + self._UniekId + '_ti={ti}><title>juridischUitgewerktOp={j}</title></rect>\n'
        svgFragment_Uitgewerkt += '<rect x="{x}" y="0" width="{w}" height="' + str(startY) + '" class="ct_tr_du{t}" data-' + self._UniekId + '_ob_g={ob} data-' + self._UniekId + '_tid={tid} data-' + self._UniekId + '_ti={ti}><title>juridischUitgewerktOp={j}</title></rect>\n'
        svgFragment_Uitgewerkt += '<path d="M {x} {y} L {x} ' + str(startY) + '" class="ct_tr_dl{t}" data-' + self._UniekId + '_ob_g="{ob}"/>\n'
        svgFragment_Uitgewerkt += '<path d="M ' + str(startX) + ' {y} L {x} {y}" class="ct_tr_dl{t}" data-' + self._UniekId + '_ob_g="{ob}"/>\n'
        svgFragment_Uitgewerkt += '<text x="{xt}" y="{yt}" class="ct_tr_dt" data-' + self._UniekId + '_ob_g={ob} data-' + self._UniekId + '_tid={tid} data-' + self._UniekId + '_ti={ti}>{inhoud}</text>\n'

        for uitwisseling in self._InstrumentData.Uitwisselingen:
            svg += '<g ' + self._Selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>\n'

            for toestand in reversed (self._CompleteToestanden.Toestanden):
                if toestand.GemaaktOp > uitwisseling.GemaaktOp or (not toestand.OverschrevenOp is None and toestand.OverschrevenOp <= uitwisseling.GemaaktOp):
                    continue
                ob = self._BeschikbaarheidCombi[toestand.OntvangenOp + ':' + toestand.BekendOp]

                x = geldigVanaf_X[toestand.GeldigVanaf]
                y = juridischWerkendVanaf_Y[toestand.JuridischWerkendVanaf]
                xt = x + (Weergave_Tijdreizen._SvgKolomBreedte/4)
                yt = y - (Weergave_Tijdreizen._SvgRijHoogte/4)
                inhoud = self._CompleteToestanden.ToestandInhoud[toestand.Inhoud]
                if inhoud.IsNietInWerking:
                    inhoud = Weergave_Symbolen.Toestand_Uitgewerkt
                else:
                    symbool = Weergave_Symbolen.ToestandBekendOfOnbekend (inhoud.Instrumentversie)
                    if symbool == Weergave_Symbolen.Toestand_BekendeInhoud:
                        inhoud = '<title>' + inhoud.Instrumentversie + '</title>' + symbool
                    else:
                        inhoud = symbool
                identificatie = self._CompleteToestanden.ToestandIdentificatie[toestand.Identificatie]
                inhoud += ','.join (letter for _, letter in self._InstrumentData.WeergaveData.Branches (identificatie.Inwerkingtredingsdoelen))
                svg += svgFragment.format (x=x, y=y, xt=xt, yt=yt, w=svgBreedte-x, ob=ob, j=toestand.JuridischWerkendVanaf, g=toestand.GeldigVanaf, t = ' uw' if toestand.GemaaktOp == uitwisseling.GemaaktOp else '', ti=toestand.Identificatie, tid=toestand._UniekId, inhoud=inhoud)

            svg += '</g>'

        svg += 'Deze browser ondersteunt geen SVG\n</svg>'
        return svg

    _SvgKolomBreedte = 42
    _SvgRijHoogte = 42
    _BeschikbaarheidVoorGeldigheid = '&#128071;'

