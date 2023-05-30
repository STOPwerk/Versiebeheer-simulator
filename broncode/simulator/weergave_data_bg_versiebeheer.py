#======================================================================
#
# Versiebeheer bij een bevoegd gezag - extractie ten behoeve
# van de weergave.
#
#======================================================================
#
# Het datamodel van het interne versiebeheer voor het bevoegd gezag
# kent geen historie. Voor de weergave van de staat van het
# versiebeheer na elke projectactie is dat wel vereist. Het datamodel
# in deze module wordt gebruikt om een kloon te maken van de gegevens
# na elke actie en die te gebruiken voor weergave. Niet alle
# informatie wordt gekloond.
#
#======================================================================

from typing import Dict, List
from copy import copy
from data_doel import Doel
from data_bg_procesverloop import Branch
from data_bg_versiebeheer import Versiebeheerinformatie, InstrumentInformatie, Instrumentversie, Tijdstempels, Consolidatie

#----------------------------------------------------------------------
#
# Versiebeheer: minimale informatie die in de bevoegd gezag software
#               bijgehouden moet worden c.q. afleidbaar moet zijn.
#
#----------------------------------------------------------------------
class VersiebeheerWeergave (Versiebeheerinformatie):

    def __init__ (self, origineel : Versiebeheerinformatie):
        """Maak een kopie van het versiebeheer bij het bevoegd gezag voor weergave.

        Argumenten:

        origineel BGVersiebeheer Staat van het versiebeheer na uitvoeren van een projectactie
        """
        super ().__init__ ()
        # Informatie over alle doelen die door bevoegd gezag beheerd worden
        self.Branches : Dict[Doel,Branch] = { d: self._KloonBranch (b) for d, b in origineel.Branches.items () }
        # De consolidatie kan bij het bevoegd gezag op het niveau van branches
        # worden bijgehouden. Dat wordt vertaald naar informatie per instrument
        # bij het omzetten naar STOP consolidatie-informatie.
        # Lijst is gesorteerd op volgorde van inwerkingtreding - juridischGeldigVanaf
        self.Consolidaties : List[Consolidatie] = origineel.Consolidaties

    def _KloonBranch (self, origineel: Branch):
        """Maak een kloon van de branch"""
        kloon = copy (origineel)
        kloon.Instrumentversies = { w: self._KloonInstrumentInformatie (kloon, m) for w, m in origineel.Instrumentversies.items () }
        kloon.Tijdstempels = copy (origineel.Tijdstempels)
        kloon.UitgewisseldeTijdstempels = copy (origineel.UitgewisseldeTijdstempels)
        return kloon

    def _KloonInstrumentInformatie (self, branch: Branch, origineel: InstrumentInformatie) -> InstrumentInformatie:
        """Maak een kloon van de InstrumentInformatie"""
        kloon = copy (origineel)
        kloon._Branch = branch
        if not origineel.Instrumentversie is None:
            kloon.Instrumentversie = copy (origineel.Instrumentversie)
        if not origineel.Uitgangssituatie is None:
            kloon.Uitgangssituatie = copy (origineel.Uitgangssituatie)
        return kloon

