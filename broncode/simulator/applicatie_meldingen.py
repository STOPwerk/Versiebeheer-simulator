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

import time

from weergave_webpagina import WebpaginaGenerator

#======================================================================
# Enkele melding
#======================================================================
class Melding:

    def __init__ (self, ernst, tekst):
        """Maak een nieuwe melding aan
        
        ernst string Niveau van de melding (FOUT, LET OP, INFO, DETAIL)
        tekst string Tekst van de melding
        """
        self.Ernst = ernst
        self.Tekst = tekst
        # self.Tijd wordt apart gezet als dat nodig is

    def HtmlTabelRij (self, verbergDetail):
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
        self.Fouten = 0
        # Het total aantal waarschuwingen dat onderdeel is van deze verzameling
        self.Waarschuwingen = 0
        # De lijst met instanties van Melding
        self.Meldingen = []
        # De tijd dat de verzameling is aangemaakt / None als geen tijd bijgehouden hoeft te worden
        self._Start = time.perf_counter () if metTijd else None

#----------------------------------------------------------------------
# Toevoegen van een melding
#----------------------------------------------------------------------
    def Fout (self, tekst):
        "Meld een fout"
        self.Fouten += 1
        return self._Melding (Melding.Ernst_Fout, tekst)

    def Waarschuwing (self, tekst):
        "Meld een waarschuwing"
        self.Waarschuwingen += 1
        return self._Melding (Melding.Ernst_Waarschuwing, tekst)
    
    def Informatie (self, tekst):
        "Informatieve melding"
        return self._Melding (Melding.Ernst_Informatie, tekst)
    
    def Detail (self, tekst):
        "Debug/trace melding"
        return self._Melding (Melding.Ernst_Detail, tekst)

    def _Melding (self, ernst, tekst):
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
    def ToonHtml (self, meldingen_pad, titel = None):
        """Toon de meldingen in de webbrowser

        Argumenten:
        meldingen_pad string Pad naar de directory waar de HTML pagina geplaatst moet worden.
        titel string  Titel van een expandeerbaar paneel waarin de meldingen geplaatst worden
        """
        generator = WebpaginaGenerator (titel if titel else "Verslag")
        self.MaakHtml (generator, None)
        generator.SchrijfHtml (meldingen_pad, True, True)

    def MaakHtml (self, generator, titel, toelichting = None):
        """Maak een webpagina met de meldingen

        Argumenten:
        generator WebpaginaGenerator  Generator voor een webpagina
        titel string  Titel van een expandeerbaar paneel waarin de meldingen geplaatst worden
        toelichting string  Toelichting die voorafgaand aan de meldingen wordt geplaatst
        """
        if not titel is None:
            if self.Fouten > 0 or self.Waarschuwingen > 0:
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
            generator.VoegHtmlToe ('<p><b>Fouten: ' + str(self.Fouten) + ', waarschuwingen: ' + str(self.Waarschuwingen) + '</b></p>')
            einde = None
        generator.LeesHtmlTemplate ("start")
        generator.VoegHtmlToe ('<table id="meldingen_tabel">')

        for melding in self.Meldingen:
            generator.VoegHtmlToe (melding.HtmlTabelRij (True))

        generator.VoegHtmlToe ("</table>")
        generator.LeesHtmlTemplate ("einde")
        generator.VoegHtmlToe (einde)

    def MaakTekst (self):
        """Retourneer een platte tekst van de meldingen"""
        return "Fouten: " + str(self.Fouten) + ", waarschuwingen: " + str (self.Waarschuwingen) + "\n" + "\n".join (m.Ernst + " " + m.Tekst for m in self.Meldingen)

    def FoutenWaarschuwingen (self):
        """Geef alleen de fouten en waarschuwingen onder de meldingen"""
        return [m for m in self.Meldingen if m.Ernst == "FOUT" or m.Ernst == "LET OP"]
