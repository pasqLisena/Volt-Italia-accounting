import pandas as pd

from .utils import to_number


def process(input_file, account_name):
    df = pd.read_csv(input_file).fillna('')
    records = []

    for i, x in df[df['Status'] == 'Paid'].iterrows():
        date = x['Created (UTC)'].split(' ')[0]
        date = '-'.join(reversed(date.split('/')))

        actor = 'Stripe Technology Europe Ltd'
        amount = to_number(x['Amount'])
        category = 'Donazioni liberali'
        subcategory = 'Persone fisiche'
        if amount == 30:
            subcategory = 'Tessera sospesa'
        descr = str(x['Description'])

        if 'Tesseramento' in descr:
            category = 'Tesseramento'
            subcategory = 'Quote associative'
        elif descr in ['Subscription update', 'Subscription creation']:
            category = 'Donazioni liberali'
            subcategory = 'Persone fisiche (ricorrenti)'
        elif 'Tessera sospesa' in descr:
            category = 'Donazioni liberali'
            subcategory = 'Tessera sospesa'

        records.append({
            'date': date,
            'category': category,
            'subcategory': subcategory,
            'actor': actor,
            'original_category': x['Status'],
            'original_note': x['Description'],
            'original_detail': x['Customer Description'],
            'amount': amount,
            'account': account_name
        })

        # add the applied fee as a separate payment
        actor = 'Stripe'
        amount = - to_number(x['Fee'])
        category = 'Servizi'
        subcategory = 'Commissione sistemi di pagamento'

        records.append({
            'date': date,
            'category': category,
            'subcategory': subcategory,
            'actor': actor,
            'original_category': x['Status'],
            'original_note': x['Description'],
            'original_detail': x['Customer Description'],
            'amount': amount,
            'account': account_name
        })
    return records