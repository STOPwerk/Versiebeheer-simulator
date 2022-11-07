#======================================================================
# Unit tests voor Python code in data_lv_consolidatie.py
#======================================================================
import unittest

import test_init
from applicatie_procesopties import ProcesOpties
from data_lv_consolidatie import GeconsolideerdInstrument
from data_doel import Doel
from applicatie_scenario import Scenario
from data_lv_versiebeheerinformatie import Instrument
from stop_consolidatieidentificatie import ConsolidatieIdentificatie

class Test_data_lv_consolidatie(unittest.TestCase):
#----------------------------------------------------------------------
#
# Test van de toestand expression maker
#
#----------------------------------------------------------------------
    def test_MaakToestandExpressionId (self):

        instrument = Instrument (None, "/akn/nl/act/gm9999/2022/instrument")
        scenario = Scenario (None, '', True)
        scenario.Opties = ProcesOpties ()
        consolidatie = GeconsolideerdInstrument (scenario, instrument)
        consolidatie.ConsolidatieIdentificatie = ConsolidatieIdentificatie (scenario, consolidatie.Instrument.WorkId, "2022-01-01")
        prefix = consolidatie.ConsolidatieIdentificatie.WorkId + "/nld@"

        # Toestand met alleen iwt
        actual = TestToestand (['doel1'])
        index = consolidatie.MaakToestandExpressionId (actual, "2022-02-03", None)
        self.assertEqual (prefix + "2022-02-03", actual.ExpressionId)
        self.assertEqual (0, index)

        # Kan zo vaak als nodig
        actual = TestToestand (['doel1'])
        index = consolidatie.MaakToestandExpressionId (actual, "2022-02-03", None)
        self.assertEqual (prefix + "2022-02-03", actual.ExpressionId)
        self.assertEqual (0, index)

        # Andere toestand, dezelfde iwt
        actual = TestToestand (['doel2'])
        index = consolidatie.MaakToestandExpressionId (actual, "2022-02-03", None)
        self.assertEqual (prefix + "2022-02-03;2", actual.ExpressionId)
        self.assertEqual (1, index)

        # Andere toestand, dezelfde iwt
        actual = TestToestand (['doel1', 'doel2'])
        index = consolidatie.MaakToestandExpressionId (actual, "2022-02-03", None)
        self.assertEqual (prefix + "2022-02-03;3", actual.ExpressionId)
        self.assertEqual (2, index)

        # Toestand met terugwerkende kracht
        actual = TestToestand (['doel1'])
        index = consolidatie.MaakToestandExpressionId (actual, "2022-02-03", "2022-01-01")
        self.assertEqual (prefix + "2022-01-01;2022-02-03", actual.ExpressionId)
        self.assertEqual (3, index)

        # Andere toestand, dezelfde iwt
        actual = TestToestand (['doel2', 'doel3'])
        index = consolidatie.MaakToestandExpressionId (actual, "2022-02-03", "2022-01-01")
        self.assertEqual (prefix + "2022-01-01;2022-02-03;2", actual.ExpressionId)
        self.assertEqual (4, index)

        # Volgorde maakt niet uit
        actual = TestToestand (['doel3', 'doel2'])
        index = consolidatie.MaakToestandExpressionId (actual, "2022-02-03", "2022-01-01")
        self.assertEqual (prefix + "2022-01-01;2022-02-03;2", actual.ExpressionId)
        self.assertEqual (4, index)

#----------------------------------------------------------------------
#
# Hulpklasse voor test_MaakToestandExpressionId
#----------------------------------------------------------------------
class TestToestand:

    def __init__ (self, iwtdoelen):
        self.ExpressionId = None
        self.Inwerkingtredingsdoelen = [Doel.DoelInstantie (d) for d in iwtdoelen]

#======================================================================
# Nodig voor unittest
#======================================================================
if __name__ == '__main__':
    unittest.main()
