
def stringlower(stringa,posizione_inizio, posizione_fine=None):
    stringa = list(stringa)
    if not posizione_fine :
        stringa[posizione_inizio] = stringa[posizione_inizio].lower()
    else: 
        for x in range(posizione_inizio,posizione_fine):
            stringa[x] = stringa[x].lower()       
    stringa = "".join(stringa)
    return stringa

def stringUPPER(stringa,posizione_inizio, posizione_fine=None):
    stringa = list(stringa)
    if not posizione_fine :
        stringa[posizione_inizio] = stringa[posizione_inizio].upper()
    else: 
        for x in range(posizione_inizio,posizione_fine):
            stringa[x] = stringa[x].upper()       
    stringa = "".join(stringa)
    return stringa
