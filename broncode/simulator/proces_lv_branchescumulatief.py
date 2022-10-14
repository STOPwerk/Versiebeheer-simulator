#======================================================================
#
# Bepaling van de bijdrage van de verschillende branches uit het
# versiebeheer voor een instrument tot en met een gegeven momentopname
#
#======================================================================
#
# In de uitgewisselde ConsolidatieInformatie wordt de positie van een
# momentopname relatief ten opzichte van andere momentopnamen gegeven.
# Voor de bepaling van de inhoud van een toestand is een cumulatief
# overzicht nodig: welke (delen van) branches dragen al dan niet bij?
#
# In STOP staan de regels beschreven hoe het cumulatieve overzicht
# opgebouwd kan worden. Een applicatie kan dan on-demand doen. Deze
# applicatie voert de bepaling uit na ontvangst van de uitwisseling
# en bewaart het resultaat bij de betreffende momentopname.
#
#======================================================================

from typing import List

from applicatie_meldingen import Meldingen
from data_doel import Doel
from data_lv_versiebeheerinformatie import Instrument, MomentopnameInstrument, BranchBijdrage

class AccumuleerBranchInformatie:

    @staticmethod
    def VoorMomentopname (log : Meldingen, momentopname : MomentopnameInstrument) -> bool:
        """Bepaal de cumulatieve bijdragen van alle branches inclusief de opgegeven momentopname en
        bewaar het resultaat in momentopname.BranchesCumulatief.

        Argumenten:

        log Meldingen  Verzameling meldingen voor de verwerking van versiebeheerinformatie
        momentopname MomentopnameInstrument  Momentopname waarvoor de accumulatie wordt uitgevoerd

        Geeft terug of de accumulatie zonder fouten is verlopen
        """
        accumulator = AccumuleerBranchInformatie (log, momentopname)
        accumulator._VoegBasisversiesToe (momentopname.Basisversies.values ())
        for versie in momentopname.OntvlochtenMet.values ():
            accumulator._OntvlechtMet (versie)
        for versie in momentopname.VervlochtenMet.values ():
            accumulator._VervlechtMet (versie)
        for doel in momentopname.Doelen:
            accumulator.BranchesCumulatief[doel] = BranchBijdrage (momentopname.GemaaktOp)
        momentopname.BranchesCumulatief = accumulator.BranchesCumulatief
        return accumulator._Valideer ()

    @staticmethod
    def VoorToestand (instrument: Instrument, inwerkingtredingsdoelen : List[Doel]):
        """Bepaal de cumulatieve bijdragen van alle branches die leiden tot de toestand.

        Argumenten:

        instrument Instrument  Instrument waarvoor de toestand gemaakt wordt
        inwerkingtredingsdoelen Doel[] Inwerkingtredingsdoelen van de toestand

        Geeft de BranchesCumulatief voor de toestand terug.
         """
        accumulator = AccumuleerBranchInformatie (None, None)
        accumulator._VoegBasisversiesToe ([instrument.Branches[doel].Momentopnamen[-1] for doel in inwerkingtredingsdoelen])
        return accumulator.BranchesCumulatief

    def __init__ (self, log : Meldingen, momentopname : MomentopnameInstrument):
        """Maak een nieuwe accumulator aan

        Argumenten:

        log Meldingen  Verzameling meldingen voor de verwerking van versiebeheerinformatie
        momentopname MomentopnameInstrument  Momentopname waarvoor de accumulatie wordt uitgevoerd
        """
        self._Log = log
        self._Momentopname = momentopname
        # Geeft aan of het resultaat valide is
        self._IsValide = True
        # Overzicht van alle branches die al dan niet bijdragen aan het versiebeheer
        # tot het punt waarvoor deze accumulator gemaakt wordt.
        # key = instantie van Branch, value = instantie van BranchBijdrage
        self.BranchesCumulatief = {}

    def _VoegBasisversiesToe (self, basisversies : List[MomentopnameInstrument]):
        """Voeg de bijdrage van een basisversie toe aan de verzamelde bijdragen

        Argumenten:

        basisversies MomentopnameInstrument[]  De basisversies van de momentopname
        """
        for versie in basisversies:
            for doel, bijdrage in versie.BranchesCumulatief.items ():
                huidig = self.BranchesCumulatief.get (doel)
                if huidig is None:
                    # Er was nog geen bijdrage voor dit doel
                    self.BranchesCumulatief[doel] = bijdrage
                    continue

                # Combineren van de bijdrage van een branch die via twee paden tot deze momentopname komt.
                if bijdrage.IsOntvlochten is None:
                    # De ontvlochten status is voor de basisversie onduidelijk, dat blijft zo
                    self.BranchesCumulatief[doel] = BranchBijdrage (huidig.LaatstVerwerkt if huidig.LaatstVerwerkt > bijdrage.LaatstVerwerkt else bijdrage.LaatstVerwerkt, None)
                    continue
                if huidig.IsOntvlochten != bijdrage.IsOntvlochten:
                    # In de ene basisversie is de branch ontvlochten, in de andere niet.
                    # Dat wordt als een merge conflict beschouwd. Ofwel moeten eerst alle basisversies
                    # dezelfde wel/niet ontvlechting krijgen, ofwel de ontvlechting wordt hier meegeleverd.
                    self.BranchesCumulatief[doel] = BranchBijdrage (huidig.LaatstVerwerkt if huidig.LaatstVerwerkt > bijdrage.LaatstVerwerkt else bijdrage.LaatstVerwerkt, None)
                    continue

                if huidig.LaatstVerwerkt < bijdrage.LaatstVerwerkt:
                    # De nieuwe bijdrage is recenter, gebruik die
                    self.BranchesCumulatief[doel] = bijdrage

    def _OntvlechtMet (self, ontvlochtenversie : MomentopnameInstrument):
        """Ontvlecht een branch met deze branch

        Argumenten:

        ontvlochtenversie MomentopnameInstrument  Een branch die ontvlochten moet worden met deze branch
        """
        huidig = self.BranchesCumulatief.get (ontvlochtenversie.Branch.Doel)
        if huidig is None:
            self._Log.Fout ('Ontvlechting van (' + str(self._Momentopname.Branch.Doel) + ', @' + self._Momentopname.GemaaktOp + ') met ' + str(ontvlochtenversie.Branch.Doel) + ' is niet mogelijk omdat dat doel geen basisversie of vervlochten versie is van de branch')
            self._IsValide = False

        elif huidig.LaatstVerwerkt > ontvlochtenversie.GemaaktOp:
            self._Log.Fout ('Doel ' + str(ontvlochtenversie.Branch.Doel) + ' is al verwerkt tot en met @' + huidig.LaatstVerwerkt + ' in (' + str(self._Momentopname.Branch.Doel) + ', @' + self._Momentopname.GemaaktOp + ', ontvlechting met @' + ontvlochtenversie.GemaaktOp + ' is overbodig of onbedoeld')
            self._IsValide = False

        else:
            self.BranchesCumulatief[ontvlochtenversie.Branch.Doel] = BranchBijdrage (ontvlochtenversie.GemaaktOp, True)

    def _VervlechtMet (self, vervlochtenversie : MomentopnameInstrument):
        """Vervlecht een branch met deze branch

        Argumenten:

        vervlochtenversie MomentopnameInstrument  Een branch die vervlochten moet worden met deze branch
        """
        for doel, bijdrage in vervlochtenversie.BranchesCumulatief.items ():
            huidig = self.BranchesCumulatief.get (doel)
            if huidig is None:
                # Er was nog geen bijdrage voor dit doel
                self.BranchesCumulatief[doel] = bijdrage
                continue

            if huidig.LaatstVerwerkt < bijdrage.LaatstVerwerkt:
                # De nieuwe bijdrage is recenter, gebruik die
                self.BranchesCumulatief[doel] = bijdrage
                continue

            if huidig.LaatstVerwerkt == bijdrage.LaatstVerwerkt:
                if huidig.IsOntvlochten is None and not bijdrage.IsOntvlochten:
                    # Dit is een bevestiging van de vervlochten status
                    self.BranchesCumulatief[doel] = bijdrage
                    continue

                if not huidig.IsOntvlochten and bijdrage.IsOntvlochten:
                    # Neem de ontvlochten status over
                    self.BranchesCumulatief[doel] = bijdrage
                    continue

            if doel == vervlochtenversie.Branch.Doel: # huidig.IsOntvlochten os None
                self._Log.Fout ('Doel ' + str(doel) + ' is al verwerkt tot en met @' + huidig.LaatstVerwerkt + ' in (' + str(self._Momentopname.Branch.Doel) + ', @' + self._Momentopname.GemaaktOp + ', vervlechting met @' + vervlochtenversie.GemaaktOp + ' is overbodig of onbedoeld')
                self._IsValide = False

    def _Valideer (self) -> bool:
        """"Verifieer dat alle bijdragen nu eenduidig bepaald zijn.
        Geeft self._IsValide terug.
        """
        for doel, huidig in self.BranchesCumulatief.items ():
            if huidig.IsOntvlochten is None:
                self._Log.Fout ('Doel ' + str(doel) + ' is zowel vervlochten als ontvlochten in basisversie(s) van (' + str(self._Momentopname.Branch.Doel) + ', @' + self._Momentopname.GemaaktOp + '); status moet (nogmaals) expliciet aangegeven worden')
                self._IsValide = False
        return self._IsValide

