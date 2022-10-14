#======================================================================
#
# Tekstvervanging: vervangt @@@DOCUMENTATIE_URL@@@ en @@@REPOSITORY_URL@@@
# door de URL van de STOP documentatie, met trailing /. Dit wordt toegepast 
# op de resultaat-webpagina, waardoor vanuit alle beschrijvingen naar de
# STOP documentatie en bestanden verwezen kan worden.
#
#======================================================================

class VervangSTOPCodumentatieURL:

    @staticmethod
    def VoerUit (html : str) -> str:
        for term, waarde in VervangSTOPCodumentatieURL._TeVervangen.items ():
            html = html.replace (term, waarde)
        return html

    _TeVervangen = {
        '@@@DOCUMENTATIE_URL@@@': 'https://koop.gitlab.io/STOP/voorinzage/standaard-preview-b/',
        '@@@REPOSITORY_URL@@@': 'https://gitlab.com/koop/STOP/voorinzage/standaard-preview-b/-/tree/master/'
    }
