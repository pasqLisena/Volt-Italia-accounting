import os
import pandas as pd

from .utils import to_number


def process(input_file, account_name, lunda_file):
    df = pd.read_csv(input_file).fillna('')
    lunda = None

    if os.path.isfile(lunda_file):
        lunda = pd.read_csv(lunda_file).fillna('')

    records = []

    to_process = df[df['Status'] == 'Paid'] if 'Status' in df else df[df['Type'] == 'charge']
    for i, x in to_process.iterrows():
        date = x['Created date (UTC)'].split(' ')[0]
        date_split = date.split('-')
        month = date_split[1]

        is_recurring = False

        actor = f"{x['Nome (metadata)']} <{x['Customer Email']}>"
        descr = str(x['Description'])
        if not actor:
            y = lunda[lunda['cause_stripe_account_payment_id'] == x['id']].iloc[0]
            actor = f"{y['donor_firstname']} {y['donor_lastname']} <{y['donor_email']}>"
            is_recurring = y['donation_type'] == 'RECURRING'
            descr = y['slug']

        amount = to_number(x['Amount'])
        category = 'Donazioni liberali'
        subcategory = 'Persone fisiche'

        if amount == 30 and month not in ['11', '12']:
            subcategory = 'Tessera sospesa'
        elif amount in [30, 20, 45]:
            subcategory = 'Donazione per AG'


        if 'Tesseramento' in descr:
            category = 'Tesseramento'
            subcategory = 'Quote associative'
        elif descr in ['Subscription update', 'Subscription creation'] or is_recurring:
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
            'original_note': descr,
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
