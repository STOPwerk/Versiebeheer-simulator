#======================================================================
#
# Aanmaken van een weergave van een tijdreisfilter en van de 
# resulterende CompleteToestanden module als onderdeel van de 
# webpagina die alle beschikbare resultaten laat zien van het 
# consolidatie proces uit proces_consolideren.
#
#======================================================================

from weergave_resultaat_data import InstrumentData, InstrumentUitwisseling
from weergave_stopmodule import Weergave_STOPModule
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Weergave_Tijdreisfilter
#
#======================================================================
class Weergave_Tijdreisfilter ():

    @staticmethod
    def VoegToe (generator : WebpaginaGenerator, instrumentData : InstrumentData):
        """Voeg de module voor complete toestanden met filterfunctionaliteit toe aan de pagina met resultaten.
        
        Argumenten:
        generator WebpaginaGenerator  Generator voor de webpagina
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        uniek_id = 'ct_tf_' + str (generator.GeefUniekeIndex ())
        einde = generator.StartSectie ('Tijdreisfilter', True)

        einde_t = generator.StartToelichting ("Toelichting op het tijdreisfilter")
        generator.LeesHtmlTemplate ('help_filter')
        generator.VoegHtmlToe (einde_t)

        generator.VoegHtmlToe (generator.LeesHtmlTemplate ('', False).replace ('UNIEK_ID', uniek_id))

        generator.VoegHtmlToe (einde)
        generator.VoegSlotScriptToe (generator.LeesJSTemplate ('', False).replace ('UNIEK_ID', uniek_id).replace ('WORK_ID', instrumentData.WorkId))

        einde = generator.StartSectie ("STOP module: CompleteToestanden")

        einde_t = generator.StartToelichting ("Toelichting op de STOP module")
        generator.LeesHtmlTemplate ('help_stopmodule')
        generator.VoegHtmlToe (einde_t)

        moduleMaker = Weergave_STOPModule (generator)
        selector = Weergave_Uitwisselingselector (instrumentData.WeergaveData.Scenario)
        for uitwisseling in instrumentData.Uitwisselingen:
            generator.VoegHtmlToe ('<div' + selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>')
            for code in uitwisseling.BeschikbareTijdreisfilters ():
                module = uitwisseling.GefilterdeCompleteToestanden (code)
                generator.VoegHtmlToe ('<div data-' + uniek_id + '_module="' + code + '">')
                moduleMaker.VoegHtmlToe (module.ModuleXml ())
                generator.VoegHtmlToe ('</div>')
            generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde)
