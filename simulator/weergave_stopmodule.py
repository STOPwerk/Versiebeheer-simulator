#======================================================================
#
# Weergave van de XML van een STOP module als onderdeel van
# de webpagina die alle beschikbare resultaten laat zien
# van het consolidatie proces uit proces_consolideren.
#
#======================================================================

class Weergave_STOPModule:

    def __init__ (self, generator):
        """Maak de generator voor de weergave van een STOP module

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        """
        self._Webpagina = generator

    def VoegModuleToe (self, titel, module):
        """Voeg de module toe aan de webpagina
        
        Argumenten:
        titel string Titel van de dicht te klappen sectie met de module
        module object  Instantie van een STOP module
        """
        xml = module.ModuleXml ()
        if xml:
            einde = self._Webpagina.StartSectie (titel)
            self._Webpagina.VoegHtmlToe (Weergave_STOPModule.MaakHtml (xml))
            self._Webpagina.VoegHtmlToe (einde)

    def VoegHtmlToe (self, xml):
        """Voeg STOP XML toe aan de webpagina
        
        Argumenten:
        xml string  Fragment van een STOP module
        """
        if xml:
            self._Webpagina.VoegHtmlToe (Weergave_STOPModule.MaakHtml (xml))

    @staticmethod
    def MaakHtml (xml):
        """Vertaal STOP XML naar HTML
        
        Argumenten:
        xml string  Fragment van een STOP module
        """
        if xml:
            return '<pre>\n' + '\n'.join (xml).replace ('\t', '  ').replace ('<', '&lt;').replace ('>', '&gt;') + '\n</pre>\n'
        return ''


