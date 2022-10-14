#======================================================================
#
# Bepaling van de annotaties behorend bij de actuele toestanden 
# via synchronisatie aan de hand van doelen.
#
#======================================================================
#
# De bepaling van de annotaties van de actuele toestanden voert 
# een proces uit dat typisch ligt bij een systeem dat zelf annotaties
# behorend bij een instrument ontvangt, en van de LVBB de informatie
# krijgt over actuele toestanden. 
# 
# Het uitgangspunt is dat de verstrekker van de annotatie (voor)kennis
# heeft van de inhoud van de actuele toestanden, en op basis daarvan
# de inhoud van de annotatie heeft samengesteld.Als dat leidt tot een
# nieuwe annotatieversie dan wordt die uitgewisseld, anders geldt
# nog steeds de eerder verstrekte annotatieversie. Ter identificatie
# van de toestand worden de (inwerkingtredings-)doelen gebruikt,
# zodat (1) de identificatie onafhankelijk wordt van de naamgeving van
# geconsolideerde instrumenten en (2) de identificatie niet bijgesteld
# hoeft te worden als er vanwege samenloop-problemen opvolgende
# instrumentversies voor de toestand uitgewisseld worden die geen
# invloed hebben op de annotatie.
#
# De bepaling is bedoeld voor alle annotaties die niet via
# het versiebeheer aan een proefversie gekoppeld worden. In deze 
# applicatie wordt ook voor de annotaties die wel via versiebeheer
# behandeld worden de synchronisatie aan de hand van doelen
# uitgevoerd, zodat in de weergave van de resultaten de twee
# methoden vergeleken kunnen worden.
#
#======================================================================

from typing import List

from data_lv_actueleannotaties import ActueleToestandenMetAnnotaties, ExTuncTijdlijn, ExTuncToestand, ActueleAnnotatieVersie
from data_lv_annotatie import Annotatie
from data_lv_consolidatie import GeconsolideerdInstrument
from stop_actueletoestanden import ActueleToestanden
from weergave_data_toestanden import  ToestandActueel

#======================================================================
#
# Aanmaken van actuele toestanden na een uitwisseling, per instrument
#
#======================================================================
class MaakActueleToestandenMetAnnotaties:

    @staticmethod
    def VoerUit (consolidatie : GeconsolideerdInstrument, annotaties: List[Annotatie], gemaaktOp, volgendeGemaaktOp):
        """Maak een nieuwe versie van de actuele toestanden.
        
        consolidatie GeconsolideerdInstrument  Informatie over het geconsolideerde instrument
        annotaties Annotatie[] Alle annotaties die gespecificeerd zijn voor het scenario.
        gemaaktOp string Tijdstip waarop de uitwisseling gemaakt is
        volgendeGemaaktOp string Tijdstip waarop de volgende uitwisseling gemaakt is
        """
        instrumentAnnotaties = [a for a in annotaties if a.WorkId == consolidatie.Instrument.WorkId]
        if len(instrumentAnnotaties) > 0:
            maker = MaakActueleToestandenMetAnnotaties (consolidatie, instrumentAnnotaties, gemaaktOp, volgendeGemaaktOp)
            maker._VoerUit ()

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, consolidatie : GeconsolideerdInstrument, annotaties: List[Annotatie], gemaaktOp, volgendeGemaaktOp):
        """Maak een nieuwe instantie.
        
        consolidatie GeconsolideerdInstrument  Informatie over het geconsolideerde instrument
        annotaties Annotatie[] Alle annotaties die gespecificeerd zijn voor dit instrument.
        gemaaktOp string Tijdstip waarop de uitwisseling gemaakt is
        volgendeGemaaktOp string Tijdstip waarop de volgende uitwisseling gemaakt is
        """
        self._GemaaktOp = gemaaktOp
        self._VolgendeGemaaktOp = volgendeGemaaktOp
        self._Consolidatie = consolidatie
        if self._Consolidatie.Annotaties is None:
            self._Consolidatie.Annotaties = ActueleToestandenMetAnnotaties (annotaties)
        # Hou alleen de annotaties over waarvoor een uitwisseling beschikbaar is
        self._Annotaties = [a for a in annotaties if volgendeGemaaktOp is None or a.Versies[0].Tijdstip () < volgendeGemaaktOp]

#----------------------------------------------------------------------
# Bepaal de ex-tunc tijdlijn van actuele toestanden en annotaties
#----------------------------------------------------------------------
    def _VoerUit (self):
        """Vul de ActueleToestandenMetAnnotaties instantie aan voor deze uitwisseling"""

        #--------------------------------------------------------------
        #
        # Maak ex-tunc tijdlijn voor de actuele toestanden
        #
        #--------------------------------------------------------------
        # Voeg de actuele toestanden toe aan de tijdlijn
        actueleToestanden = [t for t in self._Consolidatie.ActueleToestanden.Toestanden if not t.NietMeerActueel]
        MaakActueleToestandenMetAnnotaties._VoegToestandenToe (self._Consolidatie.Annotaties.ActueleToestanden, [ExTuncToestand (self._GemaaktOp, t.JuridischWerkendVanaf, t) for t in actueleToestanden], MaakActueleToestandenMetAnnotaties._IsToestandActueelGelijkAan)

        #--------------------------------------------------------------
        #
        # Annotaties die bij de proefversies opgezocht worden via het
        # versiebeheer
        #
        #--------------------------------------------------------------
        nieuweToestanden = { a : [] for a in  self._Annotaties if a.ViaVersiebeheer } # Alle nieuwe toestanden voor de versiebeheer-annotaties
        for toestand in actueleToestanden:
            if toestand.Instrumentversie is None:
                # Geen instrumentversie, dan ook geen bekende annotatieversies
                for annotatie, lijst in nieuweToestanden.items ():
                    versie = ActueleAnnotatieVersie ([], "Geen instrumentversie voor de toestand, dus ook geen bekende annotatieversie.")
                    lijst.append (ExTuncToestand (self._GemaaktOp, toestand.JuridischWerkendVanaf, versie))
            else:
                # Er moet altijd een uitspraak over een annotatieversie gedaan kunnen worden, tenzij de annotatie nog niet bestaodn
                versies = { a : ActueleAnnotatieVersie (None, "Annotatie bestaat nog niet.") for a in  self._Annotaties if a.ViaVersiebeheer } # Alle nieuwe versies voor de versiebeheer=annotaties
                for proefversie in self._Consolidatie.Proefversies:
                    # Zoek de proefversie op
                    if proefversie.Instrumentversie == toestand.Instrumentversie:
                        # Neem de annotaties over
                        for annotatie in proefversie.Annotaties:
                            if not annotatie.Versie is None:
                                if annotatie.Versie:
                                    versies[annotatie._Annotatie].Versies = [annotatie.Versie]
                                    versies[annotatie._Annotatie].Uitleg = None
                                else:
                                    # Details waarom dat niet kan moeten maar bij de proefversie bekeken worden
                                    versies[annotatie._Annotatie].Versies = list (annotatie._TegenstrijdigeVersies)
                                    versies[annotatie._Annotatie].Uitleg = "Annotatieversie kan niet eenduidig bepaald worden voor de proefversie die voor de instrumentversie van de toestand is gemaakt."
                        break
                for annotatie, versie in versies.items ():
                    nieuweToestanden[annotatie].append (ExTuncToestand (self._GemaaktOp, toestand.JuridischWerkendVanaf, versie))

        # Voeg de annotaties toe aan de tijdlijn
        for annotatie, toestanden in nieuweToestanden.items ():
            toestanden.sort (key = lambda t: t.JuridischWerkendVanaf)
            MaakActueleToestandenMetAnnotaties._VoegToestandenToe (self._Consolidatie.Annotaties.UitProefversies[annotatie], toestanden, MaakActueleToestandenMetAnnotaties._IsAnnotatieVersieGelijkAan)

        #--------------------------------------------------------------
        #
        # Alle annotaties via doel-synchronisatie, waarbij de annotatie
        # voor een specifieke toestand is gemaakt. Dwz alle doelen
        # voor een toestand moeten in de annotatieversie worden genoemd.
        #
        #--------------------------------------------------------------
        for annotatie in self._Annotaties:
            nieuweToestanden = {} # De nieuwe toestanden voor de annotatie. Key = tijdstip, value = toestanden met oplopende JWV
            for versie in annotatie.Versies:
                # Annotatieversies kunnen op elk moment in het verleden (dus voor self._GemaaktOp) uitgewisseld zijn
                if (self._VolgendeGemaaktOp is None or versie.Tijdstip () < self._VolgendeGemaaktOp):
                    # Alle doelen moeten matchen
                    doelen = '\n'.join (d.Identificatie for d in versie.Doelen)
                    # Op deze plaats speelt het ex-tunc aanname een rol. Alle annotatieversies die in dit tijdinterval binnenkomen
                    # mogen niet meer voor een historische toestand zijn, en moeten dus bij een actuele toestand horen.
                    for toestand in actueleToestanden:
                        if doelen == '\n'.join (d.Identificatie for d in toestand.Inwerkingtredingsdoelen):
                            # Het tijdstip mag niet eerder zijn dan self._GemaaktOp, want voor dat tijdstip waren de actuele toestanden misschien anders
                            # en hoorde deze versie misschien niet bij een toestand. Als dat wel zo is, dan wordt de ExTuncToestand niet toegevoegd aan de tijdlijn
                            # omdat het niet tot een andere uitkomst van tijdreizen leidt.
                            tijdstip = versie.Tijdstip () if versie.Tijdstip () >= self._GemaaktOp else self._GemaaktOp
                            lijst = nieuweToestanden.get (tijdstip)
                            if lijst is None:
                                nieuweToestanden[tijdstip] = lijst = []
                            lijst.append (ExTuncToestand (tijdstip, toestand.JuridischWerkendVanaf, ActueleAnnotatieVersie ([versie], None)))
                            break

            for tijdstip in sorted (nieuweToestanden.keys ()):
                nieuweToestanden[tijdstip].sort (key = lambda t: t.JuridischWerkendVanaf)
                MaakActueleToestandenMetAnnotaties._VoegToestandenToe (self._Consolidatie.Annotaties.VoorToestandViaDoelen[annotatie], nieuweToestanden[tijdstip], MaakActueleToestandenMetAnnotaties._IsAnnotatieVersieGelijkAan)


        #--------------------------------------------------------------
        #
        # Alle annotaties via doel-synchronisatie, waarbij een 
        # annotatieversie voor een specifiek doel is gemaakt. Dwz
        # een versie voor 1 doel van de toestand is genoeg.
        #
        #--------------------------------------------------------------
        for annotatie in self._Annotaties:
            # Kijk per tijdstip wat de beste match qua annotaties is
            # Dit algoritme is niet erg efficiënt: voor alle tijdstippen worden alle actuele toestanden 
            # opnieuw van een annotatie voorzien, ook al is (voor tijdstippen na self._GemaaktOp) ook 
            # wel te zien dat een toestand niet geraakt wordt door de annotatieversie die op dat tijdstip 
            # wordt uitgewisseld. Omdat het bij deze applicatie altijd om kleine aantallen toestanden en 
            # annotatieversies gaat, wordt hier voor eenvoud van de code gekozen.
            tijdstippen = set([self._GemaaktOp])
            for versie in annotatie.Versies:
                if versie.Tijdstip () > self._GemaaktOp and (self._VolgendeGemaaktOp is None or versie.Tijdstip () < self._VolgendeGemaaktOp):
                    tijdstippen.add (versie.Tijdstip ())

            for totEnMet in sorted (tijdstippen):
                nieuweToestanden = [] # De nieuwe toestanden voor de annotatie.

                # Kijk per actuele toestand wat de passende versie(s) zijn
                for toestand in actueleToestanden:
                    gevondenVersies = [] # Versies die passen bij de toestand
                    for versie in reversed (annotatie.Versies): # aflopende volgorde van tijdstempels
                        # Annotatieversies kunnen op elk moment in het verleden (dus voor self._GemaaktOp) uitgewisseld zijn
                        if versie.Tijdstip () <= totEnMet:
                            if len (set (versie.Doelen) & set (toestand.Inwerkingtredingsdoelen)) == len (versie.Doelen):
                                # Alle doelen van de versie komen voor in de iwt-doelen van de toestand
                                # Gebruik deze versie tenzij er al een andere versie is gevonden voor dezelfde doelen
                                gebruiken = True
                                for gevonden in gevondenVersies:
                                    if len (set (versie.Doelen) & set (gevonden.Doelen)) == len (versie.Doelen):
                                        # Alle doelen van de versie zijn onderdeel van de doelen van de gevonden versie
                                        gebruiken = False
                                        break
                                if gebruiken:
                                    gevondenVersies.append (versie)

                    if len (gevondenVersies) > 0:
                        # Er is/zijn annotatieversies voor de toestand
                        nieuweToestanden.append (ExTuncToestand (totEnMet, toestand.JuridischWerkendVanaf, ActueleAnnotatieVersie (gevondenVersies, "Annotatieversie kan niet eenduidig bepaald worden" if len (gevondenVersies) > 1 else None)))

                # Voeg de nieuwe toestanden toe (als dat nodig is)
                nieuweToestanden.sort (key = lambda t: t.JuridischWerkendVanaf)
                MaakActueleToestandenMetAnnotaties._VoegToestandenToe (self._Consolidatie.Annotaties.VoorDoel[annotatie], nieuweToestanden, MaakActueleToestandenMetAnnotaties._IsAnnotatieVersieGelijkAan)


#----------------------------------------------------------------------
#
# Toevoegen van toestanden aan de tijdlijn, behalve de toestanden waarvan 
# het toevoegen geen effect heeft op het vinden van toestanden via tijdreizen.
#
#----------------------------------------------------------------------
    @staticmethod
    def _VoegToestandenToe (tijdlijn: ExTuncTijdlijn, nieuweToestanden: List[ExTuncToestand], isGelijkAan):
        """Voeg een reeks nieuwe toestanden toe die allemaal op hetzelfde tijdstip ontstaan zijn

        Argumenten:

        tijdlijn ExTuncTijdlijn  De tijdlijn waar een toestand aan toegevoegd moet worden.
        nieuweToestanden ExTuncToestand[]  De nieuwe toestanden, met als Inhoud de daadwerkelijke inhoud en niet de index ervan in de tijdlijn.ToestandInhoud
        isGelijkAan (functie)  Functie om te bepalen of de inhoud van twee toestanden gelijk is.
        """
        # Voeg de toestanden toe op volgorde van oplopende JWV
        nieuweToestanden.sort (key = lambda t: t.JuridischWerkendVanaf)
        for idx, nieuweToestand in enumerate (nieuweToestanden):
            MaakActueleToestandenMetAnnotaties._VoegToestandToe (tijdlijn, nieuweToestand, nieuweToestanden[idx+1].JuridischWerkendVanaf if idx < len (nieuweToestanden) - 1 else None, isGelijkAan)

    @staticmethod
    def _VoegToestandToe (tijdlijn: ExTuncTijdlijn, nieuweToestand: ExTuncToestand, jwvVolgendeNieuweToestand, isGelijkAan):
        """Voeg een nieuwe toestand toe aan de tijdlijn, als dat nodig is.

        Argumenten:

        tijdlijn ExTuncTijdlijn  De tijdlijn waar een toestand aan toegevoegd moet worden.
        nieuweToestand ExTuncToestand  De nieuwe toestand, met als Inhoud de daadwerkelijke inhoud en niet de index ervan in de tijdlijn.ToestandInhoud
        jwvVolgendeNieuweToestand string  De JWV van de volgende nieuwe toestand die hierna wordt ingevoegd; als er meerdere toestanden ingevoegd moeten worden,
                                          dan moeten ze op volgorde van toenemende JWV aangeboden worden.
        isGelijkAan (functie)  Functie om te bepalen of de inhoud van twee toestanden gelijk is.
        """

        # Vervang de inhoud door de index ervan
        isBekendeInhoud = False
        for idx, inhoud in enumerate (tijdlijn.ToestandInhoud):
            if isGelijkAan (inhoud, nieuweToestand.Inhoud):
                nieuweToestand.Inhoud = idx
                isBekendeInhoud = True
                break
        if not isBekendeInhoud:
            # Voeg toe aan de inhoud
            tijdlijn.ToestandInhoud.append (nieuweToestand.Inhoud)
            nieuweToestand.Inhoud = len (tijdlijn.ToestandInhoud) - 1
            # De toestand moet sowieso worden toegevoegd
        else:
            # Kijk of er een bestaande toestand met gelijke inhoud is die opnieuw gebruikt kan worden
            minimaleJwvBestaandeToestanden = None

            for bestaandeToestand in tijdlijn.Toestanden:
                if bestaandeToestand.Inhoud == nieuweToestand.Inhoud:
                    # Inhoudelijk dezelfde versie
                    if minimaleJwvBestaandeToestanden is None:
                        # De bestaande toestand is de eerste van de tijdlijn. De nieuwe toestand alleen toevoegen als de jwv kleiner is dan 
                        # van de bestaande, omdat er dan tijdreizen zijn (met nieuweToestand.JuridischWerkendVanaf <= jwv < bestaandeToestand.JuridischWerkendVanaf
                        # en uitgewisseldOp >= nieuweToestand.Tijdstip) die niet bij de bestaande toestand uitkomen.
                        if nieuweToestand.JuridischWerkendVanaf < bestaandeToestand.JuridischWerkendVanaf:
                            break
                        return
                    else:
                        # De nieuwe toestand kan weggelaten worden als geen van de bestaande toestanden tussen de nieuwe en de gevonden bestaande toestand
                        # door de nieuwe toestand met tijdreizen worden afgeschermd. Elk van die bestaande toestanden moet hebben:
                        # - toestand.JuridischWerkendVanaf >= jwvVolgendeNieuweToestand, want dan komt de tijdreis bij een van de andere nieuwe toestanden terecht
                        if not jwvVolgendeNieuweToestand is None and minimaleJwvBestaandeToestanden >= jwvVolgendeNieuweToestand:
                            return
                        break
                else:
                    # Het is een andere toestand. Hou vanwege de voorgaande overwegingen bij wat de minimale JWV is
                    if minimaleJwvBestaandeToestanden is None or minimaleJwvBestaandeToestanden > bestaandeToestand.JuridischWerkendVanaf:
                        minimaleJwvBestaandeToestanden = bestaandeToestand.JuridischWerkendVanaf

        # Voeg de toestand toe
        tijdlijn.Toestanden.insert (0, nieuweToestand)

#----------------------------------------------------------------------
#
# Vergelijking van de inhoud van toestanden en annotatieversies
#
#----------------------------------------------------------------------
    @staticmethod
    def _IsToestandActueelGelijkAan (toestand1 : ToestandActueel, toestand2: ToestandActueel):
        """Geeft aan of de inhoud van de de ene toestand gelijk is aan die van de andere toestand.
        Hierbij worden tijdaspecten buiten beschouwing gelaten. Dit type vergelijking speelt een rol 
        bij het vertalen van een reeks actuele toestand2en naar een tijdlijn met gescheiden datums en inhoud.
        """
        if toestand1 is None:
            return toestand2 is None
        if toestand1.ExpressionId != toestand2.ExpressionId:
            return False
        if toestand1.Instrumentversie != toestand2.Instrumentversie:
            return False
        if len (toestand1.TegensprekendeDoelen)!= len (toestand2.TegensprekendeDoelen):
            return False
        if len (toestand1.TeOntvlechtenDoelen)!= len (toestand2.TeOntvlechtenDoelen):
            return False
        if len (toestand1.TeVerwerkenDoelen) != len (toestand2.TeVerwerkenDoelen):
            return False
        for idx, d in enumerate (toestand1.TegensprekendeDoelen):
            if '\n'.join (d.ModuleXmlElement()) != '\n'.join (toestand2.TegensprekendeDoelen[idx].ModuleXmlElement ()):
                return False
        for idx, d in enumerate (toestand1.TeOntvlechtenDoelen):
            if '\n'.join (d.ModuleXmlElement()) != '\n'.join (toestand2.TeOntvlechtenDoelen[idx].ModuleXmlElement ()):
                return False
        for idx, d in enumerate (toestand1.TeVerwerkenDoelen):
            if '\n'.join (d.ModuleXmlElement()) != '\n'.join (toestand2.TeVerwerkenDoelen[idx].ModuleXmlElement ()):
                return False
        return True

    @staticmethod
    def _IsAnnotatieVersieGelijkAan (versie1 : ActueleAnnotatieVersie, versie2 : ActueleAnnotatieVersie):
        """Geeft aan of de inhoud van de de ene versie gelijk is aan die 
        van de andere versie.
        """
        if versie1 is None:
            return versie2 is None
        if versie1.Uitleg != versie2.Uitleg:
            return False
        if versie1.Versies is None:
            return versie2.Versies is None
        elif versie2.Versies is None:
            return False
        if len (versie1.Versies) != len (versie2.Versies):
            return False
        for idx, v in enumerate (versie1.Versies):
            if v._Nummer != versie2.Versies[idx]._Nummer:
                return False
        return True
