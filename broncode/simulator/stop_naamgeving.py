#======================================================================
#
# Naamgeving is een hulpklasse waarin logica is ondergebracht om met
# identificaties van regelingen en informatieobjecten om te kunnen
# gaan.
#
#======================================================================

class Naamgeving:

#----------------------------------------------------------------------
# Informatie over een identificatie
#----------------------------------------------------------------------
    @staticmethod
    def IsExpression (identificatie):
        """Geeft aan of de identificatie van een versie (expression) is en niet van een work"""
        return identificatie.find ("@") > 0

    @staticmethod
    def IsRegeling (identificatie):
        """Geeft aan of de identificatie van een regeling of regelingversie is"""
        return identificatie[0:12] == "/akn/nl/act/"

    @staticmethod
    def IsInformatieobject (identificatie):
        """Geeft aan of de identificatie van een informatieobject of informatieobjectversie is"""
        return identificatie[0:17] == "/join/id/regdata/"

#----------------------------------------------------------------------
# Manipulatie van een identificatie
#----------------------------------------------------------------------
    @staticmethod
    def WorkVan (identificatie):
        """Geeft de work-identificatie van een identificatie"""
        idx = identificatie.find ("@")
        if idx < 0:
            return identificatie
        work = identificatie[0:idx]
        if work[-4:] == "/nld":
            work = work[0:-4]
        return work

    @staticmethod
    def WorkVoorConsolidatieVan (identificatie, jaar, volgnummer):
        """Geeft de work-identificatie van de consolidatie van een regeling of informatieobject
        
        Argumenten:
        identificatie string Identificatie van work of expression van een regeling of informatieobject
        jaar int jaar van eerste inwerkingtreding
        volgnummer int Volgnummer voor de geconsolideerde regeling/informatieobject
        """
        if Naamgeving.IsRegeling (identificatie):
            work = "/akn/nl/act/"
            onderdelen = identificatie.split ('/')
            if len (onderdelen) > 4:
                if onderdelen[4][0:2] == "gm":
                    work += "gemeente"
                elif onderdelen[4][0:2] == "ws":
                    work += "waterschap"
                elif onderdelen[4][0:2] == "pv":
                    work += "provincie"
                else:
                    work += "land"
            else:
                work += "land"
            work += "/"
            naam = "regeling"
        elif Naamgeving.IsInformatieobject (identificatie):
            work = "/join/id/regdata/consolidatie/"
            naam = "io"
        else:
            return
        work += str(jaar) + "/" + naam + str(volgnummer)
        return work
