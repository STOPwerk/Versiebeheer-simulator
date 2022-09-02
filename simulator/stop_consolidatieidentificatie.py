#======================================================================
#
# In-memory representatie van de STOP ConsolidatieIdentificatie module.
#
#======================================================================
#
# Dit is een uitgeklede versie van de STOP module, zonder gegevens over
# soortWork en relatie tussen tijdelijk regelingdeel en hoofdregeling.
# Doel binnen deze applicatie is alleen om de relatie tussen het
# instrument en de consolidatie ervan vast te leggen.
#
#======================================================================

from stop_naamgeving import Naamgeving

#======================================================================
#
# ConsolidatieIdentificatie
#
#======================================================================
class ConsolidatieIdentificatie:

    def __init__ (self, scenario, instrumentWorkId, juridischWerkendVanaf):
        """Maak de identificatie voor het geconsolideerde instrument aan

        Argumenten:
        scenario Scenario  Scenrario waar het instrument onderdeel van is
        instrumentWorkId string  Work-identificatie van het niet=geconsildeerde instrument
        juridischWerkendVanaf string  Datum van eerste inwerkingtreding
        """
        # De work-identificatie van het instrument
        self.IsConsolidatieVan = instrumentWorkId
        # De work-identificatie van het geconsolideerde element
        self.WorkId  = Naamgeving.WorkVoorConsolidatieVan (instrumentWorkId, int (juridischWerkendVanaf[0:4]), scenario._InstrumentVolgnummer)
        scenario._InstrumentVolgnummer += 1
