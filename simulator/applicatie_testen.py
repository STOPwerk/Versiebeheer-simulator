#======================================================================
#
# Uitvoeren van testen
#
#----------------------------------------------------------------------
#
# Ondersteuning voor het uitvoeren van (unit) testen door de
# applicatie. Het is bewerkelijk om alle unit testen in Python te
# coderen. Daarom kan de applicatie zelf ook unit testen uitvoeren.
# Zo'n unit test is een map met invoerbestanden voor de consolidatie
# (als gebruikelijk), en daarnaast bestanden met de verwachte 
# resultaten in JSON ("<data>_verwacht.json"). De applicatie
# bewaart de gegenereerde data ("<data>_actueel.json") en vergelijkt
# de twee na uitvoeren van het consolidatieproces.
# 
# Een test kan uitgevoerd worden door de applicatie te draaien 
# met --testen als argument. Gebruik optie --alle om een reeks
# unit testen in subdirectories te testen.
#
#----------------------------------------------------------------------
#
# Het hart van de unit test functionaliteit is de UnitTests klasse
# die op applicatieniveau voor elk gevonden scenario (= set van 
# invoerbestanden) wordt uitgevoerd.
#
# Om de resultaten van de consolidatie te kunnen bewaren als JSON
# zijn en aantal JsonEncoders opgenomen.
#
#======================================================================

import json
from json import JSONEncoder
import os
import os.path
import time

from data_actueleannotaties import ActueleToestandenMetAnnotaties
from data_doel import Doel
from data_scenario import Scenario
from data_versiebeheerinformatie import Branch, Instrument, Momentopname, Uitwisseling
from proces_consolidatie import Proces_Consolidatie
from weergave_data_proefversies import ProefversieAnnotatie
from weergave_resultaat import ResultaatGenerator
from weergave_webpagina import WebpaginaGenerator


#======================================================================
#
# Uitvoeren van de unit tests
#
#======================================================================
class UnitTests:
    
    @staticmethod
    def VoerUit (scenario : Scenario):
        """Voeren de unit tests uit
        
        Argumenten:
        scenario Scenario Invoer voor het consolidatiescenario

        Geeft terug of de unit test is geslaagd
        """

        test = UnitTests (scenario)
        test._VoerUit ()
        return test.Succes

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, scenario : Scenario):
        """Maak een nieuwe instantie voor het testen
        
        Argumenten:
        scenario Scenario Invoer voor het consolidatiescenario
        """
        self._Scenario = scenario
        # Proces voor het uitvoeren van de consolidatie
        self._Proces = Proces_Consolidatie (self._Scenario)
        # Basisnaam voor het bestand met meldingen uit het proces
        self._MeldingenBasisPad = os.path.join (self._Scenario.Pad, "Test_Meldingen")
        # Basisnaam voor het bestand met versiebeheerinformatie
        self._VersiebeheerinformatieBasisPad = os.path.join (self._Scenario.Pad, "Test_Versiebeheerinformatie")
        # Basisnaam voor het bestand met cumulatieve branch informatie
        self._BranchesCumulatiefBasisPad = os.path.join (self._Scenario.Pad, "Test_BranchesCumulatief")
        # Basisnaam voor het bestand met proefversies
        self._ProefversiesBasisPad = os.path.join (self._Scenario.Pad, "Test_Proefversies")
        # Basisnaam voor het bestand met actuele toestanden
        self._ActueleToestandenBasisPad = os.path.join (self._Scenario.Pad, "Test_ActueleToestanden")
        # Basisnaam voor het bestand met complete toestanden
        self._CompleteToestandenBasisPad = os.path.join (self._Scenario.Pad, "Test_CompleteToestanden")
        # Basisnaam voor het bestand met annotaties bij complete toestanden
        self._AnnotatiesBasisPad = os.path.join (self._Scenario.Pad, "Test_Annotaties")
        # Geeft aan of de unit tests geslaagd zijn
        self.Succes = True

    # Deel van de bestandsnaam die achter de basisnaam komt voor het bestand met de gegenereerde data
    _Actueel_Extensie = "_actueel.json"
    # Deel van de bestandsnaam die achter de basisnaam komt voor het bestand met de verwachte data
    _Verwacht_Extensie = "_verwacht.json"
    
    def _VoerUit (self):
        """Voer het testproces uit"""
        try:
            if self._Scenario.IsValide:
                self._Scenario.ApplicatieLog.Detail ("Start van unit test: " + self._Scenario.Pad)
                start = time.perf_counter ()
                self._Proces.VoerUit ()
                tijd = time.perf_counter() - start
                self._Scenario.ApplicatieLog.Informatie ("Consolidatie voor test uitgevoerd ({:.3f}s)".format(tijd))
            else:
                self._Scenario.ApplicatieLog.Informatie ("Scenario in '" + self._Scenario.Pad + "' niet uitgevoerd wegens invalide invoer")

            self._BewaarEnTestResultaten ()
            self._Scenario.ApplicatieLog.Informatie ('Voor een verslag zie: <a href="' + WebpaginaGenerator.UrlVoorPad (self._Scenario.ResultaatPad) + '">' +  self._Scenario.ResultaatPad + '</a>')

        except Exception as e:
            self.Succes = False
            self._Scenario.ApplicatieLog.Fout ("Potverdorie, een fout in het testen die niet voorzien werd: " + str(e))

#----------------------------------------------------------------------
#
# Bewaar de resultaten als JSON en vergelijk de json met de verwachte waarde
#
##----------------------------------------------------------------------

    def _BewaarEnTestResultaten (self):
        """Bewaar alle gegenereerde informatie als JSON."""

        self._BewaarEnTestResultaat ("Fouten en waarschuwingen", self._MeldingenBasisPad, json.dumps (self._Scenario.Log.FoutenWaarschuwingen (), indent=4, cls=JsonClassEncoder, ensure_ascii=False))

        # Maak JSON voor data
        versiebeheerinformatie = None
        branchesCumulatief = None
        proefversies = None
        actueleToestanden = None
        completeToestanden = None
        annotaties = None
        if self._Scenario.Versiebeheerinformatie:
            versiebeheerinformatie = json.dumps({ "Testresultaat - Versiebeheerinformatie" : self._Scenario.Versiebeheerinformatie }, indent=4, cls=JsonClassEncoder, ensure_ascii=False)
            data = { "Testresultaat - Cumulatieve versieinformatie" : {
                instr.WorkId : {
                    str (b.Doel) : [
                        { 
                            "GemaaktOp" : mo.GemaaktOp, 
                            "Cumulatief": None if mo.BranchesCumulatief is None else { str(d) : bc for d, bc in sorted (mo.BranchesCumulatief.items (), key = lambda x: x[0].Identificatie) }
                        } for mo in b.Momentopnamen
                    ]
                    for b in sorted (instr.Branches.values (), key = lambda x: x.Doel.Identificatie)
                } for instr in sorted (self._Scenario.Versiebeheerinformatie.Instrumenten.values (), key = lambda x: x.WorkId)
            } }
            branchesCumulatief = json.dumps(data, indent=4, cls=JsonClassEncoder, ensure_ascii=False)

            if not self._Scenario.WeergaveData is None:
                if self._Scenario.Opties.Proefversies:
                    data = { "Testresultaat - Proefversies" : { workId : [i.Proefversies for i in data.Uitwisselingen if hasattr (i, 'Proefversies') ] for workId,data in self._Scenario.WeergaveData.InstrumentData.items () if data.HeeftProefversies } }
                    proefversies = json.dumps(data, indent=4, cls=JsonClassEncoder, ensure_ascii=False)

                if self._Scenario.Opties.ActueleToestanden:
                    data = { "Testresultaat - ActueleToestanden" : { workId : [i.ActueleToestanden for i in data.Uitwisselingen] for workId,data in self._Scenario.WeergaveData.InstrumentData.items () if data.HeeftActueleToestanden } }
                    actueleToestanden = json.dumps(data, indent=4, cls=JsonClassEncoder, ensure_ascii=False)

                    if len (self._Scenario.Annotaties) > 0:
                        data = { "Testresultaat - Annotaties" : { workId :  JsonClassEncoder.NaarJsonableObject(data.Annotaties) for workId,data in self._Scenario.GeconsolideerdeInstrumenten.items () if not data.Annotaties is None } }
                        annotaties = json.dumps(data, indent=4, cls=JsonClassEncoder, ensure_ascii=False)

                if self._Scenario.Opties.CompleteToestanden:
                    data = { "Testresultaat - CompleteToestanden" : { workId : data.Uitwisselingen[-1].GefilterdeCompleteToestanden() for workId,data in self._Scenario.WeergaveData.InstrumentData.items () if data.HeeftCompleteToestanden } }
                    completeToestanden = json.dumps(data, indent=4, cls=JsonClassEncoder, ensure_ascii=False)

        self._BewaarEnTestResultaat ("Versiebeheerinformatie", self._VersiebeheerinformatieBasisPad, versiebeheerinformatie)
        self._BewaarEnTestResultaat ("Cumulatieve versieinformatie", self._BranchesCumulatiefBasisPad, branchesCumulatief)
        self._BewaarEnTestResultaat ("Proefversies", self._ProefversiesBasisPad, proefversies)
        self._BewaarEnTestResultaat ("Actuele toestanden", self._ActueleToestandenBasisPad, actueleToestanden)
        self._BewaarEnTestResultaat ("Complete toestanden", self._CompleteToestandenBasisPad, completeToestanden)
        self._BewaarEnTestResultaat ("Annotaties", self._AnnotatiesBasisPad, annotaties)
        
        if self._Scenario.Opties.Applicatie_Resultaat:
            ResultaatGenerator.MaakPagina (self._Scenario)
        else:
            ResultaatGenerator.MaakMeldingen (self._Scenario)


    def _BewaarEnTestResultaat (self, naam, basispad, json):
        """Bewaar de JSON van de gegenereerde data en vergelijk dat met de verwachting (indien beschikbaar)
        
        Argumenten:
        naam string  Naam van de informatie
        basispad string  Basispad voor de opslag van de JSON
        json string  Gegenereerde informatie als json
        """

        # Bewaar de informatie als json
        actueel_pad = basispad + UnitTests._Actueel_Extensie
        if json is None:
            if os.path.isfile (actueel_pad):
                try:
                    os.remove (actueel_pad)
                except Exception as e:
                    self._Scenario.Log.Waarschuwing ("Kan bestand '" + naam + ".json' niet verwijderen: " + str(e))
        else:
            try:
                with open (actueel_pad, "w", encoding = "utf-8") as jsonBestand:
                    jsonBestand.write (json)
            except Exception as e:
                self._Scenario.Log.Waarschuwing ("Kan bestand '" + naam + ".json' niet schrijven: " + str(e))

        # Vergelijk dat met het verwachte resultaat
        if self._IsVerwachtingBeschikbaar (basispad):
            verwacht_pad = basispad + UnitTests._Verwacht_Extensie
            with open (verwacht_pad, "r", encoding = "utf-8") as jsonBestand:
                json_verwacht = [*filter(None, jsonBestand.read ().replace ('\r','').split ('\n'))]
            if len (json_verwacht) > 0:
                verwacht_resultaat_bestand = '<a href="' + os.path.basename (basispad) + UnitTests._Verwacht_Extensie + '" target="_blank">json</a>'
                verwacht_resultaat_pad = '<a href="' + WebpaginaGenerator.UrlVoorPad (verwacht_pad) + '" target="_blank">json</a>'

            if json:
                json = [*filter(None, json.replace ('\r','').split ('\n'))]
                actueel_resultaat_bestand = '<a href="' + os.path.basename (basispad) + UnitTests._Actueel_Extensie + '" target="_blank">json</a>'
                actueel_resultaat_pad = '<a href="' + WebpaginaGenerator.UrlVoorPad (actueel_pad) + '" target="_blank">json</a>'

                if len (json_verwacht) > 0:
                    idxFout = None
                    for idx, regel in enumerate(json):
                        if idx >= len(json_verwacht):
                            idxFout = idx
                            break
                        if json_verwacht[idx].strip () != regel.strip ():
                            idxFout = idx
                            break
                    if idxFout is None and len(json) < len(json_verwacht):
                        idxFout = len(json)

                    if idxFout is None:
                        self._Scenario.Log.Informatie (naam + ": resultaat (data) komt overeen met de verwachting")
                    else:
                        self._Scenario.Log.Fout (naam + ': verwacht (' + verwacht_resultaat_bestand + ') en uitkomst (' + actueel_resultaat_bestand + ') verschillen vanaf regel ' + str (idxFout+1))
                        self._Scenario.ApplicatieLog.Fout (naam + ': verwacht (' + verwacht_resultaat_pad + ') en uitkomst (' + actueel_resultaat_pad + ') verschillen vanaf regel ' + str (idxFout+1) +  ' (' + self._Scenario.Pad + ')')
                        self.Succes = False
                else:
                    self._Scenario.Log.Fout (naam + ': verwacht (geen data) en uitkomst (' + actueel_resultaat_bestand + ') verschillen')
                    self._Scenario.ApplicatieLog.Fout (naam + ': verwacht (geen data) en uitkomst (' + actueel_resultaat_pad + ') verschillen (' + self._Scenario.Pad + ')')
                    self.Succes = False
            else:
                if len (json_verwacht) > 0:
                    self._Scenario.Log.Fout (naam + ': verwacht (' + verwacht_resultaat_bestand + ') en uitkomst (geen data) verschillen')
                    self._Scenario.ApplicatieLog.Fout (naam + ': verwacht (' + verwacht_resultaat_pad + ') en uitkomst (geen data) verschillen (' + self._Scenario.Pad + ')')
                    self.Succes = False
                else:
                    self._Scenario.Log.Informatie (naam + ": resultaat (geen data) komt overeen met de verwachting")
        elif not json is None:
            self._Scenario.Log.Informatie (naam + ": geen verwachte resultaten beschikbaar")

    def _IsVerwachtingBeschikbaar (self, basispad):
        """Geeft aan of er een verwachting beschikbaar is voor de gegenereerde data
        
        Argumenten:
        basispad string Basisnaam van het bestand waarin de resultaten worden opgeslagen
        """
        return os.path.isfile (basispad + UnitTests._Verwacht_Extensie)

#======================================================================
#
# Hulpklassen voor het vertalen van in-memory data van/naar json.
#
#======================================================================

#----------------------------------------------------------------------
# Encoder om in-memory objecten die als class zijn gedefinieerd 
# naar json te kunnen vertalen, met weglating van de "verborgen"
# attributen.
#
# Daarnaast worden voor specifieke objecten attributen weggelaten
# die als circulaire referentie gezien worden.
#----------------------------------------------------------------------
class JsonClassEncoder(JSONEncoder):

    def default(self, o):
        """Overschrijft standaard serialisatie van objecten"""
        if isinstance (o, set):
            return sorted (o)
        behalveAttributen = set()
        if isinstance (o, Branch):
            behalveAttributen = set([
                'Doel' # Zit al in dictionary
                ])
        if isinstance (o, Doel):
            return o.Identificatie
        elif isinstance (o, Instrument):
            behalveAttributen = set([
                'WorkId' # Zit al in dictionary
                ])
        elif isinstance (o, Momentopname):
            behalveAttributen = set([
                'Branch', # Verwijzing naar eigenaar
                'BranchesCumulatief' # Overzicht van versiebeheer tot nu toe
                ])
        elif isinstance (o, Uitwisseling):
            behalveAttributen = set([
                'Proefversies' # Wordt apart naar een json geschreven
                ])

        data = {}
        for key in sorted (o.__dict__.keys()): # Sorteer zodat de JSON er hetzelfde uitziet ongeacht implementatie
            if key == 'Basisversies' or key == 'VervlochtenMet' or key == 'OntvlochtenMet':
                # Eigenschap van Momentopname: lijst van instanties
                lijst = o.__dict__[key]
                if lijst:
                    verwijzingen = {}
                    for doel, momentopname in sorted (lijst.items (), key = lambda x: x[0].Identificatie):
                        verwijzingen[doel.Identificatie] = momentopname.GemaaktOp
                    data[key] = verwijzingen
                continue
            if key[0:1] == '_' or key in behalveAttributen:
                continue
            value = o.__dict__[key]
            if value is None:
                continue
            if (isinstance (value, dict) or isinstance (value, list)) and len (value) == 0:
                continue
            if isinstance (value, dict):
                if isinstance (list(value.keys())[0], Doel):
                    value = { k.Identificatie : v for k, v in value.items() }

            data[key] = value
        return data

    @staticmethod
    def NaarJsonString (data, enkeleRegel = False):
        """Vertaal de data naar json

        Argumenten:
        data object  Data die naar json vertaald moet worden
        enkeleRegel boolean Geeft aan of alle json op een enkele regel moet komen
        """
        if enkeleRegel:
            return JsonClassEncoder().encode (data)
        else:
            return json.dumps(data, indent=4, cls=JsonClassEncoder)

    @staticmethod
    def NaarJsonableObject (o : ActueleToestandenMetAnnotaties):
        data = ActueleToestandenMetAnnotaties ([])
        data.ActueleToestanden = o.ActueleToestanden
        data.UitProefversies = { a.Naam: t for a, t in o.UitProefversies.items () }
        data.VoorToestandViaDoelen = { a.Naam: t for a, t in o.VoorToestandViaDoelen.items () }
        data.VoorDoel = { a.Naam: t for a, t in o.VoorDoel.items () }
        return data
