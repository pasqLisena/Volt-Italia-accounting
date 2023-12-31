import pandas as pd

from .utils import to_number, is_tesseramento


def process(input_file, account_name):
    df = pd.read_csv(input_file).fillna('')

    records = []
    for i, x in df.iterrows():
        date = '-'.join(reversed(x['Data'].split('/')))

        actor = x['Nome']
        amount = to_number(x['Lordo'])
        category = ''
        subcategory = ''

        if is_tesseramento(x, 'Messaggio', 'Lordo') or amount == 30.00 or amount == 20.00:
            category = 'Tesseramento'
            subcategory = 'Quote associative'
        elif amount > 0:
            category = 'Donazioni liberali'
            subcategory = 'Persone fisiche (ricorrenti)' if x['Tipo'] == 'Pagamento abbonamento' else 'Persone fisiche'
        elif 'rimborso spese' in x['Messaggio'].lower():
            category = 'Rimborsi spese'
            if actor in ['Eliana Canavesio', 'Gianluca Guerra']:
                subcategory = 'Presidenti'

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