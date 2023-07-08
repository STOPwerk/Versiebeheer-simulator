#======================================================================
# Unit tests voor Python code in data_annotatie.py
#======================================================================
import unittest

import json

import test_init
from applicatie_meldingen import Meldingen
from data_doel import Doel
from data_annotatie import Annotatie

class Test_data_lv_annotatie(unittest.TestCase):
#======================================================================
# Lezen van de specificatie
#======================================================================

#----------------------------------------------------------------------
# Valide
#----------------------------------------------------------------------
    def test_Minimaal_GemaaktOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "Initieel" }
    ]
}''','''{
    "Naam": "test",
    "WorkId": "/akn/nl/act/gm9999/2022/reg001",
    "Synchronisatie": "P",
    "Versies": [
        {
            "Doelen": [
                "doel1"
            ],
            "_Beschrijving": "Initieel",
            "GemaaktOp": "2022-05-25T07:00:00Z"
        }
    ]
}''')

    def test_Uitgebreid_GemaaktOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/join/id/regdata/2022/io001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "Initieel" },
        { "GemaaktOp": "2022-04-25T07:00:00Z", "Doelen": [ "doel2", "doel3" ], "Beschrijving": "Dubbel" },
        { "GemaaktOp": "2022-08-25T07:00:00Z", "Doelen": [ "doel42" ], "Beschrijving": "Tweede" }
    ]
}''','''{
    "Naam": "test",
    "WorkId": "/join/id/regdata/2022/io001",
    "Synchronisatie": "P",
    "Versies": [
        {
            "Doelen": [
                "doel2",
                "doel3"
            ],
            "_Beschrijving": "Dubbel",
            "GemaaktOp": "2022-04-25T07:00:00Z"
        },
        {
            "Doelen": [
                "doel1"
            ],
            "_Beschrijving": "Initieel",
            "GemaaktOp": "2022-05-25T07:00:00Z"
        },
        {
            "Doelen": [
                "doel42"
            ],
            "_Beschrijving": "Tweede",
            "GemaaktOp": "2022-08-25T07:00:00Z"
        }
    ]
}''')

    def test_Minimaal_UitgewisseldOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Synchronisatie": "Doel",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "UitgewisseldOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "Initieel" }
    ]
}''','''{
    "Naam": "test",
    "WorkId": "/akn/nl/act/gm9999/2022/reg001",
    "Synchronisatie": "W",
    "Versies": [
        {
            "Doelen": [
                "doel1"
            ],
            "_Beschrijving": "Initieel",
            "UitgewisseldOp": "2022-05-25T07:00:00Z"
        }
    ]
}''')

    def test_Uitgebreid_UitgwisseldOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Synchronisatie": "Toestand",
    "Instrument": "/join/id/regdata/2022/io001",
    "Uitwisselingen": [
        { "UitgewisseldOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "Initieel" },
        { "UitgewisseldOp": "2022-04-25T07:00:00Z", "Doelen": [ "doel2", "doel3" ], "Beschrijving": "Dubbel" },
        { "UitgewisseldOp": "2022-08-25T07:00:00Z", "Doelen": [ "doel42" ], "Beschrijving": "Tweede" }
    ]
}''','''{
    "Naam": "test",
    "WorkId": "/join/id/regdata/2022/io001",
    "Synchronisatie": "T",
    "Versies": [
        {
            "Doelen": [
                "doel2",
                "doel3"
            ],
            "_Beschrijving": "Dubbel",
            "UitgewisseldOp": "2022-04-25T07:00:00Z"
        },
        {
            "Doelen": [
                "doel1"
            ],
            "_Beschrijving": "Initieel",
            "UitgewisseldOp": "2022-05-25T07:00:00Z"
        },
        {
            "Doelen": [
                "doel42"
            ],
            "_Beschrijving": "Tweede",
            "UitgewisseldOp": "2022-08-25T07:00:00Z"
        }
    ]
}''')

#----------------------------------------------------------------------
# Met fouten
#----------------------------------------------------------------------
    def test_Fout_GeenNaam(self):
        self._Test_LeesJson ('''{
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None,True)

    def test_Fout_NaamGeenString(self):
        self._Test_LeesJson ('''{
    "Annotatie": 42,
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_GeenIntrument(self):
        self._Test_LeesJson ('''{
    "Naam": "naam",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None,True)

    def test_Fout_IntrumentGeenString(self):
        self._Test_LeesJson ('''{
    "Annotatie": "naam",
    "Instrument": 42,
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_IntrumentGeenWork(self):
        self._Test_LeesJson ('''{
    "Annotatie": "naam",
    "Instrument": "instrument",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_IntrumentExpression(self):
        self._Test_LeesJson ('''{
    "Annotatie": "naam",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001@nld/2022/1242",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_GeenUitwisselingen(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001"
}''',None)

    def test_FoutUitwisselingenLeeg(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [ ]
}''',None)

    def test_Fout_UitwisselingenTekst(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": "ja"
}''',None)


    def test_Fout_UitwisselingenObject(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": { "ja": 42 }
}''',None)

    def test_Fout_GemaaktOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": 42, "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_GemaaktOpOngeldig(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25", "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_WelNietGemaaktOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "Doelen": [ "doel1" ], "Beschrijving": "test" },
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel2" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_GemaaktOpDubbel(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" },
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel2" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_UitgewisseldOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Synchronisatie": "Toestand",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "UitgewisseldOp": 42, "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_UitgewisseldOpOngeldig(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Synchronisatie": "Toestand",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "UitgewisseldOp": "2022-05-25", "Doelen": [ "doel1" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_WelNietUitgewisseldOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Synchronisatie": "Toestand",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "Doelen": [ "doel1" ], "Beschrijving": "test" },
        { "UitgewisseldOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel2" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_UitgewisseldOpDubbel(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Synchronisatie": "Toestand",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "UitgewisseldOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" },
        { "UitgewisseldOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel2" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_GemaaktOpIpvUitgewisseldOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Synchronisatie": "Toestand",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-04-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" },
        { "UitgewisseldOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel2" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_UitgewisseldOpIpvGemaaktOp(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-04-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": "test" },
        { "UitgewisseldOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel2" ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_GeenDoelen(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_DoelenLeeg(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_Doelen(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ 42 ], "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_DoelenTekst(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": "ja", "Beschrijving": "test" }
    ]
}''',None)

    def test_Fout_DoelenDubbel(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1", "doel1" ], "Beschrijving": "test" }
    ]
}''',None, aantalFouten = 0, aantalWaarschuwingen = 1)

    def test_Fout_GeenBeschrijving(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ] }
    ]
}''',None)

    def test_Fout_BeschrijvingGeenString(self):
        self._Test_LeesJson ('''{
    "Annotatie": "test",
    "Instrument": "/akn/nl/act/gm9999/2022/reg001",
    "Uitwisselingen": [
        { "GemaaktOp": "2022-05-25T07:00:00Z", "Doelen": [ "doel1" ], "Beschrijving": 42 }
    ]
}''',None)

#----------------------------------------------------------------------
# Uitvoeren van de test
#----------------------------------------------------------------------
    def _Test_LeesJson (self, data, verwacht, geenActual = False, aantalFouten = 1, aantalWaarschuwingen = 0):
        """Lees de JSON in en vergelijk dat met de verwachte uitkomst
        
        Argumenten:
        data  string JSON van de specificatie
        verwacht string  dump naar JSON van de ingelezen specificatie, of None als een fout verwacht wordt
        geenActual bool Geeft aan dat het inlezen van de JSON niet leidt tot een (al dan niet valide) instantie van Annotatie
        aantalFouten int Als verwacht is None: aantal fouten dat verwacht wordt
        aantalWaarschuwingen int Aantal waarschuwingen dat verwacht wordt
        """
        log = Meldingen (False)
        actual = Annotatie.LeesJson (log, "test.json", json.loads (data))
        if verwacht is None:
            if geenActual:
                self.assertIsNone (actual)
            else:
                if log.Fouten != aantalFouten or log.Waarschuwingen != aantalWaarschuwingen:
                    self.fail ("Fouten (" + str(aantalFouten) + ")/waarschuwingen (" + str(aantalWaarschuwingen) + ") verwacht, maar: " + log.MaakTekst ())
                if not actual is None:
                    self.assertEqual (log.Fouten == 0, actual._IsValide)
        else:
            if log.Fouten > 0 or log.Waarschuwingen != aantalWaarschuwingen:
                self.fail ("Fouten (0/waarschuwingen (" + str(aantalWaarschuwingen) + ") verwacht, maar: " + log.MaakTekst ())
            self.assertIsNotNone (actual)
            self.assertEqual (verwacht.strip (), json.dumps (actual, indent=4, cls=JsonClassEncoder).strip ())
            self.assertTrue (actual._IsValide)

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
        if isinstance (o, Doel):
            return o.Identificatie
        data = {}
        for key in o.__dict__.keys():
            if key[0:1] == '_' and key != '_Beschrijving':
                continue
            value = o.__dict__[key]
            if isinstance (value, list) and len (value) == 0:
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
