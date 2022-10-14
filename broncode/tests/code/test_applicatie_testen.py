#======================================================================
# Unit tests voor Python code in applicatie_testen.py
#======================================================================
import unittest

import test_init
from applicatie_testen import JsonClassEncoder

class Test_applicatie_testen(unittest.TestCase):

#----------------------------------------------------------------------
# Test van de encoder
#----------------------------------------------------------------------
    def test_JsonClassEncoder(self):

        data = TestData (42, "test")
        actual = JsonClassEncoder.NaarJsonString (data, False)
        self.assertEqual ('''{
    "Waarde": "test"
}''', actual)

        data = TestData (data, data)
        actual = JsonClassEncoder.NaarJsonString (data, True)
        self.assertEqual ('{"Waarde": {"Waarde": "test"}}', actual)

#----------------------------------------------------------------------
# Hulp class voor de test
#----------------------------------------------------------------------
class TestData:

    def __init__ (self, verborgen, waarde):
        self._Verborgen = verborgen
        self.Waarde = waarde

#======================================================================
# Nodig voor unittest
#======================================================================
if __name__ == '__main__':
    unittest.main()
