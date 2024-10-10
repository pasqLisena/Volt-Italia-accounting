import pandas as pd


def process(input_file, account_name):
    df = pd.read_excel(input_file).fillna('')
    records = []
    for i, x in df.iterrows():
        if x[('Payment Method')] == "External Payment":
            continue
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


def process_charges(input_file, account_name):
    df = pd.read_excel(input_file).fillna('')
    records = []
    for i, x in df.iterrows():
        date = x.get('Inserted On', x.get('Validated On'))

        actor = 'ClubCollect'
        category = 'Servizi'
        subcategory = 'Commissione sistemi di pagamento'

        amount = x['Amount']

        records.append({
            'date': date.replace('/', '-'),
            'category': category,
            'subcategory': subcategory,
            'actor': actor,
            'original_category': 'Company Charge',
            'original_note': x['Reference'],
            'original_detail': x['Invoice Number'],
            'amount': -amount,
            'account': account_name
        })

    return records
