#======================================================================
#
# Symbolen die op verschillende plaatsen in de code en in verschillende 
# diagrammen gebruikt worden. Hier opgenomen zodat steeds dezelfde
# symbolen gebruikt worden.
#
#======================================================================

from stop_actueletoestanden import ToestandActueel

class Weergave_Symbolen:

#----------------------------------------------------------------------
# Representatie van consolidatie-informatie
#----------------------------------------------------------------------
    # Instrument_Versie = "&#128195;" # https://unicode-table.com/en/1F4C3/ page
    # Instrument_OnbekendeVersie = "&#128459;" # https://unicode-table.com/en/1F5CB/ empty page
    Instrument_Versie = "&#128214;" # https://unicode-table.com/en/1F4D6/ open book
    Instrument_OnbekendeVersie = "&#128216;" # https://unicode-table.com/en/1F4D8/ closed book
    Instrument_Terugtrekking = "&#128465;" # https://unicode-table.com/en/1F5D1/ waste basket
    Instrument_Intrekking = "&#128683;" # https://unicode-table.com/en/1F6AB/ no entry
    Tijdstempel_Waarde = "&#128344;" # https://unicode-table.com/en/1F558/ clock 9
    Tijdstempel_Terugtrekking = "&#128173;" # https://unicode-table.com/en/1F4AD/ though balloon

    BenoemdeTijdreis = "&#128269;" # Symbool te gebruiken voor een benoemde tijdreis

    Toestand_BekendeInhoud = Instrument_Versie
    Toestand_OnbekendeInhoud = Instrument_OnbekendeVersie
    Toestand_MeerdereVersies = "&#128218;" # https://unicode-table.com/en/1F4DA/ multiple books
    Toestand_Uitgewerkt = "&#128683;" # https://unicode-table.com/en/1F6AB/ no entry
    Toestand_MaterieelUitgewerkt = "&#128123;" # https://unicode-table.com/en/1F47B/ ghost

    Annotatie_Uitwisseling = "&#128391;" # https://unicode-table.com/en/1F587/ paperclips
    Annotatie_BekendeVersie = '<span class="a_symbool_goed">&#x2713;</span>' # ✓
    Annotatie_MeerdereVersies = '<span class="a_symbool_fout">!</span>'
    Annotatie_OnbekendeVersie = '<span class="a_symbool_fout">?</span>'

    @staticmethod
    def ToestandSymbool (toestand : ToestandActueel):
        if not toestand.Instrumentversie is None:
            return Weergave_Symbolen.Toestand_BekendeInhoud
        if len (toestand.TegensprekendeDoelen) > 0:
            return Weergave_Symbolen.Toestand_MeerdereVersies
        return Weergave_Symbolen.Toestand_OnbekendeInhoud
