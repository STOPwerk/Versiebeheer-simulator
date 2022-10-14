#======================================================================
#
# Beschrijven van de manier waarop een toestand is bepaald.
# Het betreft een toelichting op de stappen die deze applicatie
# gezet heeft om te komen tot de toestand zoals beschreven.
#
#======================================================================

from data_lv_versiebeheerinformatie import Instrument
from stop_toestand import Toestandidentificatie
from weergave_data_toestanden import ConsolidatieprocesInformatie
from weergave_resultaat_data import InstrumentData, InstrumentUitwisseling
from weergave_stopmodule import Weergave_STOPModule
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_versiebeheer_diagram import DiagramGenerator, DiagramGeneratorOpties
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Weergave_Toestandbepaling
#
#======================================================================
class Weergave_Toestandbepaling ():

    @staticmethod
    def VoegActueleToestandenToe (generator : WebpaginaGenerator, instrumentData : InstrumentData):
        """Licht de bepaling van de actuele toestanden toe
        
        Argumenten:
        generator WebpaginaGenerator  Generator voro de webpagina met resultaten
        instrumentData InstrumentUitwisseling Weer te geven consolidatie informatie voor het instrument
        """
        uniekId = 'atb_' + str(generator.GeefUniekeIndex()) # string  Korte unieke string die gebruikt wordt om deze weergave te onderscheiden van andere
        selector = Weergave_Uitwisselingselector (instrumentData.WeergaveData.Scenario)
        uitlegStappen = { }

        # Maak de toelichtingen
        einde = generator.StartSectie ('Bepaling van de actuele toestanden', True)

        einde_t = generator.StartToelichting ('Toelichting op de inhoud van deze sectie')
        generator.LeesHtmlTemplate ('help_actueletoestand')
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('<div class="' + uniekId + '" style="display: none;">')

        einde_t = generator.StartToelichting ("1 - 2: Toestanden op basis van doelen en tijdstempels")
        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.ActueleToestanden is None:
                generator.VoegHtmlToe ('<div' + selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>')
                maker = Weergave_Toestandbepaling (generator, uniekId, uitwisseling, False, uitlegStappen)

                for toestand  in uitwisseling.ActueleToestanden.Toestanden:
                     generator.VoegHtmlToe ('<div data-' + uniekId + '_ti="' + str(toestand.Identificatie) + '">')
                     maker._VindToestandenHtml (toestand, toestand, toestand, toestand._Consolidatieproces._Uitleg, toestand._Consolidatieproces)
                     generator.VoegHtmlToe ('</div>')

                generator.VoegHtmlToe ('</div>')
        generator.VoegHtmlToe (einde_t)

        einde_t = generator.StartToelichting ("3 - 4: Bepaal kandidaat-instrumentversie")
        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.ActueleToestanden is None:
                generator.VoegHtmlToe ('<div' + selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>')
                maker = Weergave_Toestandbepaling (generator, uniekId, uitwisseling, False, uitlegStappen)

                for toestand  in uitwisseling.ActueleToestanden.Toestanden:
                     generator.VoegHtmlToe ('<div data-' + uniekId + '_ti="' + str(toestand.Identificatie) + '">')
                     maker._BepaalInhoudHtml (toestand, toestand._Consolidatieproces)
                     generator.VoegHtmlToe ('</div>')

                generator.VoegHtmlToe ('</div>')
        generator.VoegHtmlToe (einde_t)

        einde_t = generator.StartToelichting ("5 - 6: Validatie kandidaat-instrumentversie")
        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.ActueleToestanden is None:
                generator.VoegHtmlToe ('<div' + selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>')
                maker = Weergave_Toestandbepaling (generator, uniekId, uitwisseling, False, uitlegStappen)

                for toestand  in uitwisseling.ActueleToestanden.Toestanden:
                     generator.VoegHtmlToe ('<div data-' + uniekId + '_ti="' + str(toestand.Identificatie) + '">')
                     maker._ValideerInhoudHtml (toestand._Consolidatieproces, True)
                     generator.VoegHtmlToe ('</div>')

                generator.VoegHtmlToe ('</div>')
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('</div>')
        generator.VoegHtmlToe (einde)
        generator.VoegSlotScriptToe (generator.LeesJSTemplate ('actueletoestanden', False).replace ("UNIEK_ID", uniekId).replace ("WORK_ID", instrumentData.WorkId))

    @staticmethod
    def VoegCompleteToestandenToe (generator : WebpaginaGenerator, instrument : Instrument, instrumentData : InstrumentData):
        """Licht de bepaling van de complete toestanden toe
        
        Argumenten:
        uniekId string  Korte unieke string die gebruikt wordt om deze weergave te onderscheiden van andere
        instrument Instrument Weer te geven versiebeheerinformatie
        instrumentData InstrumentUitwisseling Weer te geven consolidatie informatie voor het instrument
        """
        # Cache voor uitleg over stappen
        uitlegStappen = { }
        uniekId = 'ctb_' + str(generator.GeefUniekeIndex()) # string  Korte unieke string die gebruikt wordt om deze weergave te onderscheiden van andere

        einde = generator.StartSectie ('Bepaling van de complete toestand', True)

        einde_t = generator.StartToelichting ("Complete toestand")
        generator.VoegHtmlToe ('<p>Hier wordt de bepaling van een complete toestand beschreven. Selecteer de te beschrijven toestand door een actuele toestand te selecteren of een toestand uit een van de overzichten van complete toestanden.</p>')
        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.CompleteToestanden is None:
                for toestand  in uitwisseling.CompleteToestanden.Toestanden:
                    if toestand.GemaaktOp != uitwisseling.GemaaktOp:
                        continue

                    generator.VoegHtmlToe ('<div data-' + uniekId + '_tid="' + str(toestand.UniekId) + '">')
                    generator.VoegHtmlToe ('<p>Dit is een beschrijving van de bepaling van de complete toestand die in het tijdreisoverzicht staat vermeld als::<table>')
                    generator.VoegHtmlToe ('<tr><td>identificatie</td><td>#' + str(toestand.Identificatie) + '</td></tr>')
                    generator.VoegHtmlToe ('<tr><td>inhoud</td><td>' + ('-' if toestand.Inhoud is None else '#' + str(toestand.Inhoud) + '') + '</td></tr>')
                    generator.VoegHtmlToe ('<tr><td>ontvangenOp</td><td>' + toestand.OntvangenOp + '</td></tr>')
                    generator.VoegHtmlToe ('<tr><td>bekendOp</td><td>' + toestand.BekendOp + '</td></tr>')
                    generator.VoegHtmlToe ('<tr><td>juridischWerkendVanaf</td><td>' + toestand.JuridischWerkendVanaf + '</td></tr>')
                    generator.VoegHtmlToe ('<tr><td>geldigVanaf</td><td>' + toestand.GeldigVanaf + '</td></tr>')
                    generator.VoegHtmlToe ('</table></p>')

                    generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde_t)
        generator.VoegHtmlToe ('<div class="' + uniekId + '" style="display: none;">')

        einde_t = generator.StartToelichting ("1 - 2: Toestanden op basis van doelen en tijdstempels")
        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.CompleteToestanden is None:
                for toestand  in uitwisseling.CompleteToestanden.Toestanden:
                    if toestand.GemaaktOp != uitwisseling.GemaaktOp:
                        continue
                    identificatie = uitwisseling.CompleteToestanden.ToestandIdentificatie[toestand.Identificatie]
                    inhoud = uitwisseling.CompleteToestanden.ToestandInhoud[toestand.Inhoud]
                    maker = Weergave_Toestandbepaling (generator, uniekId, uitwisseling, True, uitlegStappen)

                    generator.VoegHtmlToe ('<div data-' + uniekId + '_tid="' + str(toestand.UniekId) + '">')
                    maker._VindToestandenHtml (identificatie, inhoud, toestand, identificatie._Uitleg, inhoud._Consolidatieproces)
                    generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde_t)

        einde_t = generator.StartToelichting ("3 - 4: Bepaal kandidaat-instrumentversie")
        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.CompleteToestanden is None:
                for toestand  in uitwisseling.CompleteToestanden.Toestanden:
                    if toestand.GemaaktOp != uitwisseling.GemaaktOp:
                        continue
                    inhoud = uitwisseling.CompleteToestanden.ToestandInhoud[toestand.Inhoud]
                    if inhoud.IsNietInWerking:
                        continue
                    identificatie = uitwisseling.CompleteToestanden.ToestandIdentificatie[toestand.Identificatie]
                    maker = Weergave_Toestandbepaling (generator, uniekId, uitwisseling, True, uitlegStappen)

                    generator.VoegHtmlToe ('<div data-' + uniekId + '_tid="' + str(toestand.UniekId) + '">')
                    maker._BepaalInhoudHtml (inhoud, inhoud._Consolidatieproces)
                    generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde_t)

        diagramInfo = {} # key = UniekId, value = (sectieId,  _OnvolledigeVersieDiagram, Diagram)

        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.CompleteToestanden is None:
                for toestand  in uitwisseling.CompleteToestanden.Toestanden:
                    if toestand.GemaaktOp != uitwisseling.GemaaktOp:
                        continue
                    inhoud = uitwisseling.CompleteToestanden.ToestandInhoud[toestand.Inhoud]
                    if inhoud.IsNietInWerking:
                        continue
                    identificatie = uitwisseling.CompleteToestanden.ToestandIdentificatie[toestand.Identificatie]
                    if not inhoud.OnvolledigeVersies is None:
                        generator.VoegHtmlToe ('<div data-' + uniekId + '_tid="' + str(toestand.UniekId) + '" class="ctb_versies">')
                        generator.VoegHtmlToe ('<p>Een groot deel van de resterende analyse is uitgevoerd voor zowel de toestand als voor bekende instrumentversies. Laat de resultaten zien voor:<ul>')

                        sectieId = uniekId + '_' + str(toestand.UniekId)

                        diagramOpties = _OnvolledigeVersieDiagram (sectieId, instrument, uitwisseling, toestand.BekendOp)
                        diagram = DiagramGenerator.VoerUit (diagramOpties)
                        diagramInfo[toestand.UniekId] = (sectieId, diagramOpties, diagram)

                        generator.VoegHtmlToe ('<li>' + diagramOpties.NogTeConsoliderenToggle (identificatie, inhoud._Consolidatieproces, '0', True) + 'Toestand</li>')
                        for idx, versie in enumerate (inhoud.OnvolledigeVersies):
                            generator.VoegHtmlToe ('<li>' + diagramOpties.NogTeConsoliderenToggle (identificatie, versie, str(idx+1), True) + versie.Instrumentversie + '</li>')
                        generator.VoegHtmlToe ('</ul></p>')
                        
                        generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe ('<table><tr><td class="ctb_diagram_td">')

        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.CompleteToestanden is None:
                for toestand  in uitwisseling.CompleteToestanden.Toestanden:
                    if toestand.GemaaktOp != uitwisseling.GemaaktOp:
                        continue
                    inhoud = uitwisseling.CompleteToestanden.ToestandInhoud[toestand.Inhoud]
                    if not inhoud.OnvolledigeVersies is None:
                        sectieId, diagramOpties, diagram = diagramInfo[toestand.UniekId]

                        generator.VoegHtmlToe ('<div data-' + uniekId + '_tid="' + str(toestand.UniekId) + '">')

                        generator.VoegHtmlToe ('<div class="ctb_diagram">' + diagram.SVG + '</div>')
                        diagram.VoegOndersteuningToe (generator)

                        generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe ('</td><td rowspan="2">')

        einde_t = generator.StartToelichting ("5 - 7: Validatie kandidaat-instrumentversie en alternatieve versies")
        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.CompleteToestanden is None:
                for toestand  in uitwisseling.CompleteToestanden.Toestanden:
                    if toestand.GemaaktOp != uitwisseling.GemaaktOp:
                        continue
                    inhoud = uitwisseling.CompleteToestanden.ToestandInhoud[toestand.Inhoud]
                    if inhoud.IsNietInWerking:
                        continue
                    identificatie = uitwisseling.CompleteToestanden.ToestandIdentificatie[toestand.Identificatie]
                    maker = Weergave_Toestandbepaling (generator, uniekId, uitwisseling, True, uitlegStappen)
                    generator.VoegHtmlToe ('<div data-' + uniekId + '_tid="' + str(toestand.UniekId) + '">')
                    if inhoud.OnvolledigeVersies is None:
                        generator.VoegHtmlToe (maker._ValideerInhoudHtml (inhoud._Consolidatieproces, True))
                    else:
                        sectieId, diagramOpties, diagram = diagramInfo[toestand.UniekId]
                        generator.VoegHtmlToe ('<div data-' + sectieId + '="0">')
                        maker._ValideerInhoudHtml (inhoud._Consolidatieproces, True)
                        maker._BepaalAlternatieven (inhoud._Consolidatieproces)
                        generator.VoegHtmlToe ('</div>')

                        for idx, versie in enumerate (inhoud.OnvolledigeVersies):
                            generator.VoegHtmlToe ('<div data-' + sectieId + '="' + str(idx+1) + '" style="display:none;">')
                            maker._ValideerInhoudHtml (versie, False)
                            maker._BepaalPublicaties (versie)
                            generator.VoegHtmlToe ('</div>')
                    generator.VoegHtmlToe ('</div>')
    
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('</td></tr><tr><td>')

        einde_t = generator.StartToelichting ("Legenda")

        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.CompleteToestanden is None:
                for toestand  in uitwisseling.CompleteToestanden.Toestanden:
                    if toestand.GemaaktOp != uitwisseling.GemaaktOp:
                        continue
                    inhoud = uitwisseling.CompleteToestanden.ToestandInhoud[toestand.Inhoud]
                    if inhoud.IsNietInWerking:
                        continue
                    identificatie = uitwisseling.CompleteToestanden.ToestandIdentificatie[toestand.Identificatie]
                    if not inhoud.OnvolledigeVersies is None:
                        sectieId, diagramOpties, diagram = diagramInfo[toestand.UniekId]

                        generator.VoegHtmlToe ('<div data-' + uniekId + '_tid="' + str(toestand.UniekId) + '">')

                        generator.VoegHtmlToe ('<div data-' + sectieId + '="0">')
                        generator.VoegHtmlToe (diagramOpties.NogTeConsoliderenInformatie (identificatie, inhoud._Consolidatieproces, '0'))
                        generator.VoegHtmlToe ('</div>')

                        for idx, versie in enumerate (inhoud.OnvolledigeVersies):
                            generator.VoegHtmlToe ('<div data-' + sectieId + '="' + str(idx+1) + '" style="display:none;">')
                            generator.VoegHtmlToe (diagramOpties.NogTeConsoliderenInformatie (identificatie, versie, str(idx+1)))
                            generator.VoegHtmlToe ('</div>')

                        generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe ('</td></tr></table>')
        generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde)
        generator.LeesCssTemplate ('completetoestanden')
        generator.VoegSlotScriptToe (generator.LeesJSTemplate ('completetoestanden', False).replace ("UNIEK_ID", uniekId).replace ("WORK_ID", instrumentData.WorkId))

#----------------------------------------------------------------------
#
# Stappen uit de consolidatiebepaling
#
#----------------------------------------------------------------------
    BepaalToestanden = 1 # Bepaal de toestanden op basis van de tijdstempels en doelen
    Validatie_GeenToestandNaIntrekking = 2 # Een nieuwe toestand mag niet juridisch werkend worden na een intrekking
    BepaalKandidaatInstrumentversie = 3 # Zoek de kandidaat-instrumentversie bij de toestand op basis van de iwt-doelen
    Validatie_DezelfdeVersieVoorAlleDoelen = 4 # Bij meerdere iwt-doelen: is voor alle dezelfde versie doorgegeven?
    Validatie_LaatsteUitwisselingVoorAlleDoelen = 5 # Zijn voor alle toestand-doelen de laatste uitwisselingen gebruikt?
    Validatie_GeenAnderDoelVerwerktInInstrumentversie = 6 # De instrumentversie mag geen bijdrage van andere doelen hebben dan die uit de toestand
    BepaalAlternatieveVersies = 7 # Zoek alternatieve versies voor de toestand
    BepaalAanvullendePublicaties = 8 # Zoek publicaties bij een alternatieve versie

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
    def __init__ (self, generator : WebpaginaGenerator, uniekId, instrumentData : InstrumentUitwisseling, voorCompleteToestanden : bool, uitlegStappen):
        """Maak de generator aan
        
        Argumenten:
        generator WebpaginaGenerator  Generator voro de webpagina met resultaten
        uniekId string  Korte unieke string die gebruikt wordt om deze weergave te onderscheiden van andere
        instrumentData InstrumentUitwisseling Weer te geven consolidatie informatie voor het instrument
        voorCompleteToestanden bool  Geeft aan of de HTML voor complete toestanden gemaakt wordt. Dee HTML wijkt op sommige plaatsen af.
        uitlegStappen {} Uitleg over de stappen. key = stap, value = html
        """
        self._Generator = generator;
        self._UniekId = uniekId
        self._InstrumentData = instrumentData
        self._WeergaveData = instrumentData.InstrumentData.WeergaveData
        self._VoorCompleteToestanden = voorCompleteToestanden
        self._UitlegStappen = uitlegStappen

    def _VindToestandenHtml (self, identificatie : Toestandidentificatie, inhoud, toestand, uitleg, proces):
        """Maak de beschrijving van het vinden van een enkele toestand
        
        Argumenten:

        identificatie Toestandidentificatie  Identificatie van de toestand
        inhoud ToestandActueel/ToestandCompleet  Inhoud van de toestand, of None na intrekking
        toestand ToestandActueel/Toestand  Geldigheid van de toestand
        uitleg Melding[] Verzameling van meldingen over het vinden van de toestanden
        proces ConsolidatieprocesInformatie  Beschrijving van het proces van de bepaling van de inhoud van de toestand
        """
        html = '<p><b>Stap 1. Bepaal relevante doelen en stel de toestanden samen.</b><br/>'
        if self._VoorCompleteToestanden:
            html += '(Deze stap is uitgevoerd bij de verwerking van uitwisseling ' + identificatie._GemaaktOp + ' toen deze toestand voor het eerst gezien is)<br/>'
        html += 'Voor deze toestand komt het erop neer te bepalen hoe de toestand eruit ziet voor JuridischWerkendVanaf = ' + toestand.JuridischWerkendVanaf + ' en '
        if self._VoorCompleteToestanden:
            html += 'GeldigVanaf = ' + toestand.GeldigVanaf + '. Deze applicatie bepaalt alle toestanden voor elke uitwisseling en bekendOp datum opnieuw. Of een toestand daadwerkelijk aan het overzicht van complete toestanden wordt toegevoegd wordt in de <i>Uitvoering van de applicatie</i> (boven aan de pagina) als detailmelding aangegeven.'
        else:        
            html += 'een GeldigVanaf die rekening houdt met andere doelen die tegelijk juridische werking hebben.'
        html += '</p>'
        self._Generator.VoegHtmlToe (html)
        self._ToonMeldingen (uitleg, Weergave_Toestandbepaling.BepaalToestanden)
        html = '<p>Het resultaat is:<table><tr><td><b>Toestand</b></td><td colspan="2">' + identificatie.ExpressionId + '</td></tr>'
        html += '<tr><td rowspan="' + str(len (identificatie.Inwerkingtredingsdoelen)) + '">Inwerkingtredingsdoelen</td>' + '<tr>'.join ('<td>' + self._WeergaveData.DoelLetter (doel) + '</td><td>' + str(doel) + '</td></tr>' for doel in identificatie.Inwerkingtredingsdoelen)
        html += '<tr><td>Juridisch werkend vanaf</td><td colspan="2">' + toestand.JuridischWerkendVanaf + (' tot ' + toestand.JuridischWerkendTot if hasattr (toestand, 'JuridischWerkendTot') and toestand.JuridischWerkendTot else '') + '</td></tr>'
        if hasattr (toestand, 'GeldigVanaf') and toestand.GeldigVanaf:
            html += '<tr><td>Geldig vanaf</td><td colspan="2">' + toestand.GeldigVanaf + '</td></tr>'
        html += '</table></p>'
        self._Generator.VoegHtmlToe (html)

        if inhoud is None:
            html = '<p>Deze toestand correspondeert met de intrekking van het instrument. Het instrument is vanaf nu juridisch uitgewerkt.</p>'

        else:
            html = '<p>Ook is gevonden dat, naast de wijzigingen die voor de inwerkingtredingsdoelen worden doorgevoegd, ook alle instellingen en wijzigingen opgenomen moeten worden voor:'
            html += '<table><tr><td rowspan="' + str(len (inhoud.Basisversiedoelen)) + '">Doelen eerdere toestanden:</td>' + '<tr>'.join ('<td>' + self._WeergaveData.DoelLetter (doel) + '</td><td>' + str(doel) + '</td></tr>' for doel in inhoud.Basisversiedoelen)
            html += '</table></p>'
            if self._VoorCompleteToestanden:
                html += '<br/>(Deze doelen zijn gevonden bij de verwerking van uitwisseling ' + inhoud._GemaaktOp + ' voor bekendOp = ' + inhoud._BekendOp + ' toen deze inhoud van de toestand voor het eerst gezien is)<br/>'

            html += '<p><b>Stap 2. Geen toestand na een intrekking.</b><br/>Als het instrument wordt ingetrokken, dan mogen er geen toestanden zijn met een juridischWerkendVanaf na de datum van intrekking.</p>'
            self._Generator.VoegHtmlToe (html)
            self._ToonMeldingen (proces._Uitleg, Weergave_Toestandbepaling.Validatie_GeenToestandNaIntrekking)

    def _BepaalInhoudHtml (self, inhoud, proces : ConsolidatieprocesInformatie):
        """Maak de beschrijving van de inhoud van een enkele toestand, tot en met het vinden van de kandidaat-instrumentversie.
        
        Argumenten:

        inhoud ToestandActueel/ToestandCompleet  Inhoud van de toestand
        proces ConsolidatieprocesInformatie  Beschrijving van het proces van de bepaling van de inhoud van de toestand
        """
        self._Generator.VoegHtmlToe (self._UitlegVoorStap ('stap3_4').replace ('<!--VOOR-->', '<br/>(Deze stap is uitgevoerd bij de verwerking van uitwisseling ' + inhoud._GemaaktOp + ' voor bekendOp = ' + inhoud._BekendOp + ' toen deze inhoud van de toestand voor het eerst gezien is)' if self._VoorCompleteToestanden else ''))

        self._Generator.VoegHtmlToe ('<p><b>Stap 3. Bepaal de instrumentversie die de inhoud van de toestand weergeeft.</b><br/>Hiervoor wordt gekeken naar de meest recente uitwisselingen voor de inwerkingtredingdoelen:</p>')

        self._ToonMeldingen (proces._Uitleg, Weergave_Toestandbepaling.BepaalKandidaatInstrumentversie)

        self._Generator.VoegHtmlToe ('<p><b>Stap 4. Is voor alle inwerkingtredingsdoelen dezelfde versie doorgegeven?</b></p>')
        self._ToonMeldingen (proces._Uitleg, Weergave_Toestandbepaling.Validatie_DezelfdeVersieVoorAlleDoelen)
        if proces.KandidaatInstrumentversie is None:
            self._Generator.VoegHtmlToe ('<p>Er is dus geen (eenduidige) kandidaat-instrumentversie. De verdere analyse van de toestand wordt gedaan alsof er al wel een kandidaat-instrumentversie voor de toestand gevonden is.</p>')
        else:
            self._Generator.VoegHtmlToe ('<p>Er is dus een (eenduidige) kandidaat-instrumentversie: ' + proces.KandidaatInstrumentversie)

        if proces.TegensprekendeDoelen:
            self._Generator.VoegHtmlToe ('Als stap 2 faalt worden de intrekkingsdoelen genoemd in <i>TegensprekendeDoelen</i>. Als stap 4 faalt dan wordt daarin van elke versie één doel opgenomen.<table><tr><td rowspan="' + str(len (proces.TegensprekendeDoelen)) + '">TegensprekendeDoelen</td>' + '<tr>'.join (('<td>' + self._WeergaveData.DoelLetter (td.Doel) + '</td><td>' + str(td.Doel) + '<br/>Laatst bekend: ' + td.LaatstBekend + '</td></tr>') for td in proces.TegensprekendeDoelen) + '</table>Laatst bekend geeft het tijdstip van de laatste momentopname die voor het doel is gebruikt om de inhoud van de toestand te bepalen.')

    def _ValideerInhoudHtml (self, proces : ConsolidatieprocesInformatie, voorToestand: bool):
        """Valideer de kandidaat-instrumentversie(s)
        
        Argumenten:

        proces ConsolidatieprocesInformatie  Beschrijving van het proces van de validatie van de inhoud van de toestand
        voorTeostand bool Geeft aan dat het proces voor een toesyand is uitgevoerd in plaats van een bekende instrumentversie
        """
        if voorToestand:
            if proces.KandidaatInstrumentversie is None:
                self._Generator.VoegHtmlToe ('<p>De verdere analyse van de toestand wordt gedaan alsof er al wel een kandidaat-instrumentversie voor de toestand gevonden is.</p>')
        else:
            self._Generator.VoegHtmlToe ('<p>Voer de analyse uit alsof ' + proces.Instrumentversie + ' de kandidaat-instrumentversie voor de toestand zou zijn.</p>')

        self._Generator.VoegHtmlToe (self._UitlegVoorStap ('stap5_6'))

        self._Generator.VoegHtmlToe ('<p><b>Stap 5. Zijn voor alle toestand-doelen de laatste uitwisselingen verwerkt?</b></p>')
        self._ToonMeldingen (proces._Uitleg, Weergave_Toestandbepaling.Validatie_LaatsteUitwisselingVoorAlleDoelen)

        self._Generator.VoegHtmlToe ('<p><b>Stap 6. Dragen uitwisselingen bij aan de kandidaat-versie voor doelen die niet in de toestand voorkomen?</b></p>')
        self._ToonMeldingen (proces._Uitleg, Weergave_Toestandbepaling.Validatie_GeenAnderDoelVerwerktInInstrumentversie)

        html = '<p>De uitkomst van de stappen 5 en 6 wordt gerapporteerd in:<table>'
        if proces.TeVerwerkenDoelen:
            html += '<tr><td rowspan="' + str(len (proces.TeVerwerkenDoelen)) + '">TeVerwerkenDoelen</td>' + '<tr>'.join (('<td>' + self._WeergaveData.DoelLetter (tvd.Doel) + '</td><td>' + str(tvd.Doel) + '<br/>Laatst bekend: ' + tvd.LaatstBekend + '<br/>Laatst verwerkt: ' + ('-' if tvd.LaatstVerwerkt is None else tvd.LaatstVerwerkt) + '</td></tr>') for tvd in proces.TeVerwerkenDoelen)
        else:
            html += '<tr><td>TeVerwerkenDoelen</td><td>-</td></tr>'
        if proces.TeOntvlechtenDoelen:
            html += '<tr><td rowspan="' + str(len (proces.TeOntvlechtenDoelen)) + '">TeOntvlechtenDoelen</td>' + '<tr>'.join (('<td>' + self._WeergaveData.DoelLetter (tod.Doel) + '</td><td>' + str(tod.Doel) + '<br/>Laatst verwerkt' + tod.LaatstVerwerkt + '</td></tr>') for tod in proces.TeOntvlechtenDoelen)
        else:
            html += '<tr><td>TeOntvlechtenDoelen</td><td>-</td></tr>'
        html += '</table>'
        if proces.TeVerwerkenDoelen or proces.TeVerwerkenDoelen:
            html += 'Laatst verwerkt geeft het tijdstip van de laatste momentopname die is gebruikt voor de bepaling van de inhoud van de toestand.'

        if voorToestand:
            if proces.Instrumentversie is None:
                html += 'Er is dus geen instrumentversie aan te wijzen die de inhoud van de toestand weergeeft'
            else:
                html += 'De kandidaat-instrumentversie is dus valide en geeft de inhoud van de toestand weer'
        html += '</p>'
        self._Generator.VoegHtmlToe (html)

    def _BepaalAlternatieven (self, proces : ConsolidatieprocesInformatie):
        """Bepaal alternatieve weergve voor een toestand
        
        Argumenten:

        proces ConsolidatieprocesInformatie  Beschrijving van het proces van de validatie van de inhoud van de toestand
        """
        self._Generator.VoegHtmlToe (self._UitlegVoorStap ('stap7_toestand'))
        if proces.Instrumentversie is None:
            self._ToonMeldingen (proces._Uitleg, Weergave_Toestandbepaling.BepaalAlternatieveVersies)
        else:
            self._Generator.VoegHtmlToe ('De kandidaat-instrumentversie ' + proces.Instrumentversie + ' geeft al de inhoud van de toestand weer.')

    def _BepaalPublicaties (self, proces : ConsolidatieprocesInformatie):
        """Bepaal de publicaties ter aanvulling op de instrumentversie
        
        Argumenten:

        proces ConsolidatieprocesInformatie  Beschrijving van het proces van de validatie van de inhoud van de toestand
        """
        self._Generator.VoegHtmlToe (self._UitlegVoorStap ('stap7_instrumentversie'))
        self._ToonMeldingen (proces._Uitleg, Weergave_Toestandbepaling.BepaalAanvullendePublicaties)

        self._Generator.VoegHtmlToe (Weergave_STOPModule.MaakHtml (self._InstrumentData.JuridischeVerantwoording))

    def _ToonMeldingen (self, meldingen, stap):
        """Geef de meldingen weer voor een bepaalde stap"""
        tekst = ''.join (m.HtmlTabelRij (False) for m in meldingen if m._Stap == stap)
        if tekst:
            self._Generator.VoegHtmlToe ('<table>' + tekst + '</table>')
        else:
            self._Generator.VoegHtmlToe ('<div>(Geen meldingen)</div>')

    def _UitlegVoorStap (self, stap):
        uitleg = self._UitlegStappen.get (stap)
        if uitleg is None:
            self._UitlegStappen[stap] = uitleg = self._Generator.LeesHtmlTemplate ('help_' + stap, False)
        return uitleg

#======================================================================
#
# Maker van teksten en symbolen voor diagram elementen, en 
# context/opties voor het maken van het diagram, met als toepasing:
# diagram voor nog te consolideren informatie voor toestand en
# onvolledige versies.
#
#======================================================================
class _OnvolledigeVersieDiagram (DiagramGeneratorOpties):

    def __init__ (self, uniekId, instrument : Instrument, instrumentData : InstrumentUitwisseling, bekendOp : str):
        """Maak de tekstgenerator aan

        Argumenten:

        instrument InstrumentData Weer te geven versiebeheerinformatie
        instrumentData InstrumentUitwisseling Weer te geven consolidatie informatie voor het instrument
        """
        super().__init__(uniekId, instrument, instrumentData.InstrumentData, False, instrumentData, bekendOp)
