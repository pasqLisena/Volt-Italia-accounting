import pandas as pd

from .utils import to_number, is_tesseramento, match_membership_fee, PRESIDENTS

LORDO = 'Lordo'

def process(input_file, account_name):
    df = pd.read_csv(input_file).fillna('')

    records = []
    for i, x in df.iterrows():
        if x['Tipo'] == 'Conversione di valuta generica':
            continue

        actor = x['Nome']

        if actor == '2Checkout.com, Inc.': # Workaround because this payment appears multiple times
            continue


        date = '-'.join(reversed(x['Data'].split('/')))

        amount = to_number(x[LORDO])
        category = ''
        subcategory = ''

        if is_tesseramento(x, 'Messaggio', LORDO):
            category = 'Tesseramento'
            subcategory = 'Quote associative'
        elif 'portermetrics.com' in x['Oggetto']:
            if amount > 0:
                continue
            actor = 'portermetrics.com'
            category = 'Servizi'
            subcategory = 'Spese per Comunicazione (Sponsorizzazioni/servizi/tool)'
        elif actor == 'Meta Platforms, Inc.':
            category = 'Servizi'
            subcategory = 'Spese per Comunicazione (Sponsorizzazioni/servizi/tool)'
        elif match_membership_fee(amount):
            category = 'Tesseramento'
            subcategory = 'Quote associative (Controlla)'
        elif amount > 0:
            category = 'Donazioni liberali'
            subcategory = 'Persone fisiche (ricorrenti)' if x['Tipo'] == 'Pagamento abbonamento' else 'Persone fisiche'
        elif 'rimborso spese' in x['Messaggio'].lower():
            category = 'Rimborsi spese'
            if actor in PRESIDENTS:
                subcategory = 'Rimborsi spese Presidenti'

        actor = actor + ' ' + x['Indirizzo email mittente']


        records.append({
            'date': date,
            'category': category,
            'subcategory': subcategory,
            'actor': actor,
            'original_category': x['Tipo'],
            'original_note': x['Oggetto'],
            'original_detail': x['Messaggio'],
            'amount': amount,
            'account': account_name
        })

        # add the applied fee as a separate payment
        amount = to_number(x['Tariffa'])
        if amount == 0:
            continue

        actor = 'PayPal'
        category = 'Servizi'
        subcategory = 'Commissione sistemi di pagamento'

        records.append({
            'date': date,
            'category': category,
            'subcategory': subcategory,
            'actor': actor,
            'original_category': x['Tipo'],
            'original_note': x['Oggetto'],
            'original_detail': x['Messaggio'],
            'amount': amount,
            'account': account_name
        })

    return records