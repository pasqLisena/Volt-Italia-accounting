import pandas as pd

from .utils import to_number


def process(input_file, account_name):
    df = pd.read_csv(input_file).fillna('')
    records = []

    to_process = df[df['Status'] == 'Paid'] if 'Status' in df else df[df['Type'] == 'charge']
    for i, x in to_process.iterrows():
        date = x['Created date (UTC)'].split(' ')[0]
        date_split = date.split('-')
        month = date_split[1]

        actor = x['Nome (metadata)'] or x['Customer Email']
        amount = to_number(x['Amount'])
        category = 'Donazioni liberali'
        subcategory = 'Persone fisiche'

        if amount == 30 and month not in ['08', '09', '10']:
            subcategory = 'Tessera sospesa'
        elif amount in [30, 20, 45]:
            subcategory = 'Donazione per AG'

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
        actor = 'Stripe Technology Europe Ltd'
        amount = - (to_number(x['Fee']) + to_number(x['Taxes On Fee']))
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
