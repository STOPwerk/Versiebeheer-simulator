#======================================================================
#
# Tekstvervanging: vervangt @@@DOCUMENTATIE_URL@@@ en @@@REPOSITORY_URL@@@
# door de URL van de STOP documentatie, met trailing /. Dit wordt toegepast 
# op de resultaat-webpagina, waardoor vanuit alle beschrijvingen naar de
# STOP documentatie en bestanden verwezen kan worden.
#
#======================================================================

import applicatie_configuratie

class VervangSTOPCodumentatieURL:

    @staticmethod
    def VoerUit (html : str) -> str:
        for term, waarde in VervangSTOPCodumentatieURL._TeVervangen.items ():
            html = html.replace (term, waarde)
        return html

    _TeVervangen = {
        '@@@DOCUMENTATIE_URL@@@': applicatie_configuratie.STOP_Documentatie_Url,
        '@@@REPOSITORY_URL@@@': applicatie_configuratie.STOP_Repository_Url
    }
