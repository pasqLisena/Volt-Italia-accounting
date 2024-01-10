import yaml

with open('./config.yaml') as f:
    config = yaml.safe_load(f)

PRESIDENTS = config['presidents']
MEMBERSHIP_FEES = config['membership_fees']

def is_tesseramento(x, detail_name, amount_name):
    det = x[detail_name].lower()
    for t in ['tesseramento', 'tessera', 'rinnovo', 'iscrizione', 'adesione', 'quota over', 'quota under',
              'annual fees']:
        if t in det:
            return True
    for t in ['quota']:
        if t in det:
            amount = to_number(x[amount_name])
            return match_membership_fee(amount)
    return False


def is_donation(detail_txt):
    det = detail_txt.lower()
    for t in ['erogazione liberale', 'donazione']:
        if t in det:
            return True
    return False


def to_number(s):
    return float(s.replace(',', '.'))

def match_membership_fee(amount):
    for x in MEMBERSHIP_FEES:
        if x == amount:
            return True

    return False
