#======================================================================
#
# Maakt een overzicht van de gegevens in het interne versiebeheer van
# het bevoegd gezag, als onderdeel van de webpagina met resultaten. 
#
#======================================================================

from typing import Dict
from applicatie_scenario import Scenario
from data_doel import Doel
from weergave_data_bg_versiebeheer import VersiebeheerWeergave
from weergave_webpagina import WebpaginaGenerator

class Weergave_BG_Versiebeheer:
    
#----------------------------------------------------------------------
#
# Indeling van de sectie
#
#----------------------------------------------------------------------
    @staticmethod
    def VoegToe (generator: WebpaginaGenerator, scenario : Scenario):
        """Voeg een overzicht van het interne versiebeheer van het bevoegd gezag toe

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        weergave = Weergave_BG_Versiebeheer (generator, scenario)
        weergave.__VoegSectieToe ('<h3>Intern versiebeheer bevoegd gezag</h3>', 'help_versiebeheer', lambda v: weergave._VoegVersiebeheerToe (v))
        weergave.__VoegSectieToe ('Overzicht consolidatie', 'help_consolidatie', lambda v: weergave._VoegConsolidatieToe (v))
        generator.LeesCssTemplate ('')
        generator.LeesJSTemplate ('')

    def __init__ (self, generator: WebpaginaGenerator, scenario : Scenario):
        """Maak de generator voor de weergave

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """
        self._Generator = generator
        # Alleen de projectacties met versiebeheer als resultaat zijn relevant
        self._Resultaten = [resultaat for resultaat in scenario.Projectvoortgang.Projectacties if not resultaat._Versiebeheer is None]
        # Sorteer de doelen op aflopende juridischWerkendVanaf, daarna op identificatie
        sortering : Dict[Doel,str] = { }
        for resultaat in self._Resultaten:
            for branch in resultaat._Versiebeheer.Branches.values ():
                waarde = ('-' if branch.InterneTijdstempels.JuridischWerkendVanaf is None else branch.InterneTijdstempels.JuridischWerkendVanaf) + str(branch._Doel)
                huidig = sortering.get (branch._Doel)
                if huidig is None or huidig < waarde:
                    sortering[branch._Doel] = waarde
        self._Doelen = list (reversed (sorted (sortering.keys (), key = lambda d: sortering[d])))

    def __VoegSectieToe (self, titel : str, help : str, inhoud):
        einde = self._Generator.StartSectie (titel, True)

        einde_t = self._Generator.StartToelichting ("Over het overzicht")
        self._Generator.LeesHtmlTemplate (help)
        self._Generator.VoegHtmlToe (einde_t)

        for idx, resultaat in enumerate (self._Resultaten):
            self._Generator.VoegHtmlToe ('<div data-pav="' + resultaat._Projectactie.UitgevoerdOp + '"')
            if idx < len (self._Resultaten) -1:
                self._Generator.VoegHtmlToe (' data-pat="' + self._Resultaten[idx+1]._Projectactie.UitgevoerdOp + '"')
            self._Generator.VoegHtmlToe ('>\n')
            inhoud (resultaat._Versiebeheer)
            self._Generator.VoegHtmlToe ('\n</div>\n')

        self._Generator.VoegHtmlToe (einde)

#----------------------------------------------------------------------
#
# Intern versiebeheer
#
#----------------------------------------------------------------------
    def _VoegVersiebeheerToe (self, versiebeheer : VersiebeheerWeergave):
        """Voeg een overzicht van de staat van het interne versiebeheer toe

        Argumenten:

        versiebeheer VersiebeheerWeergave  Staat van het interne versiebeheer na de projectactie
        """
        self._Generator.VoegHtmlToe ('<dl>')

        for doel in self._Doelen:
            branch = versiebeheer.Branches.get (doel)
            if branch is None:
                continue

            self._Generator.VoegHtmlToe ('<dt>Branch/doel: <b>' + str(branch._Doel) + '</b></dt><dd><table class="bgvb_overzicht">')

            if branch._ViaProject:
                self._Generator.VoegHtmlToe ('<tr><th>Uitgangssituatie</th><td>')
                if not branch.Uitgangssituatie_Doel is None:
                    self._Generator.VoegHtmlToe ('Instrumentversies van branch ' + str(branch.Uitgangssituatie_Doel._Doel))
                elif not branch.Uitgangssituatie_GeldigOp is None:
                    self._Generator.VoegHtmlToe ('Regelgeving geldig op ' + branch.Uitgangssituatie_GeldigOp)
                else:
                    self._Generator.VoegHtmlToe ('Geen; initiële versie')
                self._Generator.VoegHtmlToe ('</td></tr>')
            else:
                self._Generator.VoegHtmlToe ('<tr><td colspan="2">Deze branch wordt in een van de overige projecten bijgehouden; intern versiebeheer is niet beschikbaar</td></tr>')
            
            for workId in sorted (branch.Instrumentversies.keys ()):
                instrumentInfo = branch.Instrumentversies[workId]
                self._Generator.VoegHtmlToe ('<tr><th>Instrument</th><td>')
                if not branch._ViaProject and not instrumentInfo.IsGewijzigd:
                    self._Generator.VoegHtmlToe (workId + '<br>Instrument wordt niet gewijzigd voor dit doel')
                elif instrumentInfo.Instrumentversie is None:
                    self._Generator.VoegHtmlToe (workId + '<br>Nog geen instrumentversie gemaakt')
                else:
                    if instrumentInfo.Instrumentversie.IsJuridischUitgewerkt:
                        self._Generator.VoegHtmlToe (workId + '<br>Juridisch uitgewerkt')
                    elif instrumentInfo.Instrumentversie.ExpressionId is None:
                        self._Generator.VoegHtmlToe (workId + '<br>Onbekende instrumentversie')
                    else:
                        self._Generator.VoegHtmlToe (instrumentInfo.Instrumentversie.ExpressionId)
                    if len (instrumentInfo.Instrumentversie.UitgewisseldVoor) > 0:
                        self._Generator.VoegHtmlToe ('<br>&nbsp;&nbsp;Voor doelen: ' + ',<br>&nbsp;&nbsp;&nbsp;&nbsp;'.join (str(d) for d in instrumentInfo.Instrumentversie.UitgewisseldVoor))

                if branch._ViaProject:
                    if not instrumentInfo.Uitgangssituatie is None:
                        if instrumentInfo.Uitgangssituatie.IsJuridischUitgewerkt:
                            self._Generator.VoegHtmlToe ('<br>Uitgangssituatie: juridisch uitgewerkt')
                        elif instrumentInfo.Uitgangssituatie.ExpressionId is None:
                            self._Generator.VoegHtmlToe ('<br>Uitgangssituatie: onbekende instrumentversie')
                        else:
                            self._Generator.VoegHtmlToe ('<br>Uitgangssituatie: ' + instrumentInfo.Uitgangssituatie.ExpressionId)
                        self._Generator.VoegHtmlToe ('<br>&nbsp;&nbsp;Voor doel: ' + ',<br>&nbsp;&nbsp;&nbsp;&nbsp;'.join (str(d) for d in instrumentInfo.Uitgangssituatie.UitgewisseldVoor))
                        if not instrumentInfo.Uitgangssituatie.UitgewisseldOp is None:
                            self._Generator.VoegHtmlToe ('<br>&nbsp;&nbsp;Laatst uitgewisseld: gemaaktOp = ' + instrumentInfo.Uitgangssituatie.UitgewisseldOp)
                    self._Generator.VoegHtmlToe ('<brInstrument wordt ' + ('' if instrumentInfo.IsGewijzigd else 'niet ') + 'gewijzigd voor dit doel')

                    if not instrumentInfo.UitgewisseldeVersie is None:
                        self._Generator.VoegHtmlToe ('<br>Laatste uitwisseling: gemaaktOp = ' + instrumentInfo.UitgewisseldeVersie.UitgewisseldOp)
                        if instrumentInfo.UitgewisseldeVersie.IsJuridischUitgewerkt:
                            self._Generator.VoegHtmlToe ('<br>&nbsp;&nbsp;Als: Intrekking')
                        elif instrumentInfo.UitgewisseldeVersie.ExpressionId is None:
                            self._Generator.VoegHtmlToe ('<br>&nbsp;&nbsp;Als: onbekende instrumentversie')
                        else:
                            self._Generator.VoegHtmlToe ('<br>&nbsp;&nbsp;Wordt-versie: ' + instrumentInfo.UitgewisseldeVersie.ExpressionId)
                            if not instrumentInfo.UitgewisseldeWasVersie is None:
                                self._Generator.VoegHtmlToe ('<br>&nbsp;&nbsp;Was-versie: ' + instrumentInfo.UitgewisseldeWasVersie)
                        if len (instrumentInfo.UitgewisseldeVersie.UitgewisseldVoor) > 0:
                            self._Generator.VoegHtmlToe ('<br>&nbsp;&nbsp;Voor doelen: ' + ',<br>&nbsp;&nbsp;&nbsp;&nbsp;'.join (str(d) for d in instrumentInfo.UitgewisseldeVersie.UitgewisseldVoor))
                else:
                    self._Generator.VoegHtmlToe ('<br>Laatste uitwisseling: gemaaktOp = ' + instrumentInfo.UitgewisseldeVersie.UitgewisseldOp)

                self._Generator.VoegHtmlToe ('</td></tr>')

            self._Generator.VoegHtmlToe ('<tr><th>Tijdstempels</th><td>')
            if branch.Tijdstempels.JuridischWerkendVanaf is None:
                self._Generator.VoegHtmlToe ('Geen tijdstempels gespecificeerd')
            else:
                self._Generator.VoegHtmlToe ('Juridisch werkend vanaf: ' + branch.Tijdstempels.JuridischWerkendVanaf)
                if not branch.Tijdstempels.GeldigVanaf is None:
                    self._Generator.VoegHtmlToe ('<br>Geldig vanaf: ' + branch.Tijdstempels.GeldigVanaf)
            if branch._ViaProject and not branch.Tijdstempels.IsGelijkAan (branch.UitgewisseldeTijdstempels):
                self._Generator.VoegHtmlToe ('<br>Tijdstempels moeten nog uitgewisseld worden')
            self._Generator.VoegHtmlToe ('</td></tr>')

            self._Generator.VoegHtmlToe ('</table></dd>')


        self._Generator.VoegHtmlToe ('</table>')

#----------------------------------------------------------------------
#
# Consolidatie
#
#----------------------------------------------------------------------
    def _VoegConsolidatieToe (self, versiebeheer : VersiebeheerWeergave):
        """Voeg een overzicht van de staat van het consolidatieproces toe

        Argumenten:

        versiebeheer VersiebeheerWeergave  Staat van het interne versiebeheer na de projectactie
        """
        self._Generator.VoegHtmlToe ('<b>TODO</b>')
