import re
import pandas as pd
from .utils import to_number, is_tesseramento, is_donation, PRESIDENTS

REGEX_BONIFICO_ENTRATA = r'(?i)Bonifico (?:Istantaneo )?(?:A Vostro Favore )?Disposto Da:? (?:MITT\.: )(.+)(?: BENEF\.:.+)'
REGEX_BONIFICO_USCITA = r'(?i)(?:Addebito Diretto |Bonifico (?:Istantaneo )?)(?:Da Voi )Disposto A Favore Di:? ?(.+)'


def process(input_file, account_name):
    h = 29 if account_name.startswith('Carta') else 27
    df = pd.read_excel(input_file, header=h, dtype=str)

    starting_balance = 0
    ending_balance = 0
    records = []
    for i, x in df.iterrows():
        date = x['Data contabile']
        note = x.get('Descrizione')
        amount = x.get('Accrediti')
        if not amount or pd.isna(amount):
            amount = x.get('Addebiti')
            if not str(amount).startswith('-'):
                # for the cards the outcomes are positive!
                amount = '-' + str(amount)
        try:
            amount = to_number(amount)
        except:
            continue

        if pd.isna(date):
            if note == 'Saldo contabile iniziale in Euro':
                starting_balance = amount
                records.append({
                    'date': '-1',
                    'category': '********',
                    'subcategory': "SALDO INIZIALE",
                    'amount': starting_balance,
                    'account': account_name
                })

            elif note == 'Saldo contabile finale in Euro':
                ending_balance = amount
                records.append({
                    'date': '2028',
                    'category': '********',
                    'subcategory': "SALDO FINALE",
                    'amount': ending_balance,
                    'account': account_name
                })
            print(amount)
            continue
        date = '-'.join(reversed(str(date).split(' ')[0].split('/')))

        actor = ''

        category = ''
        subcategory = ''
        descr = x.get('Descrizione estesa')
        if not descr or pd.isna(descr):
            if not pd.isna(note):
                descr = note
            else:
                descr = ''

        z = re.search(REGEX_BONIFICO_ENTRATA, descr)
        if z:
            actor = z.group(1)
            if is_tesseramento(x, 'Descrizione estesa', 'Accrediti'):
                category = 'Tesseramento'
                subcategory = 'Quote associative'
        else:
            z = re.search(REGEX_BONIFICO_USCITA, descr)
            if z:
                actor = z.group(1)

        if descr.startswith('Facebk '):
            actor = 'Facebook'
            category = 'Servizi'
            subcategory = 'Spese per Comunicazione (Sponsorizzazioni/servizi/tool)'
        elif actor == 'Stripe Technology Europe Ltd' or 'Club Collect' in descr:
            category = 'Giroconti'
            subcategory = 'Sistemi di pagamento'
        elif any(['VODAFONE ITALIA S P A' in descr, 'AMAZON WEB SERVICES EMEA SARL' in descr]):
            category = 'Servizi'
            subcategory = 'Costi IT e Telefonia'
        elif 'World Services Information SAS' in descr:
            category = 'Servizi'
            subcategory = 'Domiciliazione Legale'
        elif note.lower() in ['canone mensile base e servizi aggiuntivi', 'commissioni e spese adue',
                              'imposta di bollo e/c e rendiconto', 'competenze di chiusura',
                              'pagamento adue',
                              'commiss. su beu internet banking', 'commiss. ricarica superflash',
                              'costo ricarica carta prepagata', 'commissione disposizione di bonifico'] \
                or note.lower().startswith('commiss. ricarica superflash') \
                or note.lower().startswith('commissione') \
                or descr.lower().startswith('canone mensile') \
                or note.lower().startswith('interessi debitori conteggiati'):
            category = 'Servizi'
            subcategory = 'Oneri di gestione conti bancari'
        elif note.lower() in ['ricarica', 'ricarica carta prepagata', 'giroconto internet da voi disposto',
                              'disposizione di giroconto'] \
                or 'Ricarica Prepagata' in descr or 'Ricarica Superflash' in descr:
            category = 'Giroconti'
            subcategory = 'Altri conti Volt'
        elif 'rimborso spese' in descr.lower():
            category = 'Rimborsi spese'
            if actor in PRESIDENTS:
                subcategory = 'Presidenti'
        elif is_donation(descr):
            category = 'Donazioni liberali'

        records.append({
            'date': date,
            'category': category,
            'subcategory': subcategory,
            'actor': actor,
            'original_category': x['Descrizione'],
            'original_note': descr,
            'original_detail': '',
            'amount': amount,
            'account': account_name
        })

        if actor == 'Stripe Technology Europe Ltd':
            records.append({
                'date': date,
                'category': category,
                'subcategory': subcategory,
                'actor': actor,
                'original_category': x['Descrizione'],
                'original_note': descr,
                'original_detail': '',
                'amount': -amount,
                'account': 'Stripe'
            })

        if 'ClubCollect' in descr :
            records.append({
                'date': date,
                'category': category,
                'subcategory': subcategory,
                'actor': actor,
                'original_category': x['Descrizione'],
                'original_note': descr,
                'original_detail': '',
                'amount': -amount,
                'account': 'Club Collect'
            })

    return records
