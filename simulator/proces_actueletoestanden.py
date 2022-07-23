#======================================================================
#
# Bepaling van de actuele toestanden op basis van de uitgewisselde
# informatie.
#
#======================================================================
#
# De bepaling van actuele toestanden maakt gebruik van een aantal
# operaties die in proces_toestanden.py zijn ondergebracht:
# - Selectie van de relevante delen uit het versiebeheer
# - Bepaling van de instrumentversie van een toestand
#
# In MaakActueleToestanden zijn ondergebrachtL
# - Bepaling welke toestanden er zijn
#
# In deze applicatie worden alle actuele toestanden (ex nunc)
# uitgerekend om te laten zien wat het effect van bijv. vernietiging
# van een besluit is. In een productie-waardige applicatie zal dat 
# niet nodig zijn. Omdat het uitsluitend over de nu en in de toekomst
# geldige toestanden gaat (zal een beperkt aantal zijn) worden alle
# toestanden opnieuw berekend. Optimalisatie door sommige
# toestanden ongewijzigd te laten vereist dat van tevoren voorspeld 
# kan worden welke toestanden geraakt worden door een uitwisseling.
# Dat is complex en foutgevoelig vanwege de terugwerking naar 
# het (verre) verleden van sommige operaties. Aangezien er (ook in
# productie-waardige) applicaties weinig actuele toestanden zullen
# zijn, zal optimalisatie weinig opleveren.
#
# De verschillende lijsten worden in deze applicatie gesorteerd
# zodat de uiteindelijke weergave onafhankelijk is van
# implementatiedetails. Dat is in een productie-waardige applicatie
# niet nodig.
#
#======================================================================

from applicatie_meldingen import Melding
from data_consolidatie import GeconsolideerdInstrument
from proces_toestanden import MaakToestanden
from stop_actueletoestanden import ActueleToestanden, TegensprekendDoel
from weergave_data_toestanden import  ToestandActueel
from weergave_toestandbepaling import Weergave_Toestandbepaling

#======================================================================
#
# Aanmaken van actuele toestanden na een uitwisseling, per instrument
#
#======================================================================
class MaakActueleToestanden (MaakToestanden):

    @staticmethod
    def VoerUit (log,  consolidatie : GeconsolideerdInstrument, gemaaktOp, ontvangenOp, bekendOp):
        """Maak een nieuwe versie van de actuele toestanden.
        
        log Meldingen Verzameling meldingen over de voortgang van het consolidatieproces
        consolidatie GeconsolideerdInstrument  Informatie over het geconsolideerde instrument
        gemaaktOp string Tijdstip waarop de uitwisseling gemaakt is
        ontvangenOp string De datum waarop de uitwisseling ontvangen is waarvoor de consolidatie opnieuw gedaan wordt.
        bekendOp string De datum waarop de uitwisseling bekend is waarvoor de consolidatie opnieuw gedaan wordt.
        """
        maker = MaakActueleToestanden (log, consolidatie, gemaaktOp, ontvangenOp, bekendOp)
        maker._VoerUit ()

#----------------------------------------------------------------------
# Implementatie
#----------------------------------------------------------------------
    def __init__ (self, log, consolidatie : GeconsolideerdInstrument, gemaaktOp, ontvangenOp, bekendOp):
        """Maak een nieuwe instantie.
        
        log Meldingen Verzameling meldingen over de voortgang van het consolidatieproces
        consolidatie GeconsolideerdInstrument  Informatie over het geconsolideerde instrument
        gemaaktOp string Tijdstip waarop de uitwisseling gemaakt is
        ontvangenOp string De datum waarop de uitwisseling ontvangen is waarvoor de consolidatie opnieuw gedaan wordt.
        bekendOp string  Maximale waarde van de bekendOp tijdstempels die meedoen in de consolidatie,
                         of None als alle versiebeheerinformatie meegenomen wordt.
        """
        super().__init__ (consolidatie, gemaaktOp, ontvangenOp, bekendOp)
        self._Log = log

#----------------------------------------------------------------------
# Bepaal de toestanden
#----------------------------------------------------------------------
    def _VoerUit (self):
        """Maak de ActueleToestanden module aan voor deze uitwisseling"""
        # Maak de module
        self._Consolidatie.ActueleToestanden = actueleToestanden = ActueleToestanden ()
        actueleToestanden.BekendOp = self._BekendOp
        actueleToestanden.OntvangenOp = self._OntvangenOp

        #
        # JWV = juridischWerkendVanaf
        # GV = geldigVanaf
        #

        # Bepaal de toestanden
        voorgaandeDoelen = [] # Alle doelen van de voorgaande toestand; lijst met instanties van Doel
        iwtDoelen = [] # Alle doelen voor de nieuwe toestand die tegelijk in werking treden; lijst met instanties van Doel
        laatsteJWV = None # JuridischWerkendVanaf in voorgaande iteratie van onderstaande loop
        laatsteGV = None # GeldigVanaf in voorgaande iteratie van onderstaande loop
        meldingen = [] # Alleen voor weergave: cumulatieve meldingen zodat elke toestand de historie tot en met de creatie van de toestand krijgt

        def _MaakToestand ():
            """Maak een nieuwe toestand op basis van de verzamelde informatie.
            Deze code is in een aparte methode gezet omdat het op twee plaatsen in de bepaling nodig is."""
            nieuw = ToestandActueel()
            nieuw.JuridischWerkendVanaf = laatsteJWV
            actueleToestanden.Toestanden.append (nieuw)
            iwtDoelen.sort (key = lambda d: d.Identificatie)
            nieuw.Inwerkingtredingsdoelen = iwtDoelen
            nieuw.Basisversiedoelen = [*voorgaandeDoelen]
            nieuw.JuridischWerkendVanaf = laatsteJWV
            nieuw.Identificatie = self._Consolidatie.MaakToestandExpressionId (nieuw, laatsteJWV, laatsteGV, meldingen)
            nieuw._Consolidatieproces._Uitleg = [*meldingen]

        consolidatieStap = Weergave_Toestandbepaling.BepaalToestanden
        def _MaakMelding (tekst, ernst = Melding.Ernst_Informatie):
            """Alleen voor weergave: maak een melding aan"""
            melding = Melding(ernst, tekst)
            melding._Stap = consolidatieStap
            meldingen.append (melding)

        # In deze applicatie worden de niet-actuele ActueleToestanden nog
        # wel bepaald omdat het effect van bijvoorbeeld een vernietiging van een
        # besluit in een ver verleden het eenvoudigste uit te leggen is via 
        # ActueleToestanden - inzichtelijker dan voor het volledig tijdreizen
        # met CompleteToestanden.
        #
        # In een productie-waardige applicatie zou het startpunt zijn:
        # - Bepaal de grootste JuridischWerkendVanaf die kleiner is dan OntvangenOp,
        #   zeg jwv_start. Dit is de inwerkingtreding van de nu geldende toestand
        # - voorgaandeDoelen bevat het Doel voor elke tijdstempel met JuridischWerkendVanaf < jwv_start, behalve de laatste
        # - gv_maximaal bevat de maximale waarde van geldigVanaf voor tijdstempels met JuridischWerkendVanaf < jwv_start
        # - Onderstaande "for tijdstempel..." itereert alleen over tijdstempels met JuridischWerkendVanaf >= jwv_start

        # De ActueleToestanden met een jwv >= jurdiischUitgewerktOp worden gewoon bepaald, ook al hebben ze geen geldighied
        # Deze toestanden krijgen een jwv >= juridischWerkendTot en geen instrumentversie, maar in de TegensprekendeDoelen
        # is te zien dat de intrekking niet verenigbaar is met deze toestand. De toestand moet vermeld worden omdat het
        # de manier is om aan de verstrekker van de informatie terug te koppelen dat er een probleem is met de toestand.
        # In het overzicht van complete toestanden worden deze toestanden wel weggelaten.

        jwv_start = None
        gv_maximaal = None # Maximale waarde voor geldigVanaf van voorgaande toestanden
        aantalBepaald = 0 # Voor meldingen: hou bij hoe veel toestanden be
        aantalNodig = 0
        for _, tijdstempel in self.TijdstempelMomentopnamen ():
            if tijdstempel.JuridischWerkendVanaf <= self._OntvangenOp:
                jwv_start = tijdstempel.JuridischWerkendVanaf
                if tijdstempel.JuridischWerkendVanaf <= self._OntvangenOp:
                    aantalNodig = 1
            else:
                aantalNodig += 1
            aantalBepaald += 1

            # Negeer alle toestanden met een geldigVanaf eerdere dan de laatste toestand (met dezelfde jwv)
            # Maak daarom pas een toestand aan nadat de volgende jwv-datum langskomt.
            geldigVanaf = tijdstempel.JuridischWerkendVanaf if tijdstempel.GeldigVanaf is None else tijdstempel.GeldigVanaf
            if not gv_maximaal is None and geldigVanaf < gv_maximaal:
                # De terugwerkende kracht overlapt met andere (complete) toestanden. Bij het maken van de complete 
                # toestanden wordt overlap vertaald naar een aparte toestand. De actuele toestand correspondeert dan
                # met een complete toestand die als GV heeft:
                geldigVanaf = gv_maximaal

            if not laatsteJWV is None:
                if laatsteJWV < tijdstempel.JuridischWerkendVanaf:
                    _MaakToestand ()
                    voorgaandeDoelen.extend (iwtDoelen)
                    voorgaandeDoelen.sort (key = lambda d: d.Identificatie)
                    iwtDoelen = []
                    laatsteJWV = None
                elif geldigVanaf > laatsteGV:
                    _MaakMelding ('Gebruik de geldigVanaf ' + geldigVanaf + ' voor doel ' + str(tijdstempel.Branch.Doel) + ' voor de nieuwe toestand want de waarde is groter dan voor een eerder doel. Negeer de toestand met eerdere geldigVanaf want die zal nooit geldig zijn.') 
            if laatsteJWV is None:
                laatsteJWV = tijdstempel.JuridischWerkendVanaf
                _MaakMelding ('Nieuwe toestand voor juridischWerkendVanaf ' + laatsteJWV + ' en geldigVanaf ' + geldigVanaf) 
            laatsteGV = geldigVanaf
            _MaakMelding ('Doel ' + str(tijdstempel.Branch.Doel) + ' is een van de inwerkingtredingsdoelen van de toestand') 
            iwtDoelen.append (tijdstempel.Branch.Doel)
            if gv_maximaal is None or geldigVanaf > gv_maximaal:
                gv_maximaal = geldigVanaf


        self._Log.Detail ('Er zijn ' + str(aantalBepaald) + ' toestand(en) bepaald, waarvan ' + str(aantalNodig) + ' strikt nodig en ' + str(aantalBepaald-aantalNodig) + ' alleen voor de weergave in deze applicatie')
        if aantalBepaald > 0:
            _MaakToestand ()

            # Alle toestanden met JuridischWerkendVanaf < jwv_start zijn dus de toestanden die 
            # in deze applicatie alleen voor de weergave bepaald zijn
            for toestand in actueleToestanden.Toestanden:
                if not jwv_start is None and toestand.JuridischWerkendVanaf < jwv_start:
                    toestand.NietMeerActueel = True
                else:
                    break

            # Completeer de informatie over de toestand
            juridischUitgewerktOp, _ = self.JuridischUitgewerktOp ()
            intrekkingstijdstempels = self.Intrekkingstijdstempels ()

            actueleToestanden.JuridischUitgewerktOp = tot = juridischUitgewerktOp
            for toestand in reversed (actueleToestanden.Toestanden):
                toestand.JuridischWerkendTot = tot
                if tot is None or toestand.JuridischWerkendVanaf < tot:
                    tot = toestand.JuridischWerkendVanaf

            # Bepaal de inhoud van de toestanden
            for toestand in actueleToestanden.Toestanden:

                consolidatieStap = Weergave_Toestandbepaling.Validatie_GeenToestandNaIntrekking
                toestandHeeftGeldigheid = True
                if not juridischUitgewerktOp is None:
                    if toestand.JuridischWerkendVanaf >= juridischUitgewerktOp:
                        # De toestand treedt in werking nadat het instrument ingetrokken is
                        # Markeer dat door te stellen dat deze toestand en de intrekking elkaar tegenspreken
                        toestand._Consolidatieproces.TegensprekendeDoelen = [TegensprekendDoel (t.Branch.Doel, t.GemaaktOp) for t in intrekkingstijdstempels if t.JuridischWerkendVanaf <= toestand.JuridischWerkendVanaf]
                        _MaakMelding ('De toestand wordt juridisch werkend vanaf ' + toestand.JuridischWerkendVanaf + ' nadat het instrument is ingetrokken per ' + juridischUitgewerktOp + '. Los de samenloop op met intrekkingsdoel:' + ''.join ('<br/>&nbsp;&nbsp;' + d.Doel for d in toestand._Consolidatieproces.TeVerwerkenDoelen), Melding.Ernst_Fout)
                        toestandHeeftGeldigheid = False
                    else: 
                        _MaakMelding ('De toestand wordt juridisch werkend vanaf ' + toestand.JuridischWerkendVanaf + ' terwijl het instrument pas ingetrokken wordt per ' + juridischUitgewerktOp + '.')
                else:
                    _MaakMelding ('Er is geen intrekking bekend voor het instrument.')

                self._BepaalInhoud (toestand._Consolidatieproces, toestand, toestand.Basisversiedoelen)

                if not toestandHeeftGeldigheid:
                    # Intrekking gaat voor de wijziging. Hou de toestand om erover te kunnen communiceren, maar wis de instrumentversie
                    toestand._Consolidatieproces.Instrumentversie = None

                toestand.Instrumentversie = toestand._Consolidatieproces.Instrumentversie
                toestand.TegensprekendeDoelen = toestand._Consolidatieproces.TegensprekendeDoelen
                toestand.TeVerwerkenDoelen = toestand._Consolidatieproces.TeVerwerkenDoelen
                toestand.TeOntvlechtenDoelen = toestand._Consolidatieproces.TeOntvlechtenDoelen
