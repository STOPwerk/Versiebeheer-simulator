#======================================================================
#
# /voorbeeld
#
#======================================================================
#
# Script om een voorbeeld te selecteren en daarvoor de GIO-wijziging
# te maken en te tonen.
#
#======================================================================

from typing import List, Dict

import json
import os

from applicatie_meldingen import Meldingen
from applicatie_web import WebApplicatie
from weergave_webpagina import WebpaginaGenerator

class Voorbeeld:
#======================================================================
#
# Webpagina's
#
#======================================================================
    @staticmethod
    def SelectieHtml():
        generator = WebpaginaGenerator ("Selecteer een voorbeeld")
        generator.VoegHtmlToe ('<p>Beschikbare voorbeelden waarvoor de simulator uitgevoerd kan worden, Klik op het vraagteken voor een beschrijving van het voorbeeld.</p>')
        Voorbeeld._VoorbeeldenLijst ().MaakHtml (generator)
        return generator.Html ()

    @staticmethod
    def VoerUit(request : Dict):
        # Haal het voorbeeld op
        lijst = Voorbeeld._VoorbeeldenLijst ()
        idx = int (request["index"]) if "index" in request else None
        if idx is None or int(idx) < 0 or int(idx) >= len (lijst.AlleSpecificaties):
            generator = WebpaginaGenerator ("Voorbeeld onbekend")
            generator.VoegHtmlToe ('Het voorbeeld is niet bekend. Selecteer een <a href="voorbeeld">ander voorbeeld</a>.')
            return generator.Html ()

        specificatie = lijst.AlleSpecificaties[idx]
        if specificatie.IsBGProces:
            try:
                return WebApplicatie.SimuleerVoorbeeld (os.path.dirname (specificatie.Pad))
                return WebApplicatie.ProjectInvoerPaginaVoorbeeld (specificatie.Pad) 
            except Exception as e:
                generator = WebpaginaGenerator ("Voorbeeld kan niet geopend worden")
                generator.VoegHtmlToe ('Het voorbeeld is niet beschikbaar. Selecteer een <a href="voorbeeld">ander voorbeeld</a>.')
                return generator.Html ()
        else:
            return WebApplicatie.SimuleerVoorbeeld (specificatie.Pad)

#======================================================================
#
# Implementatie
#
#======================================================================
    class VoorbeeldSpecificatie:
        def __init__ (self, isBGProces, bronUrl, specFilePath, titel, beschrijving, index):
            self.Pad = specFilePath
            self.Titel = titel
            self.Beschrijving = beschrijving
            self.IsBGProces = isBGProces
            self.BronUrl = bronUrl
            self.Index = index

    class VoorbeeldDirectory:
        def __init__ (self, path, name, top):
            self.Pad = path
            self.BronUrl = '@@@@@@Simulator_Url@@@@@@tree/main/broncode/simulator/voorbeelden' if top is None else top.BronUrl + '/' + name
            self.Naam = None if top is None else name
            self.Voorbeelden = []
            self.Specificatie : Voorbeeld.VoorbeeldSpecificatie = None
            self.AlleSpecificaties : List[Voorbeeld.VoorbeeldSpecificatie] = []

            def _Lees_Beschrijving_BGCode (path):
                try:
                    with open (path, 'r', encoding='utf-8') as jsonFile:
                        data = json.load(jsonFile)
                except:
                    return (None, False)
                return (data["Beschrijving"] if "Beschrijving" in data else None, "BevoegdGezag" in data)

            beschrijving = None
            openSpecificatie = False
            file_bg_process = None
            file_anders = False
            for fd in sorted (os.scandir(self.Pad), key=lambda f: f.name):
                if fd.is_dir ():
                    vb = Voorbeeld.VoorbeeldDirectory (fd.path, fd.name, self if top is None else top)
                    self.Voorbeelden.append (vb)
                    if top is None:
                        vb.IsDataBron = True
                elif not top is None and fd.is_file ():
                    if fd.name.lower () == "bg_proces.json":
                        file_bg_process = fd.path
                        if beschrijving is None:
                            beschrijving, openSpecificatie = _Lees_Beschrijving_BGCode (fd.path)
                    elif fd.name.lower ().endswith ("beschrijving.json"):
                        file_anders = True
                        if beschrijving is None:
                            beschrijving, _ = _Lees_Beschrijving_BGCode (fd.path)
                    elif fd.name.lower ().endswith (".json") or fd.name.lower ().endswith (".xml"):
                        file_anders = True
            if file_anders:
                spec = Voorbeeld.VoorbeeldSpecificatie (False, self.BronUrl, self.Pad, self.Naam, beschrijving, len (top.AlleSpecificaties))
                top.AlleSpecificaties.append (spec)
                self.Specificatie = spec
            elif not file_bg_process is None:
                spec = Voorbeeld.VoorbeeldSpecificatie (openSpecificatie, None, file_bg_process, self.Naam, beschrijving, len (top.AlleSpecificaties))
                top.AlleSpecificaties.append (spec)
                self.Specificatie = spec

        def MaakHtml (self, generator : WebpaginaGenerator):
            if self.Specificatie is None and len (self.Voorbeelden) == 0:
                return

            if not self.Naam is None:
                generator.VoegHtmlToe ('<dt><b>' + self.Naam + '</b>')
                if not self.Specificatie is None:
                    if self.Specificatie.IsBGProces:
                        generator.VoegHtmlToe (' - <a href="start_voorbeeld?index=' + str(self.Specificatie.Index) + '">Openen</a>')
                    else:
                        generator.VoegHtmlToe (' - <a href="start_voorbeeld?index=' + str(self.Specificatie.Index) + '">Uitvoeren</a>')
                    if not self.Specificatie.BronUrl is None:
                        generator.VoegHtmlToe (' - <a href="' + self.Specificatie.BronUrl + '">Bronbestanden</a>')
                generator.VoegHtmlToe ('</dt><dd>')
                if not self.Specificatie is None and not self.Specificatie.Beschrijving is None:
                    einde = generator.StartToelichting ("Beschrijving", False)
                    generator.VoegHtmlToe (self.Specificatie.Beschrijving)
                    generator.VoegHtmlToe (einde)
            if len (self.Voorbeelden) > 0:
                generator.VoegHtmlToe ('<dl>')
                for sp in self.Voorbeelden:
                    sp.MaakHtml (generator)
                generator.VoegHtmlToe ('</dl>')
            if not self.Naam is None:
                generator.VoegHtmlToe ('</dd>')

    @staticmethod
    def _VoorbeeldenLijst () -> VoorbeeldDirectory:
        """Maak de lijst met voorbeelden"""
        voorbeeldenPad = os.path.join (os.path.dirname (os.path.abspath (__file__)), 'voorbeelden')
        return Voorbeeld.VoorbeeldDirectory(voorbeeldenPad, None, None)

