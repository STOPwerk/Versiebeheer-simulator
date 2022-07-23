#======================================================================
#
# Aanmaken van een webpagina die alle beschikbare resultaten laat zien
# van het consolidatie proces uit proces_consolidatie.py.
#
#----------------------------------------------------------------------
#
# De ResultaatGenerator maakt een webpagina van alle beschikbare
# resultaten in Consolidatie uit proces_consolideren. Voor de
# HTML generatie wordt gebruik gemaakt van code uit andere weergave_*
# modules en uit applicatie_meldingen.
#
#======================================================================

import os.path

from data_scenario import Scenario
from stop_naamgeving import Naamgeving
from weergave_actueletoestanden import Weergave_ActueleToestanden
from weergave_annotaties import Weergave_Annotaties
from weergave_completetoestanden import Weergave_CompleteToestanden
from weergave_proefversies import Weergave_Proefversies
from weergave_resultaat_data import InstrumentData
from weergave_tijdreisfilter import Weergave_Tijdreisfilter
from weergave_tijdreizen import Weergave_Tijdreizen
from weergave_toestandbepaling import Weergave_Toestandbepaling
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_versiebeheer import Weergave_Versiebeheer
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Generator voor webpagina die alle beschikbare resultaten
#
#======================================================================
class ResultaatGenerator (WebpaginaGenerator):

    @staticmethod
    def MaakPagina (scenario : Scenario):
        """Maak een webpagina met de resultaten van de consolidatie
        
        Argumenten:
        scenario Scenario  De invoer en resultaten van de consolidatie
        """
        generator = ResultaatGenerator (scenario)
        try:
            generator._MaakPagina ()
        except:
            # Invalide invoer kan het maken van een pagina in de weg zitten
            generator = ResultaatGenerator (scenario)
            generator.VoegHtmlToe ('<p>De resultaatpagina kan niet gemaakt worden</p>')
            generator._AlleenMeldingen ()
        generator.SchrijfHtml (scenario.ResultaatPad)

    @staticmethod
    def MaakMeldingen (scenario : Scenario):
        """Maak een webpagina met alleen de meldingen
        
        Argumenten:
        scenario Scenario  De invoer en resultaten van de consolidatie
        """
        generator = ResultaatGenerator (scenario)
        generator._AlleenMeldingen ()
        generator.SchrijfHtml (scenario.ResultaatPad)

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, scenario : Scenario):
        """Maak een generator aan voor de resultaten van de consolidatie
        
        Argumenten:
        scenario Scenario  De invoer en resultaten van de consolidatie
        """
        super().__init__ (os.path.basename (os.path.dirname (scenario.ResultaatPad)))
        self.Scenario = scenario

    def _AlleenMeldingen (self):
        self.Scenario.Log.MaakHtml (self, 'Uitvoering van de applicatie')

    def _MaakPagina (self):

        self.VoegHtmlToe ('<div id="intro">')
        if self.Scenario.Opties.Beschrijving:
            einde = self.StartToelichting ('Beschrijving van het scenario')
            self.VoegHtmlToe (self.Scenario.Opties.Beschrijving)
            self.VoegHtmlToe (einde)

        if not self.Scenario.Versiebeheerinformatie is None:
            Weergave_Uitwisselingselector(self.Scenario).VoegSelectorToe (self)
        self.VoegHtmlToe ('</div>')

        if self.Scenario.Versiebeheerinformatie is None:
            self.Scenario.Log.MaakHtml (self, 'Uitvoering van de applicatie')
            return
        else:
            self.VoegHeadScriptToe (self.LeesJSTemplate ('Applicatie', False).replace ('TOESTANDEN_DATA', self._MaakToestandenData()))
            self.VoegHtmlToe ('<p>Inhoudsopgave? <span id="accordion-sluiten" class="aslink">Verberg</span> alle teksten.</p>')

            einde = self.StartToelichting ('Over deze pagina')
            self.LeesHtmlTemplate ('help')
            self.VoegHtmlToe (einde)

            self.Scenario.Log.MaakHtml (self, 'Uitvoering van de applicatie', self.LeesHtmlTemplate ('help_meldingen', False))
            
            Weergave_Uitwisselingselector(self.Scenario).VoegBeschrijvingToe (self)

        for instrument in sorted (self.Scenario.Versiebeheerinformatie.Instrumenten.values (), key = lambda x: x.WorkId):
            instrumentData = self.Scenario.WeergaveData.InstrumentData.get (instrument.WorkId)
            if instrumentData is None:
                instrumentData = InstrumentData (self.Scenario.WeergaveData, instrument.WorkId)

            self.VoegHtmlToe ('<h2>' + ('Informatieobject' if Naamgeving.IsInformatieobject (instrument.WorkId) else 'Regeling') + ': ' + instrument.WorkId + '</h2>')

            Weergave_Versiebeheer.VoegToe (self, instrument, instrumentData)

            if instrumentData.HeeftActueleToestanden:
                Weergave_Toestandbepaling.VoegActueleToestandenToe (self, instrumentData)
                Weergave_ActueleToestanden.VoegToe (self, instrumentData)

            if instrumentData.HeeftProefversies:
                Weergave_Proefversies.VoegToe (self, instrument, instrumentData)

            if instrumentData.HeeftAnnotaties:
                Weergave_Annotaties.VoegToe (self, instrumentData)

            if instrumentData.HeeftCompleteToestanden:
                Weergave_CompleteToestanden.VoegToe (self, instrumentData)
                Weergave_Tijdreisfilter.VoegToe (self, instrumentData)
                Weergave_Toestandbepaling.VoegCompleteToestandenToe (self, instrument, instrumentData)
                Weergave_Tijdreizen.VoegToe (self, instrument, instrumentData)

#----------------------------------------------------------------------
#
# Informatie over toestanden
#
#----------------------------------------------------------------------
    def _MaakToestandenData (self):
        """Maak Javascript data met de relatie tussen toestanden en uitwisselingen"""
        # Verzamel de laatste UniekId van een toestand per identificatie/gemaaktOp
        data = {}
        for instrument in sorted (self.Scenario.Versiebeheerinformatie.Instrumenten.values (), key = lambda x: x.WorkId):
            instrumentData = self.Scenario.WeergaveData.InstrumentData.get (instrument.WorkId)
            if not instrumentData is None and len (instrumentData.Uitwisselingen) > 0 and hasattr (instrumentData.Uitwisselingen[-1], 'CompleteToestanden'):
                for toestand in instrumentData.Uitwisselingen[-1].CompleteToestanden.Toestanden:
                    toestandData = data.get (toestand.Identificatie)
                    if toestandData is None:
                        data[toestand.Identificatie] = toestandData = {}

                    if not toestand.GemaaktOp in toestandData:
                        toestandData[toestand.GemaaktOp] = toestand.UniekId

        return ',\n'.join (str(d) + ': [' + ', '.join ('["' + g + '", ' + str (u) + ']' for g, u in sorted (gu.items(), key = lambda x: x[0])) + ']' for d, gu in data.items ())
