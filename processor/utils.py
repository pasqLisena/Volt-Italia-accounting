PRESIDENTS = ['Eliana Canavesio', 'Gianluca Guerra']

def is_tesseramento(x, detail_name, amount_name):
    det = x[detail_name].lower()
    for t in ['tesseramento', 'tessera', 'rinnovo', 'iscrizione', 'adesione', 'quota over', 'quota under',
              'annual fees']:
        if t in det:
            return True
    for t in ['quota']:
        if t in det:
            amount = to_number(x[amount_name])
            return amount == 30 or amount == 20
    return False


def is_donazione(detail_txt):
    det = detail_txt.lower()
    for t in ['erogazione liberale', 'donazione']:
        if t in det:
            return True
    return False


def to_number(s):
    return float(s.replace(',', '.'))