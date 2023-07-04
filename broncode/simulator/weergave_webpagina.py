#======================================================================
#
# Webpagina generator
#
#----------------------------------------------------------------------
#
# Generator voor een webpagina waarin de resultaten van de uitvoering
# van (een deel van) de applicatie in beschreven staan.
#
#======================================================================

import inspect
import os
import tempfile
import urllib.parse
import urllib.request
import webbrowser

#======================================================================
# Generatie van een webpagina
#======================================================================
class WebpaginaGenerator:

    def __init__ (self, titel = None, favicon = None):
        """Maak een generator aan voor een webpagina

        Argumenten:
        titel string/HTML  Titel van de pagina
        favicon string  URL van het favicon voor de webpagina; moet een PNG plaatje zijn
        """
        super().__init__ ()
        # Template voor de start van de pagina
        self._Start = self.LeesHtmlTemplate ("start", False)
        # Inhoud van de pagina
        self._Html = ""
        # Template voor het einde van de pagina
        self._Einde = self.LeesHtmlTemplate ("einde", False)
        # CSS dat die aan de <style> toegevoegd moet worden 
        self._Css = set()
        # Scripts die aan de <head> toegevoegd moeten worden 
        self._HeadScript = set()
        # Scripts die aan het einde van de pagina toegevoegd moeten worden 
        self._SlotScript = set()
        # Index voor het uniek maken van repeterende HTML fragmenten
        self._Index = 0

        if favicon is None:
            favicon = ''
        else:
            favicon = '\n<link rel="icon" type="image/png" href="' + favicon + '">'

        if not titel is None:
            self._Start = self._Start.replace ("<!--TITEL-->", "<title>" + titel + "</title>" + favicon)
            self._Html += "<h1>" + titel + "</h1>"

#----------------------------------------------------------------------
# Bewaren / tonen webpagina
#----------------------------------------------------------------------
    def Html (self):
        """Geef de HTML van de webpagina"""
        return self._Start.replace ("/*EXTRASTYLE*/", "\n".join (sorted(self._Css))).replace ("/*EXTRASCRIPT*/", "\n".join (sorted(self._HeadScript))) + self._Html + self._Einde.replace ("/*EXTRASCRIPT*/", "\n".join (sorted(self._SlotScript)))

    def SchrijfHtml (self, pad, toonInBrowser = False, genereerNaam = False):
        """Schrijf de webpagina naar een bestand
        
        Argumenten:
        pad string  Pad naar het bestand waarin de webpagina bewaard moet worden.
        toonInBrowser boolean  Geeft aan dat de pagina na het schrijven bewaard moet worden
        genereerNaam boolean  Geeft aan dat de bestandsnaam gegenereerd moet worden, waarbij pad de map is waarin het bestand geplaatst moet worden

        Geeft het pad van het geschreven bestand terug
        """
        if not pad is None:
            os.makedirs (pad if genereerNaam else os.path.dirname (pad), exist_ok=True)
        if genereerNaam:
            with tempfile.NamedTemporaryFile ("w", suffix = ".html", delete = False, dir = pad, encoding="utf-8") as logFile:    
                pad = logFile.name
                logFile.write (self.Html ())
        else:
            with open (pad, "w", encoding="utf-8") as logFile:
                logFile.write (self.Html ())

        if toonInBrowser:
            webbrowser.open (WebpaginaGenerator.UrlVoorPad (pad))
        return pad

    @staticmethod
    def UrlVoorPad (pad):
        """Geef de URL van een pad voor gebruik als URL voor een hyoerlink
        
        Argumenten:
        pad string Pad naar het HTML bestand
        """
        return urllib.parse.urljoin ("file:", urllib.request.pathname2url (os.path.abspath (pad)))

#----------------------------------------------------------------------
# Maken van de webpagina
#----------------------------------------------------------------------
    def LeesCssTemplate (self, suffix, voegToeAanCss = True):
        """Lees de styling van het webfragment uit een template bestand dat bij de code staat

        Argumenten:
        suffix string Laatste deel van de bestandsnaam; volledige bestandsnaam is <codebestandsnaam> "_" <suffix> ".html"
        voegToeAanCss boolean  Geeft aan of de inhoud aan de CSS van de webpagina toegevoegd moet worden
        """
        pad = os.path.splitext (os.path.abspath(inspect.getfile(inspect.currentframe().f_back)))[0] + ("_" if suffix else '') + suffix + ".css"
        css = self._LeesTemplate (pad)
        if voegToeAanCss and css:
            self._Css.add (css)
        return css

    def LeesHtmlTemplate (self, suffix, voegToeAanHtml = True):
        """Lees een deel van de webpagina uit een template bestand dat bij de code staat

        Argumenten:
        suffix string Laatste deel van de bestandsnaam; volledige bestandsnaam is <codebestandsnaam> "_" <suffix> ".html"
        voegToeAanHtml boolean  Geeft aan of de inhoud aan de webpagina toegevoegd moet worden
        """
        pad = os.path.splitext (os.path.abspath(inspect.getfile(inspect.currentframe().f_back)))[0] + ("_" if suffix else '') + suffix + ".html"
        html = self._LeesTemplate (pad)
        if voegToeAanHtml and html:
            self._Html += html + "\n"
        return html

    def LeesJSTemplate (self, suffix, voegToeAanPagina = True, voegToeInHead = False):
        """Lees een deel van de webpagina uit een template bestand dat bij de code staat

        Argumenten:
        suffix string Laatste deel van de bestandsnaam; volledige bestandsnaam is <codebestandsnaam> "_" <suffix> ".html"
        voegToeAanPagina boolean  Geeft aan of de inhoud aan de webpagina toegevoegd moet worden
        voegToeInHead boolean  Geeft aan of de inhoud aan de head van de webpagina toegevoegd moet worden als voegToeAanPagina True is (ipv aan het slot)
        """
        pad = os.path.splitext (os.path.abspath(inspect.getfile(inspect.currentframe().f_back)))[0] + ("_" if suffix else '') + suffix + ".js"
        js = self._LeesTemplate (pad)
        if voegToeAanPagina and js:
            if voegToeInHead:
                self._HeadScript.add (js)
            else:
                self._SlotScript.add (js)
        return js

    def _LeesTemplate (self, pad):
        """Lees een deel van de webpagina uit een template bestand dat bij de code staat

        Argumenten:
        pad string Volledige bestandsnaam
        """
        if os.path.isfile (pad):
            with open (pad, "r", encoding="utf-8") as templateFile:
                return templateFile.read ()
        return ""

    def VoegHtmlToe (self, html):
        """Voeg extra html toe aan de webpagina"""
        if html:
            self._Html += html + "\n"

    def StartToelichting (self, titel, startOpen = True):
        """Start een inklapbare toelichting in de HTML
        
        Argumenten:

        titel str  De titel van de toelichting, alleen te tonen als de toelichting verborgen is.
        startOpen bool  Geeft aan of de secite initieel opengeklapt moet worden

        Geeft de html terug die aan het einde van de sectie opgenomen moet worden
        """
        WebpaginaGenerator._AccordionPaneel += 1
        id = str(WebpaginaGenerator._AccordionPaneel)
        active = ' active' if startOpen else ''
        block = ' style="display: block"' if startOpen else ' style="display: none"'
        nietblock = ' style="display: none"' if startOpen else ' style="display: block"'
        self._Html += '<table><tr><td><button data-accordion="' + id + '" class="accordion_t' + active + '">?</button></td>\n'
        self._Html += '<td data-accordion-titel="' + id + '" class="accordion_t_titel"''' + nietblock + '>&#8678;' + titel + '</td>\n'
        self._Html += '<td data-accordion-paneel="' + id + '" class="accordion_t_paneel"''' + block + '>\n'
        return '</td></tr></table>\n'

    def StartSectie (self, titel, startOpen = False, bevriesHoogte = False):
        """Start een inklapbare sectie in de HTML
        
        Argumenten:

        titel str  De titel van de sectie
        startOpen bool  Geeft aan of de secite initieel opengeklapt moet worden

        Geeft de html terug die aan het einde van de sectie opgenomen moet worden
        """
        WebpaginaGenerator._AccordionPaneel += 1
        id = str(WebpaginaGenerator._AccordionPaneel)
        active = ' active' if startOpen else ''
        block = ' style="display: block"' if startOpen else ''
        data = ' data-bh="0"' if bevriesHoogte else ''
        self._Html += '<button data-accordion="' + id + '" class="accordion_h' + active + '''">''' + titel + '</button>\n'
        self._Html += '<div data-accordion-paneel="' + id + '" class="accordion_h_paneel"''' + block + data + '>\n'
        return '</div>\n'

    _AccordionPaneel = 0

    def GeefUniekeIndex (self):
        """Geef een (voor de pagina) unieke index waarmee repeterende HTML fragmenten uniek gemaakt kunnen worden"""
        self._Index += 1
        return self._Index

    def GebruikSvgScript (self):
        """Voeg de scripting toe nodig om SVG diagrammen op te nemen in de webpagina
        """
        if not hasattr (self, '_svgScript'):
            setattr (self, '_svgScript', True)
            self.LeesJSTemplate ("svg-pan-zoom", True, True)

    def GebruikSyntaxHighlighting (self):
        """Voeg de scripting/css toe nodig om XML en JSON data met syntax highlighting op te nemen in de webpagina
        """
        if not hasattr (self, '_highlight'):
            setattr (self, '_highlight', True)
            self.LeesJSTemplate ("highlight", True, True)
            self.LeesCssTemplate ("highlight")

    def VoegCssToe (self, css):
        """Voeg CSSstyle toe
        
        Argumenten
        css string  CSS voor de styling van een html fragment
        """
        self._Css.add (css)


    def VoegHeadScriptToe (self, js):
        """Voeg Javascript toe aan de head van de pagina
        
        Argumenten
        js string  Javascript uit te voeren bij het laden van de pagina
        """
        self._HeadScript.add (js)

    def VoegSlotScriptToe (self, js):
        """Voeg Javascript toe aan het einde van de pagina
        
        Argumenten
        js string  Javascript uit te voeren nadat de pagina gemaakt is
        """
        self._SlotScript.add (js)

