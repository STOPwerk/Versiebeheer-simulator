#======================================================================
# Unit tests voor Python code in data_doel.py
#======================================================================
import unittest

import test_init
from data_doel import Doel

class Test_data_doel(unittest.TestCase):

#======================================================================
# Test van Doel
#======================================================================
    def test_Doel(self):

        actual = Doel.DoelInstantie ("/join/id/proces/gm9999/2020/Instelling")
        self.assertIsNotNone (actual)
        self.assertNotEqual (actual.Index, 0)
        self.assertEqual (actual.Identificatie, "/join/id/proces/gm9999/2020/Instelling")

        actual = Doel.DoelInstantie (actual)
        self.assertIsNotNone (actual)
        self.assertNotEqual (actual.Index, 0)
        self.assertEqual (actual.Identificatie, "/join/id/proces/gm9999/2020/Instelling")

        actual2 = Doel.DoelInstantie ("/join/id/proces/gm9999/2020/Instelling")
        self.assertTrue (actual.Index, actual2.Index)

        self.assertTrue (actual == actual)
        self.assertTrue (actual2 == actual)

        actual3 = Doel.DoelInstantie ("/join/id/proces/gm9999/2020/Wijziging")
        self.assertTrue (actual3 != actual)
        self.assertFalse (actual3 == actual)

        lijst = [ actual ]
        self.assertTrue (actual in lijst)
        self.assertTrue (actual2 in lijst)
        self.assertFalse (actual3 in lijst)

        collectie = {}
        collectie[actual] = 42 
        self.assertTrue (actual in collectie)
        self.assertTrue (actual2 in collectie)
        self.assertFalse (actual3 in collectie)
        self.assertEqual (collectie[actual], 42)
        self.assertEqual (collectie[actual2], 42)

#======================================================================
# Nodig voor unittest
#======================================================================
if __name__ == '__main__':
    unittest.main()
