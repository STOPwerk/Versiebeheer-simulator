#======================================================================
#
# Aanmaken van een webpagina die alle beschikbare resultaten laat zien
# van het consolidatie proces uit proces_lv_consolidatie.py.
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

from applicatie_scenario import Scenario
import applicatie_configuratie
from stop_naamgeving import Naamgeving
from weergave_actueletoestanden import Weergave_ActueleToestanden
from weergave_annotaties import Weergave_Annotaties
from weergave_bg_versiebeheer import Weergave_BG_Versiebeheer
from weergave_completetoestanden import Weergave_CompleteToestanden
from weergave_consolidatieinformatie import Weergave_ConsolidatieInformatie
from weergave_proefversies import Weergave_Proefversies
from weergave_project_uitwisselingen import Weergave_Project_Uitwisselingen
from weergave_projecten import Weergave_Projecten
from weergave_resultaat_data import InstrumentData
from weergave_tijdreisfilter import Weergave_Tijdreisfilter
from weergave_tijdreizen import Weergave_Tijdreizen
from weergave_toestandbepaling import Weergave_Toestandbepaling
from weergave_uitwisselingen import Weergave_Uitwisselingen
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
    def MaakPagina (scenario : Scenario, favicon = None):
        """Maak een webpagina met de resultaten van de consolidatie
        
        Argumenten:
        scenario Scenario  De invoer en resultaten van de consolidatie
        favicon string  URL van het favicon voor de webpagina; moet een PNG plaatje zijn

        Geeft de generator terug
        """
        generator = ResultaatGenerator (scenario, favicon)
        try:
            generator._MaakPagina ()
        except Exception as e:
            # Invalide invoer kan het maken van een pagina in de weg zitten
            scenario.ApplicatieLog.Fout ("Potverdorie, een fout in het maken van de resultaatpagina die niet voorzien werd: " + str(e))
            if scenario.ApplicatieLog != scenario.Log:
                scenario.Log.Fout ("Potverdorie, een fout in het maken van de resultaatpagina die niet voorzien werd: " + str(e))

            # Maak een pagina met alleen de meldingen
            generator = ResultaatGenerator (scenario)
            generator.VoegHtmlToe ('<p>De resultaatpagina kan niet gemaakt worden</p>')
            generator._AlleenMeldingen ()
        if not scenario.ResultaatPad is None:
            generator.SchrijfHtml (scenario.ResultaatPad)
        return generator

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
    def __init__ (self, scenario : Scenario, favicon = None):
        """Maak een generator aan voor de resultaten van de consolidatie
        
        Argumenten:
        scenario Scenario  De invoer en resultaten van de consolidatie
        favicon string  URL van het favicon voor de webpagina; moet een PNG plaatje zijn
        """
        super().__init__ (scenario.Titel, favicon)
        self.Scenario = scenario

    def _AlleenMeldingen (self):
        self.Scenario.Log.MaakHtml (self, 'Uitvoering van de applicatie')

#======================================================================
#
# Indeling van de pagina
#
#======================================================================
    def _MaakPagina (self):

        if self.Scenario.Versiebeheerinformatie is None:
            # Als er geen versiebeheerinformatie is, dan is de uitvoering van de applicatie niet goed gegaan
            self.Scenario.Log.MaakHtml (self, 'Uitvoering van de applicatie')
            return

        #--------------------------------------------------------------
        #
        # Algemene informatie over de pagina en het scenario
        #
        #--------------------------------------------------------------
        self.VoegHtmlToe ('<p>Inhoudsopgave? <span id="accordion-sluiten" class="aslink">Verberg</span> alle teksten.<br><a href="https://github.com/STOPwerk/Versiebeheer-simulator">Versiebeheer-simulator</a> ' + applicatie_configuratie.Applicatie_versie + '</p>')

        self.VoegHtmlToe ('<div id="intro">')
        if self.Scenario.Opties.Beschrijving:
            einde = self.StartToelichting ('Beschrijving van het scenario')
            self.VoegHtmlToe (self.Scenario.Opties.Beschrijving)
            self.VoegHtmlToe (einde)
        Weergave_Uitwisselingselector(self.Scenario).VoegSelectorToe (self)
        self.VoegHeadScriptToe (self.LeesJSTemplate ('Applicatie', False).replace ('TOESTANDEN_DATA', self._MaakToestandenData()))
        self.VoegHtmlToe ('</div>')

        einde = self.StartToelichting ('Over deze pagina')
        self.LeesHtmlTemplate ('help_pagina')
        self.VoegHtmlToe (einde)

        self.Scenario.Log.MaakHtml (self, 'Uitvoering van de applicatie', self.LeesHtmlTemplate ('help_meldingen', False))
        
        # Beschrijving van de geselecteerde uitwisseling
        Weergave_Uitwisselingselector(self.Scenario).VoegBeschrijvingToe (self)

        if self.Scenario.Opties.Versiebeheer:
            #--------------------------------------------------------------
            #
            # Simulatie van bevoegd gezag systemen
            #
            #--------------------------------------------------------------
            self.VoegHtmlToe ('<div class="sectie_bg"><h1>Opstellen en consolideren</h1>')
            einde = self.StartToelichting ('Over opstellen en consolideren')
            self.LeesHtmlTemplate ('help_sectie_bg')
            self.VoegHtmlToe (einde)

            Weergave_Projecten.VoegToe (self, self.Scenario)
            Weergave_Project_Uitwisselingen.VoegToe (self, self.Scenario)
            Weergave_BG_Versiebeheer.VoegToe (self, self.Scenario)

            self.VoegHtmlToe ('</div>')

        #--------------------------------------------------------------
        #
        # Simulatie van de uitwisselingen/publicaties
        #
        #--------------------------------------------------------------
        self.VoegHtmlToe ('<div class="sectie_op"><h1>Publiceren</h1>')
        einde = self.StartToelichting ('Over publiceren')
        self.LeesHtmlTemplate ('help_sectie_op')
        self.VoegHtmlToe (einde)
        Weergave_Uitwisselingen.VoegToe (self, self.Scenario)
        Weergave_ConsolidatieInformatie.VoegToe (self, self.Scenario)
        self.VoegHtmlToe ('</div>')

        #--------------------------------------------------------------
        #
        # Simulatie van landelijke voorzieningen
        #
        #--------------------------------------------------------------
        self.VoegHtmlToe ('<div class="sectie_lv"><h1>Beschikbaar stellen</h1>')
        einde = self.StartToelichting ('Over beschikbaar stellen')
        self.LeesHtmlTemplate ('help_sectie_lv')
        self.VoegHtmlToe (einde)

        altDiv = 0
        for instrument in sorted (self.Scenario.Versiebeheerinformatie.Instrumenten.values (), key = lambda x: x.WorkId):
            if altDiv == 0:
                altDiv = 1
            else:
                self.VoegHtmlToe ('</div><div class="sectie_lv_alt' + str(altDiv) + '">')
                altDiv = 3 - altDiv

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

            if instrumentData.HeeftAnnotaties and instrumentData.HeeftActueleToestanden:
                Weergave_Annotaties.VoegToe (self, instrumentData)

            if instrumentData.HeeftCompleteToestanden:
                Weergave_CompleteToestanden.VoegToe (self, instrumentData)
                Weergave_Tijdreisfilter.VoegToe (self, instrumentData)
                Weergave_Toestandbepaling.VoegCompleteToestandenToe (self, instrument, instrumentData)
                Weergave_Tijdreizen.VoegToe (self, instrument, instrumentData)

        self.VoegHtmlToe ('</div>')

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
            if not instrumentData is None and len (instrumentData.Uitwisselingen) > 0 and hasattr (instrumentData.Uitwisselingen[-1], 'CompleteToestanden') and not instrumentData.Uitwisselingen[-1].CompleteToestanden is None:
                for toestand in instrumentData.Uitwisselingen[-1].CompleteToestanden.Toestanden:
                    toestandData = data.get (toestand.Identificatie)
                    if toestandData is None:
                        data[toestand.Identificatie] = toestandData = {}

                    if not toestand.GemaaktOp in toestandData:
                        toestandData[toestand.GemaaktOp] = toestand._UniekId

        return ',\n'.join (str(d) + ': [' + ', '.join ('["' + g + '", ' + str (u) + ']' for g, u in sorted (gu.items(), key = lambda x: x[0])) + ']' for d, gu in data.items ())
