#======================================================================
#
# Maakt een selector voor de keuze van de uitwisseling (via gemaaktOp)
# als onderdeel van de webpagina met resultaten
#
#======================================================================

from weergave_webpagina import WebpaginaGenerator

class Weergave_Uitwisselingselector:
    
    def __init__ (self, scenario):
        """Maak de weergavegenerator aan

        Argumenten:

        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        # De gemaaktOp voor de beschikbare uitwisselingen
        self._Waarden = [u.GemaaktOp for u in reversed (scenario.Versiebeheerinformatie.Uitwisselingen)]
        # De titels voor de uitwisselingen
        # key = gemaaktOp, value = titel
        self._Optie = { w: w for w in self._Waarden }
        self._Naam = { w: w for w in self._Waarden }
        self._Beschrijving = { w: '' for w in self._Waarden }
        # Benoemde uitwisselingen die beschikbaar zijn
        self._Benoemd = []
        self._HeeftBeschrijving = False
        for benoemd in scenario.Opties.Uitwisselingen:
            if benoemd.GemaaktOp in self._Optie:
                self._Benoemd.append (benoemd)
                self._Optie[benoemd.GemaaktOp] = benoemd.GemaaktOp + " " + benoemd.Naam
                self._Naam[benoemd.GemaaktOp] = benoemd.Naam
                if benoemd.Beschrijving:
                    self._Beschrijving[benoemd.GemaaktOp] = benoemd.Beschrijving
                    self._HeeftBeschrijving = True
        if len (self._Waarden) > 1:
            # De waarde die als eerste getoond moet worden
            self._StartWaarde = self._Waarden[0] if len (self._Benoemd) == 0 else self._Benoemd[0].GemaaktOp

    def AttributenToonVoor (self, gemaaktOp):
        """Geef de attributen die aan een HTML element toegevoegd moeten worden zodat de zichtbaarheid van
        het element overeenkomt met de selectie in de selector

        Argumenten:
        gemaaktOp string  Tijdstip van de uitwisseling waarvan dit element de resultaten toont
        """
        if len (self._Waarden) <= 1:
            return ''
        # style="display: none" werkt niet altijd goed, doe de startsituatie via javascript
        return ' data-u="' + gemaaktOp + '" '

    def AttributenToonIn (self, gemaaktOpVanaf, gemaaktOpTot):
        """Geef de attributen die aan een HTML element toegevoegd moeten worden zodat de opmaak van
        het element overeenkomt met de selectie in de selector.

        Argumenten:
        gemaaktOpVanaf string  Tijdstip van de eerste uitwisseling waarvoor dit element de resultaten toont
        gemaaktOpTot string  Tijdstip van de eerste uitwisseling waarvoor dit element de resultaten niet meer toont
        """
        if len (self._Waarden) <= 1:
            return ''
        # style="display: none" werkt niet altijd goed, doe de startsituatie via javascript
        return ' data-uv="' + gemaaktOpVanaf + ('" data-ut="' + gemaaktOpTot if gemaaktOpTot else '') + '" '

    def VoegSelectorToe (self, generator: WebpaginaGenerator):
        """Als er meerdere uitwisselingen zijn, voeg dan een selector toe om een 
        uitwisseling te kiezen.

        Argumenten:
        generator WebpaginaGenerator  Generator voor de webpagina
        """
        if len (self._Waarden) <= 1:
            return
        generator.LeesCssTemplate ("")
        html = generator.LeesHtmlTemplate ("", False)
        html = html.replace ("<!--START-->", self._StartWaarde)
        html = html.replace ("<!--BENOEMD-->", ''.join ('<div class="uitwisselingselectorknop" data-uw="' + b.GemaaktOp + ('" title="' + b.Beschrijving if b.Beschrijving else '') + '">' + b.Naam + '</div>'for b in sorted (self._Benoemd, key = lambda x: x.GemaaktOp)))
        opties = ''
        for gemaaktOp in self._Waarden:
            opties += '<option value="' + gemaaktOp + '"' + (' selected' if gemaaktOp == self._StartWaarde else '') + '>' + self._Optie[gemaaktOp] + '</option>\n'
        html = html.replace ("<!--OPTIES-->", opties)

        generator.VoegHtmlToe (html)
        generator.VoegSlotScriptToe (generator.LeesJSTemplate ("", False).replace ("<!--START-->", self._StartWaarde))

    def VoegBeschrijvingToe (self, generator: WebpaginaGenerator):
        """Als er beschrijvingen zijn voor uitwisselingen, voeg die dan toe aan de pagina.

        Argumenten:
        generator WebpaginaGenerator  Generator voor de webpagina
        """
        if not self._HeeftBeschrijving:
            return
        generator.VoegHtmlToe ('<p>')
        einde = generator.StartToelichting ('Geselecteerde uitwisseling')
        generator.VoegHtmlToe (''.join ('<div' + self.AttributenToonVoor (gemaaktOp) + '>Getoond worden de resultaten na de uitwisseling: <b>' + self._Naam[gemaaktOp] + '</b><br/>' + self._Beschrijving[gemaaktOp] + '</div>' for gemaaktOp in self._Waarden))
        generator.VoegHtmlToe (einde)
        generator.VoegHtmlToe ('</p>')
