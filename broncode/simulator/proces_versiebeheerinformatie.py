#======================================================================
#
# Verwerking van consolidatie-informatie en omzetting naar
# versiebeheerinformatie.
#
#======================================================================
#
# In de applicatie wordt eerst een in-memory representatie van de
# inhoud van de XML bestanden gemaakt, zoals in de module
# stop_consolidatieinformatie is geïmplementeerd. Daarna worden 
# alle ingelezen ConsolidatieInformatie instanties omgezet naar 
# het interne datamodel dat in data_versiebeheerinformatie is
# gedeclareerd. De code voor de omzetting is geïmplementeerd 
# in de klasse WerkVersiebeheerinformatieBij, die de verschillende 
# Verwerk* klassen gebruikt voor de interpretatie van de consolidatie-
# informatie. De omzetting gebeurt per uitwisseling, op volgorde
# van uitwisselen (d.w.z. op volgorde van gemaaktOp).
#
#======================================================================
from typing import List, Dict, Set, Tuple 

from applicatie_meldingen import Melding, Meldingen
from data_doel import Doel
from data_versiebeheerinformatie import Versiebeheerinformatie, Uitwisseling, UitgewisseldeInstrumentversie, Instrument, Branch, MomentopnameInstrument, MomentopnameTijdstempels
from proces_branchescumulatief import AccumuleerBranchInformatie
from stop_consolidatieinformatie import ConsolidatieInformatie, VoorInstrument, BeoogdeVersie, Terugtrekking, Intrekking, TerugtrekkingIntrekking, VoorTijdstempel, Tijdstempel, TerugtrekkingTijdstempel, MaterieelUitgewerkt
from stop_juridischeverantwoording import JuridischeVerantwoording, Verantwoording, Publicatie
from weergave_symbolen import Weergave_Symbolen

#======================================================================
#
# Vertaling van ConsolidatieInformatie naar het datamodel.
#
#======================================================================

#----------------------------------------------------------------------
# Verwerking van consolidatie informatie voor een instrument
#----------------------------------------------------------------------

class VerwerkVoorInstrument:

    def __init__ (self, voorInstrument : VoorInstrument):
        """Initialiseer een instantie die de wijziging in de ConsolidatieInformatie
        omzet naar een wijziging van de BeheerdeInformatie.
        
        Argumenten:
        voorInstrument VoorInstrument Onderdeel van ConsolidatieInformatie
        """
        self.VoorInstrument = voorInstrument

class VerwerkBeoogdInstrument(VerwerkVoorInstrument):
    def __init__ (self, beoogdInstrument : BeoogdeVersie):
        super().__init__ (beoogdInstrument)

    def Verwerk (self, verwerking, doel, momentopname : MomentopnameInstrument):
        """Verwerk de wijziging van beoogde instrumentversie
        
        Argumenten:
        verwerking ConsolidatieInformatieVerwerking  Context van de verwerking
        doel string  Doel/branch waarvoor de beheerde informatie wordt bijgewerkt
        momentopname Momentopname  huidige staat van de beheerde informatie; deze moet gewijzigd worden

        Geeft terug of de informatie is bijgewerkt
        """
        if momentopname.IsIngetrokken:
            # De intrekking van het instrument wordt ongedaan gemaakt
            verwerking._Log.Detail ("Instrumentversie per (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ") is '" + self.VoorInstrument.ExpressionId + "'; intrekking is ongedaan gemaakt")
            momentopname.IsIngetrokken = False
        elif self.VoorInstrument.ExpressionId is None:
            if not doel in self.VoorInstrument.Basisversies:
                verwerking._Log.Fout ("Beoogde instrumentversie kan niet onbekend zijn voor nieuwe branch (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ") voor " + self.VoorInstrument.WorkId)
                verwerking.IsValide = False
                return False
            else:
                verwerking._Log.Detail ("Instrumentversie per (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ") is " + 'onbekend')
        else:
            verwerking._Log.Detail ("Instrumentversie per (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ") is " + "'" + self.VoorInstrument.ExpressionId + "'" )
        momentopname.ExpressionId = self.VoorInstrument.ExpressionId
        momentopname.IsTeruggetrokken = False
        momentopname._Symbool = Weergave_Symbolen.Instrument_OnbekendeVersie if self.VoorInstrument.ExpressionId is None else Weergave_Symbolen.Instrument_Versie
        return True

class VerwerkTerugtrekking(VerwerkVoorInstrument):
    def __init__ (self, terugtrekking : Terugtrekking):
        super().__init__ (terugtrekking)

    def Verwerk (self, verwerking, doel, momentopname : MomentopnameInstrument):
        """Verwerk de terugtrekking
        
        Argumenten:
        verwerking ConsolidatieInformatieVerwerking  Context van de verwerking
        doel string  Doel/branch waarvoor de beheerde informatie wordt bijgewerkt
        momentopname Momentopname  huidige staat van de beheerde informatie; deze moet gewijzigd worden

        Geeft terug of de informatie is bijgewerkt
        """
        if momentopname.IsTeruggetrokken:
            verwerking._Log.Waarschuwing ("Terugtrekking (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ") voor " + self.VoorInstrument.WorkId + ": wijziging/intrekking instrument is al teruggetrokken")
            return False
        else:
            if momentopname.IsIngetrokken:
                verwerking._Log.Fout ("Terugtrekking van versie (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ") voor " + self.VoorInstrument.WorkId + " niet mogelijk: instrument is ingetrokken")
                verwerking.IsValide = False
                return False
            else:
                verwerking._Log.Detail ("Wijziging van instrument " + self.VoorInstrument.WorkId + " teruggetrokken per (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ")")
        momentopname.IsIngetrokken = False
        momentopname.ExpressionId = None
        momentopname.IsTeruggetrokken = True
        momentopname._Symbool = Weergave_Symbolen.Instrument_Terugtrekking
        return True

class VerwerkIntrekking(VerwerkVoorInstrument):
    def __init__ (self, intrekking : Intrekking):
        super().__init__ (intrekking)

    def Verwerk (self, verwerking, doel, momentopname : MomentopnameInstrument):
        """Verwerk de intrekking van het instrument
        
        Argumenten:
        verwerking ConsolidatieInformatieVerwerking  Context van de verwerking
        doel string  Doel/branch waarvoor de beheerde informatie wordt bijgewerkt
        momentopname Momentopname  huidige staat van de beheerde informatie; deze moet gewijzigd worden

        Geeft terug of de informatie is bijgewerkt
        """
        if momentopname.IsIngetrokken:
            verwerking._Log.Detail ("Instrument " + self.VoorInstrument.WorkId + " ingetrokken per (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ") - is al eerder gemeld")
        else:
            verwerking._Log.Detail ("Instrument " + self.VoorInstrument.WorkId + " ingetrokken per (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ")")
        momentopname.IsIngetrokken = True
        momentopname.ExpressionId = None
        momentopname.IsTeruggetrokken = False
        momentopname._Symbool = Weergave_Symbolen.Instrument_Intrekking
        return True

class VerwerkTerugtrekkingIntrekking(VerwerkVoorInstrument):
    def __init__ (self, terugtrekkingIntrekking : TerugtrekkingIntrekking):
        super().__init__ (terugtrekkingIntrekking)

    def Verwerk (self, verwerking, doel, momentopname : MomentopnameInstrument):
        """Verwerk de terugtrekking
        
        Argumenten:
        verwerking ConsolidatieInformatieVerwerking  Context van de verwerking
        doel string  Doel/branch waarvoor de beheerde informatie wordt bijgewerkt
        momentopname Momentopname  huidige staat van de beheerde informatie; deze moet gewijzigd worden

        Geeft terug of de informatie is bijgewerkt
        """
        if momentopname.IsTeruggetrokken:
            verwerking._Log.Waarschuwing ("Terugtrekking (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ") voor " + self.VoorInstrument.WorkId + ": wijziging/intrekking instrument is al teruggetrokken")
            return False
        else:
            if not momentopname.IsIngetrokken:
                verwerking._Log.Fout ("Terugtrekking van intrekking (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ") voor " + self.VoorInstrument.WorkId + " niet mogelijk: instrument is niet ingetrokken")
                verwerking.IsValide = False
                return False
            else:
                verwerking._Log.Detail ("Intrekking van instrument " + self.VoorInstrument.WorkId + " teruggetrokken per (" + str(doel) + " @" + self.VoorInstrument.ConsolidatieInformatie.GemaaktOp + ")")
        momentopname.IsIngetrokken = False
        momentopname.ExpressionId = None
        momentopname.IsTeruggetrokken = True
        momentopname._Symbool = Weergave_Symbolen.Instrument_Terugtrekking
        return True

#----------------------------------------------------------------------
# Verwerking van consolidatie informatie voor tijdstempels
#----------------------------------------------------------------------
class VerwerkTijdstempel:
    def __init__ (self, voorTijdstempel : VoorTijdstempel):
        """Initialiseer een instantie die een tijdstempel in de ConsolidatieInformatie
        omzet naar een MomentopnameTijdstempels.
        
        Argumenten:
        voorTijdstempel Tijdstempel Onderdeel van ConsolidatieInformatie
        """
        self.VoorTijdstempel = voorTijdstempel

class VerwerkTijdstempel (VerwerkTijdstempel):
    def __init__ (self, tijdstempel : Tijdstempel):
        super().__init__ (tijdstempel)

    def Verwerk (self, verwerking, momentopname : MomentopnameTijdstempels):
        """Verwerk de tijdstempel
        
        Argumenten:
        verwerking ConsolidatieInformatieVerwerking  Context van de verwerking
        momentopname MomentopnameTijdstempels  huidige staat van de beheerde informatie; deze moet gewijzigd worden

        Geeft terug of de informatie is bijgewerkt
        """
        if self.VoorTijdstempel.IsGeldigVanaf:
            momentopname.GeldigVanaf = self.VoorTijdstempel.Datum
        else:
            momentopname.JuridischWerkendVanaf = self.VoorTijdstempel.Datum
        if momentopname.GeldigVanaf and momentopname.JuridischWerkendVanaf and momentopname.GeldigVanaf > momentopname.JuridischWerkendVanaf:
            verwerking._Log.Fout ("GeldigVanaf (" + momentopname.GeldigVanaf + ") mag niet groter zijn dan JuridischWerkendVanaf (" + momentopname.JuridischWerkendVanaf + ") (" + str(self.VoorTijdstempel.Doel) + " @" + self.VoorTijdstempel.ConsolidatieInformatie.GemaaktOp + ")")
            verwerking.IsValide = False
            return False
        else:
            verwerking._Log.Detail (("GeldigVanaf" if self.VoorTijdstempel.IsGeldigVanaf else "JuridischWerkendVanaf") + " = " + self.VoorTijdstempel.Datum + " per (" + str(self.VoorTijdstempel.Doel) + " @" + self.VoorTijdstempel.ConsolidatieInformatie.GemaaktOp + ")")
            momentopname._Symbool = Weergave_Symbolen.Tijdstempel_Waarde
        return True

    def ConsolidatieInformatieElement (self):
        """Geef de naam van het gebruikte ConsolidatieInformatie element, voor meldingen"""
        return ("Tijdstempel-GeldigVanaf" if self.VoorTijdstempel.IsGeldigVanaf else "Tijdstempel-JuridischWerkendVanaf")


class VerwerkTerugtrekkingTijdstempel (VerwerkTijdstempel):
    def __init__ (self, terugtrekkingTijdstempel : TerugtrekkingTijdstempel):
        super().__init__ (terugtrekkingTijdstempel)

    def Verwerk (self, verwerking, momentopname: MomentopnameTijdstempels):
        """Verwerk de terugtrekking van de tijdstempel
        
        Argumenten:
        verwerking ConsolidatieInformatieVerwerking  Context van de verwerking
        momentopname MomentopnameTijdstempels  huidige staat van de beheerde informatie; deze moet gewijzigd worden

        Geeft terug of de informatie is bijgewerkt
        """
        if self.VoorTijdstempel.IsGeldigVanaf:
            if momentopname is None or momentopname.GeldigVanaf is None:
                verwerking._Log.Waarschuwing ("Terugtrekking van GeldigVanaf (" + str(self.VoorTijdstempel.Doel) + " @" + self.VoorTijdstempel.ConsolidatieInformatie.GemaaktOp + "): geen GeldigVanaf datum bekend")
                return False
            momentopname.GeldigVanaf = None
            if momentopname._Symbool is None:
                # Toon dit als een nieuwe waarde, geen terugtrekking
                momentopname._Symbool = Weergave_Symbolen.Tijdstempel_Waarde
        else:
            if momentopname is None or momentopname.JuridischWerkendVanaf is None:
                verwerking._Log.Waarschuwing ("Terugtrekking van JuridischWerkendVanaf (" + str(self.VoorTijdstempel.Doel) + " @" + self.VoorTijdstempel.ConsolidatieInformatie.GemaaktOp + "): geen JuridischWerkendVanaf datum bekend")
                return False
            momentopname.JuridischWerkendVanaf = None
            # Toon dit als een terugtrekking
            momentopname._Symbool = Weergave_Symbolen.Tijdstempel_Terugtrekking
        verwerking._Log.Detail (("GeldigVanaf" if self.VoorTijdstempel.IsGeldigVanaf else "JuridischWerkendVanaf") + " teruggetrokken per (" + str(self.VoorTijdstempel.Doel) + " @" + self.VoorTijdstempel.ConsolidatieInformatie.GemaaktOp + ")")
        return True

    def ConsolidatieInformatieElement (self):
        """Geef de naam van het gebruikte ConsolidatieInformatie element, voor meldingen"""
        return "TerugtrekkingTijdstempel-" + ("GeldigVanaf" if self.VoorTijdstempel.IsGeldigVanaf else "JuridischWerkendVanaf")


#======================================================================
#
# WerkVersiebeheerinformatieBij implementeert de vertaling van 
# ConsolidatieInformatie naar Versiebeheerinformatie voor een enkele
# uitwisseling.
#
#======================================================================
class UitwisselingInformatie:

    def __init__ (self):
        # Geeft aan of de vertaling goed is gegaan
        self.IsValide = True
        # De beschrijving van de uitwisseling
        self.Uitwisseling : Uitwisseling = None
        # Eerste datum dat aspecten van de uitwisseling voor het eerst publiek bekend zijn,
        # per instrument. Als tijdreizen op bekendOp ondersteund wordt moeten vanaf deze datum
        # de complete toestanden opnieuw berekend worden.
        # key = work-Id, value = datum (string)
        self.EersteBekendOp : Dict[str,str] = {}
        # De instrumenten waarvoor de consolidatie verandert. De instrumenten zijn nodig om 
        # te weten welke consolidaties uitgevoerd moeten worden.
        # Set van work-id
        self.Instrumenten : Set[str] = set ()
        # De doelen waarvoor consolidatie-informatie is uitgewisseld
        self.Doelen :Set[Doel] = set()
        # De bijdragen aan de juridische verantwoording 
        # Key = workId
        self.Verantwoording : Dict[str,JuridischeVerantwoording] = {}

class WerkVersiebeheerinformatieBij:

    @staticmethod
    def VoerUit (log, versiebeheerinformatie : Versiebeheerinformatie, publicatieblad : str, consolidatieInformatie : ConsolidatieInformatie) -> UitwisselingInformatie:
        """Vertaal de uitgewisselde ConsolidatieInformatie naar versiebeheer voor een enkele uitwisseling
        
        Argumenten:
        log Verzameling van meldingen
        versiebeheerinformatie Versiebeheerinformatie Alle versiebeheerinformatie gereconstrueerd tot deze uitwisseling
        publicatieblad string Identificatie van het publicatieblad waarin de publicatie is verschenen voor hetgeen door de consolidatie-informatie is beschreven; kan None zijn
        consolidatieInformatie ConsolidatieInformatie[] alle uitgewisselde consolidatie-informatie modules

        Resultaat is een indicatie of er geen fouten gevonden zijn tijdens de verwerking.
        """
        verwerking = WerkVersiebeheerinformatieBij (log, versiebeheerinformatie, publicatieblad)
        verwerking._VerwerkConsolidatieInformatie (consolidatieInformatie)
        return verwerking.Resultaat

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, log : Meldingen, versiebeheerinformatie : Versiebeheerinformatie, publicatieblad : str):
        """Maak een instantie met alle informatie nodig tijdens de vertaling"""
        # Versiebeheerinformatie die bijgewerkt moet worden
        self.Versiebeheerinformatie = versiebeheerinformatie
        # Identificatie van het publicatieblad
        self._Publicatieblad = publicatieblad
        # Verzameling van meldingen
        self._Log = log
        # De beschrijving van de uitwisseling die volgt uit de vertaling
        # Instantie van UitwisselingInformatie
        self.Resultaat = UitwisselingInformatie ()
        # Tijdens de verwerking van een ConsolidatieInformatie module:
        # de instrument-gerelateerde wijzigingen
        self._ToegevoegdeMomentopnamen : List[MomentopnameInstrument] = []

#----------------------------------------------------------------------
# Verwerk een enkele ConsolidatieInformatie module
#----------------------------------------------------------------------
    def _VerwerkConsolidatieInformatie (self, consolidatieInformatie : ConsolidatieInformatie):
        """Verwerk de consolidatie-informatie op instrument, verwerking, gemaaktOp"""

        # Nieuwe uitwisseling
        self.Resultaat.Uitwisseling = Uitwisseling (consolidatieInformatie.GemaaktOp, consolidatieInformatie.OntvangenOp)
        self.Resultaat.Uitwisseling._Publicatieblad = self._Publicatieblad
        self.Resultaat.Uitwisseling._ConsolidatieInformatie = consolidatieInformatie
        self.Versiebeheerinformatie.Uitwisselingen.append (self.Resultaat.Uitwisseling)

        # Verwerk de instrument-gerelateerde wijzigingen
        for element in consolidatieInformatie.TerugtrekkingenIntrekking:
            self._VerwerkInstrumentConsolidatieElement (VerwerkTerugtrekkingIntrekking (element), False)

        for element in consolidatieInformatie.Terugtrekkingen:
            self._VerwerkInstrumentConsolidatieElement (VerwerkTerugtrekking (element), False)

        for element in consolidatieInformatie.Intrekkingen:
            self._VerwerkInstrumentConsolidatieElement (VerwerkIntrekking (element), True)

        for element in consolidatieInformatie.BeoogdeVersies:
            self._VerwerkInstrumentConsolidatieElement (VerwerkBeoogdInstrument (element), True)
            ui = UitgewisseldeInstrumentversie (self.Resultaat.Uitwisseling, self.Versiebeheerinformatie.Instrumenten[element.WorkId], element.Doelen, element.ExpressionId, list(element.Basisversies.values())[0] if len (element.Basisversies) > 0 else None)
            self.Resultaat.Uitwisseling.Instrumentversies.append (ui)
            self.Versiebeheerinformatie._UitwisselingInstrumentversie[element.ExpressionId] = ui

        # Neem basisversies en ont-/vervlechtingen over, en update LaatsteMomentopnameVoorConsolidatie
        for nieuweMomentopname in self._ToegevoegdeMomentopnamen:
            self._NeemMomentopnameReferentiesOver (nieuweMomentopname)

        # Bepaal de cumulatieve bijdragen van de branches voor elke momentopname
        self._BepaalCumulatieveBijdragen ()

        # Verwerk dan de tijdstempels
        for element in consolidatieInformatie.TijdstempelTerugtrekkingen:
            self._VerwerkTijdstempelElement (VerwerkTerugtrekkingTijdstempel (element), False)

        for element in consolidatieInformatie.Tijdstempels:
            self._VerwerkTijdstempelElement (VerwerkTijdstempel (element), True)

        # Verwerk materieel uitgewerkt
        for element in consolidatieInformatie.MaterieelUitgewerkt:
            self._VerwerkMaterieelUitgewerkt (element)


#----------------------------------------------------------------------
# Hulpmethoden om consolidatie-informatie `voor een instrument te verwerken
#----------------------------------------------------------------------
    def _VerwerkInstrumentConsolidatieElement (self, verwerk : VerwerkVoorInstrument, maakBranchAlsNietBestaat):
        """Verwerk een element uit de ConsolidatieInformatie dat een instrument betreft
        
        Argumenten:
        verwerk Verwerk*  Klasse die de interpretatie van de consolidatie informatie implementeert
        maakBranchAlsNietBestaat boolean Maak hiervoor een branch aan als die nog niet bestaat
        """
        for doel in verwerk.VoorInstrument.Doelen:
            nieuweMomentopname = self._MomentOpnameVoorInstrument (verwerk.VoorInstrument, doel, maakBranchAlsNietBestaat)
            if nieuweMomentopname:
                if verwerk.Verwerk (self, doel, nieuweMomentopname.Momentopname):
                    self._ToegevoegdeMomentopnamen.append (nieuweMomentopname)
                    nieuweMomentopname.Branch.Momentopnamen.append (nieuweMomentopname.Momentopname)

                    bekendOp = verwerk.VoorInstrument.BekendOp ()
                    self._VoegInstrumentDoelenToe (self.Versiebeheerinformatie.Instrumenten[verwerk.VoorInstrument.WorkId], doel, bekendOp, True, verwerk.VoorInstrument.eId)

                    self.Resultaat.Doelen.add (doel)
                    if self.Resultaat.Uitwisseling.BekendOp is None or bekendOp > self.Resultaat.Uitwisseling.BekendOp:
                        self.Resultaat.Uitwisseling.BekendOp = bekendOp

    def _MomentOpnameVoorInstrument (self, voorInstrument : VoorInstrument, doel, maakBranchAlsNietBestaat):
        """Geef de momentopname voor een branch van het instrument

        Argumenten:
        voorInstrument VoorInstrument  ConsolidatieInformatie element waaruit de momentopname afkomstig is
        doel string  Doel van de momentopname
        maakBranchAlsNietBestaat boolean Maak een branch aan als die nog niet bestaat

        Resultaat is een NieuweMomentopname of None
        """
        instrument = self.Versiebeheerinformatie.Instrumenten.get (voorInstrument.WorkId)
        if instrument is None:
            if maakBranchAlsNietBestaat:
                self.Versiebeheerinformatie.Instrumenten[voorInstrument.WorkId] = instrument = Instrument (self.Versiebeheerinformatie, voorInstrument.WorkId)
            else:
                self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor onbekend instrument " + voorInstrument.WorkId + " @" + voorInstrument.ConsolidatieInformatie.GemaaktOp)
                self.Resultaat.IsValide = False
                return
        bekendOp = voorInstrument.BekendOp ()
        instrument.BekendOp.add (bekendOp)

        branch = instrument.Branches.get (doel)
        if not branch is None:
            # Voeg momentopname toe aan bestaande branch
            laatste = branch.Momentopnamen[-1]

            if laatste.GemaaktOp == voorInstrument.ConsolidatieInformatie.GemaaktOp:
                self._Log.Fout ("Twee ConsolidatieInformatie elementen aanwezig voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en instrument " + voorInstrument.WorkId)
                self.Resultaat.IsValide = False
                return

            nieuw = MomentopnameInstrument (branch, voorInstrument)
            if nieuw.BekendOp < laatste.BekendOp:
                self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en instrument " + voorInstrument.WorkId + " is eerder bekend (op " + nieuw.BekendOp + ") dan voorgaande (@" + laatste.GemaaktOp + " op " + laatste.BekendOp + ")")
                self.Resultaat.IsValide = False
                return

            if not doel in voorInstrument.Basisversies:
                self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en instrument " + voorInstrument.WorkId + " moet (" + str(doel) + ", @" + laatste.GemaaktOp + ") als basisversie hebben")
                self.Resultaat.IsValide = False
            else:
                basis = voorInstrument.Basisversies[doel].GemaaktOp
                if basis != laatste.GemaaktOp:
                    self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en instrument " + voorInstrument.WorkId + " moet (" + str(doel) + ", @" + laatste.GemaaktOp + ") en niet (" + str(doel) + ", @" + basis + ") als basisversie hebben")
                    self.Resultaat.IsValide = False
                    del voorInstrument.Basisversies[doel] # blijf validaties uitvoeren

        elif maakBranchAlsNietBestaat:
            # Eerste momentopname in nieuwe branch
            branch = Branch (doel)
            instrument.Branches[doel] = branch
            self.Versiebeheerinformatie._BekendeDoelenVoorInstrumenten.add (doel)
            nieuw = MomentopnameInstrument (branch, voorInstrument)

            if len (voorInstrument.Basisversies) == 0:
                if instrument.InitieleDoelen is None:
                    instrument.InitieleDoelen = voorInstrument.Doelen
                elif not doel in instrument.InitieleDoelen:
                    for anderDoel in instrument.InitieleDoelen:
                        andereBranch = instrument.Branches.get (anderDoel)
                        if not andereBranch is None:
                            self._Log.Fout ("Instrument " + voorInstrument.WorkId + ": zowel " + voorInstrument.ModuleXmlNaam () + " voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en als " + andereBranch.Momentopnamen[0]._ConsolidatieInformatieElementen[0].ModuleXmlNaam () + " voor (" + str(andereBranch.Doel) + ", @" + andereBranch.Momentopnamen[0].GemaaktOp + ") zijn initiële uitwisselingen voor het instrument (zonder basisversies)")
                    self.Resultaat.IsValide = False
            else:
                if doel in voorInstrument.Basisversies:
                    self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en instrument " + voorInstrument.WorkId + " mag geen basisversie hebben voor hetzelfde doel maar heeft als basisversie (" + str(doel) + ", @" + voorInstrument.Basisversies[doel].GemaaktOp + ")")
                    self.Resultaat.IsValide = False
                    del voorInstrument.Basisversies[doel] # blijf validaties uitvoeren
        else:
            self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor onbekend doel '" + str(doel) + "' @" + voorInstrument.ConsolidatieInformatie.GemaaktOp)
            self.Resultaat.IsValide = False
            return

        return NieuweMomentopname (instrument, branch, nieuw)

#----------------------------------------------------------------------
# Hulpmethoden om consolidatie-informatie voor tijdstempels te verwerken
#----------------------------------------------------------------------
    def _VerwerkTijdstempelElement (self, verwerk : VerwerkTijdstempel, maakAlsDoelNietBestaat):
        """Verwerk een element uit de ConsolidatieInformatie dat een instrument betreft
        
        Argumenten:
        verwerk Verwerk*  Klasse die de interpretatie van de consolidatie informatie implementeert
        maakAlsDoelNietBestaat boolean Maak de momentopname zelfs aan als er nog geen tijdstempels voor het doel zijn
        """
        branch, momentopname, isNieuw = self._MomentOpnameVoorTijdstempels (verwerk.VoorTijdstempel, maakAlsDoelNietBestaat)
        if momentopname:
            if verwerk.Verwerk (self, momentopname):
                if isNieuw:
                    branch.Momentopnamen.append (momentopname)
                self.Resultaat.Doelen.add (verwerk.VoorTijdstempel.Doel)

                bekendOp = verwerk.VoorTijdstempel.BekendOp ()
                if self.Resultaat.Uitwisseling.BekendOp is None or bekendOp > self.Resultaat.Uitwisseling.BekendOp:
                    self.Resultaat.Uitwisseling.BekendOp = bekendOp

                # Dit raakt alle instrumenten met een niet-teruggetrokken branch voor het doel
                for instrument in self.Versiebeheerinformatie.Instrumenten.values ():
                    if verwerk.VoorTijdstempel.Doel in instrument.Branches:
                        branch = instrument.Branches[verwerk.VoorTijdstempel.Doel]
                        if len (branch.Momentopnamen) > 0 and not branch.Momentopnamen[-1].IsTeruggetrokken:
                            instrument.BekendOp.add (bekendOp)
                            self._VoegInstrumentDoelenToe (instrument, verwerk.VoorTijdstempel.Doel, bekendOp, False, verwerk.VoorTijdstempel.eId)

    def _MomentOpnameVoorTijdstempels (self, voorTijdstempel : VoorTijdstempel, maakAlsDoelNietBestaat):
        """Geef de momentopname voor de tijdstempels

        Argumenten:
        doel Doel  Doel voor de momentopname
        voorTijdstempel VoorTijdstempel ConsolidatieInformatie element waaruit de momentopname afkomstig is
        maakAlsDoelNietBestaat boolean Maak de momentopname zelfs aan als er nog geen tijdstempels voor het doel zijn

        Resultaat is: (branch, Momentopname, isNieuweMomentopname) of (*, None).
        """
        branch = self.Versiebeheerinformatie.Tijdstempels.get (voorTijdstempel.Doel)
        if branch is None:
            if not voorTijdstempel.Doel in self.Versiebeheerinformatie._BekendeDoelenVoorInstrumenten:
                self._Log.Fout (voorTijdstempel.ModuleXmlNaam () + " voor doel '" + str(voorTijdstempel.Doel) + "' dat nog niet voor een instrument gebruikt is, @" + voorTijdstempel.ConsolidatieInformatie.GemaaktOp)
                self.Resultaat.IsValide = False
                return (None, None, None)
            elif maakAlsDoelNietBestaat:
                self.Versiebeheerinformatie.Tijdstempels[voorTijdstempel.Doel] = branch = Branch (voorTijdstempel.Doel)
            else:
                self._Log.Fout (voorTijdstempel.ModuleXmlNaam () + " voor onbekend doel '" + str(voorTijdstempel.Doel) + "' @" + voorTijdstempel.ConsolidatieInformatie.GemaaktOp)
                self.Resultaat.IsValide = False
                return (None, None, None)

        nieuw = None
        if len (branch.Momentopnamen) > 0:
            laatste = branch.Momentopnamen[-1]
            if laatste.GemaaktOp == voorTijdstempel.ConsolidatieInformatie.GemaaktOp:
                laatste._ConsolidatieInformatieElementen.append (voorTijdstempel)
                return (branch, laatste, False)
            else:
                nieuw = MomentopnameTijdstempels (branch, voorTijdstempel)
                if nieuw.BekendOp < laatste.BekendOp:
                    self._Log.Fout (voorTijdstempel.ModuleXmlNaam () + " voor (" + str(voorTijdstempel.Doel) + "" + ", @" + voorTijdstempel.ConsolidatieInformatie.GemaaktOp + ") is eerder bekend (op " + nieuw.BekendOp + ") dan voorgaande verandering van tijdstempels (@" + laatste.GemaaktOp + " op " + laatste.BekendOp + ")")
                    self.Resultaat.IsValide = False
                    nieuw = None
        else:
            nieuw = MomentopnameTijdstempels (branch, voorTijdstempel)

        return (branch, nieuw, True)

#----------------------------------------------------------------------
# Hulpmethode om indicatie van materieel uitgewerkt te verwerken
#----------------------------------------------------------------------
    def _VerwerkMaterieelUitgewerkt (self, element : MaterieelUitgewerkt):
        """Verwerk een element uit de ConsolidatieInformatie dat de materieel uitgewerkt status aangeeft
        
        Argumenten:
        element MaterieelUitgewerkt  Informatie uit de consolidatie informatie
        """
        instrument = self.Versiebeheerinformatie.Instrumenten.get (element.WorkId)
        if instrument is None:
            self._Log.Fout ("MaterieelUitgewerkt voor onbekend instrument " + element.WorkId + " @" + element.ConsolidatieInformatie.GemaaktOp)
            self.Resultaat.IsValide = False
            return
        if element.Datum is None:
            if instrument.MaterieelUitgewerkt is None:
                self._Log.Waarschuwing ("Instrument " + element.WorkId + " is niet materieel uitgewerkt; geen wijziging @" + element.ConsolidatieInformatie.GemaaktOp)
                return
            self._Log.Detail ("Instrument " + element.WorkId + " is niet meer materieel uitgewerkt @" + element.ConsolidatieInformatie.GemaaktOp)
        else:
            if instrument.MaterieelUitgewerkt == element.Datum:
                self._Log.Waarschuwing ("Instrument " + element.WorkId + " is al materieel uitgewerkt per " + element.Datum + "; geen wijziging @" + element.ConsolidatieInformatie.GemaaktOp)
                return
            self._Log.Detail ("Instrument " + element.WorkId + " is materieel uitgewerkt per " + element.Datum + " @" + element.ConsolidatieInformatie.GemaaktOp)

        instrument.MaterieelUitgewerkt = element.Datum
        self.Resultaat.Instrumenten.add (instrument.WorkId)
        if self.Resultaat.Uitwisseling.BekendOp is None or element.BekendOp() > self.Resultaat.Uitwisseling.BekendOp:
            self.Resultaat.Uitwisseling.BekendOp = element.BekendOp()

#----------------------------------------------------------------------
# Hulpmethoden om het resultaat bij te werken
#----------------------------------------------------------------------
    def _VoegInstrumentDoelenToe (self, instrument, doel, bekendOp, isInhoud, eId):
        """Werk de administratie bij dat er voor dit instrument voor dit doel
        en deze bekendOp datum iets is gebeurd.
        """
        self.Resultaat.Instrumenten.add (instrument.WorkId)

        instrument.BekendOp.add (bekendOp)
        eersteBekendOp = self.Resultaat.EersteBekendOp.get (instrument.WorkId)
        if eersteBekendOp is None or eersteBekendOp > bekendOp:
            self.Resultaat.EersteBekendOp[instrument.WorkId] = bekendOp

        if not self._Publicatieblad is None:
            juridischeVarantwoording = self.Resultaat.Verantwoording.get (instrument.WorkId)
            if juridischeVarantwoording is None:
                self.Resultaat.Verantwoording[instrument.WorkId] = juridischeVarantwoording = JuridischeVerantwoording ()
            verantwoording = juridischeVarantwoording.Verantwoording.get (doel)
            if verantwoording is None:
                juridischeVarantwoording.Verantwoording[doel] = verantwoording = Verantwoording ()
                verantwoording.Doel = doel
                verantwoording.Publicaties.append (Publicatie ())
                verantwoording.Publicaties[0].Publicatieblad = self._Publicatieblad
                verantwoording.Publicaties[0].GemaaktOp = self.Resultaat.Uitwisseling.GemaaktOp

            if isInhoud:
                verantwoording.Publicaties[0].eIdInhoud = 'eid_inhoud_onbekend' if eId is None else eId
            else:
                # Deze simulator werkt niet goed als de twee soorten tijdstempels andere eId hebben
                # Dan wordt de eerste gekozen
                verantwoording.Publicaties[0].eIdTijdstempels = 'eid_tijdstempel_onbekend' if eId is None else eId


#----------------------------------------------------------------------
# Hulpmethoden om de cumulatieve bijdrage te bepalen voor elke momentopname
#----------------------------------------------------------------------
    def _BepaalCumulatieveBijdragen (self):

        # Houdt bij welke momentopnamen al afgehandeld zijn.
        gedaan = set ()

        def __VoerBepalingUit (momentopname: MomentopnameInstrument, cyclischeVerwijzingen):
            """Zorg dat de cumulatieve bijdrage voor de momentopname bepaald wordt

            Argumenten:

            momentopname MomentopnameInstrument  Momentopname waarvoor de bijdrage bepaald moet worden of nodig is
            cyclischeVerwijzingen {} ConsolidatieInformatie van momentopnamen die de cumulatieve bijdragen van deze momentopname nodig hebben.

            Geeft terug of de cumulatieve bijdrage bekend is.
            """
            if not momentopname.BranchesCumulatief is None:
                # Is al bekend
                return True

            if momentopname.Branch in cyclischeVerwijzingen:
                self._Log.Fout ("Consolidatie-informatie verwijst in een cirkel naar elkaar: " + ", ".join (ci.ModuleXmlNaam () + " voor (" + str(b.Doel) + "" + ", @" + ci.ConsolidatieInformatie.GemaaktOp + ")" for b, ci in cyclischeVerwijzingen.items ()))
                self.Resultaat.IsValide = False
                return False
            cyclischeVerwijzingen[momentopname.Branch] = momentopname._ConsolidatieInformatieElementen[0]

            if momentopname in gedaan:
                # Is niet bekend maar is al wel eerder naar gekeken. Onderdeel van cyslische verwijzingen
                return False
            gedaan.add (momentopname)

            # Zorg dat de cumulatieve bijdragen van de bronnen van verwijzingen bekend zijn
            isValide = True
            for versie in momentopname.Basisversies.values ():
                if versie.BranchesCumulatief is None:
                    if not __VoerBepalingUit (versie, {**cyclischeVerwijzingen}):
                        isValide = False
            for versie in momentopname.VervlochtenMet.values ():
                if versie.BranchesCumulatief is None:
                    if not __VoerBepalingUit (versie, {**cyclischeVerwijzingen}):
                        isValide = False
            for versie in momentopname.OntvlochtenMet.values ():
                if versie.BranchesCumulatief is None:
                    if not __VoerBepalingUit (versie, {**cyclischeVerwijzingen}):
                        isValide = False

            if isValide:
                # Voer de bepaling uit
                AccumuleerBranchInformatie.VoorMomentopname (self._Log, momentopname)
            return isValide

        for nieuweMomentopname in self._ToegevoegdeMomentopnamen:
            if not nieuweMomentopname in gedaan:
                __VoerBepalingUit (nieuweMomentopname.Momentopname, {})


#----------------------------------------------------------------------
# Hulpmethoden om momentopnameverwijzingen over te nemen
#----------------------------------------------------------------------
    def _NeemMomentopnameReferentiesOver (self, nieuweMomentopname : MomentopnameInstrument):
        """Neem de basisversies en ont-/vervlochten versies over
        
        Argumenten:
        nieuweMomentopname NieuweMomentopname Momentopname waarin de verwijzingen overgenomen moeten worden
        """
        voorInstrument = nieuweMomentopname.Momentopname._ConsolidatieInformatieElementen[0]

        # Hou bij welke (andere) doelen bijdragen aan deze momentopname
        # key = doel, value = instantie van VerwerkteMomentopname
        verwerkteDoelen = { } 
        for versie in voorInstrument.Basisversies.values():
            verwijzing = self._ZoekMomentopname (nieuweMomentopname.Instrument, voorInstrument, nieuweMomentopname.Branch.Doel, versie, "Basisversie", verwerkteDoelen)
            if not verwijzing is None:
                nieuweMomentopname.Momentopname.Basisversies[versie.Doel] = verwijzing
                verwerkteDoelen[versie.Doel] = VerwerkteMomentopname ("Basisversie", verwijzing, True)
                if verwijzing.IsTeruggetrokken:
                    # Een ingetrokken basisversie is niet toegestaan als startpunt voor een nieuwe branch
                    if not verwijzing.Branch.Doel in nieuweMomentopname.Momentopname.Doelen:
                        self._Log.Fout ('Teruggetrokken branch (' + str(versie.Doel) + ',@' + verwijzing.GemaaktOp + ') mag geen basisversie zijn voor de branch(es) ' + ', '.join (str(d) for d in nieuweMomentopname.Momentopname.Doelen) + ", @" + nieuweMomentopname.Momentopname.GemaaktOp)
                        self.Resultaat.IsValide = False

        if hasattr (voorInstrument, 'VervlochtenVersies'):
            for versie in voorInstrument.VervlochtenVersies.values():
                verwijzing = self._ZoekMomentopname (nieuweMomentopname.Instrument, voorInstrument, nieuweMomentopname.Branch.Doel, versie, "VervlochtenVersies", verwerkteDoelen)
                if not verwijzing is None:
                    nieuweMomentopname.Momentopname.VervlochtenMet[versie.Doel] = verwijzing
                    verwerkteDoelen[versie.Doel] = VerwerkteMomentopname ("VervlochtenVersies", verwijzing, False)
                    if verwijzing.IsTeruggetrokken:
                        # Een ingetrokken basisversie is niet toegestaan als vervlochten versie
                        self._Log.Fout ('Teruggetrokken branch (' + str(versie.Doel) + ',@' + verwijzing.GemaaktOp + ') mag niet vervlochten worden met een andere branch (' + str(nieuweMomentopname.Momentopname.Branch.Doel) + ", @" + nieuweMomentopname.Momentopname.GemaaktOp + ')')
                        self.Resultaat.IsValide = False

        if hasattr (voorInstrument, 'OntvlochtenVersies'):
            for versie in voorInstrument.OntvlochtenVersies.values():
                verwijzing = self._ZoekMomentopname (nieuweMomentopname.Instrument, voorInstrument, nieuweMomentopname.Branch.Doel, versie, "OntvlochtenVersies", verwerkteDoelen)
                if not verwijzing is None:
                    nieuweMomentopname.Momentopname.OntvlochtenMet[versie.Doel] = verwijzing
                    verwerkteDoelen[versie.Doel] = VerwerkteMomentopname ("OntvlochtenVersies", verwijzing, False)


    def _ZoekMomentopname (self, instrument : Instrument, voorInstrument : VoorInstrument, doel, verwijzing, collectieType, verwerkteDoelen):
        """Zoek een verwijzing naar een momentopname op in de momentopnamen van de branches van het instrument
        
        Argumenten:
        instrument Instrument  Instrument waarvoor de momentopname gemaakt is
        voorInstrument VoorInstrument ConsolidatieInformatie element waarvan de verwijzingen overgenomen moeten worden
        doel string  Doel van de momentopname waarvan de verwijzingen overgenomen moeten worden
        verwijzing ConsolidatieInformatie.Momentopname  Op te zoeken verwijzing naar een momentopname
        collectietype string  Geeft aan waar de verwijzing vandaan komt (Basisversie, VervlochtenVersie, OntvlochtenVersie)
        verwerkteDoelen dictionary Verwijzingen die al verwerkt zijn

        Resultaat is de Momentopname of None
        """
        if not verwijzing.Doel in instrument.Branches:
            self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en instrument " + voorInstrument.WorkId + " heeft " + collectieType + " voor onbekend doel " + str(verwijzing.Doel))
            self.Resultaat.IsValide = False
            return

        if verwijzing.Doel in verwerkteDoelen:
            alVerwerkt = verwerkteDoelen[verwijzing.Doel]
            if not alVerwerkt.IsBasisversie:
                self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en instrument " + voorInstrument.WorkId + " heeft " + collectieType + " voor doel " + str(verwijzing.Doel) + " dat ook al vermeld is in " + alVerwerkt.CollectieType)
                self.Resultaat.IsValide = False
                return
            elif verwijzing.GemaaktOp <= alVerwerkt.Momentopname.GemaaktOp:
                self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en instrument " + voorInstrument.WorkId + " heeft " + collectieType + " voor doel " + str(verwijzing.Doel) + " met een gemaaktOp die niet groter is dan van de basisversie voor hetzelfde doel")
                self.Resultaat.IsValide = False
                return

        branch = instrument.Branches[verwijzing.Doel]
        for mo in branch.Momentopnamen:
            if mo.GemaaktOp == verwijzing.GemaaktOp:
                return mo

        self._Log.Fout (voorInstrument.ModuleXmlNaam () + " voor (" + str(doel) + ", @" + voorInstrument.ConsolidatieInformatie.GemaaktOp + ") en instrument " + voorInstrument.WorkId + " heeft een " + collectieType + " die verwijst naar een " + ("toekomstige" if voorInstrument.ConsolidatieInformatie.GemaaktOp < verwijzing.GemaaktOp else "onbekende") + " momentopname (" + str(verwijzing.Doel) + ", @" + verwijzing.GemaaktOp + ")")
        self.Resultaat.IsValide = False

class NieuweMomentopname:

    def __init__(self, instrument : Instrument, branch : Branch, momentopname : MomentopnameInstrument):
        """Bewaar het instrument en de branch voor een nieuwe momentopname,
        zodat er geen onderlinge verwijzingen in het datamodel nodig zijn.
        """
        self.Instrument = instrument
        self.Branch = branch
        self.Momentopname = momentopname

class VerwerkteMomentopname:

    def __init__ (self, collectietype, momentopname : MomentopnameInstrument, isBasisversie):
        """Maak een cogistratie van een momentopname-verwijzing die reeds verwerkt is

        Argumenten:
        collectietype string  Geeft aan waar de verwijzing vandaan komt (Basisversie, VervlochtenVersie, OntvlochtenVersie)
        momentopname Momentopname De momentopname waarnaar verwezen wordt
        isBasisVersie boolean  Geeft aan dat dit een basisversie is
        """
        self.CollectieType = collectietype
        self.Momentopname = momentopname
        self.IsBasisversie = isBasisversie

