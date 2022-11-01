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
from data_bg_versiebeheer import Versiebeheer, Branch, MomentopnameInstrument, MomentopnameTijdstempels, Consolidatie, Consolidatieversie

#----------------------------------------------------------------------
#
# Versiebeheer: minimale informatie die in de bevoegd gezag software
#               bijgehouden moet worden c.q. afleidbaar moet zijn.
#
#----------------------------------------------------------------------
class VersiebeheerWeergave:

    def __init__ (self, origineel : Versiebeheer):
        """Maak een kopie van het versiebeheer bij het bevoegd gezag voor weergave.

        Argumenten:

        origineel BGVersiebeheer Staat van het versiebeheer na uitvoeren van een projectactie
        """
        super ().__init__ ()
        # Informatie over alle doelen die door bevoegd gezag beheerd worden
        self.Branches : Dict[Doel,Branch] = { d: self._KloonBranch (b) for d, b in origineel.Branches.items () }
        # De consolidaties van elk bekend instrument
        self.Consolidaties : Dict[str,Consolidatie] = { w: self._KloonConsolidatie (c) for w, c in origineel.Consolidaties.items () }

    def _KloonBranch (self, origineel: Branch):
        """Maak een kloon van de branch"""
        kloon = Branch (origineel._Doel)
        kloon.Uitgangssituatie_Doel = origineel.Uitgangssituatie_Doel # Hoeft geen kloon te zijn, alleen doel wordt gebruikt
        kloon.Uitgangssituatie_GeldigOp = origineel.Uitgangssituatie_GeldigOp
        kloon.InterneInstrumentversies = { w: self._KloonMomentopnameInstrument (kloon, m) for w, m in origineel.InterneInstrumentversies.items () }
        kloon.InterneTijdstempels = self._KloonMomentopnameTijdstempels (kloon, origineel.InterneTijdstempels)
        kloon.PubliekeInstrumentversies = { w: self._KloonMomentopnameInstrument (kloon, m) for w, m in origineel.PubliekeInstrumentversies.items () }
        kloon.PubliekeTijdstempels = self._KloonMomentopnameTijdstempels (kloon, origineel.PubliekeTijdstempels)
        return kloon

    def _KloonMomentopnameInstrument (self, branch: Branch, origineel: MomentopnameInstrument):
        """Maak een kloon van de MomentopnameInstrument"""
        kloon = MomentopnameInstrument (branch, origineel._WorkId)
        kloon.ExpressionId = origineel.ExpressionId
        kloon.IsJuridischUitgewerkt = origineel.IsJuridischUitgewerkt
        kloon.IsTeruggetrokken = origineel.IsTeruggetrokken
        kloon.Uitgangssituatie = None if origineel.Uitgangssituatie is None else origineel.Uitgangssituatie.copy ()
        kloon.GemaaktOp = origineel.GemaaktOp
        kloon.MetBijdragenVan = origineel.MetBijdragenVan.copy ()
        kloon.ZonderBijdragenVan = origineel.ZonderBijdragenVan.copy ()
        return kloon

    def _KloonMomentopnameTijdstempels (self, branch: Branch, origineel: MomentopnameTijdstempels):
        """Maak een kloon van de MomentopnameTijdstempels"""
        kloon = MomentopnameTijdstempels (branch)
        kloon.JuridischWerkendVanaf = origineel.JuridischWerkendVanaf
        kloon.GeldigVanaf = origineel.GeldigVanaf
        return kloon

    def _KloonConsolidatie (self, origineel : Consolidatie):
        """Maak een kloon van de Consolidatie"""
        kloon = Consolidatie (origineel._WorkId)
        kloon.Versies = origineel.Versies.copy ()
        return kloon

