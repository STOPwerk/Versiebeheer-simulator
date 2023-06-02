#======================================================================
#
# Maakt een overzicht van de activiteiten van BG en adviesbureaus
# als onderdeel van de webpagina met resultaten. Via dit overzicht
# is ook een activiteit te selecteren, en tevens een uitwisseling als een 
# activiteit tot een uitwisseling leidt.
#
#======================================================================

from applicatie_scenario import Scenario
from data_bg_procesverloop import Activiteitverloop, Procesvoortgang
from data_bg_versiebeheer import Versiebeheerinformatie
from weergave_webpagina import WebpaginaGenerator

class Weergave_BG_Proces:
    
#======================================================================
#
# Sectie indeling
#
#======================================================================
    def VoegToe (generator: WebpaginaGenerator, scenario : Scenario):
        """Voeg een overzicht van de uitwisselingen toe

        Argumenten:

        generator WebpaginaGenerator  Generator voor de webpagina
        scenario Scenario  Scenario waar de generator voor gemaakt wordt
        """

        weergave = Weergave_BG_Proces (generator, scenario.Procesvoortgang)
        weergave._VoegToe ();

    def __init__ (self, generator: WebpaginaGenerator, procesverloop : Procesvoortgang):
        self._Generator = generator
        self._Procesverloop = procesverloop

    def _VoegToe (self):
        einde = self._Generator.StartSectie ("<h3>Procesverloop</h3>", True)
        einde_t = self._Generator.StartToelichting ("Over het overzicht")
        self._Generator.LeesHtmlTemplate ('help')
        self._Generator.VoegHtmlToe (einde_t)

        self._Generator.VoegHtmlToe ('<p><table class="w100"><tr><th>Activiteiten</th><th>Uitvoering</th><th>Status consolidatie</th></tr><tr><td rowspan="3" class="nw">')
        self._Activiteiten ()
        self._Generator.VoegHtmlToe ('</td><td rowspan="3" class="w100">')
        self._ActiviteitUitvoering ()
        self._Generator.VoegHtmlToe ('</td><td class="nw" style="height: 1px">')
        self._Consolidatiestatus ()
        self._Generator.VoegHtmlToe ('</td></tr><tr><th class="nw" style="height: 1px">Onderhanden besluiten</th></tr><tr><td class="nw">')
        self._Besluiten ()
        self._Generator.VoegHtmlToe ('</td></tr></table></p>')

        self._Generator.VoegHtmlToe (einde)
        self._Generator.LeesCssTemplate ('')
        self._Generator.LeesJSTemplate ('')

#======================================================================
#
# Activiteiten en de uitvoering daarvan
#
#======================================================================
    def _Activiteiten (self):

        # Overzicht van de activiteiten
        toonUitvoerder = False
        for verloop in self._Procesverloop.Activiteiten:
            if verloop.UitgevoerdDoor != verloop._Uitvoerder_BevoegdGezag:
                toonUitvoerder = True
                break

        projecten = list (sorted (self._Procesverloop.Projecten.values (), key=lambda p: p.GestartOp))
        self._Generator.VoegHtmlToe ('<p><table class="activiteiten_overzicht"><tr>')
        for idx, project in enumerate (projecten):
            self._Generator.VoegHtmlToe ('<tr>')
            if idx > 0:
                self._Generator.VoegHtmlToe ('<th class="ph2" rowspan="' + str (len(projecten)-idx+1) + '">&nbsp;</th>')
            self._Generator.VoegHtmlToe ('<th class="ph1" colspan="' + str(len(projecten)-idx+1) + '">' + project.Naam + '</th>')
            self._Generator.VoegHtmlToe ('</tr>')
        self._Generator.VoegHtmlToe ('<tr><th class="ph2">&nbsp;</th><th class="nw">Activiteit</th></tr>')
            
        for activiteit in self._Procesverloop.Activiteiten:
            self._Generator.VoegHtmlToe ('<tr data-bga="' + activiteit.UitgevoerdOp + '"')
            if len (activiteit.Uitgewisseld) > 0:
                self._Generator.VoegHtmlToe (' class="uw"')
            self._Generator.VoegHtmlToe ('>')
            for project in projecten:
                self._Generator.VoegHtmlToe ('<td class="c">' + ('&#x2714;' if project.Naam in activiteit.Projecten else '') + '</td>')
            self._Generator.VoegHtmlToe ('<td class="nw">' + activiteit.Naam)
            if activiteit.UitgevoerdDoor != Activiteitverloop._Uitvoerder_BevoegdGezag:
                self._Generator.VoegHtmlToe ('<br/>(' + activiteit.UitgevoerdDoor + ')')
            self._Generator.VoegHtmlToe ('</td></tr>')

        self._Generator.VoegHtmlToe ('</table></p>')

    def _ActiviteitUitvoering (self):
        for activiteit in self._Procesverloop.Activiteiten:
            self._Generator.VoegHtmlToe ('<div class="activiteit_uitvoering" data-bga="' + activiteit.UitgevoerdOp + '"><table>')
            self._Generator.VoegHtmlToe ('<tr><th>Activiteit</th><td>' + activiteit.Naam + '</td></tr>')
            self._Generator.VoegHtmlToe ('<tr><th>Uitgevoerd op</th><td>' + activiteit.UitgevoerdOp.replace ("T00:00:00Z", "") + '</td></tr>')
            if activiteit.UitgevoerdDoor != Activiteitverloop._Uitvoerder_BevoegdGezag:
                self._Generator.VoegHtmlToe ('<tr><th>Uitgevoerd door</th><td>' + activiteit.UitgevoerdDoor + '</td></tr>')
            self._Generator.VoegHtmlToe ('</table>')
            if not activiteit.Beschrijving is None:
                self._Generator.VoegHtmlToe ('<p><b>Beschrijving</b><br/>' + activiteit.Beschrijving + '</p>')
            if len (activiteit.InteractieVerslag) > 0:
                self._Generator.VoegHtmlToe ('<p><b>Interactie eindgebruiker - software</b></p><table>')
                laatsteType = None
                for melding in activiteit.InteractieVerslag:
                    if melding.IsInstructie != laatsteType:
                        if not laatsteType is None:
                            self._Generator.VoegHtmlToe ('</ul></td></tr>')
                        laatsteType = melding.IsInstructie
                        self._Generator.VoegHtmlToe ('<tr><td>' + ('Instructie' if melding.IsInstructie else 'Eindgebruiker') + '</td><td><ul>')
                    self._Generator.VoegHtmlToe ('<li>' + melding.Melding + '</li>')
                self._Generator.VoegHtmlToe ('</ul></td></tr></table>')
            self._Generator.VoegHtmlToe ('</div>')

#======================================================================
#
# Status van de consolidatie bij BG
#
#======================================================================
    def _Consolidatiestatus (self):
        self._Generator.VoegHtmlToe ('TODO')

#======================================================================
#
# Onderhanden besluiten
#
#======================================================================
    def _Besluiten (self):
        self._Generator.VoegHtmlToe ('TODO')
