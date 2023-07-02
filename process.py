import os
import argparse
import pandas as pd

from processor import intesasanpaolo, paypal, stripe, clubcollect

CONTI_ROOT = 'conti'

REGEX_BONIFICO_ENTRATA = r'Bonifico (?:Istantaneo )?(?:A Vostro Favore )?Disposto Da (.+)'
REGEX_BONIFICO_USCITA = r'(?:Addebito Diretto |Bonifico (?:Istantaneo )?)Disposto A Favore Di (.+)'


def run(input_folder, output_folder):
    records = []

    print('Processing Bank Accounts:')
    for x in os.listdir(os.path.join(input_folder, CONTI_ROOT)):
        if not x.endswith('xlsx'):
            continue
        name = x.replace('.xlsx', '').capitalize()
        print('_', name)

        name = name if name.startswith('Carta') else 'c/c ' + name
        res = intesasanpaolo.process(os.path.join(input_folder, CONTI_ROOT, x), name)
        records.extend(res)

    print('Processing Paypal')
    res = paypal.process(os.path.join(input_folder, 'paypal.csv'), 'PayPal')
    records.extend(res)

    print('Processing Stripe')
    res = stripe.process(os.path.join(input_folder, 'stripe.csv'), 'Stripe')
    records.extend(res)

    print('Processing ClubCollect')
    res = clubcollect.process(os.path.join(input_folder, 'club-collect.xlsx'), 'ClubCollect')
    records.extend(res)

    records.sort(key=lambda r: r['date'])

    os.makedirs(output_folder, exist_ok=True)

    rec = pd.DataFrame(records)
    rec.to_csv(os.path.join(output_folder, 'output.csv'), index=False)

    # to accountability
    lines = []
    for x in records:
        direction = 'Entrate ' if x['amount'] > 0 else 'Uscite '

        lines.append({
            'data': x['date'],
            'esecutore': x['actor'],
            'causale': x.get('original_note', x.get('original_detail', x.get('original_category'))),
            'categoria': x['category'],
            'sottocategoria': x['subcategory'],
            direction + x['account']: abs(x['amount'])
        })

    pd.DataFrame(lines).to_csv(os.path.join(output_folder, 'accounting.csv'), index=False)


parser = argparse.ArgumentParser(
    prog='Volt Italia accounting',
    description='This program reads the tabular input coming from Volt Italia\'s bank or payment accounts and transpile them into accounting tables',
    epilog='Author: pasquale.lisena@volteuropa.org')

parser.add_argument('-i', '--input', default='./input/')
parser.add_argument('-o', '--output', default='./output/')
args = parser.parse_args()
run(args.input, args.output)
