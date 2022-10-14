#======================================================================
# Unit tests voor Python code in applicatie_meldingen.py
#======================================================================
import unittest

import test_init
from applicatie_meldingen import Meldingen

class Test_applicatie_meldingen(unittest.TestCase):

    def test_Melding_MetTijd (self):
        self._test_Melding (True)

    def test_Melding_ZonderTijd (self):
        self._test_Melding (False)

    def _test_Melding (self, metTijd):
        actual = Meldingen (metTijd)
        actual.Detail ("Start")
        self.assertEqual (1, len (actual.Meldingen))
        self.assertEqual ("Start", actual.Meldingen[-1].Tekst)
        self.assertEqual ("DETAIL", actual.Meldingen[-1].Ernst)
        self.assertEqual (0, actual.Fouten)
        self.assertEqual (0, actual.Waarschuwingen)
        self.assertEqual (0, len (actual.FoutenWaarschuwingen()))

        actual.Fout ("Oeps")
        self.assertEqual (2, len (actual.Meldingen))
        self.assertEqual ("Oeps", actual.Meldingen[-1].Tekst)
        self.assertEqual ("FOUT", actual.Meldingen[-1].Ernst)
        self.assertEqual (1, actual.Fouten)
        self.assertEqual (0, actual.Waarschuwingen)
        self.assertEqual (1, len (actual.FoutenWaarschuwingen()))

        actual.Waarschuwing ("Och jee")
        self.assertEqual (3, len (actual.Meldingen))
        self.assertEqual ("Och jee", actual.Meldingen[-1].Tekst)
        self.assertEqual ("LET OP", actual.Meldingen[-1].Ernst)
        self.assertEqual (1, actual.Fouten)
        self.assertEqual (1, actual.Waarschuwingen)
        self.assertEqual (2, len (actual.FoutenWaarschuwingen()))

        actual.Informatie ("Ter info")
        self.assertEqual (4, len (actual.Meldingen))
        self.assertEqual ("Ter info", actual.Meldingen[-1].Tekst)
        self.assertEqual ("INFO", actual.Meldingen[-1].Ernst)
        self.assertEqual (1, actual.Fouten)
        self.assertEqual (1, actual.Waarschuwingen)
        self.assertEqual (2, len (actual.FoutenWaarschuwingen()))

        actual.Detail ("Einde")
        self.assertEqual (5, len (actual.Meldingen))
        self.assertEqual (1, actual.Fouten)
        self.assertEqual (1, actual.Waarschuwingen)
        self.assertEqual (2, len (actual.FoutenWaarschuwingen()))

        for melding in actual.Meldingen:
            self.assertEqual (metTijd, hasattr (melding, "Tijd"))
        self.assertNotEqual ("", actual.MaakTekst ())

#======================================================================
# Nodig voor unittest
#======================================================================
if __name__ == '__main__':
    unittest.main()
