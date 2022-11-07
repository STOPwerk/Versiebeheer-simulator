#======================================================================
# Unit tests voor Python code in data_bg_project.py
#======================================================================
import unittest

import json

import test_init
from applicatie_meldingen import Meldingen
from data_doel import Doel
from data_bg_project import Project

class Test_data_bg_project(unittest.TestCase):
#======================================================================
# Lezen van de specificatie
#======================================================================

#----------------------------------------------------------------------
# Valide
#----------------------------------------------------------------------
    def test_NieuwDoel_Initieel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Nieuw doel",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project"
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Nieuw doel",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project"
        }
    ]
}''')

    def test_NieuwDoel_Regelgeving(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Nieuw doel",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Uitgangssituatie": "2022-06-01"
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Nieuw doel",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GebaseerdOp_GeldigOp": "2022-06-01"
        }
    ]
}''')

    def test_NieuwDoel_AnderDoel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Nieuw doel",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Uitgangssituatie": "/join/id/proces/gm9999/2022/Instelling"
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Nieuw doel",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GebaseerdOp_Doel": "/join/id/proces/gm9999/2022/Instelling"
        }
    ]
}''')

    def test_Project_Beschrijving(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Beschrijving": "Enig project",
    "Acties": [
        {
            "SoortActie": "Nieuw doel",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Uitgangssituatie": "2022-06-01"
        }
    ]
}''','''{
    "Code": "P1",
    "Beschrijving": "Enig project",
    "Acties": [
        {
            "SoortActie": "Nieuw doel",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GebaseerdOp_GeldigOp": "2022-06-01"
        }
    ]
}''')

    def test_Download(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GebaseerdOp_GeldigOp": "2022-06-01"
        }
    ]
}''')


    def test_Wijziging(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_B/nld@2022;P1" },
                { "Instrumentversie": "/join/id/regdata/2022/IO_B@2022;P1" },
                { "JuridischUitgewerkt": "/akn/nl/act/gm9999/2022/REG_A" },
                { "JuridischUitgewerkt": "/join/id/regdata/2022/IO_A" },
                { "OnbekendeVersie": "/akn/nl/act/gm9999/2022/REG_E" },
                { "OnbekendeVersie": "/join/id/regdata/2022/IO_F" },
                { "Teruggetrokken": "/join/id/regdata/2022/IO_C" },
                { "Teruggetrokken": "/join/id/regdata/2022/IO_D" }
            ],
            "JuridischWerkendVanaf": "2022-08-01",
            "GeldigVanaf": "2022-06-01"
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": {
                "/akn/nl/act/gm9999/2022/REG_B": {
                    "ExpressionId": "/akn/nl/act/gm9999/2022/REG_B/nld@2022;P1",
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": false
                },
                "/join/id/regdata/2022/IO_B": {
                    "ExpressionId": "/join/id/regdata/2022/IO_B@2022;P1",
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": false
                },
                "/akn/nl/act/gm9999/2022/REG_A": {
                    "IsJuridischUitgewerkt": true,
                    "IsTeruggetrokken": false
                },
                "/join/id/regdata/2022/IO_A": {
                    "IsJuridischUitgewerkt": true,
                    "IsTeruggetrokken": false
                },
                "/akn/nl/act/gm9999/2022/REG_E": {
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": false
                },
                "/join/id/regdata/2022/IO_F": {
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": false
                },
                "/join/id/regdata/2022/IO_C": {
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": true
                },
                "/join/id/regdata/2022/IO_D": {
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": true
                }
            },
            "JuridischWerkendVanaf": "2022-08-01",
            "GeldigVanaf": "2022-06-01"
        }
    ]
}''')


    def test_Wijziging_Datums(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "JuridischWerkendVanaf": "-",
            "GeldigVanaf": "?"
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "JuridischWerkendVanaf": "-",
            "GeldigVanaf": "-"
        }
    ]
}''')


    def test_Uitwisseling(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Uitwisseling",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project"
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Uitwisseling",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project"
        }
    ]
}''')


    def test_BijwerkenUitgangssituatieRegelgeving(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Bijwerken uitgangssituatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "JuridischUitgewerkt": "/join/id/regdata/2022/IO_A" },
                { "Teruggetrokken": "/join/id/regdata/2022/IO_B" }
            ]
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Bijwerken uitgangssituatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GebaseerdOp_GeldigOp": "2022-06-01",
            "Instrumentversies": {
                "/akn/nl/act/gm9999/2022/REG_A": {
                    "ExpressionId": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1",
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": false
                },
                "/join/id/regdata/2022/IO_A": {
                    "IsJuridischUitgewerkt": true,
                    "IsTeruggetrokken": false
                },
                "/join/id/regdata/2022/IO_B": {
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": true
                }
            }
        }
    ]
}''')

    def test_BijwerkenUitgangssituatieBranch(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Bijwerken uitgangssituatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "JuridischUitgewerkt": "/join/id/regdata/2022/IO_A" },
                { "Teruggetrokken": "/join/id/regdata/2022/IO_B" }
            ]
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Bijwerken uitgangssituatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": {
                "/akn/nl/act/gm9999/2022/REG_A": {
                    "ExpressionId": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1",
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": false
                },
                "/join/id/regdata/2022/IO_A": {
                    "IsJuridischUitgewerkt": true,
                    "IsTeruggetrokken": false
                },
                "/join/id/regdata/2022/IO_B": {
                    "IsJuridischUitgewerkt": false,
                    "IsTeruggetrokken": true
                }
            }
        }
    ]
}''')


    def test_Publicatie(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project_D1", "/join/id/proces/gm9999/2022/Project_D2" ],
            "SoortPublicatie": "Besluit"
        }
    ]
}''','''{
    "Code": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [
                "/join/id/proces/gm9999/2022/Project_D1",
                "/join/id/proces/gm9999/2022/Project_D2"
            ],
            "SoortPublicatie": "Besluit"
        }
    ]
}''')
#----------------------------------------------------------------------
# Met fouten
#
# Omdat het lezen van specificaties gebeurt aan de hand van
# eigenschappen van de actie-objecten is het niet van belang welk
# van de acties met een bepaald kenmerk gebruikt wordt.
#----------------------------------------------------------------------
    def test_Fout_GeenProject(self):
        self._Test_LeesJson ('''{
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None,True)

    def test_Fout_ProjectGeenString(self):
        self._Test_LeesJson ('''{
    "Project": 42,
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None)

    def test_Fout_BeschrijvingGeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Beschrijving": 42,
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None)

    def test_Fout_GeenActies(self):
        self._Test_LeesJson ('''{
    "Project": "P1"
}''',None)

    def test_Fout_ActiesLeeg(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
    ]
}''',None)

    def test_Fout_ActieGeenObject(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        "Gaan met die banaan"
    ]
}''',None)

    def test_Fout_GeenSoortActie(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie"
        }
    ]
}''',None)

    def test_Fout_SoortActieGeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": 42,
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie"
        }
    ]
}''',None)

    def test_Fout_SoortActieOngeldigeWaarde(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "ActieBestaatNiet",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie"
        }
    ]
}''',None)

    def test_Fout_GeenUitgevoerdOp(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None)

    def test_Fout_UitgevoerdOpGeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": 42,
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None)

    def test_Fout_UitgevoerdOpOngeldig(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "AAAA-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None)

    def test_Fout_UitgevoerdOpDubbel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        },
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ]
        }
    ]
}''',None)

    def test_Fout_GeenBeschrijving(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None)

    def test_Fout_BeschrijvingGeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": true,
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None)

    def test_Fout_GeenDatumUitspraak(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Verwerking uitspraak rechter",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project" ],
            "Vernietigd": true,
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "JuridischUitgewerkt": "/join/id/regdata/2022/IO_A" }
            ]
        }
    ]
}''',None)

    def test_Fout_DatumUitspraak_GeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Verwerking uitspraak rechter",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project" ],
            "DatumUitspraak": 20225020,
            "Vernietigd": true,
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "JuridischUitgewerkt": "/join/id/regdata/2022/IO_A" }
            ]
        }
    ]
}''',None)

    def test_Fout_DatumUitspraak_Ongeldig(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Verwerking uitspraak rechter",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project" ],
            "DatumUitspraak": "2022-05-20Z",
            "Vernietigd": true,
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "JuridischUitgewerkt": "/join/id/regdata/2022/IO_A" }
            ]
        }
    ]
}''',None)
    
    def test_Fout_GeenDoel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None)

    def test_Fout_DoelGeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": 42,
            "GeldigOp": "2022-06-01"
        }
    ]
}''',None)

    def test_Fout_GeenDoelen(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "SoortPublicatie": "Besluit"
        }
    ]
}''',None)

    def test_Fout_Doelen_GeenArray(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": { "doel": 42 },
            "SoortPublicatie": "Besluit"
        }
    ]
}''',None)
    def test_Fout_Doelen_LeegArray(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ ],
            "SoortPublicatie": "Besluit"
        }
    ]
}''',None)

    def test_Fout_Doelen_Geenstring(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ 42 ],
            "SoortPublicatie": "Besluit"
        }
    ]
}''',None)

    def test_Fout_Doelen_Dubbel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project", "/join/id/proces/gm9999/2022/Project" ],
            "SoortPublicatie": "Besluit"
        }
    ]
}''',None)

    def test_Fout_GebaseerdOp_GeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Nieuw doel",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Uitgangssituatie": 42
        }
    ]
}''',None)

    def test_Fout_GebaseerdOp_GeenGeldigOp(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project"
        }
    ]
}''',None)

    def test_Fout_GebaseerdOp_GeldigOpGeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": true
        }
    ]
}''',None)

    def test_Fout_GebaseerdOp_GeldigOpOngeldig(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Download",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "GeldigOp": "2022-05-25T07:00:00Z"
        }
    ]
}''',None)

    def test_Fout_InstrumentversiesGeenArray(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": 42
        }
    ]
}''',None)

    def test_Fout_InstrumentversiesGeenObject(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                "versie"
            ]
        }
    ]
}''',None)

    def test_Fout_InstrumentversiesOngeldigObjectVerkeerdeNaam(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "VerkeerdeNaam": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ]
        }
    ]
}''',None)

    def test_Fout_InstrumentversiesOngeldigObjectTeveelNamen(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1", "Extra": 42 }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_Instrumentversie_GeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": 42 }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_Instrumentversie_GeenInstrument(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/geen/work@2022;P1" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_Instrumentversie_GeenExpression(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_JuridischUitgewerkt_GeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "JuridischUitgewerkt": true }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_JuridischUitgewerkt_GeenInstrument(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "JuridischUitgewerkt": "/geen/work" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_JuridischUitgewerkt_GeenWork(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "JuridischUitgewerkt": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_OnbekendeVersie_GeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "OnbekendeVersie": true }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_OnbekendeVersie_GeenInstrument(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "OnbekendeVersie": "/geen/work" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_OnbekendeVersie_GeenWork(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "OnbekendeVersie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ]
        }
    ]
}''',None)
    def test_Fout_Instrumentversies_Teruggetrokken_GeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Teruggetrokken": true }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_Teruggetrokken_GeenInstrument(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Teruggetrokken": "/geen/work" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_Teruggetrokken_GeenWork(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Teruggetrokken": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_Instrumentversie_Dubbel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_Instrumentversie_JuridischUitgewerkt_Dubbel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "JuridischUitgewerkt": "/akn/nl/act/gm9999/2022/REG_A" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_Instrumentversie_Teruggetrokken_Dubbel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "Teruggetrokken": "/akn/nl/act/gm9999/2022/REG_A" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_JuridischUitgewerkt_Dubbel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "JuridischUitgewerkt": "/akn/nl/act/gm9999/2022/REG_A" },
                { "JuridischUitgewerkt": "/akn/nl/act/gm9999/2022/REG_A" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_JuridischUitgewerkt_Teruggetrokken_Dubbel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "JuridischUitgewerkt": "/akn/nl/act/gm9999/2022/REG_A" },
                { "Teruggetrokken": "/akn/nl/act/gm9999/2022/REG_A" }
            ]
        }
    ]
}''',None)

    def test_Fout_Instrumentversies_Teruggetrokken_Dubbel(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Teruggetrokken": "/akn/nl/act/gm9999/2022/REG_A" },
                { "Teruggetrokken": "/akn/nl/act/gm9999/2022/REG_A" }
            ]
        }
    ]
}''',None)

    def test_Fout_JuridischWerkendVanafGeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ],
            "JuridischWerkendVanaf": 2022
        }
    ]
}''',None)

    def test_Fout_JuridischWerkendVanafOngeldigeDatum(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ],
            "JuridischWerkendVanaf": "2022"
        }
    ]
}''',None)

    def test_Fout_GeldigVanafGeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ],
            "JuridischWerkendVanaf": "2022-01-01",
            "GeldigVanaf": 2022
        }
    ]
}''',None)

    def test_Fout_GeldigVanafOngeldigeDatum(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Wijziging",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doel": "/join/id/proces/gm9999/2022/Project",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" }
            ],
            "JuridischWerkendVanaf": "2022-01-01",
            "GeldigVanaf": "2022"
        }
    ]
}''',None)

    def test_Fout_GeenSoortPublicatie(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project" ]
        }
    ]
}''',None)

    def test_Fout_SoortPublicatie_GeenString(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project" ],
            "SoortPublicatie": true
        }
    ]
}''',None)

    def test_Fout_SoortPublicatie_OngeldigeWaarsw(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Publicatie",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project" ],
            "SoortPublicatie": "OngelidgeWaarde"
        }
    ]
}''',None)



    def test_Fout_GeenVernietigd(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Verwerking uitspraak rechter",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project" ],
            "DatumUitspraak": "2022-05-20",
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "JuridischUitgewerkt": "/join/id/regdata/2022/IO_A" }
            ]
        }
    ]
}''',None)

    def test_Fout_Vernietigd_GeenBool(self):
        self._Test_LeesJson ('''{
    "Project": "P1",
    "Acties": [
        {
            "SoortActie": "Verwerking uitspraak rechter",
            "UitgevoerdOp": "2022-05-25T07:00:00Z",
            "Beschrijving": "Enige actie",
            "Doelen": [ "/join/id/proces/gm9999/2022/Project" ],
            "DatumUitspraak": "2022-05-20",
            "Vernietigd": 42,
            "Instrumentversies": [
                { "Instrumentversie": "/akn/nl/act/gm9999/2022/REG_A/nld@2022;P1" },
                { "JuridischUitgewerkt": "/join/id/regdata/2022/IO_A" }
            ]
        }
    ]
}''',None)
 
#----------------------------------------------------------------------
# Uitvoeren van de test
#----------------------------------------------------------------------
    def _Test_LeesJson (self, data, verwacht, geenActual = False, aantalFouten = 1, aantalWaarschuwingen = 0):
        """Lees de JSON in en vergelijk dat met de verwachte uitkomst
        
        Argumenten:
        data  string  JSON van de specificatie
        verwacht string  dump naar JSON van de ingelezen specificatie, of None als een fout verwacht wordt
        geenActual bool Geeft aan dat het inlezen van de JSON niet leidt tot een (al dan niet valide) instantie van Project
        aantalFouten int  Als verwacht is None: aantal fouten dat verwacht wordt
        aantalWaarschuwingen int  Aantal waarschuwingen dat verwacht wordt
        """
        log = Meldingen (False)
        actual = Project.LeesJson (log, "test.json", json.loads (data))
        if verwacht is None:
            if geenActual:
                self.assertIsNone (actual)
            else:
                if log.Fouten != aantalFouten or log.Waarschuwingen != aantalWaarschuwingen:
                    self.fail ("Fouten (" + str(aantalFouten) + ")/waarschuwingen (" + str(aantalWaarschuwingen) + ") verwacht, maar: " + log.MaakTekst ())
                if not actual is None:
                    if log.Fouten == 0:
                        if not actual._IsValide:
                            self.fail ("Geen fouten, maar resultaat is toch niet valide: " + log.MaakTekst ())
                    else:
                        if actual._IsValide:
                            self.fail ("Wel fouten, maar resultaat is toch valide: " + log.MaakTekst ())
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
            if key[0:1] == '_':
                continue
            value = o.__dict__[key]
            if value is None:
                continue
            if isinstance (value, dict) and len (value) == 0:
                continue
            if isinstance (value, list) and len (value) == 0:
                continue
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
