#======================================================================
#
# Project-gericht werken bij een bevoegd gezag: specificatie van 
# een project.
#
#======================================================================
#
# STOP schrijft niet voor hoe een bevoegd gezag moet werken. Een
# mogelijke werkwijze is projectmatig werken. Per beoogde instelling/
# wijziging van regelgeving wordt dan een project opgezet om de 
# wijziging voor te bereiden en een consultatie- en besluitvormings-
# proces te doorlopen. In een project wordt geïsoleerd van andere 
# projecten gewerkt; op specifieke punten worden wijzigingen uit andere
# projecten overgenomen.
#
# Deze applicatie kan dat simuleren door in een scenario een of meer 
# projectspecificaties op te nemen. De applicatie bepaalt dan aan de
# hand van de gespecificeerde acties hoe de consolidatie-informatie
# eruit moet zien en welke keuze voor was-wordt-mutaties bestaat.
# De projecten kunnen gecombineerd worden met een of meer STOP
# ConsolidatieInformatie modules; die worden dan als "overige projecten"
# weergegeven.
#
# In deze applicatie wordt het versiebeheer voor de ontvangende
# systemen (landelijke voorzieningen) per instrument uitgevoerd.
# Voor projectmatig werken aan de verzendende (bevoegd gezag) kant
# hanteert deze applicatie versiebeheer per doel binnen een project.
# Eenvoudige projecten zullen één doel kennen, uitgebreidere projecten
# mogelijk meer.
#
#======================================================================

from typing import Dict
from data_doel import Doel
from stop_consolidatieinformatie import ConsolidatieInformatie
from stop_naamgeving import Naamgeving

#======================================================================
#
# Intern datamodel voor het versiebeheer
#
#======================================================================

#----------------------------------------------------------------------
# ProjectActie: een actie die binnen het project wordt uitgevoerd.
#               Dit is een actie op het gebied van versiebeheer en/of
#               een specifiek type uitwisseling die al dan niet tot een
#               publicatie leidt. Voor elke actie is een aparte afgeleide
#               klasse beschikbaar
#----------------------------------------------------------------------
class ProjectActie:

    def __init__ (self, project):
        """Maak een specificatie van een actie aan die binnen een project is/wordt
        uitgevoerd. Een actie leidt tenminste tot een of meer nieuwe instrumentversies
        of intrekking ervan, en optioneel tot een officiële publicatie.

        Argumenten:

        project Project  Project waarvoor de actie is gespecificeerd
        """
        self._Project = project
        project.Acties.append (self)
        # De soort actie die binnen het project uitgevoerd wordt
        self.SoortActie = None
        # Begintijdstip van de actie, og het gemaaktOp tijdstip als het om 
        # uitwisselingen gaat.
        self.UitgevoerdOp = None
        # Geeft aan dat de actie een uitwisseling is en dat UitgevoerdOp als een gemaaktOp tijdstip gezien moet worden
        self._IsUitwisseling = False
        # Beschrijving van een actie die binnen het project wordt uitgevoerd
        # Alleen nodig voor weergave
        self.Beschrijving = None

    _SoortActie_NieuwDoel = 'Nieuw doel' # Start van werken aan een nieuw doel bij BG
    _SoortActie_Download = 'Download' # Actie door adviesbureau: download uit de LVBB
    _SoortActie_Uitwisseling = 'Uitwisseling' # Wissel aangepaste versie uit tussen adviesbureau en bevoegd gezag
    _SoortActie_Wijziging = 'Wijziging' # Pas de instrumentversie(s) en tijdstempels op een branch aan
    _SoortActie_BijwerkenUitgangssituatie = 'Bijwerken uitgangssituatie' # Neem de wijzigingen over van (nu of later) geldende regelgeving of van een branch, afhankelijk van de uitgangssituatie.
    _SoortActie_Publicatie = 'Publicatie' # Publicatie van een besluit/mededeling/revisie

    # Constructors om de acties te maken (bij het inlezen van de specificatie) op basis van de SoortActie
    _SoortActie_Constructor = {
        _SoortActie_NieuwDoel: (lambda p: ProjectActie_NieuwDoel(p)),
        _SoortActie_Download: (lambda p: ProjectActie_Download(p)),
        _SoortActie_Uitwisseling: (lambda p: ProjectActie_Uitwisseling(p)),
        _SoortActie_Wijziging: (lambda p: ProjectActie_Wijziging(p)),
        _SoortActie_BijwerkenUitgangssituatie: (lambda p: ProjectActie_BijwerkenUitgangssituatie(p)),
        _SoortActie_Publicatie: (lambda p: ProjectActie_Publicatie(p))
    }


#----------------------------------------------------------------------
# Actie: Nieuw doel
#----------------------------------------------------------------------
class ProjectActie_NieuwDoel (ProjectActie):

    def __init__ (self, project):
        """Maak een specificatie van de actie om een nieuwe branch te maken.

        Argumenten:

        project Project  Project waarvoor de actie is gespecificeerd
        """
        super().__init__(project)
        self.SoortActie = ProjectActie._SoortActie_NieuwDoel
        # Nieuw doel. 
        # Instantie van Doel
        self.Doel = None
        # Doel dat de basisversie voor dit doel levert
        # Instantie van Doel
        self.GebaseerdOp_Doel = None
        self._GebaseerdOp_Doel = "Uitgangssituatie" # Naam in specificatie
        self._GebaseerdOp_Doel_Optioneel = True
        # Geldig-op datum van de regelgeving waarop de branch is gebaseerd
        self.GebaseerdOp_GeldigOp = None
        self._GebaseerdOp_GeldigOp = "Uitgangssituatie" # Naam in specificatie
        self._GebaseerdOp_GeldigOp_Optioneel = True

#----------------------------------------------------------------------
# Actie: Download
#----------------------------------------------------------------------
class ProjectActie_Download (ProjectActie):

    def __init__ (self, project):
        """Maak een specificatie van de actie om een nieuwe branch te maken op basis 
        van een gedownloade versie van geldende regelgeving.

        Argumenten:

        project Project  Project waarvoor de actie is gespecificeerd
        """
        super().__init__(project)
        self.SoortActie = ProjectActie._SoortActie_Download
        self._IsUitwisseling = True
        # Nieuw doel. 
        # Instantie van Doel
        self.Doel = None
        # Geldig-op datum van de regelgeving waarop de branch is gebaseerd
        self.GebaseerdOp_GeldigOp = None
        self._GebaseerdOp_GeldigOp = "GeldigOp" # Naam in specificatie

#----------------------------------------------------------------------
# Actie: Wijziging
#----------------------------------------------------------------------
class ProjectActie_Wijziging (ProjectActie):

    def __init__ (self, project):
        """Maak een specificatie van de actie om de inhoud van een branch te wijzigen.

        Argumenten:

        project Project  Project waarvoor de actie is gespecificeerd
        """
        super().__init__(project)
        self.SoortActie = ProjectActie._SoortActie_Wijziging
        # Doel waarvoor de instrumentversies aangepast worden. 
        # Instantie van Doel
        self.Doel = None
        # De instrumentversies voor alle instrumenten in de branch na de wijziging.
        # Key = workId
        self.Instrumentversies : Dict[str,Instrumentversie] = {}
        # De waarde van de juridischWerkendVanaf tijdstempel, of None als die niet opgegeven is, of '-' als die niet meer bekend is
        self.JuridischWerkendVanaf = None
        # De waarde van de geldigVanaf tijdstempel, of None als die niet opgegeven is, of '-' als die niet meer bekend is.
        self.GeldigVanaf = None

#----------------------------------------------------------------------
# Actie: Uitwisseling
#----------------------------------------------------------------------
class ProjectActie_Uitwisseling (ProjectActie):

    def __init__ (self, project):
        """Maak een specificatie van de actie om de inhoud van een branch uit te wisselen 
        tussen adviesbureau en bevoegd gezag.

        Argumenten:

        project Project  Project waarvoor de actie is gespecificeerd
        """
        super().__init__(project)
        self.SoortActie = ProjectActie._SoortActie_Uitwisseling
        self._IsUitwisseling = True
        # Doel waarvoor de gegevens uitgewisseld worden. 
        # Instantie van Doel
        self.Doel = None

#----------------------------------------------------------------------
# Actie: BijwerkenUitgangssituatie
#----------------------------------------------------------------------
class ProjectActie_BijwerkenUitgangssituatie (ProjectActie):

    def __init__ (self, project):
        """Maak een specificatie van de actie om wijzigingen in de regelgeving
        over te nemen in de instrumentversies van een branch.

        Argumenten:

        project Project  Project waarvoor de actie is gespecificeerd
        """
        super().__init__(project)
        self.SoortActie = ProjectActie._SoortActie_BijwerkenUitgangssituatie
        # Doel waarvoor de instrumentversies aangepast worden. 
        # Instantie van Doel
        self.Doel = None
        # Geldig-op datum van de regelgeving waarvan de wijzigingen overgenomen moeten worden
        self.GebaseerdOp_GeldigOp = None
        self._GebaseerdOp_GeldigOp = "GeldigOp" # Naam in specificatie
        self._GebaseerdOp_GeldigOp_Optioneel = True # Optioneel, validatie wordt gedaan bij uitvoeren actie
        # De instrumentversies voor alle instrumenten in de branch na het overnemen van de wijziging.
        # Key = workId
        self.Instrumentversies : Dict[str,Instrumentversie] = {}

#----------------------------------------------------------------------
# Actie: Publicatie
#----------------------------------------------------------------------
class ProjectActie_Publicatie (ProjectActie):

    def __init__ (self, project):
        """Maak een specificatie van de actie om een besluit te publiceren.

        Argumenten:

        project Project  Project waarvoor de actie is gespecificeerd
        """
        super().__init__(project)
        self.SoortActie = ProjectActie._SoortActie_Publicatie
        self._IsUitwisseling = True
        # Doelen in het besluit waar de rechter een uitspraak over gedaan heeft.
        # Lijst met instanties van Doel
        self.Doelen = []
        # De soort publicatie; moet een van de _SoortPublicatie_* waarden zijn
        self.SoortPublicatie = None

    _SoortPublicatie_Consultatie = 'Consultatie' # Consolidatie, d.w.z. wel publicatie maar geen officiële publicatie.
    _SoortPublicatie_Voorontwerp = 'Voorontwerp' # Voorontwerp, d.w.z. wel publicatie maar geen officiële publicatie.
    _SoortPublicatie_Ontwerpbesluit = 'Ontwerpbesluit' # Publicatie van een ontwerpbesluit
    _SoortPublicatie_Besluit = 'Besluit' # Bekendmaking van het vastgestelde besluit
    _SoortPublicatie_Rectificatie = 'Rectificatie' # Rectificatie van het gepubliceerde besluit
    _SoortPublicatie_MededelingUitspraakRechter = 'Mededeling uitspraak rechter' # Mededeling van de uitspraak van de rechter in beroep
    _SoortPublicatie_Revisie = 'Revisie' # Revisie van een geconsolideerd instrument

    # Alle mogelijke waarden
    _SoortPublicaties = [
        _SoortPublicatie_Consultatie,
        _SoortPublicatie_Voorontwerp,
        _SoortPublicatie_Ontwerpbesluit,
        _SoortPublicatie_Besluit,
        _SoortPublicatie_Rectificatie,
        _SoortPublicatie_MededelingUitspraakRechter,
        _SoortPublicatie_Revisie
    ]
    # Alle publicaties waarbij consolidatie-informatie uitgewisseld wordt
    _SoortPublicatie_ViaSTOPVersiebeheer = [
        _SoortPublicatie_Ontwerpbesluit,
        _SoortPublicatie_Besluit,
        _SoortPublicatie_Rectificatie,
        _SoortPublicatie_MededelingUitspraakRechter,
        _SoortPublicatie_Revisie
    ]
    # Alle publicaties die geen concept of ontwerp zijn
    _SoortPublicatie_GeenConceptOfOntwerp = [
        _SoortPublicatie_Besluit,
        _SoortPublicatie_Rectificatie,
        _SoortPublicatie_MededelingUitspraakRechter,
        _SoortPublicatie_Revisie
    ]

#----------------------------------------------------------------------
# Instrumentversie: beoogde versie voor een instrument, inclusief
#                   onbekende versie en ingetrokken/juridisch uitgewerkt.
#----------------------------------------------------------------------
class Instrumentversie:

    def __init__ (self):
        # ExpressionId van de instrumentversie
        # Als de ExpressionId None is en IsJuridischUitgewerkt False, dan gaat het om een onbekende versie
        self.ExpressionId = None
        # Geeft aan of het instrument juridisch uitgewerkt is (dus ingetrokken is/moet worden)
        self.IsJuridischUitgewerkt = False
        # Geeft aan of een wijziging van het instrument geen onderdeel meer is van het eindbeeld voor het doel
        self.IsTeruggetrokken = False

#----------------------------------------------------------------------
# Project: representeert een enkel project waarin aan nieuwe versie(s)
#          voor een of meer instrumenten gewerkt wordt, voor één of meer
#          doelen.
#----------------------------------------------------------------------
class Project:

    def __init__ (self):
        # Code/zeer korte naam voor het project, te gebruiken voor weergave
        self.Code = None
        # Beschrijving van het project (optioneel)
        self.Beschrijving = None
        # De (relevante) acties die in het project worden uitgevoerd
        self.Acties = []
        # Geeft aan of de specificatie van het project valide is
        self._IsValide = True

#======================================================================
#
# Inlezen specificatie
#
#======================================================================
    @staticmethod
    def LeesJson (log, pad, data):
        """Lees de inhoud van de module uit het json bestand.
        
        Argumenten:
        log Meldingen  Verzameling van meldingen
        pad string  Pad van het JSON bestand
        data string  JSON specificatie van het project
        
        Resultaat van de methode is een Project instantie, of None als de JSON 
        geen specificatie van een project is
        """
        if not "Project" in data:
            return None
        project = Project()

        project.Code = data["Project"]
        if not isinstance (project.Code, str):
            log.Fout ("Bestand '" + pad + "': 'Project' moet als waarde een string hebben")
            project._IsValide = False

        if "Beschrijving" in data:
            if not isinstance (data["Beschrijving"], str):
                log.Fout ("Bestand '" + pad + "': 'Beschrijving' moet als waarde een string hebben")
                project._IsValide = False
            else:
                project.Beschrijving = data["Beschrijving"]

        if not "Acties" in data or not isinstance (data["Acties"], list) or len (data["Acties"]) == 0:
            log.Fout ("Bestand '" + pad + "': 'Acties' moet een niet-leeg array zijn")
            project._IsValide = False
        else:
            alleUitgevoerdOp = []
            for actieSpec in data["Acties"]:
                if not isinstance (actieSpec, dict):
                    log.Fout ("Bestand '" + pad + "': element van 'Acties' moet een object zijn")
                    project._IsValide = False
                    continue

                if not "SoortActie" in actieSpec or not isinstance (actieSpec["SoortActie"], str):
                    log.Fout ("Bestand '" + pad + "': 'SoortActie' moet bij elke actie voorkomen en als waarde een string hebben")
                    project._IsValide = False
                    continue
                if not actieSpec["SoortActie"] in ProjectActie._SoortActie_Constructor:
                    log.Fout ("Bestand '" + pad + "': '" + actieSpec["SoortActie"] + "' is geen toegestane waarde voor 'SoortActie'")
                    project._IsValide = False
                    continue

                actie = ProjectActie._SoortActie_Constructor[actieSpec["SoortActie"]] (project)

                if not "UitgevoerdOp" in actieSpec:
                    log.Fout ("Bestand '" + pad + "': 'UitgevoerdOp' moet bij elke actie (behalve '" + ProjectActie._SoortActie_Download + "') voorkomen")
                    project._IsValide = False
                else:
                    actie.UitgevoerdOp = actieSpec["UitgevoerdOp"]
                    if not isinstance (actie.UitgevoerdOp, str):
                        log.Fout ("Bestand '" + pad + "': 'UitgevoerdOp' moet een string zijn")
                        project._IsValide = False
                    elif not ConsolidatieInformatie.ValideerGemaaktOp (log, pad, actie.UitgevoerdOp, 'UitgevoerdOp'):
                        project._IsValide = False
                    elif actie.UitgevoerdOp in alleUitgevoerdOp:
                        log.Fout ("Bestand '" + pad + "': tijdstip van uitvoering '" + actie.UitgevoerdOp + "' komt meerdere keren voor")
                        project._IsValide = False
                    else:
                        alleUitgevoerdOp.append (actie.UitgevoerdOp)

                if not "Beschrijving" in actieSpec or not isinstance (actieSpec["Beschrijving"], str):
                    log.Fout ("Bestand '" + pad + "': 'Beschrijving' is verplicht voor een actie en moet als waarde een string hebben")
                    project._IsValide = False
                else:
                    actie.Beschrijving = actieSpec["Beschrijving"]

                if hasattr (actie, "Doel"):
                    if not "Doel" in actieSpec:
                        log.Fout ("Bestand '" + pad + "': 'Doel' is verplicht voor actie: " + actie.SoortActie)
                        project._IsValide = False
                    elif not isinstance (actieSpec["Doel"], str):
                        log.Fout ("Bestand '" + pad + "': 'Doel' moet als waarde een string hebben")
                        project._IsValide = False
                    else:
                        actie.Doel = Doel.DoelInstantie (actieSpec["Doel"])
                elif hasattr (actie, "Doelen"):
                    if not "Doelen" in actieSpec:
                        log.Fout ("Bestand '" + pad + "': 'Doelen' is verplicht voor actie: " + actie.SoortActie)
                        project._IsValide = False
                    elif not isinstance (actieSpec["Doelen"], list) or len (actieSpec["Doelen"]) == 0:
                        log.Fout ("Bestand '" + pad + "': 'Doelen' moet als waarde een array van strings hebben")
                        project._IsValide = False
                    else:
                        for doelSpec in actieSpec["Doelen"]:
                            if not isinstance (doelSpec, str):
                                log.Fout ("Bestand '" + pad + "': 'Doelen' moet als waarde een array van strings hebben")
                                project._IsValide = False
                            else:
                                doel = Doel.DoelInstantie (doelSpec)
                                if doel in actie.Doelen:
                                    log.Fout ("Bestand '" + pad + "': '" + doelSpec + "' komt meerdere keren voor in 'Doelen'")
                                    project._IsValide = False
                                else:
                                    actie.Doelen.append (doel)

                if hasattr (actie, "GebaseerdOp_GeldigOp"):
                    if not actie._GebaseerdOp_GeldigOp in actieSpec:
                        if hasattr (actie, "_GebaseerdOp_GeldigOp_Optioneel") and actie._GebaseerdOp_GeldigOp_Optioneel:
                            pass
                        elif not hasattr (actie, "GebaseerdOp_Doel"): # Bij sommige acties is er keuze tussen een datum en een doel
                            log.Fout ("Bestand '" + pad + "': '" + actie._GebaseerdOp_GeldigOp + "' is verplicht voor actie: " + actie.SoortActie)
                            project._IsValide = False
                    elif not isinstance (actieSpec[actie._GebaseerdOp_GeldigOp], str):
                        if not hasattr (actie, "GebaseerdOp_Doel"):
                            log.Fout ("Bestand '" + pad + "': '" + actie._GebaseerdOp_GeldigOp + "' moet als waarde een string hebben")
                            project._IsValide = False
                    elif not hasattr (actie, "GebaseerdOp_Doel") or len (actieSpec[actie._GebaseerdOp_GeldigOp]) == 10:
                        if not ConsolidatieInformatie.ValideerDatum (log, pad, actie._GebaseerdOp_GeldigOp, actieSpec[actie._GebaseerdOp_GeldigOp]):
                            project._IsValide = False
                        else:
                            actie.GebaseerdOp_GeldigOp = actieSpec[actie._GebaseerdOp_GeldigOp]

                if hasattr (actie, "GebaseerdOp_Doel"):
                    if not hasattr (actie, "GebaseerdOp_GeldigOp") or actie.GebaseerdOp_GeldigOp is None:
                        if not actie._GebaseerdOp_Doel in actieSpec:
                            if not hasattr (actie, "_GebaseerdOp_Doel_Optioneel") or not actie._GebaseerdOp_Doel_Optioneel:
                                log.Fout ("Bestand '" + pad + "': '" + actie._GebaseerdOp_Doel + "' is verplicht voor actie: " + actie.SoortActie)
                                project._IsValide = False
                        elif not isinstance (actieSpec[actie._GebaseerdOp_Doel], str):
                            log.Fout ("Bestand '" + pad + "': '" + actie._GebaseerdOp_Doel + "' moet als waarde een string hebben")
                            project._IsValide = False
                        else:
                            actie.GebaseerdOp_Doel = Doel.DoelInstantie (actieSpec[actie._GebaseerdOp_Doel])

                if hasattr (actie, "Instrumentversies"):
                    if "Instrumentversies" in actieSpec:
                        if not isinstance (actieSpec["Instrumentversies"], list):
                            log.Fout ("Bestand '" + pad + "': 'Instrumentversies' moet een array zijn voor actie: " + actie.SoortActie)
                            project._IsValide = False
                        else:
                            for versieSpec in actieSpec["Instrumentversies"]:
                                if not isinstance (versieSpec, dict) or len (versieSpec) != 1:
                                    log.Fout ("Bestand '" + pad + "': element van 'Instrumentversies' moet een object met één kenmerk ('Instrumentversie', 'JuridischUitgewerkt', 'Teruggetrokkens') zijn")
                                    project._IsValide = False
                                    continue

                                if "Instrumentversie" in versieSpec:
                                    if not isinstance (versieSpec["Instrumentversie"], str):
                                        log.Fout ("Bestand '" + pad + "': element 'Instrumentversie' in 'Instrumentversies' moet als waarde een string hebben")
                                        project._IsValide = False
                                        continue
                                    if (not Naamgeving.IsRegeling (versieSpec["Instrumentversie"]) and not Naamgeving.IsInformatieobject (versieSpec["Instrumentversie"])) or not Naamgeving.IsExpression (versieSpec["Instrumentversie"]):
                                        log.Fout ("Bestand '" + pad + "': 'Instrumentversie' in 'Instrumentversies' moet als waarde een expression-identificatie van een regeling of informatieobject hebben, niet '" + versieSpec["Instrumentversie"] + "'")
                                        project._IsValide = False
                                        continue
                                    versie = Instrumentversie ()
                                    versie.ExpressionId = versieSpec["Instrumentversie"]
                                    workId = Naamgeving.WorkVan (versie.ExpressionId)
                                elif "OnbekendeVersie" in versieSpec:
                                    if not isinstance (versieSpec["OnbekendeVersie"], str):
                                        log.Fout ("Bestand '" + pad + "': element 'OnbekendeVersie' in 'Instrumentversies' moet als waarde een string hebben")
                                        project._IsValide = False
                                        continue
                                    if (not Naamgeving.IsRegeling (versieSpec["OnbekendeVersie"]) and not Naamgeving.IsInformatieobject (versieSpec["OnbekendeVersie"])) or Naamgeving.IsExpression (versieSpec["OnbekendeVersie"]):
                                        log.Fout ("Bestand '" + pad + "': 'OnbekendeVersie' in 'Instrumentversies' moet als waarde een work-identificatie van een regeling of informatieobject hebben, niet '" + versieSpec["OnbekendeVersie"] + "'")
                                        project._IsValide = False
                                        continue
                                    versie = Instrumentversie ()
                                    workId = versieSpec["OnbekendeVersie"]
                                elif "JuridischUitgewerkt" in versieSpec:
                                    if not isinstance (versieSpec["JuridischUitgewerkt"], str):
                                        log.Fout ("Bestand '" + pad + "': 'JuridischUitgewerkt' in 'Instrumentversies' moet als waarde een string hebben")
                                        project._IsValide = False
                                        continue
                                    if (not Naamgeving.IsRegeling (versieSpec["JuridischUitgewerkt"]) and not Naamgeving.IsInformatieobject (versieSpec["JuridischUitgewerkt"])) or Naamgeving.IsExpression (versieSpec["JuridischUitgewerkt"]):
                                        log.Fout ("Bestand '" + pad + "': 'JuridischUitgewerkt' moet als waarde een work-identificatie hebben, niet '" + versieSpec["JuridischUitgewerkt"] + "'")
                                        project._IsValide = False
                                        continue
                                    versie = Instrumentversie ()
                                    versie.IsJuridischUitgewerkt = True
                                    workId = versieSpec["JuridischUitgewerkt"]
                                elif "Teruggetrokken" in versieSpec:
                                    if not isinstance (versieSpec["Teruggetrokken"], str):
                                        log.Fout ("Bestand '" + pad + "': 'Teruggetrokken' in 'Instrumentversies' moet als waarde een string hebben")
                                        project._IsValide = False
                                        continue
                                    if (not Naamgeving.IsRegeling (versieSpec["Teruggetrokken"]) and not Naamgeving.IsInformatieobject (versieSpec["Teruggetrokken"])) or Naamgeving.IsExpression (versieSpec["Teruggetrokken"]):
                                        log.Fout ("Bestand '" + pad + "': 'Teruggetrokken' moet als waarde een work-identificatie hebben, niet '" + versieSpec["Teruggetrokken"] + "'")
                                        project._IsValide = False
                                        continue
                                    versie = Instrumentversie ()
                                    versie.IsTeruggetrokken = True
                                    workId = versieSpec["Teruggetrokken"]
                                else:
                                    log.Fout ("Bestand '" + pad + "': element van 'Instrumentversies' moet een object met één kenmerk ('Instrumentversie', 'JuridischUitgewerkt', 'Teruggetrokkens') zijn")
                                    project._IsValide = False
                                    continue

                                if workId in actie.Instrumentversies:
                                    log.Fout ("Bestand '" + pad + "': 'Instrumentversies' bevat twee specificaties voor het work " + workId)
                                    project._IsValide = False
                                else:
                                    actie.Instrumentversies[workId] = versie


                if hasattr (actie, "JuridischWerkendVanaf"):
                    if "JuridischWerkendVanaf" in actieSpec:
                        if not isinstance (actieSpec["JuridischWerkendVanaf"], str):
                            log.Fout ("Bestand '" + pad + "': 'JuridischWerkendVanaf' moet als waarde een string hebben")
                            project._IsValide = False
                        elif actieSpec["JuridischWerkendVanaf"] in ['-', '?']:
                            actie.JuridischWerkendVanaf = '-'
                        elif not ConsolidatieInformatie.ValideerDatum (log, pad, 'JuridischWerkendVanaf', actieSpec["JuridischWerkendVanaf"]):
                            project._IsValide = False
                        else:
                            actie.JuridischWerkendVanaf = actieSpec["JuridischWerkendVanaf"]

                if hasattr (actie, "GeldigVanaf"):
                    if "GeldigVanaf" in actieSpec:
                        if not isinstance (actieSpec["GeldigVanaf"], str):
                            log.Fout ("Bestand '" + pad + "': 'GeldigVanaf' moet als waarde een string hebben")
                            project._IsValide = False
                        elif actieSpec["GeldigVanaf"] in ['-', '?']:
                            actie.GeldigVanaf = '-'
                        elif not ConsolidatieInformatie.ValideerDatum (log, pad, 'GeldigVanaf', actieSpec["GeldigVanaf"]):
                            project._IsValide = False
                        else:
                            actie.GeldigVanaf = actieSpec["GeldigVanaf"]

                if hasattr (actie, "SoortPublicatie"):
                    if not "SoortPublicatie" in actieSpec:
                        log.Fout ("Bestand '" + pad + "': 'SoortPublicatie' is verplicht voor actie: " + actie.SoortActie)
                        project._IsValide = False
                    elif not isinstance (actieSpec["SoortPublicatie"], str):
                        log.Fout ("Bestand '" + pad + "': 'SoortPublicatie' moet als waarde een string zijn")
                        project._IsValide = False
                    elif not actieSpec["SoortPublicatie"] in ProjectActie_Publicatie._SoortPublicaties:
                        log.Fout ("Bestand '" + pad + "': '" + actieSpec["SoortPublicatie"] + "' is geen toegestane waarde voor 'SoortPublicatie'")
                        project._IsValide = False
                    else:
                        actie.SoortPublicatie = actieSpec["SoortPublicatie"]

        return project
