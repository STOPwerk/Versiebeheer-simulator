#======================================================================
# Unit tests voor Python code in stop_naamgeving.py
#======================================================================

import unittest

import test_init
from stop_naamgeving import Naamgeving

class Test_stop_naamgeving(unittest.TestCase):

#----------------------------------------------------------------------
# Informatie over een identificatie
#----------------------------------------------------------------------
    def test_IsExpression(self):
        self.assertEqual(False, Naamgeving.IsExpression ("/akn/nl/act/gm9999/2022/reg001"))
        self.assertEqual(True, Naamgeving.IsExpression ("/akn/nl/act/gm9999/2022/reg001/nld@2022"))
        self.assertEqual(False, Naamgeving.IsExpression ("/join/id/regdata/2022/io001"))
        self.assertEqual(True, Naamgeving.IsExpression ("/join/id/regdata/2022/io001@2022"))
        self.assertEqual(False, Naamgeving.IsRegeling ("huh"))

    def test_IsRegeling(self):
        self.assertEqual(True, Naamgeving.IsRegeling ("/akn/nl/act/gm9999/2022/reg001"))
        self.assertEqual(True, Naamgeving.IsRegeling ("/akn/nl/act/gm9999/2022/reg001/nld@2022"))
        self.assertEqual(False, Naamgeving.IsRegeling ("/akn/nl/bill/gm9999/2022/reg001"))
        self.assertEqual(False, Naamgeving.IsRegeling ("/join/id/pubdata/2022/io001"))
        self.assertEqual(False, Naamgeving.IsRegeling ("/join/id/pubdata/2022/io001@2022"))
        self.assertEqual(False, Naamgeving.IsRegeling ("/join/id/regdata/2022/io001"))
        self.assertEqual(False, Naamgeving.IsRegeling ("/join/id/regdata/2022/io001@2022"))
        self.assertEqual(False, Naamgeving.IsRegeling ("huh"))

    def test_IsInformatieobject(self):
        self.assertEqual(False, Naamgeving.IsInformatieobject ("/akn/nl/act/gm9999/2022/reg001"))
        self.assertEqual(False, Naamgeving.IsInformatieobject ("/akn/nl/act/gm9999/2022/reg001/nld@2022"))
        self.assertEqual(False, Naamgeving.IsInformatieobject ("/akn/nl/bill/gm9999/2022/reg001"))
        self.assertEqual(False, Naamgeving.IsInformatieobject ("/join/id/pubdata/2022/io001"))
        self.assertEqual(False, Naamgeving.IsInformatieobject ("/join/id/pubdata/2022/io001@2022"))
        self.assertEqual(True, Naamgeving.IsInformatieobject ("/join/id/regdata/2022/io001"))
        self.assertEqual(True, Naamgeving.IsInformatieobject ("/join/id/regdata/2022/io001@2022"))
        self.assertEqual(False, Naamgeving.IsInformatieobject ("huh"))

#----------------------------------------------------------------------
# Manipulatie van een identificatie
#----------------------------------------------------------------------
    def test_WorkVan(self):
        self.assertEqual("/akn/nl/act/gm9999/2022/reg001", Naamgeving.WorkVan ("/akn/nl/act/gm9999/2022/reg001"))
        self.assertEqual("/akn/nl/act/gm9999/2022/reg001", Naamgeving.WorkVan ("/akn/nl/act/gm9999/2022/reg001/nld@2022"))
        self.assertEqual("/join/id/regdata/2022/io001", Naamgeving.WorkVan ("/join/id/regdata/2022/io001"))
        self.assertEqual("/join/id/regdata/2022/io001", Naamgeving.WorkVan ("/join/id/regdata/2022/io001@2022"))

    def test_WorkVoorConsolidatieVan(self):
        self.assertEqual("/akn/nl/act/gemeente/2023/regeling42", Naamgeving.WorkVoorConsolidatieVan ("/akn/nl/act/gm9999/2022/reg001", 2023, 42))
        self.assertEqual("/akn/nl/act/waterschap/2024/regeling123", Naamgeving.WorkVoorConsolidatieVan ("/akn/nl/act/ws999/2022-05-06/reg001/nld@2022", 2024, 123))
        self.assertEqual("/akn/nl/act/provincie/2025/regeling345", Naamgeving.WorkVoorConsolidatieVan ("/akn/nl/act/pv99/2022-05-06/reg001/nld@2022", 2025, 345))
        self.assertEqual("/akn/nl/act/land/2026/regeling1", Naamgeving.WorkVoorConsolidatieVan ("/akn/nl/act/mn9999/2022/reg001/nld@2022", 2026, 1))
        self.assertEqual("/join/id/regdata/consolidatie/2027/io42", Naamgeving.WorkVoorConsolidatieVan ("/join/id/regdata/2022/io001", 2027, 42))
        self.assertEqual("/join/id/regdata/consolidatie/2028/io1", Naamgeving.WorkVoorConsolidatieVan ("/join/id/regdata/2022-01-01/io001@2022", 2028, 1))

#======================================================================
# Nodig voor unittest
#======================================================================
if __name__ == '__main__':
    unittest.main()
