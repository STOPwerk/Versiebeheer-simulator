#======================================================================
#
# Aanmaken van een weergave van de annotaties die bij complete 
# toestanden horen, als onderdeel van de webpagina die alle 
# beschikbare resultaten laat ,zien van het consolidatie proces 
# uit proces_consolideren.
#
#======================================================================

from typing import Annotated
from data_lv_annotatie import Annotatie
from weergave_resultaat_data import InstrumentData
from weergave_symbolen import Weergave_Symbolen
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Weergave_Annotaties
#
#======================================================================
class Weergave_Annotaties ():

    @staticmethod
    def VoegToe (generator : WebpaginaGenerator, instrumentData : InstrumentData):
        """Voeg de module voor complete toestanden met filterfunctionaliteit toe aan de pagina met resultaten.
        
        Argumenten:
        generator WebpaginaGenerator  Generator voor de webpagina
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        maker = Weergave_Annotaties (generator.GeefUniekeIndex(), instrumentData)
        maker._MaakTijdreisOverzicht ()

        einde = generator.StartSectie ('<h3>Actuele toestanden en annotaties</h3>', True)

        einde_t = generator.StartToelichting ("Toelichting op het omgaan met annotaties")
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('<table><tr><td>')

        generator.VoegHtmlToe ('<table><tr><td>') # Toestanden en legenda onder elkaar
        generator.VoegHtmlToe (maker._MaakToestandenHtml ())
        generator.VoegHtmlToe ('</td></tr><tr><td>')

        einde_t = generator.StartToelichting ("Legenda")
        generator.VoegHtmlToe ('<table><tr><td>')
        # generator.VoegHtmlToe (maker._MaakAnnotatienummersHtml ())
        generator.VoegHtmlToe (maker._MaakDoelenHtml ())
        generator.VoegHtmlToe ('</td><td>')
        # generator.VoegHtmlToe (maker._MaakBepalingHtml ())
        generator.VoegHtmlToe (maker._MaakLegendaHtml ())
        generator.VoegHtmlToe ('</td></tr></table>')
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('</td></tr></table>')

        generator.VoegHtmlToe ('</td><td>') # Ernaast: toelichtingen

        generator.VoegHtmlToe (maker._MaakTijdijnSelector ())
        einde_t = generator.StartToelichting ("Toelichting op een geselecteerde tijdreis")
        generator.VoegHtmlToe (maker._MaakToelichtingenHtml ())
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('</td></tr></table>')

        generator.VoegHtmlToe (einde)
        generator.LeesCssTemplate ('')
        generator.VoegSlotScriptToe (generator.LeesJSTemplate ('', False).replace ('DIAGRAM_ID', maker.DiagramId))

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
    def __init__ (self, diagram_id : int, instrumentData : InstrumentData):
        """Maak de weergave-maker aan.
        
        Argumenten:

        diagram_id int  Uniek nummer om kopieën van dit fragment in de pagina te onderscheiden
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        self.DiagramId = 'at_a_' + str(diagram_id)
        self._InstrumentData = instrumentData
        self._Selector = Weergave_Uitwisselingselector (self._InstrumentData.WeergaveData.Scenario)
        self._Annotaties = list (sorted ([a for a in self._InstrumentData.WeergaveData.Scenario.Annotaties if a.WorkId == self._InstrumentData.WorkId], key = lambda a:a.Naam))
        self._Synchronisatie = set ([a.Synchronisatie for a in self._Annotaties])
        self._ActueleToestandenMetAnnotarties = self._InstrumentData.WeergaveData.Scenario.GeconsolideerdeInstrument (self._InstrumentData.WorkId).Annotaties
        self._Tabelrijen = [] # Alle rijen in de tabel met toestanden, index 0 = bovenste rij
        self._Tabelkolommen = [] # Alle kolommen in de tabel met toestanden, index 0 = linker kolom

#----------------------------------------------------------------------
#
# Legenda en selectors
#
#----------------------------------------------------------------------
    def _MaakAnnotatienummersHtml (self):
        html = '<table><tr><th>Nummer</th><th>Annotatie</th><tr></tr>'
        for idx, a in enumerate (self._Annotaties):
            html += '<tr><th>' + str(idx+1) + '</th><td>' + a.Naam + '</td></tr>'
        html += '</table>'
        return html

    def _MaakDoelenHtml (self):
        html = ''
        for uitwisseling in reversed (self._InstrumentData.Uitwisselingen):
            if hasattr (uitwisseling, 'DoelenCompleteToestanden'):
                html += '<table' + self._Selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>\n'
                html += '<tr><th>Letter</th><th>Doel</th></tr>\n'
                for doel, branchId in self._InstrumentData.WeergaveData.Branches (uitwisseling.DoelenCompleteToestanden):
                    html += '<tr><td>' + branchId + '</td><td>' + str(doel) + '</td></tr>'
                html += '</table>'
        return html

    def _MaakBepalingHtml (self):
        
        html = '<table><tr><th colspan="2">Wijze van synchronisatie</th></tr>'
        if Annotatie._Synchronisatie_Versiebeheer in self._Synchronisatie:
            html += '<tr><th>' + Weergave_Annotaties._Bepaling_P + '</th><td>' + Weergave_Annotaties._Bepaling_P_Toelichting + '</td></tr>'
        if Annotatie._Synchronisatie_Toestand in self._Synchronisatie:
            html += '<tr><th>' + Weergave_Annotaties._Bepaling_T + '</th><td>' + Weergave_Annotaties._Bepaling_T_Toelichting + '</td></tr>'
        if Annotatie._Synchronisatie_Doel in self._Synchronisatie:
            html += '<tr><th>' + Weergave_Annotaties._Bepaling_W + '</th><td>' + Weergave_Annotaties._Bepaling_W_Toelichting + '</td></tr>'
        html += '</table>'
        return html

    _Bepaling_P = "P"
    _Bepaling_P_Toelichting = "Instrumentversie als proefversie"
    _Bepaling_T = "T"
    _Bepaling_T_Toelichting = "Toestand geïdentificeerd via inwerkingtredingsdoelen"
    _Bepaling_W = "W"
    _Bepaling_W_Toelichting = "Wijzigingsproject geïdentificeerd met doel"

    def _MaakLegendaHtml (self):
        
        html = '<table><tr><th colspan="2">Symbolen</th></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Toestand_BekendeInhoud + '</td><td>Bekende inhoud</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Toestand_OnbekendeInhoud + '</td><td>Onbekende inhoud</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Annotatie_Uitwisseling + '</td><td>Annotatie uitgewisseld</td></tr>'
        #html += '<tr><td>' + Weergave_Symbolen.Annotatie_BekendeVersie + '</td><td>Bekende annotatieversies</td></tr>'
        html += '<tr><td>#</td><td>Bekende annotatieversies</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Annotatie_MeerdereVersies + '</td><td>Meerdere annotatieversies</td></tr>'
        html += '<tr><td>' + Weergave_Symbolen.Annotatie_OnbekendeVersie + '</td><td>Onbekende annotatieversie</td></tr>'
        html += '<tr><td class="at_a_t">#</td><td>Deze uitwisseling</td></tr>'
        html += '<tr><td class="at_a_oud">#</td><td>Eerdere uitwisselingen</td></tr>'
        html += '<tr><td class="at_a_sel_tl">#</td><td>Geselecteerde tijdlijn</td></tr>'
        html += '<tr><td class="at_a_sel_tr">#</td><td>Geselecteerde tijdreis</td></tr>'
        html += '</table>'
        return html

    def _MaakTijdijnSelector (self):
        html = '<p>Toon tijdlijn voor <input type="radio" name="' + self.DiagramId + '_selector" value="-1" id="' + self.DiagramId + '_selector_alles"><label for="' + self.DiagramId + '_selector_alles">alles</label>, '
        html += '<input type="radio" name="' + self.DiagramId + '_selector" value="0" id="' + self.DiagramId + '_selector_at"><label for="' + self.DiagramId + '_selector_at">actuele toestanden</label> of: '
        html += '<table><tr><th>Nummer</th><th>Annotatie</th>'
        if Annotatie._Synchronisatie_Versiebeheer in self._Synchronisatie:
            html += '<th>' + Weergave_Annotaties._Bepaling_P + '</th>'
        if Annotatie._Synchronisatie_Toestand in self._Synchronisatie:
            html += '<th>' + Weergave_Annotaties._Bepaling_T + '</th>'
        if Annotatie._Synchronisatie_Doel in self._Synchronisatie:
            html += '<th>' + Weergave_Annotaties._Bepaling_W + '</th>'
        html += '<tr>'
        kolom = 0
        for idx, a in enumerate (self._Annotaties):
            html += '<tr><th>' + str(idx+1) + '</th><td>' + a.Naam + '</td>'
            for s in [Annotatie._Synchronisatie_Versiebeheer, Annotatie._Synchronisatie_Toestand, Annotatie._Synchronisatie_Doel]:
                if a.Synchronisatie == s:
                    kolom += 1
                    html += '<td><input type="radio" name="' + self.DiagramId + '_selector" value="' + str(kolom) + '"></td>'
                elif s in self._Synchronisatie:
                    html += '<td></td>'
            html += '</tr>'
        html += '</table>'
        html += self._MaakBepalingHtml ()
        html += '</p>'
        return html

#----------------------------------------------------------------------
#
# Toestanen en annotaties
#
#----------------------------------------------------------------------

    def _MaakToestandenHtml (self):
        html = '<table class="at_a_toestanden"><tr><th>uitgewisseld op</th><th>juridischWerkendVanaf</th>'
        for kolom in self._Tabelkolommen:
            css = ' class="s2"'
            html += '<th' + (' colspan="' + str(kolom.Subkolommen) + '"' if kolom.Subkolommen > 1 else '') + css + '>' + kolom.KolomTitel + "</th>"
        html += '</tr>'

        for uitwisseling in reversed (self._InstrumentData.Uitwisselingen):
            uitwisselingHtml = ''
            for rij in self._Tabelrijen:
                if  uitwisseling.GemaaktOp <= rij.UitgewisseldOp and (uitwisseling.VolgendeGemaaktOp is None or rij.UitgewisseldOp < uitwisseling.VolgendeGemaaktOp):
                    data_tijdlijnen = ' data-' + self.DiagramId + '_k="|' + '|'.join (str(i) for i in rij.Elementen.keys ()) + '|" data-' + self.DiagramId + '_tr="' + rij.Index + '" data-' + self.DiagramId + '_r="|' + rij.Index + '|"'
                    uitwisselingHtml += '<tr {attr}><td' + data_tijdlijnen + '>' + rij.UitgewisseldOp + '</td><td' + data_tijdlijnen + '>' + rij.JuridischWerkendVanaf + '</td>'
                    for idx, kolom in enumerate (self._Tabelkolommen):
                        css = ' class="s2"'
                        elt = rij.Elementen.get (idx)
                        if elt is None:
                            uitwisselingHtml += '<td' + (' colspan="' + str(kolom.Subkolommen) + '"' if kolom.Subkolommen > 1 else '') + css + '></td>'
                        else:
                            attr = ' data-' + self.DiagramId + '_k="|' + str(idx) + '|" data-' + self.DiagramId + '_r="|' + '|'.join (str(i) for i in elt.InTijdreisVoorRij) + '|"'
                            uitwisselingHtml += '<td' + css + attr + '>' + elt.Tekst + '</td>'
                            if kolom.Subkolommen > 1:
                                for tekst in elt.ExtraSubkolommen:
                                    uitwisselingHtml += '<td' + attr + '>' + tekst + '</td>'
                    uitwisselingHtml += '</tr>'
            html += uitwisselingHtml.format (attr = 'class="at_a_t"' + self._Selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp))
            if not uitwisseling.VolgendeGemaaktOp is None:
                html += uitwisselingHtml.format (attr = 'class="at_a_oud"' + self._Selector.AttributenToonIn (uitwisseling.VolgendeGemaaktOp, None))

        html += '</table>'

        return html

    def _MaakToelichtingenHtml (self):
        html = ''
        for rij in self._Tabelrijen:
            html += '<table data-' + self.DiagramId + '_rt="' + str(rij.Index) + '" class="at_a_toelichting" style="display: none">\n'

            for idx, kolom in enumerate (self._Tabelkolommen):
                elt = rij.Elementen.get (idx)
                if elt is None:
                    elt = rij.Tijdreiselementen.get (idx)
                    if elt is None:
                        continue
                if not elt.ActueleToestand is None:
                    html += '<tr><th>Toestand</th><td colspan="2">' + elt.ActueleToestand.ExpressionId + '</td></tr>'
                    html += '<tr><td rowspan="' + str(len (elt.ActueleToestand.Inwerkingtredingsdoelen)) + '">Inwerkingtredingsdoelen</td>' + '<tr>'.join ('<td>' + self._InstrumentData.WeergaveData.DoelLetter (doel) + '</td><td>' + str(doel) + '</td></tr>\n' for doel in elt.ActueleToestand.Inwerkingtredingsdoelen)
                    html += '<tr><td>Instrumentversie</td><td colspan="2">' + (elt.ActueleToestand.Instrumentversie if elt.ActueleToestand.Instrumentversie else 'Onbekend') + '</td></tr>'

                else:
                    html += '<tr class="at_a_toelichting_sep"><th>Annotatie</th><td>' + str(self._Annotaties.index (kolom.Annotatie)+1) + '</td><td>' + kolom.Annotatie.Naam + '</td></tr>'
                    html += '<tr><td></td><th colspan="2">' + kolom.Titel + '</th></tr>'
                    if not elt.AnnotatieVersie.Uitleg is None:
                        html += '<tr><td></td><td>' + elt.Tekst + '</td><td>' + elt.AnnotatieVersie.Uitleg + '</td></tr>'
                    if not elt.AnnotatieVersie.Versies is None:
                        for versie in elt.AnnotatieVersie.Versies:
                            html += '<tr><td rowspan="' + str(len (versie.Doelen)) + '">Versie voor</td>' + '<tr>'.join ('<td>' + self._InstrumentData.WeergaveData.DoelLetter (doel) + '</td><td>' + str(doel) + '</td></tr>\n' for doel in versie.Doelen)
                            html += '<tr><td>Uitgewisseld op</td><td colspan="2">' + versie.Tijdstip () + ' (#' + str(versie._Nummer) + ')</td></tr>'
                            html += '<tr><td></td><td colspan="2">' + versie._Beschrijving + '</td></tr>'

            html += '</table>\n'

        return html

    def _MaakTijdreisOverzicht (self):
        """Maak het overzicht van alle tijdstippen en de uitkomsten van alle tijdreizen"""

        # Maak eerst alle rijen van de tabel aan
        tabelrijen = {}
        for toestand in self._ActueleToestandenMetAnnotarties.ActueleToestanden.Toestanden:
            actueleToestand = self._ActueleToestandenMetAnnotarties.ActueleToestanden.ToestandInhoud[toestand.Inhoud]
            elt = _TabelElement ()
            elt.Tekst = ' '.join (letter for _, letter in self._InstrumentData.WeergaveData.Branches (actueleToestand.Inwerkingtredingsdoelen))
            elt.ExtraSubkolommen = [ Weergave_Symbolen.Toestand_OnbekendeInhoud if actueleToestand.Instrumentversie is None else Weergave_Symbolen.Toestand_BekendeInhoud ]
            elt.ActueleToestand = actueleToestand
            _TabelRij.VoegToe (tabelrijen, toestand).Elementen[len(self._Tabelkolommen)] = elt
        self._Tabelkolommen.append (_TabelKolom ("Toestand", "Actuele toestand", 2))

        def _AnnotatieToestanden (annotatie, tijdlijn, tabeltitel, titel):
            """Voeg een tijdlijn voor een van de bepalingen van een annotatie toe"""
            if not tijdlijn is None:
                for toestand in tijdlijn.Toestanden:
                    versie = tijdlijn.ToestandInhoud[toestand.Inhoud]
                    elt = _TabelElement ()
                    if versie.Versies is None:
                        elt.Tekst = Weergave_Symbolen.Annotatie_OnbekendeVersie
                    elif len (versie.Versies) == 1:
                        elt.Tekst = '#' + str(versie.Versies[0]._Nummer)
                    else:
                        elt.Tekst = Weergave_Symbolen.Annotatie_MeerdereVersies
                    elt.AnnotatieVersie = versie
                    _TabelRij.VoegToe (tabelrijen, toestand).Elementen[len(self._Tabelkolommen)] = elt
                kolom = _TabelKolom (tabeltitel, titel)
                kolom.Annotatie = annotatie
                self._Tabelkolommen.append (kolom)

        for idx, annotatie in enumerate (self._Annotaties):
            if annotatie.Synchronisatie == Annotatie._Synchronisatie_Versiebeheer:
                _AnnotatieToestanden (annotatie, self._ActueleToestandenMetAnnotarties.UitProefversies.get (annotatie), str(idx+1) + ' ' + Weergave_Annotaties._Bepaling_P, Weergave_Annotaties._Bepaling_P_Toelichting)
            elif annotatie.Synchronisatie == Annotatie._Synchronisatie_Toestand:
                _AnnotatieToestanden (annotatie, self._ActueleToestandenMetAnnotarties.VoorToestandViaDoelen.get (annotatie), str(idx+1) + ' ' + Weergave_Annotaties._Bepaling_T, Weergave_Annotaties._Bepaling_T_Toelichting)
            elif annotatie.Synchronisatie == Annotatie._Synchronisatie_Doel:
                _AnnotatieToestanden (annotatie, self._ActueleToestandenMetAnnotarties.VoorDoel.get (annotatie), str(idx+1) + ' ' + Weergave_Annotaties._Bepaling_W, Weergave_Annotaties._Bepaling_W_Toelichting)

        # Sorteer de rijen
        for tijdstip in reversed (sorted (tabelrijen.keys ())):
            for jwv in reversed (sorted (tabelrijen[tijdstip].keys ())):
                rij = tabelrijen[tijdstip][jwv]
                rij.Index = str(len (self._Tabelrijen))
                self._Tabelrijen.append (rij)

        # Bepaal voor elke kolom welke waarde in de tijdreis voor deze rij hoort
        for idxRij, rij in enumerate (self._Tabelrijen):
            for kolom, _ in enumerate (self._Tabelkolommen):
                elt = rij.Elementen.get (kolom)
                if not elt is None:
                    elt.InTijdreisVoorRij.append (rij.Index)
                else:
                    # Voer een tijdreis uit naar de eerdere elementen in de tijdlijn
                    index = idxRij
                    while index < len (self._Tabelrijen)-1:
                        index += 1
                        if self._Tabelrijen[index].JuridischWerkendVanaf <= rij.JuridischWerkendVanaf:
                            # De waarde op deze rij zou gebruikt kunnen worden
                            tijdreisElt = self._Tabelrijen[index].Elementen.get (kolom)
                            if not tijdreisElt is None:
                                # Er is een waarde gegeven
                                tijdreisElt.InTijdreisVoorRij.append (rij.Index)
                                rij.Tijdreiselementen[kolom] = tijdreisElt
                                break


class _TabelKolom:

    def __init__ (self, kolomTitel, titel, subkolommen = 1):
        # Titel van de kolom in de tabel
        self.KolomTitel = kolomTitel
        # Titel van de kolom in de toelichting
        self.Titel = titel
        # Aantal subkolommen waarin de kolom is opgedeeld
        self.Subkolommen = subkolommen
        # Annotatie, als de kolom voor een annotatie is gemaakt
        self.Annotatie = None

class _TabelRij:
    def __init__(self, uitgewisseldOp, juridischWerkendVanaf):
        """Maak een tijdstip aan waarop er iets gebeurt met een toestand of een annotatieversie"""
        self.UitgewisseldOp = uitgewisseldOp
        self.JuridischWerkendVanaf = juridischWerkendVanaf
        # Index van de rij
        self.Index = None
        # Informatie over een toestand of annotatie
        # key = kolom, value = instantie van _WaardeOpTijdstip
        self.Elementen = {}
        # Als er voor de kolom geen eleemnt is: het element dat via tijdreizen gevonden wordt.
        # key = kolom, value = instantie van _WaardeOpTijdstip
        self.Tijdreiselementen = {}

    @staticmethod
    def VoegToe (tabelrijen, toestand):
        """Haal het eerder gemaakte _Tijdstip uit de verzameling, of maak het aan en voeg het toe als het nog niet bestaat."""
        subrij = tabelrijen.get (toestand.Tijdstip)
        if subrij is None:
            tabelrijen[toestand.Tijdstip] = subrij = {}
        resultaat = subrij.get (toestand.JuridischWerkendVanaf)
        if resultaat is None:
            subrij[toestand.JuridischWerkendVanaf] = resultaat = _TabelRij (toestand.Tijdstip, toestand.JuridischWerkendVanaf)
        return resultaat

class _TabelElement:
    def __init__ (self):
        # Tekst in de kolom
        self.Tekst = ''
        # Als de kolom in subkolommen is opgedeeld, dan de tekst voor de tweede e.v. subkolom
        self.ExtraSubkolommen = None
        # Actuele toestand die door dit element gerepresenteerd wordt
        # Instantie van ToestandActueel
        self.ActueleToestand = None
        # Annotatieversie die door dit element gerepresenteerd wordt.
        # Instantie van ActueleAnnotatieVersie
        self.AnnotatieVersie = None
        # Lijst met elke Index van de rij waarvoor dit element het antwoord
        # is op de tijdreis met uitgewisseldOp,jwv gelijk aan de tijdstempwls van de rij
        self.InTijdreisVoorRij = []
