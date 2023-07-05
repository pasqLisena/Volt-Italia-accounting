import pandas as pd

from .utils import to_number


def process(input_file, account_name):
    df = pd.read_excel(input_file).fillna('')
    records = []
    for i, x in df.iterrows():
        date = x.get('Fully paid at', x.get('Paid at')).split(' ')[0]

        category = 'Tesseramento'
        subcategory = 'Quote associative'

        actor = x['Full Name']
        amount = x['Amount Paid']

        records.append({
            'date': date.replace('/', '-'),
            'category': category,
            'subcategory': subcategory,
            'actor': actor,
            'original_category': x['Payment Method'],
            'original_note': x['Invoice Number'],
            'original_detail': '',
            'amount': amount,
            'account': account_name
        })

    return records
