#======================================================================
#
# Aanmaken van een weergave van de ActueleToestanden module als 
# onderdeel van de webpagina die alle beschikbare resultaten laat 
# zien van het consolidatie proces uit proces_consolideren.
#
#======================================================================

from weergave_resultaat_data import InstrumentData
from weergave_stopmodule import Weergave_STOPModule
from weergave_uitwisselingselector import Weergave_Uitwisselingselector
from weergave_webpagina import WebpaginaGenerator

#======================================================================
#
# Weergave_ActueleToestanden
#
#======================================================================
class Weergave_ActueleToestanden ():

    @staticmethod
    def VoegToe (generator : WebpaginaGenerator, instrumentData : InstrumentData):
        """Voeg de actuele toestanden toe aan de pagina met resultaten.
        
        Argumenten:
        generator WebpaginaGenerator  Generator voor de webpagina
        instrumentData InstrumentData Extra informatie over het instrument uit de consolidatie
        """
        einde = generator.StartSectie ("STOP module: ActueleToestanden")

        einde_t = generator.StartToelichting ('Toelichting')
        generator.LeesHtmlTemplate ('help')
        generator.VoegHtmlToe (einde_t)

        selector = Weergave_Uitwisselingselector (instrumentData.WeergaveData.Scenario)
        moduleMaker = Weergave_STOPModule (generator)
        for uitwisseling in instrumentData.Uitwisselingen:
            if not uitwisseling.ActueleToestanden is None:
                generator.VoegHtmlToe ('<div ' + selector.AttributenToonIn (uitwisseling.GemaaktOp, uitwisseling.VolgendeGemaaktOp) + '>')
                moduleMaker.VoegHtmlToe (uitwisseling.ActueleToestanden.ModuleXml ())
                generator.VoegHtmlToe ('</div>')

        generator.VoegHtmlToe (einde)
