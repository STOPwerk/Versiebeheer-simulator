#======================================================================
#
# Bepaling van de proefversies voor uitgewisselde instrumentversies
# en van de non-STOP annotaties die daarbij horen.
#
#----------------------------------------------------------------------
#
# Voor elke uitwisseling waarin instrumentversies uitgewisseld worden
# kan per instrumentversie informatie over de versie uit het
# versiebeheer gegeven worden. Daarmee kunnen andere systemen extra
# informatie (zoals non-STOP annotaties) aan de versie koppelen.
# Die andere informatie moet dan wel meedoen met het STOP versiebeheer
# en dezelfde doelen + gemaaktOp hebben als de proefversies.
#
#======================================================================

from typing import List

from applicatie_meldingen import Melding
from data_annotatie import Annotatie
from data_versiebeheerinformatie import Uitwisseling, UitgewisseldeInstrumentversie
from stop_proefversies import Annotatiebron, AnnotatiebronOvernme
from weergave_data_proefversies import Proefversie, ProefversieAnnotatie

class MaakProefversies:

    @staticmethod
    def VoerUit (uitwisseling : Uitwisseling, annotaties : List[Annotatie]):
        """Maak de STOP module met proefversies voor een Uitwisseling

        Argumenten:

        uitwisseling Uitwisseling  Model voor de uitwisseling dat onderdeel is van het versiebeheer
        annotaties Annotatie[] Lijst met instanties van Annotaties

        Geeft een lijst van instanties van Proefversie terug
        """
        proefversies = []
        for instrumentversie in uitwisseling.Instrumentversies:
            # Maak alleen proefversies als er annotaties zijn voor dit instrument die van versiebeheer gebruik maken
            instrumentAnnotaties = [a for a in annotaties if a.WorkId == instrumentversie._Instrument.WorkId and a.ViaVersiebeheer]
            if len(instrumentAnnotaties) > 0:
                # Maak de proefversie met de annotaties tot en met deze uitwisseling
                maker = MaakProefversies (instrumentversie)
                maker._VoerUit ([a for a in instrumentAnnotaties if a.Versies[0].GemaaktOp <= uitwisseling.GemaaktOp])
                proefversies.append (maker.Proefversie)
        return proefversies

#----------------------------------------------------------------------
#
# Implementatie
#
#----------------------------------------------------------------------
    def __init__(self, instrumentversie : UitgewisseldeInstrumentversie):
        """Maak een proefversie generator aan

        Argumenten:

        instrumentversie UitgewisseldeInstrumentversie  Beschrijving van de instrumentversie
        """
        self._Instrumentversie = instrumentversie
        # Proefversie
        self.Proefversie = Proefversie ()
        self.Proefversie.Instrumentversie = self._Instrumentversie.Instrumentversie
        self.Proefversie.Doelen = self._Instrumentversie.Doelen

    def _VoerUit (self, annotaties : List[Annotatie]):
        """Bepaal de proefversie met bijbehorende annotaties

        Argumenten:

        annotaties Annotatie[] Lijst met instanties van Annotaties
        """
        self._BepaalProefversie ()
        for annotatie in annotaties:
            self._BepaalAnnotatieVersie (annotatie)

#----------------------------------------------------------------------
#
# Bepaling STOP proefversie
#
#----------------------------------------------------------------------
    def _BepaalProefversie (self):
        """Maak de Proefversie voor een uitwisseling van een versie van het niet-geconsolideerde instrument"""

        def _Melding (sorteerOp, tekst):
            """Voeg een melding toe voor de uitleg van de bepaling van de proefversies"""
            melding = Melding (Melding.Ernst_Informatie, tekst)
            melding._SorteerOp = sorteerOp
            self.Proefversie._Uitleg.append (melding)

        # Loop het versiebeheer af, te beginnen met de doelen/gemaaktOp van de uitwisseling
        # key = branch, value = te onderzoeken laatste momentopname
        teOnderzoeken = {}
        for doel in self._Instrumentversie.Doelen:
            for momentopname in reversed (self._Instrumentversie._Instrument.Branches[doel].Momentopnamen):
                if momentopname.GemaaktOp <= self._Instrumentversie._Uitwisseling.GemaaktOp:
                    teOnderzoeken[momentopname.Branch] = momentopname
                    break
        # Resulterende bronnen
        # key = branch, value = instantie van Annotatiebron
        bronnen = {}

        while len (teOnderzoeken) > 0:
            laatsteMomentopname = list(teOnderzoeken.values ())[0]
            del teOnderzoeken[laatsteMomentopname.Branch]

            # Maak een proefversie aan
            bron = bronnen.get (laatsteMomentopname.Branch)
            if bron is None:
                bronnen[laatsteMomentopname.Branch] = bron = Annotatiebron (laatsteMomentopname.Branch.Doel)
                self.Proefversie.Annotatiebronnen.append (bron)

            # Zoek de meest recente momentopnamen van andere branches op waar een annotatie van
            # overgenomen is (via een basisversie relatie).
            for momentopname in laatsteMomentopname.Branch.Momentopnamen:
                if not bron.TotEnMet is None and bron.TotEnMet >= momentopname.GemaaktOp:
                    # Al eerder verwerkt
                    continue
                if momentopname.GemaaktOp > laatsteMomentopname.GemaaktOp:
                    # Te recente uitwisseling
                    break
                bron.TotEnMet = momentopname.GemaaktOp

                for basisversieMomentopname in momentopname.Basisversies.values ():
                    if basisversieMomentopname.Branch == momentopname.Branch:
                        continue
                    # Registreer de basisversie als bron voor overerving
                    _Melding (str(momentopname.Branch.Doel) + '\n' + momentopname.GemaaktOp, "Annotaties voor " + str(momentopname.Branch.Doel) + " vanaf " + momentopname.GemaaktOp + " kunnen overgenomen worden uit basisversie " + str(basisversieMomentopname.Branch.Doel) + " tot en met " + basisversieMomentopname.GemaaktOp)
                    bron.AnnotatiesOvernemenVan.append (AnnotatiebronOvernme (momentopname.GemaaktOp, basisversieMomentopname.Branch.Doel, basisversieMomentopname.GemaaktOp))

                    # Is de bron al ondersocht/opgevoerd om te onderzoeken?
                    andereBranch = teOnderzoeken.get (basisversieMomentopname.Branch)
                    if andereBranch is None:
                        andereBranch = bronnen.get (basisversieMomentopname.Branch)
                        if andereBranch is None or andereBranch.TotEnMet < basisversieMomentopname.GemaaktOp:
                            # Nee / niet de laatste versie
                            teOnderzoeken[basisversieMomentopname.Branch] = basisversieMomentopname
                    elif andereBranch.GemaaktOp < basisversieMomentopname.GemaaktOp:
                        # Niet de laatste versie
                        teOnderzoeken[basisversieMomentopname.Branch] = basisversieMomentopname

        # Alleen voor weergave: sorteren en completeren van meldingen
        # Van de sortering wordt ook gebruik gemaakt in _BepaalAnnotatieVersie
        for bron in bronnen.values ():
            _Melding (str(bron.Doel) + '\nA', "Annotaties kunnen uit " + str(bron.Doel) + " tot en met " + bron.TotEnMet + " afkomstig zijn; onderzoek de branch op basisversies.")
            bron.AnnotatiesOvernemenVan.sort (key = lambda x: x.Vanaf + str(x.Doel), reverse = True)
        self.Proefversie.Annotatiebronnen.sort (key = lambda x: x.TotEnMet + str(x.Doel), reverse = True)
        self.Proefversie._Uitleg.sort (key = lambda x: x._SorteerOp, reverse = True)

#----------------------------------------------------------------------
#
# Bepaling STOP proefversie
#
#----------------------------------------------------------------------
    def _BepaalAnnotatieVersie (self, annotatie: Annotatie):
        """Maak de Proefversie voor een uitwisseling van een versie van het niet-geconsolideerde instrument
        
        Argumenten:
        
        annotatie Annotatie  De annotatie waarvan een waarde aan de proefversie gekoppend moet worden"""

        annotatieVersie = ProefversieAnnotatie ()
        annotatieVersie.Naam = annotatie.Naam
        annotatieVersie._Annotatie = annotatie
        self.Proefversie.Annotaties.append (annotatieVersie)

        def _Melding (tekst, ernst = Melding.Ernst_Informatie):
            """Voeg een melding toe voor de uitleg van de bepaling van de proefversies"""
            melding = Melding (ernst, tekst)
            annotatieVersie._Uitleg.append (melding)

        # Het vinden van de juiste versie komt neer op het aflopen van de versiebeheer boom
        # Bewaar alle tussenresultaten zodat niet meermalen dezelfde tak bewandeld wordt
        gevonden = {} # key = gemaaktOp + doel, value = instantie van AnnotatieUitwisseling, of False als de versie niet bepaald kan worden

        #--------------------------------------------------------------
        #
        # Kern van de bepaling: annotatieversie voor een doel
        #
        #--------------------------------------------------------------
        def _Onderzoek (doel, totEnMet):
            """Bepaal de annotatie voor dit doel en meest recente gemaaktOp.
            Geeft de gevonden AnnotatieUitwisseling terug, of False als er meerdere versies zijn
            """
            
            gevondenKey = totEnMet + str(doel)
            resultaat = gevonden.get (gevondenKey)
            if not resultaat is None:
                # Eerder opgezocht
                return resultaat

            _Melding ('Zijn er annotaties aangeleverd voor ' + str(doel) + ' tot en met ' + totEnMet + '?')

            uitgewisseldeVersie = None
            onderzochtVanaf = None
            for versie in reversed (annotatie.Versies):
                if versie.GemaaktOp <= totEnMet:
                    if doel in versie.Doelen:
                        # Dit is een goede annotatieversie
                        _Melding ('Annotatie aangeleverd; versie van ' + versie.GemaaktOp)
                        uitgewisseldeVersie = versie
                        onderzochtVanaf = versie.GemaaktOp
                        annotatieVersie._Bronnen.append ((doel, uitgewisseldeVersie.GemaaktOp))
                    break

            overerving = None
            overervingBron = None
            maakMelding = True
            isTegenstrijdig = False
            for bron in self.Proefversie.Annotatiebronnen:
                if bron.Doel == doel:
                    for overnemenVan in bron.AnnotatiesOvernemenVan:
                        if overnemenVan.Vanaf <= totEnMet:
                            if uitgewisseldeVersie is None or uitgewisseldeVersie.GemaaktOp < overnemenVan.Vanaf:
                                if maakMelding:
                                    maakMelding = False
                                    if uitgewisseldeVersie is None:
                                        _Melding ('Geen annotatie aangeleverd; neem de annotatie over van basisversies')
                                    else:
                                        _Melding ('Er zijn basisversies voor latere uitwisselingen voor het doel; neem de annotaties daarvan ook mee')
                                if onderzochtVanaf is None or overnemenVan.Vanaf < onderzochtVanaf:
                                    onderzochtVanaf = overnemenVan.Vanaf

                                u = _Onderzoek (overnemenVan.Doel, overnemenVan.GemaaktOp)
                                if not u is None:
                                    if not u: # False
                                        # Tegenstrijdige annotatie, dat wordt niets meer
                                        _Melding ('Annotatieversie kan niet bepaald worden omdat er geen eenduidige versie uit de basisversies afgeleid kan worden')
                                        gevonden[gevondenKey] = False
                                        isTegenstrijdig = True # Ga toch door om een complete weergave te krijgen
                            
                                    elif not uitgewisseldeVersie is None and u != uitgewisseldeVersie:
                                        # Tegenstrijdige annotatie, dat wordt niets meer
                                        _Melding ('Uitgewisselde annotatieversie voor doel ' + str(doel) + ' tot en met ' + totEnMet + ' (versie van ' + uitgewisseldeVersie.GemaaktOp + ') en annotatie op ' + overnemenVan.Vanaf + ' overgenomen van doel ' + str(overnemenVan.Doel) + ' tot en met ' + overnemenVan.GemaaktOp + ' (versie van ' + u.GemaaktOp + ') zijn verschillend', Melding.Ernst_Fout)
                                        gevonden[gevondenKey] = False
                                        isTegenstrijdig = True # Ga toch door om een complete weergave te krijgen
                                        annotatieVersie._Tegenstrijdig.append ((doel, overnemenVan.Vanaf)) # Het gaat mis bij binnenkomst van de basisversie
                                        annotatieVersie._TegenstrijdigeVersies.add (uitgewisseldeVersie)
                                        annotatieVersie._TegenstrijdigeVersies.add (u)

                                    elif not overerving is None and u != overerving:
                                        # Tegenstrijdige annotatie, dat wordt niets meer
                                        _Melding ('Annotatieversie op ' + overervingBron.Vanaf + ' overgenomen van doel ' + str(overervingBron.Doel) + ' tot en met ' + overervingBron.GemaaktOp + ' (versie van ' + overerving.GemaaktOp + ') en op ' + overnemenVan.Vanaf + ' overgenomen van doel ' + str(overnemenVan.Doel) + ' tot en met ' + overnemenVan.GemaaktOp + ' (versie van ' + u.GemaaktOp + ') zijn verschillend', Melding.Ernst_Fout)
                                        gevonden[gevondenKey] = False
                                        isTegenstrijdig = True # Ga toch door om een complete weergave te krijgen
                                        annotatieVersie._Tegenstrijdig.append ((doel, overervingBron.Vanaf)) # Het gaat mis bij binnenkomst van de vorige (latere) basisversie
                                        annotatieVersie._TegenstrijdigeVersies.add (overerving)
                                        annotatieVersie._TegenstrijdigeVersies.add (u)

                                    else:
                                        overerving = u
                                        overervingBron = overnemenVan

                    break

            annotatieVersie._Onderzocht.append ((doel, onderzochtVanaf, totEnMet))
            if isTegenstrijdig:
                return False
            # Alle (relevante) basisversies zijn onderzocht
            if uitgewisseldeVersie is None:
                uitgewisseldeVersie = overerving
            gevonden[gevondenKey] = uitgewisseldeVersie
            return uitgewisseldeVersie

        #--------------------------------------------------------------
        #
        # Bepaal de annotatieversie voor elk van de doelen
        #
        #--------------------------------------------------------------

        if len (self.Proefversie.Doelen) == 1:
            # Met 1 doel is de bepaling eenvoudiger
            annotatieVersie.Versie = _Onderzoek (self.Proefversie.Doelen[0], self._Instrumentversie._Uitwisseling.GemaaktOp)
        else:
            # Bij meerdere doelen moet voor elk doel hetzelfde gevonden worden
            # Gevonden uitwisselingen
            # Key = AnnotatieUitwisseling, value = lijst van doelen
            doelVoorResultaat = {}
            for doel in self.Proefversie.Doelen:
                u = _Onderzoek (doel, self._Instrumentversie._Uitwisseling.GemaaktOp)
                eerderGevonden = doelVoorResultaat.get ('' if u is None else u)
                if eerderGevonden is None:
                    doelVoorResultaat['' if u is None else u] = eerderGevonden = []
                eerderGevonden.append (doel)

            if len(doelVoorResultaat) > 1:
                _Melding ('Verschillende annotatieversies gevonden:\n' + '\n'.join (('Geen annotatie' if u == '' else 'Uitwisseling: ' + u.GemaaktOp) + ' voor ' + ', '.join (str(d) for d in doelen) for u, doelen in doelVoorResultaat), Melding.Ernst_Fout)
                for versie, doelen in doelVoorResultaat.items ():
                    annotatieVersie._Tegenstrijdig.extend ((d, self._Instrumentversie._Uitwisseling.GemaaktOp) for d in doelen)
                    if versie:
                        annotatieVersie._TegenstrijdigeVersies.add (versie)
            else:
                annotatieVersie.Versie = list (doelVoorResultaat.keys())[0]
