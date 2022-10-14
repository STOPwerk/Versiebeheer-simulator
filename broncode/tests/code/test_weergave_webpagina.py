#======================================================================
# Unit tests voor Python code in weergave_webpagina.py
#======================================================================
import unittest

import test_init
from weergave_webpagina import WebpaginaGenerator


class Test_weergave_webpagina(unittest.TestCase):
#======================================================================
# Unit testen voor WebpaginaGenerator
#======================================================================
    def test_WebpaginaGenerator(self):
        actual = WebpaginaGenerator ()
        html = actual.Html ()
        self.assertIsNotNone (html)
        self.assertNotEqual ("", html.strip ())
        self.assertFalse (html.find ("<title>") > 0)
        self.assertFalse (html.find ("<h1>") > 0)

        actual = WebpaginaGenerator ("DIT IS EEN TITEL")
        html = actual.Html ()
        self.assertIsNotNone (html)
        self.assertNotEqual ("", html.strip ())
        self.assertTrue (html.find ("<title>DIT IS EEN TITEL</title>") > 0)
        self.assertTrue (html.find ("<h1>DIT IS EEN TITEL</h1>") > 0)


        actual.VoegHtmlToe ("DIT IS EEN TEST")
        html = actual.Html ()
        self.assertNotEqual ("", html)
        self.assertTrue (html.find ("DIT IS EEN TEST") > 0)

        einde = actual.StartSectie ("Paneel")
        actual.VoegHtmlToe ("DIT IS NOG EEN TEST")
        actual.VoegHtmlToe (einde)
        html = actual.Html ()
        self.assertNotEqual ("", html)
        self.assertTrue (html.find ("DIT IS NOG EEN TEST") > 0)

#======================================================================
# Nodig voor unittest
#======================================================================
if __name__ == '__main__':
    unittest.main()
