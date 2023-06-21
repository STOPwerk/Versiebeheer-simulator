#======================================================================
#
# Interne modellering van Doel
#
#======================================================================
#
# Er wordt veel gerekend met doelen. Als het doel iedere keer
# uitgeschreven wordt, dan neemt dat veel (werk)geheugen in beslag.
# In plaats daarvan gebruikt deze applicatie een verwijzing naar
# een instantie voor het in-memory model, en/of de index van het doel
# waar doelen een sleutel zijn.
#
#======================================================================

class Doel:

#----------------------------------------------------------------------
# Conversie van identificatie naar Doel instantie
#----------------------------------------------------------------------
    @staticmethod
    def DoelInstantie (identificatie : str):
        """Geef de unieke instantie voor een nieuw doel aan.

        Argumenten:

        identificatie string  JOIN identificatie voor het doel
        """
        if identificatie is None:
            return None
        if isinstance (identificatie, Doel):
            return identificatie
        doel = Doel._DoelIndex.get (identificatie)
        if doel is None:
            Doel._DoelIndex[identificatie] = doel = Doel (identificatie, len (Doel._DoelIndex) + 1)
        return doel

    _DoelIndex = {}

    def __init__ (self, identificatie : str, index : int):
        """Maak een instantie voor een nieuw doel aan.

        Argumenten:

        identificatie string  JOIN identificatie voor het doel
        index int  Index van het doel in de verzameling van alle doelen
        """
        self.Identificatie = identificatie
        self.Index = index
        # Verkorte identificatie van het doel
        self.Naam = identificatie[identificatie.rindex ('/')+1:]

#----------------------------------------------------------------------
# Ondersteuning voor werken in Python
#----------------------------------------------------------------------
    def __str__(self):
        return self.Identificatie

    def __hash__(self):
        return hash(self.Index)

    def __eq__(self, other):
        return self.Index == other.Index
