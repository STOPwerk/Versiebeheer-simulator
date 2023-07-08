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

from typing import Dict, List, Set, Tuple

from applicatie_meldingen import Meldingen
from data_versiebeheerinformatie import UitgewisseldeInstrumentversie, Versiebeheerinformatie
from data_proefversie import Proefversie
from nonstop_annotatie import NonSTOPAnnotatie
from stop_naamgeving import Naamgeving
from weergave_data_stop_uitwisseling import STOPModuleUitwisseling

class MaakProefversies:

    @staticmethod
    def VoerUit (log: Meldingen, versiebeheer: Versiebeheerinformatie, uitgewisseldeVersies : List[UitgewisseldeInstrumentversie], annotaties : Dict[str,Dict[str,object]], uitgewisseldeModules : List[STOPModuleUitwisseling]) -> List[Proefversie]:
        """Maak de STOP module met proefversies voor een Uitwisseling

        Argumenten:

        log Meldingen  Verzameling van meldingen
        versiebeheer Versiebeheerinformatie  Alle informatie over instrumentversies
        uitgewisseldeVersies UitgewisseldeInstrumentversie[] De instrumentversies uit deze uitwisseling
        collectie ProefversieCollectie De proefversies die tot nu toe zijn aangemaakt
        annotaties {} Annotaties per instrumentversie en per modulenaam
        uitgewisseldeModules STOPModuleUitwisseling[]  De lijst met STOP modules die op dit moment uitgewisseld worden

        Geeft een dictionary met per work een lijst van instanties van Proefversie terug
        """
        # De basisversies van de instrumentversies kunnen in dezelfde uitwisseling zitten
        # Maak eerst alle proefversies aan
        proefversies : Dict[str,List[Proefversie]] = {}
        maakAnnotaties : Dict[Proefversie,bool] = {}
        for instrumentversie in sorted (uitgewisseldeVersies, key = lambda u: u.Instrumentversie): # Volgorde ivm weergave op resultaatpagina
            workId = Naamgeving.WorkVan (instrumentversie.Instrumentversie)
            if instrumentversie in versiebeheer.Instrumenten[workId].Proefversies:
                # Is al eerder uitgewisseld, is geen proefversie bij de publicatie
                continue

            proefversie = Proefversie ()
            proefversie.Instrumentversie = instrumentversie.Instrumentversie
            if not instrumentversie.Basisversie is None:
                instrument = versiebeheer.Instrumenten.get (workId)
                if not instrument is None:
                    branch = instrument.Branches.get (instrumentversie.Basisversie.Doel)
                    if not branch is None:
                        for mo in branch.Momentopnamen:
                            if mo.GemaaktOp == instrumentversie.Basisversie.GemaaktOp:
                                if not mo.ExpressionId is None:
                                    proefversie.Basisversie = mo.ExpressionId
                                break
            lijst = proefversies.get (workId)
            if lijst is None:
                proefversies[workId] = [proefversie]
            else:
                lijst.append (proefversie)
            maakAnnotaties[proefversie] = workId

        # De annotaties erven over van de basisversie
        while True:
            nogIetsTeDoen = False
            ietsGedaanDezeKeer = False
            for proefversie in maakAnnotaties:
                if not maakAnnotaties[proefversie] is None:
                    nogIetsTeDoen = True
                    # Neem de annotaties van de basisversie over
                    if not proefversie.Basisversie is None:
                        basisversie = versiebeheer.Proefversies.get (proefversie.Basisversie)
                        if basisversie is None:
                            # Proefversie voor de basisversie is nog niet beschikbaar
                            continue
                        proefversie.Annotaties = basisversie.Annotaties.copy ()

                    # Pas de opgegeven mutaties toe voor de annotaties
                    mutaties = annotaties.get (proefversie.Instrumentversie)
                    if not mutaties is None:
                        for mutatie in sorted (mutaties.values (), key = lambda m: m.RootElement): # Volgorde ivm weergave op resultaatpagina
                            if isinstance (mutatie, NonSTOPAnnotatie):
                                mutatie.VoerMutatieUit (proefversie.Annotaties.get (mutatie.RootElement))
                            proefversie.Annotaties[mutatie.RootElement] = mutatie
                            uitgewisseldeModules.append (STOPModuleUitwisseling (STOPModuleUitwisseling.Systeem_BevoegdGezag, STOPModuleUitwisseling.Systeem_LVBB, mutatie))

                        del annotaties[proefversie.Instrumentversie]

                    # Deze is gemaakt
                    versiebeheer.Instrumenten[maakAnnotaties[proefversie]].Proefversies[proefversie.Instrumentversie] = proefversie
                    maakAnnotaties[proefversie] = None
                    ietsGedaanDezeKeer = True

            if not nogIetsTeDoen:
                break;
            if not ietsGedaanDezeKeer:
                # Dit moet een circulaire referentie zijn
                # Zou al eerder afgevongen moeten zijn
                log.Fout ("Proefversies kunnen niet bepaald worden voor: " + ", ".join (p.Instrumentversie for p,m in maakAnnotaties.items() if m))
                break

        return proefversies
