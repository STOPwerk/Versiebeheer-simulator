#======================================================================
#
# Gemeenschappelijke functies voor data validatie
#
#======================================================================

import re

class Valideer:
    @staticmethod
    def Datum (datum):
        """Valideer de waarde van een datum

        Argumenten:
        datum string  Te valideren waarde

        Geeft de waarde terug als de waarde valide is, anders None
        """
        if datum and Valideer._DatumPatroon.match (datum):
            return datum
        return None

    _DatumPatroon = re.compile ('^[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}$')


    @staticmethod
    def GemaaktOp (gemaaktOp):
        """Valideer de waarde van een gemaaktOp tijdstip

        Argumenten:
        gemaaktOp string  Te valideren waarde

        Geeft de waarde terug als de waarde valide is, anders None
        """
        if gemaaktOp and Valideer._GemaaktOpPatroon.match (gemaaktOp):
            return gemaaktOp
        return None

    _GemaaktOpPatroon = re.compile ('^[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$')
