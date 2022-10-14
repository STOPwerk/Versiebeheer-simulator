#======================================================================
# Unit tests voor Python code in applicatie_procesopties.py
#======================================================================
import unittest

import json

import test_init
from applicatie_procesopties import ProcesOpties
from applicatie_meldingen import Meldingen

class Test_applicatie_procesopties(unittest.TestCase):
#======================================================================
# Lezen van de specificatie van ProcesOpties
#======================================================================

#----------------------------------------------------------------------
# Valide opties
#----------------------------------------------------------------------
    def test_GeenSimulator(self):
        self._Test_LeesJson ('''{
    "SimulatorScenario": false
}''','''{
    "ActueleToestanden": true,
    "CompleteToestanden": true,
    "Applicatie_Resultaat": true,
    "SimulatorScenario": false,
    "IsValide": true
}''')

    def test_ActueleToestanden(self):
        self._Test_LeesJson ('''{
    "ActueleToestanden": false
}''','''{
    "ActueleToestanden": false,
    "CompleteToestanden": true,
    "Applicatie_Resultaat": true,
    "SimulatorScenario": true,
    "IsValide": true
}''')

    def test_CompleteToestanden(self):
        self._Test_LeesJson ('''{
    "CompleteToestanden": false
}''','''{
    "ActueleToestanden": true,
    "CompleteToestanden": false,
    "Applicatie_Resultaat": true,
    "SimulatorScenario": true,
    "IsValide": true
}''')

    def test_Applicatie_Resultaat(self):
        self._Test_LeesJson ('''{
    "Applicatie_Resultaat": false
}''','''{
    "ActueleToestanden": true,
    "CompleteToestanden": true,
    "Applicatie_Resultaat": false,
    "SimulatorScenario": true,
    "IsValide": true
}''')

    def test_Meerdere(self):
        self._Test_LeesJson ('''{
    "CompleteToestanden": false,
    "ActueleToestanden": false
}''', '''{
      "ActueleToestanden": false,
    "CompleteToestanden": false,
    "Applicatie_Resultaat": true,
    "SimulatorScenario": true,
      "IsValide": true
  }''')

    def test_Alles(self):
        self._Test_LeesJson ('''{
    "Procesopties": true
}''', '''{
      "ActueleToestanden": true,
    "CompleteToestanden": true,
    "Applicatie_Resultaat": true,
    "SimulatorScenario": true,
      "IsValide": true
  }''')

    def test_Niets(self):
        self._Test_LeesJson ('''{
    "Procesopties": false
}''','''{
    "ActueleToestanden": false,
    "CompleteToestanden": false,
    "Applicatie_Resultaat": true,
    "SimulatorScenario": true,
    "IsValide": true
}''')

    def test_Leeg(self):
        self._Test_LeesJson ('''{}''', None, True)

#----------------------------------------------------------------------
# Valide weergave
#----------------------------------------------------------------------

    def test_Beschrijving(self):
        self._Test_LeesJson ('''{
    "Beschrijving": "Een <html> beschrijving"
}''','''{
    "ActueleToestanden": true,
    "CompleteToestanden": true,
    "Applicatie_Resultaat": true,
    "Beschrijving": "Een <html> beschrijving",
    "SimulatorScenario": true,
    "IsValide": true
}''')

    def test_Uitwisseling(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ { "naam": "test", "gemaaktOp" : "2022-06-03T17:30:00Z" } ]
}''','''{
    "ActueleToestanden": true,
    "CompleteToestanden": true,
    "Applicatie_Resultaat": true,
    "Uitwisselingen": [
        { 
            "Naam": "test", 
            "GemaaktOp": "2022-06-03T17:30:00Z",
            "IsRevisie": false
        }
    ],
    "SimulatorScenario": true,
    "IsValide": true
}''')

    def test_UitwisselingBeschrijving(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ { "naam": "test", "gemaaktOp" : "2022-06-03T17:30:00Z", "beschrijving": "alstublieft" } ]
}''','''{
    "ActueleToestanden": true,
    "CompleteToestanden": true,
    "Applicatie_Resultaat": true,
    "Uitwisselingen": [
        { 
            "Naam": "test", 
            "GemaaktOp": "2022-06-03T17:30:00Z",
            "Beschrijving": "alstublieft",
            "IsRevisie": false
        }
    ],
    "SimulatorScenario": true,
    "IsValide": true
}''')

    def test_UitwisselingRevisie(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ { "naam": "test", "gemaaktOp" : "2022-06-03T17:30:00Z", "beschrijving": "alstublieft", "revisie": true } ]
}''','''{
    "ActueleToestanden": true,
    "CompleteToestanden": true,
    "Applicatie_Resultaat": true,
    "Uitwisselingen": [
        { 
            "Naam": "test", 
            "GemaaktOp": "2022-06-03T17:30:00Z",
            "Beschrijving": "alstublieft",
            "IsRevisie": true
        }
    ],
    "SimulatorScenario": true,
    "IsValide": true
}''')

    def test_Tijdreis(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId" : [ { "beschrijving": "op reis", "ontvangenOp" : "2022-06-04", "bekendOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-06", "geldigOp" : "2022-06-05" } ] }
}''','''{
    "ActueleToestanden": true,
    "CompleteToestanden": true,
    "Applicatie_Resultaat": true,
    "Tijdreizen": {
        "workId": [
            { 
                "ontvangenOp": "2022-06-04",
                "bekendOp": "2022-06-03",
                "juridischWerkendOp": "2022-06-06",
                "geldigOp": "2022-06-05",
                "Beschrijving": "op reis"
            }
        ]
    },
    "SimulatorScenario": true,
    "IsValide": true
}''')

#----------------------------------------------------------------------
# Met fouten
#----------------------------------------------------------------------

    def test_Fout_Leeg(self):
        self._Test_LeesJson ('''{
    "Anders": "ja"
}''',None,True)

    def test_Fout_String(self):
        self._Test_LeesJson ('''{
    "CompleteToestanden": "ja"
}''',None)

    def test_Fout_Beschrijving(self):
        self._Test_LeesJson ('''{
    "Beschrijving": 42
}''',None)

    def test_Fout_Uitwisseling_Array(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": 42
}''',None)

    def test_Fout_Uitwisseling_ObjectArray(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ 42 ]
}''',None)

    def test_Fout_Uitwisseling_GeenNaam(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ { "gemaaktOp" : "2022-06-03T17:30:00Z" } ]
}''',None)

    def test_Fout_Uitwisseling_Naam(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ { "naam": 42, "gemaaktOp" : "2022-06-03T17:30:00Z" } ]
}''',None)

    def test_Fout_Uitwisseling_Parameters(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ { "naam": "test" } ]
}''',None)

    def test_Fout_Uitwisseling_gemaaktOp(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ { "naam": "test", "gemaaktOp" : "2022-06-03" } ]
}''',None)

    def test_Fout_Uitwisseling_Beschrijving(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ { "naam": "test", "gemaaktOp" : "2022-06-03T17:30:00Z", "beschrijving": 42 } ]
}''',None)

    def test_Fout_Uitwisseling_Revisie(self):
        self._Test_LeesJson ('''{
    "Uitwisselingen": [ { "naam": "test", "gemaaktOp" : "2022-06-03T17:30:00Z", "revisie": "ja" } ]
}''',None)

    def test_Fout_Tijdreis_Object(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": 42
}''',None)

    def test_Fout_Tijdreis_ObjectValueArray(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": 42 }
}''',None)

    def test_Fout_Tijdreis_ObjectValueObjectArray(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ 42 ] }
}''',None)

    def test_Fout_Tijdreis_GeenBeschrijving(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "ontvangenOp" : "2022-06-04", "bekendOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-06", "geldigOp" : "2022-06-05" } ] }
}''',None)

    def test_Fout_Tijdreis_Beschrijving(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": 42, "ontvangenOp" : "2022-06-04", "bekendOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-06", "geldigOp" : "2022-06-05" } ] }
}''',None)

    def test_Fout_Tijdreis_GeenBekendOp(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "ontvangenOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-03", "geldigOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_BekendOpGeenString(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "bekendOp" : 42, "ontvangenOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-03", "geldigOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_BekendOpGeenDatum(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "bekendOp" : "2022-06-03T17:30:00Z", "ontvangenOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-03", "geldigOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_GeenOntvangenOp(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "bekendOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-03", "geldigOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_OntvangenOpGeenString(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "ontvangenOp" : 42, "bekendOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-03", "geldigOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_OntvangenOpGeenDatum(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "ontvangenOp" : "2022-06-03T17:30:00Z", "bekendOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-03", "geldigOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_GeenJuridischWerkendOp(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "bekendOp" : "2022-06-03", "ontvangenOp" : "2022-06-03", "geldigOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_JuridischWerkendOpGeenString(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "juridischWerkendOp" : 42, "bekendOp" : "2022-06-03", "ontvangenOp" : "2022-06-03", "geldigOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_JuridischWerkendOpGeenDatum(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "juridischWerkendOp" : "2022-06-03T17:30:00Z", "bekendOp" : "2022-06-03", "ontvangenOp" : "2022-06-03", "geldigOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_GeenGeldigOp(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "bekendOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-03", "ontvangenOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_GeldigOpGeenString(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "geldigOp" : 42, "bekendOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-03", "ontvangenOp" : "2022-06-03" } ] }
}''',None)

    def test_Fout_Tijdreis_GeldigOpGeenDatum(self):
        self._Test_LeesJson ('''{
    "Tijdreizen": { "workId": [ { "beschrijving": "test", "geldigOp" : "2022-06-03T17:30:00Z", "bekendOp" : "2022-06-03", "juridischWerkendOp" : "2022-06-03", "ontvangenOp" : "2022-06-03" } ] }
}''',None)

#----------------------------------------------------------------------
# Uitvoeren van de test
#----------------------------------------------------------------------
    def _Test_LeesJson (self, data, verwacht, geenActual = False, aantalFouten = 1, aantalWaarschuwingen = 0):
        """Lees de JSON in en vergelijk dat met de verwachte uitkomst
        
        Argumenten:
        data  string JSON van de specificatie
        verwacht string  dump naar JSON van de ingelezen specificatie, of None als een fout verwacht wordt
        aantalFouten int Als verwacht is None: aantal fouten dat verwacht wordt
        aantalWaarschuwingen int Aantal waarschuwingen dat verwacht wordt
        """
        log = Meldingen (False)
        actual = ProcesOpties.LeesJson (log, "test.json", json.loads (data))
        if verwacht is None:
            if geenActual:
                self.assertIsNone (actual)
            else:
                if log.Fouten != aantalFouten or log.Waarschuwingen != aantalWaarschuwingen:
                    self.fail ("Fouten (" + str(aantalFouten) + ")/waarschuwingen (" + str(aantalWaarschuwingen) + ") verwacht, maar: " + log.MaakTekst ())
                if not actual is None:
                    self.assertEqual (log.Fouten == 0, actual.IsValide)
        else:
            if log.Fouten > 0 or log.Waarschuwingen != aantalWaarschuwingen:
                self.fail ("Fouten (0)/waarschuwingen (" + str(aantalWaarschuwingen) + ") verwacht, maar: " + log.MaakTekst ())
            self.assertIsNotNone (actual)
            self.assertEqual ('\n'.join (x.strip () for x in verwacht.strip ().split ('\n')), '\n'.join (x.strip () for x in json.dumps (actual, indent=4, cls=JsonClassEncoder).strip ().split('\n')))
            self.assertTrue (actual.IsValide)
 
#----------------------------------------------------------------------
# Encoder om in-memory objecten die als class zijn gedefinieerd 
# naar json te kunnen vertalen, met weglating van de "verborgen"
# attributen en None values.
#----------------------------------------------------------------------
class JsonClassEncoder(json.JSONEncoder):

    def default(self, o):
        """Overschrijft standaard serialisatie van objecten"""
        if isinstance (o, set):
            return sorted (o)
        data = {}
        for key in o.__dict__.keys():
            if key[0:1] == '_':
                continue
            value = o.__dict__[key]
            if (isinstance (value, list) or isinstance (value, dict)) and len(value) == 0:
                continue
            if not value is None:
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


#======================================================================
# Nodig voor unittest
#======================================================================
if __name__ == '__main__':
    unittest.main()
