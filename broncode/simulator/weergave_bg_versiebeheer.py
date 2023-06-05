#======================================================================
#
# Maakt een overzicht van de gegevens in het interne versiebeheer van
# het bevoegd gezag, als onderdeel van de webpagina met resultaten. 
#
#======================================================================
from pickle import FALSE
from typing import List, Dict, Set, Tuple

from data_bg_procesverloop import Activiteitverloop, Procesvoortgang, Branch
from data_bg_versiebeheer import Versiebeheerinformatie, Commit, Instrument, Instrumentversie
from data_doel import Doel
from weergave_webpagina import WebpaginaGenerator

class Weergave_BG_Versiebeheer:
    
#----------------------------------------------------------------------
#
# Indeling van de sectie
#
#----------------------------------------------------------------------
    @staticmethod
    def VoegToe (generator: WebpaginaGenerator, scenario):
        """Voeg een overzicht van het interne versiebeheer van het bevoegd gezag toe

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        weergave = Weergave_BG_Versiebeheer (generator, scenario.Procesvoortgang, scenario.BGVersiebeheerinformatie)
        weergave._VoegToe ();

    def __init__ (self, generator: WebpaginaGenerator, procesverloop : Procesvoortgang, versiebeheerInformatie : Versiebeheerinformatie):
        self._Generator = generator
        self._Procesverloop = procesverloop
        self._VersiebeheerInformatie = versiebeheerInformatie

    def _VoegToe (self):
        einde = self._Generator.StartSectie ("Intern versiebeheer", True)
        einde_t = self._Generator.StartToelichting ("Over het overzicht")
        self._Generator.LeesHtmlTemplate ('help')
        self._Generator.VoegHtmlToe (einde_t)

        self._Diagram ()

        idx = 0
        for activiteit in self._Procesverloop.Activiteiten:
            if len (activiteit.VersiebeheerVerslag.Meldingen) > 0 or len (activiteit.Commits) > 0:
                idx += 1
                self._Verslag (idx, activiteit)

        self._Generator.VoegHtmlToe (einde)
        self._Generator.LeesCssTemplate ('')
        self._Generator.LeesJSTemplate ('')

#----------------------------------------------------------------------
#
# Verslag en commits
#
#----------------------------------------------------------------------
    def _Verslag (self, idx, activiteit : Activiteitverloop):
        self._Generator.VoegHtmlToe ('<div class="bgvb_verslag" data-bgvba="' + activiteit.UitgevoerdOp + '">')
        self._Generator.VoegHtmlToe ('<table>')
        self._Generator.VoegHtmlToe ('<tr><th>Activiteit</th><td>' + activiteit.Naam + '</td></tr>')
        self._Generator.VoegHtmlToe ('<tr><th>Uitgevoerd op</th><td>' + activiteit.UitgevoerdOp.replace ("T00:00:00Z", "") + '</td></tr>')
        if len (activiteit.Projecten) > 1:
            self._Generator.VoegHtmlToe ('<tr><th>Projecten</th><td>' + ", ".join (sorted (activiteit.Projecten)) + '</td></tr>')
        elif len (activiteit.Projecten) == 1:
            self._Generator.VoegHtmlToe ('<tr><th>Project</th><td>' + list(activiteit.Projecten)[0] + '</td></tr>')
        if activiteit.UitgevoerdDoor != Activiteitverloop._Uitvoerder_BevoegdGezag:
            self._Generator.VoegHtmlToe ('<tr><th>Uitgevoerd door</th><td>' + activiteit.UitgevoerdDoor + '</td></tr>')
        self._Generator.VoegHtmlToe ('</table>')

        if len (activiteit.Commits) > 0:
            self._Generator.VoegHtmlToe ('<p><b>Versiebeheerinformatie</b><br/>(Bijgewerkte informatie is vetgedrukt)</p>')
            commits = sorted (activiteit.Commits, key=lambda c: self._BranchSorteerKey (c._Branch))

            volgnummers = set (c.Volgnummer for c in commits)
            if len (volgnummers) > 1:
                self._Generator.VoegHtmlToe ('<p>De eindgebruiker (of de simulator) wijzigt de versiebeheerinformatie meerdere keren tijdens deze activiteit</p>')
            self._Generator.VoegHtmlToe ('<table class="bgvb_info">')
            fase = 0
            for volgnummer in sorted (volgnummers):
                dezeCommits = [c for c in commits if c.Volgnummer == volgnummer]
                self._Generator.VoegHtmlToe ('<tr>')
                if len (volgnummers) > 1:
                    fase += 1
                    self._Generator.VoegHtmlToe ('<td rowspan="' + str(len(dezeCommits)) + '">#' + str(fase) + '</td>')

                startTR = ''
                for commit in dezeCommits:
                    self._Generator.VoegHtmlToe (startTR + '<td>Branch ' + commit._Branch._Doel.Naam + '<br/>(' + commit._Branch.InteractieNaam + ')</td><td><table>')
                    startTR = '<tr>'

                    versies : Dict[Instrument,Tuple[Instrumentversie,bool]] = {
                        **{ self._VersiebeheerInformatie.Instrumenten[w] : (v, False) for w, v in  commit.InstrumentversiesBijStart.items() },
                        **{ self._VersiebeheerInformatie.Instrumenten[w] : (v, True) for w, v in  commit.Instrumentversies.items() }
                    }
                    for instrument, (versie, gewijzigd) in sorted (versies.items (), key = lambda v: v[0].SorteerKey ()):
                        self._Generator.VoegHtmlToe ('<tr' + (' class="gewijzigd"' if gewijzigd else '') + '><td>' + instrument._Soort + '</td><td>' + instrument.Naam + '</td><td>:')

                        if versie.IsJuridischUitgewerkt:
                            if versie.ExpressionId is None:
                                self._Generator.VoegHtmlToe ('geen wijziging op deze branch (terugtrekking)')
                            else:
                                self._Generator.VoegHtmlToe ('juridisch uitgewerkt')
                        elif versie.ExpressionId is None:
                            self._Generator.VoegHtmlToe ('versie is onbekend / niet gespecificeerd')
                        else:
                            self._Generator.VoegHtmlToe (versie.ExpressionId)

                        self._Generator.VoegHtmlToe ('</td></tr>')

                    tijdstempels = commit.TijdstempelsBijStart
                    gewijzigd = False
                    if not commit.Tijdstempels is None and not commit.Tijdstempels.IsGelijkAan (commit.TijdstempelsBijStart):
                        gewijzigd= True
                        tijdstempels = commit.Tijdstempels
                    self._Generator.VoegHtmlToe ('<tr' + (' class="gewijzigd"' if gewijzigd else '') + '><td colspan="2">Tijdstempels</td><td>:')
                    if tijdstempels.JuridischWerkendVanaf is None:
                        self._Generator.VoegHtmlToe ('inwerkingtreding is onbekend')
                    else:
                        self._Generator.VoegHtmlToe ('juridisch werkend vanaf ' + tijdstempels.JuridischWerkendVanaf)
                        if not tijdstempels.GeldigVanaf is None:
                            self._Generator.VoegHtmlToe ('<br/>geldig vanaf ' + tijdstempels.GeldigVanaf)
                    self._Generator.VoegHtmlToe ('</td></tr>')

                    uitgangssituatie_renvooi = commit.Uitgangssituatie_Renvooi_BijStart
                    gewijzigd = False
                    if not commit.Uitgangssituatie_Renvooi is None and not commit.Uitgangssituatie_Renvooi.IsGelijkAan (uitgangssituatie_renvooi):
                        uitgangssituatie_renvooi = commit.Uitgangssituatie_Renvooi
                        gewijzigd = True
                    self._Generator.VoegHtmlToe ('<tr' + (' class="gewijzigd"' if gewijzigd else '') + '><td colspan="2">Renvooi ten opzichte van</td><td>:')
                    if uitgangssituatie_renvooi is None:
                        self._Generator.VoegHtmlToe ('geen renvooi mogelijk, eerste versie voor dit instrument')
                    else:
                        self._Generator.VoegHtmlToe ('branch ' + uitgangssituatie_renvooi._Branch._Doel.Naam + ', gemaaktOp = ' + uitgangssituatie_renvooi.GemaaktOp + '</td></tr>')
                    self._Generator.VoegHtmlToe ('</td></tr>')

                    self._Generator.VoegHtmlToe ('</table></td>')

                self._Generator.VoegHtmlToe ('</tr>')
            self._Generator.VoegHtmlToe ('</table>')

        if len (activiteit.VersiebeheerVerslag.Meldingen) > 0:
            self._Generator.VoegHtmlToe ('<p><b>Uitvoering van de activiteit</b></p>')
            activiteit.VersiebeheerVerslag.MaakHtml (self._Generator, 'act_log_' + str(idx), None, toonFilter=False, toonSamenvatting = False)

        self._Generator.VoegHtmlToe ('</div>')

    def _BranchSorteerKey (self, branch : Branch):
        return ((branch._OntstaanOp + '-' + branch._Doel.Naam) if branch.Project is None else self._Procesverloop.Projecten[branch.Project].GestartOp) + '\n' + branch._OntstaanOp

#----------------------------------------------------------------------
#
# Diagram met branches, momentopnamen en ver-/ontvlechtingen
#
#----------------------------------------------------------------------
    def _Diagram (self):
        diagram = Weergave_BG_Versiebeheer.SVGDiagram ()

        branches = list (sorted (self._VersiebeheerInformatie.Branches.values (), key = lambda b: self._BranchSorteerKey (b)))
        for branch in branches:
            diagram.SchrijfBranchTekst (branch)

        for activiteit in self._Procesverloop.Activiteiten:
            volgnummerUitlevering = None
            volgnummers : Set[int] = set ()
            if len (activiteit.Commits) > 0:
                volgnummers.update (c.Volgnummer for c in activiteit.Commits)

            if len (volgnummers) > 0:
                volgnummerKolom : Dict[int,int] = { v: k for k,v in enumerate (sorted (volgnummers)) }
                aantalKolommen = len (volgnummerKolom)
                diagram.SchrijfTijdstip (activiteit.UitgevoerdOp, aantalKolommen)

                for volgnummer in sorted (volgnummers):
                    for commit in activiteit.Commits:
                        if commit.Volgnummer == volgnummer:
                            diagram.TekenCommit (commit, volgnummerKolom[volgnummer], aantalKolommen, activiteit.UitgevoerdDoor == Activiteitverloop._Uitvoerder_BevoegdGezag)

        diagram.CompleteerSVG ()
        self._Generator.VoegHtmlToe ('<div class="bgvb_diagram" style="width: 1024px; height:500px">' + diagram.SVG + '</div>')
        self._Generator.GebruikSvgScript ()
        pass

    class SVGDiagram:
        def __init__(self):
            # Breedte tot nu toe
            self.Breedte = 0
            # Hoogte tot nu toe
            self.Hoogte = 0
            # Inner-SVG tot nu toe
            self.SVG = ''
            # Cache met (x,y,w,h) positie van een element (Commit of Branch of tijdstip)
            self._Positie : Dict[object,Tuple[int,int,int,int]] = {}

        def _Registreer (self, item, x, y, w, h):
            self._Positie[item] = (x, y, w, h)
            t = x + w
            if t > self.Breedte:
                self.Breedte = t
            t = y + h
            if t > self.Hoogte:
                self.Hoogte = t

        _SvgElementBreedte = 45 # Breedte van een momentopname rechthoek in diagram-eenheden
        _SvgHalveElementBreedte = int(_SvgElementBreedte/2)
        _SvgElementHoogte = 30 # Hoogte van een momentopname rechthoek in diagram-eenheden
        _SvgHalveElementHoogte = int (_SvgElementHoogte/2)
        _SvgDatumBreedte = 50 # Breedte van de tekst met een datum
        _SvgTijdstipBreedte = 100 # Breedte van de tekst met een tijdstip
        _SvgNaamBreedte = 100 # Breedte van de naam van een branch
        _Svg_Punt_d = 7 # Afstand punt-punt tot raakpunt haaks op de lijn
        _Svg_Punt_0 = 4 # Afstand punt - raakpunt langs de lijn
        _Svg_Punt_1 = 5 # Afstand punt-punt - raakpunt langs de lijn

        def SchrijfBranchTekst (self, branch : Branch):
            x = 0
            y = (self._SvgElementHoogte if self.Hoogte == 0 else self.Hoogte) + self._SvgHalveElementHoogte
            w = self._SvgNaamBreedte
            h = self._SvgElementHoogte
            self._Registreer (branch, x, y, self._SvgNaamBreedte, self._SvgElementHoogte)
            self.SVG += '<text x="{x}" y="{y}" dominant-baseline="middle" text-anchor="start" class="bgvbd_txt">{tekst}</text>\n'.format (x = x + self._SvgHalveElementBreedte, y = y + self._SvgHalveElementHoogte, tekst = branch._Doel.Naam)

        def SchrijfTijdstip (self, gemaaktOp : str, aantalKolommen : int):
            label = gemaaktOp.replace ("T00:00:00Z", "")
            x = self.Breedte + self._SvgHalveElementBreedte
            y = 0
            if aantalKolommen == 1:
                w = self._SvgNaamBreedte if len(label) < len(gemaaktOp) else self._SvgTijdstipBreedte
            else:
                w = self._SvgDatumBreedte + (aantalKolommen -1) * (self._SvgElementBreedte + self._SvgHalveElementBreedte)
            h = self._SvgElementHoogte
            self._Registreer (gemaaktOp, x, y, w, h)
            self.SVG += '<text x="{x}" y="{y}" dominant-baseline="hanging" text-anchor="middle" class="bgvbd_txt" data-bgvba="{act}">{tekst}</text>\n'.format (x = x + int(w/2), y = y + self._SvgHalveElementHoogte, tekst = label, act=gemaaktOp)
            if aantalKolommen > 1:
                wl = int ((w- self._SvgDatumBreedte)/2)
                self.SVG += '<path d="M {xb} {y} L {xe} {y}" class="bgvbd_txt_l" data-bgvba="{act}"/>\n'.format (xb = x + int(w/2) - wl, xe = x + int(w/2) + wl, y = y + h, act=gemaaktOp)

        def TekenCommit (self, commit : Commit, kolom: int, aantalKolommen : int, doorBG : bool):

            x,y,w,h = self._Positie[commit.GemaaktOp]
            xCommit = x + int (w/2) - int (((aantalKolommen - 2 * kolom) * (self._SvgElementBreedte + self._SvgHalveElementBreedte) - self._SvgHalveElementBreedte) / 2)
            xBranch,yBranch,wBranch,hBranch = self._Positie[commit._Branch]
            yCommit = yBranch + int (hBranch/2) - self._SvgHalveElementHoogte
            wCommit = self._SvgElementBreedte
            hCommit = self._SvgElementHoogte
            self._Registreer (commit, xCommit, yCommit, wCommit, hCommit)
            self.SVG += '<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" ry="3" class="bgvbd_mo_{cls}" data-bgvba="{act}"></rect>\n'.format (x = xCommit, y = yCommit, w = wCommit, h = hCommit, act=commit.GemaaktOp, cls = 'bg' if doorBG else 'a')

            if not commit.SoortUitwisseling is None:
                if commit.SoortUitwisseling == Commit._Uitwisseling_Adviesbureau_Naar_BG:
                    symbol = "&#8658;"
                elif commit.SoortUitwisseling == Commit._Uitwisseling_BG_Naar_Adviesbureau:
                    symbol = "&#8658;"
                if commit.SoortUitwisseling == Commit._Uitwisseling_BG_Naar_LVBB:
                    symbol = "&#8657;"
                if commit.SoortUitwisseling == Commit._Uitwisseling_LVBB_Naar_Adviesbureau:
                    symbol = "&#8659;"
                self.SVG += '<text x="{x}" y="{y}" dominant-baseline="middle" text-anchor="middle" class="bgvbd_txt">{tekst}</text>\n'.format (x = xCommit + int(wCommit/2), y = yCommit + int (hCommit/2), tekst = symbol)

            if commit != commit._Branch.Commits[0]:
                # Teken een lijn naar het vorige element op de branch
                self.SVG += '<path d="M {xb} {y} L {xe} {y}" class="bgvbd_line_{c}"/>\n'.format (xb = xBranch + wBranch, xe = xCommit, y = yCommit + int(hCommit/2), c = "branch" if commit.Basisversie is None else "exbranch")


            def _LijnEnPijl (ander, dx, dy, t_dy, top, cls):
                dx = int (dx * self._SvgHalveElementBreedte)
                dy = int (dy * self._SvgHalveElementBreedte)
                t_dy = int (t_dy * self._SvgHalveElementHoogte)
                x,y,w,h = self._Positie[ander]
                xb = x + w
                xt1 = xb + dx
                xt2 = xCommit - self._SvgHalveElementBreedte + dx
                if xt2 <= xt1 + 2:
                    xt2 = xt1
                xe = xCommit
                if y < yCommit:
                    yb = y + int(h/2) + dy
                    yt1 = y + h + t_dy
                    yt2 = yCommit - t_dy
                    ye = yCommit + int (hCommit/2) - dy
                    if yt2 <= yt1 + 2:
                        yt2 = yt1
                else:
                    yb = y
                    yt1 = y - t_dy
                    yt2 = yCommit + hCommit + t_dy
                    ye = yCommit + int (hCommit/2) + dy
                    if yt1 <= yt2 + 2:
                        yt1 = yt2
                self.SVG += '<path d="M {xb} {yb} L {xt1} {yb}'.format (xb=xb, xt1=xt1, yb=yb, yt1=yt1)
                if top:
                    self.SVG += ' L {xt1} {yt1}'.format (xb=xb, xt1=xt1, yb=yb, yt1=yt1)
                    if xt1 != xt2:
                        self.SVG += ' L {xt2} {yt1}'.format (xt2=xt2, yt1=yt1)
                    if yt1 != yt2:
                        self.SVG += ' L {xt2} {yt2}'.format (xt2=xt2, yt2=yt2)
                else:
                    self.SVG += ' L {xt1} {yt2}'.format (xb=xb, xt1=xt1, yt2=yt2)
                    if xt1 != xt2:
                        self.SVG += ' L {xt2} {yt2}'.format (xt2=xt2, yt2=yt2)
                self.SVG += ' L {xt2} {ye} L {xe} {ye}" class="bgvbd_line_{cls}"/>\n'.format (xt2=xt2, xe=xe, ye=ye, cls=cls)
                self.SVG += '<path d="M {xe} {ye} L {xep1} {yep1} L {xep0} {ye} L {xep1} {yep_1} Z" class="bgvbd_line_{cls}_p"/>\n'.format (xe=xe, ye=ye, xep0=xe-self._Svg_Punt_0, xep1=xe-self._Svg_Punt_1, yep_1=ye-self._Svg_Punt_d, yep1=ye+self._Svg_Punt_d, cls=cls)

            if not commit.Basisversie is None:
                # Teken de (nieuwe) basisversie
                _LijnEnPijl (commit.Basisversie, 0.5, 0, 0.25, False, "basis")

            for versie in commit.VervlochtenVersie:
                # Teken de vervlochten
                _LijnEnPijl (versie, 0.25, 0.5, 0.5, True, "vv")

            for versie in commit.OntvlochtenVersie:
                # Teken de vervlochten
                _LijnEnPijl (versie, 0.375, -0.5, 0.375, True, "ov")


            # Dit is nu het laatste element op de branch
            self._Registreer (commit._Branch, xCommit + wCommit, yBranch, 0, hBranch)
 
        def CompleteerSVG (self):
            self.Breedte += self._SvgHalveElementBreedte
            self.Hoogte += self._SvgHalveElementHoogte
            self.SVG = '<svg id="bgvb_svg" xmlns="http://www.w3.org/2000/svg" style="display: inline; width: 100%; height: 100%;" viewBox="0 0 ' + str(self.Breedte) + ' ' + str(self.Hoogte) + ' " version="1.1">\n' + self.SVG + 'Deze browser ondersteunt geen SVG\n</svg>'
