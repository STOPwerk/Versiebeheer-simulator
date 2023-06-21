#======================================================================
#
# Meldingen over de applicatie uitvoering
#
#----------------------------------------------------------------------
#
# Beheer van een verzameling meldingen over de uitvoering van de
# applicatie. Het verslag kan zowel in JSON (tbv testen) als HTML
# (voor mensen) opgeslagen worden.
#
#======================================================================
from typing import List, Dict, Set, Tuple

import time

from weergave_webpagina import WebpaginaGenerator

#======================================================================
# Enkele melding
#======================================================================
class Melding:

    def __init__ (self, ernst : str, tekst : str):
        """Maak een nieuwe melding aan
        
        ernst string Niveau van de melding (FOUT, LET OP, INFO, DETAIL)
        tekst string Tekst van de melding
        """
        self.Ernst : str = ernst
        self.Tekst : str = tekst
        # self.Tijd wordt apart gezet als dat nodig is

    def HtmlTabelRij (self, verbergDetail : bool) -> str:
        """Maak de HTMl voor de melding als een tij (tr) van een tabel.

        Argumenten:
        verbergDetail boolean  Verberg de detailmeldingen
        """
        style = self.Ernst.replace (' ', '')
        html = '<tr'
        if verbergDetail and self.Ernst == "DETAIL":
            html += ' style="display: none"'
        html += ' class="entry_' + style + '">'
        if hasattr (self, 'Tijd'):
            html += '<td class="message_detail">' + "{:.3f}".format(self.Tijd) + '</td>'
        html += '<td class="level_' + style + '">' + self.Ernst + '</td>'
        html += '<td class="message_' + style + ' main">' + self.Tekst + '</td>'
        html += '</tr>'
        return html

    Ernst_Fout = "FOUT"
    Ernst_Waarschuwing = "LET OP"
    Ernst_Informatie = "INFO"
    Ernst_Detail = "DETAIL"


#======================================================================
# Verzameling van meldingen
#======================================================================
class Meldingen:

#----------------------------------------------------------------------
# Aanmaken/verwijderen van nieuwe verzameling
#----------------------------------------------------------------------
    def __init__(self, metTijd):
        """Maak een nieuwe verzameling van meldingen actief.

        Argumenten:
        metTijd boolean  Geeft aan of bij elke melding de tijd sinds het 
                         aanmaken van de verzameling bijgehouden moet worden
        """
        # Het total aantal foutmeldingen dat onderdeel is van deze verzameling
        self.Fouten : int = 0
        # Het total aantal waarschuwingen dat onderdeel is van deze verzameling
        self.Waarschuwingen : int = 0
        # De lijst met instanties van Melding
        self.Meldingen : List[Melding] = []
        # De tijd dat de verzameling is aangemaakt / None als geen tijd bijgehouden hoeft te worden
        self._Start : float = time.perf_counter () if metTijd else None

#----------------------------------------------------------------------
# Toevoegen van een melding
#----------------------------------------------------------------------
    def Fout (self, tekst : str) -> Melding:
        "Meld een fout"
        self.Fouten += 1
        return self._Melding (Melding.Ernst_Fout, tekst)

    def Waarschuwing (self, tekst : str) -> Melding:
        "Meld een waarschuwing"
        self.Waarschuwingen += 1
        return self._Melding (Melding.Ernst_Waarschuwing, tekst)
    
    def Informatie (self, tekst : str) -> Melding:
        "Informatieve melding"
        return self._Melding (Melding.Ernst_Informatie, tekst)
    
    def Detail (self, tekst : str) -> Melding:
        "Debug/trace melding"
        return self._Melding (Melding.Ernst_Detail, tekst)

    def _Melding (self, ernst : str, tekst : str) -> Melding:
        """Maak een nieuwe melding aan en geeft de melding terug"""
        melding = Melding (ernst, tekst)
        if not self._Start is None:
            melding.Tijd = time.perf_counter() - self._Start
        self.Meldingen.append (melding)
        return melding

#----------------------------------------------------------------------
# Bewaren/tonen van de meldingen
# Roep deze methoden pas aan nadat de verzameling is afgesloten
#----------------------------------------------------------------------
    def ToonHtml (self, tabel_id : str, meldingen_pad : str, titel : str = None):
        """Toon de meldingen in de webbrowser

        Argumenten:
        tabel_id string  Naam van de tabel in de HTML  
        meldingen_pad string Pad naar de directory waar de HTML pagina geplaatst moet worden.
        titel string  Titel van een expandeerbaar paneel waarin de meldingen geplaatst worden
        """
        generator = WebpaginaGenerator (titel if titel else "Verslag")
        self.MaakHtml (generator, tabel_id, None)
        generator.SchrijfHtml (meldingen_pad, True, True)

    def MaakHtml (self, generator, tabel_id : str, titel : str, toelichting : str = None, toonFilter: bool = True, toonSamenvatting: bool = True):
        """Maak een webpagina met de meldingen

        Argumenten:
        generator WebpaginaGenerator  Generator voor een webpagina
        tabel_id string  Naam van de tabel in de HTML  
        titel string  Titel van een expandeerbaar paneel waarin de meldingen geplaatst worden
        toelichting string  Toelichting die voorafgaand aan de meldingen wordt geplaatst
        toonFilter bool Toon een filter om de verschillende soorten meldingen te kunnen filteren.
        toonSamenvatting bool Toon de samenvatting met het aantal fouten en waarschuwingen
        """
        if not titel is None:
            if toonSamenvatting and (self.Fouten > 0 or self.Waarschuwingen > 0):
                generator.VoegHtmlToe ('<p>Er ' + ('is' if self.Fouten + self.Waarschuwingen == 1 else 'zijn') + ' ')
                if self.Fouten > 0:
                    if self.Fouten == 1:
                        generator.VoegHtmlToe ('een foutmelding')
                    else:
                        generator.VoegHtmlToe (str(self.Fouten) + ' foutmeldingen')
                    if self.Waarschuwingen > 0:
                        generator.VoegHtmlToe (' en ')
                if self.Waarschuwingen == 1:
                    generator.VoegHtmlToe ('een waarschuwing')
                elif self.Waarschuwingen > 1:
                    generator.VoegHtmlToe (str(self.Waarschuwingen) + ' waarschuwingen')
                generator.VoegHtmlToe ('; klik op <i>' + titel + '</i> om deze te bekijken</p>')
            einde = generator.StartSectie (titel)
            if not toelichting is None:
                generator.VoegHtmlToe (toelichting)
        else:
            if not toelichting is None:
                generator.VoegHtmlToe (toelichting)
            if toonSamenvatting:
                generator.VoegHtmlToe ('<p><b>Fouten: ' + str(self.Fouten) + ', waarschuwingen: ' + str(self.Waarschuwingen) + '</b></p>')
            einde = None
        if toonFilter:
            generator.VoegHtmlToe (generator.LeesHtmlTemplate ("filter", False).replace ("@@@ID@@@", tabel_id))
        generator.VoegHtmlToe (generator.LeesHtmlTemplate ("start", False).replace ("@@@ID@@@", tabel_id))

        for melding in self.Meldingen:
            generator.VoegHtmlToe (melding.HtmlTabelRij (True))
            
        generator.LeesHtmlTemplate ("einde")
        generator.LeesJSTemplate ('')
        generator.VoegHtmlToe (einde)

    def MaakTekst (self) -> str:
        """Retourneer een platte tekst van de meldingen"""
        return "Fouten: " + str(self.Fouten) + ", waarschuwingen: " + str (self.Waarschuwingen) + "\n" + "\n".join (m.Ernst + " " + m.Tekst for m in self.Meldingen)

    def FoutenWaarschuwingen (self) -> List[Melding]:
        """Geef alleen de fouten en waarschuwingen onder de meldingen"""
        return [m for m in self.Meldingen if m.Ernst == "FOUT" or m.Ernst == "LET OP"]
