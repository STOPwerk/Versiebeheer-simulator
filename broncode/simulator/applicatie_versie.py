#======================================================================
#
# Configuratie van de applicatie
#
#======================================================================

def Applicatie_versie ():
    """Geef het versienummer van de applicatie"""
    # In een uitgeleverde versie van de simulator bevat de eerste string
    # het specifieke versienummer; het is een van de parameters die
    # bij het uitleveren vervangen wordt
    versie = '2022-11-12 22:22:08'
    if versie == '@@@VER' + 'SIE@@@':
        versie = '- ontwikkelversie'
    return versie
