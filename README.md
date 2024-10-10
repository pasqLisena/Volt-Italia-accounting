# Volt Italia Accounting

This program reads the tabular input coming from Volt Italia's bank or payment accounts and transpile them into accounting tables.

Features:
- automatic conversion from different input format to an harmonized template;
- automatic assignment of categories and subcategories based on string-based rules (regex and similar).

### Dependencies

This code requires a recent version of Python (tested on 3.8+).

For installing the dependencies libraries run the following:

    pip install -r requirements


### How to prepare the input.

In the same folder insert the different tabular inputs.
- subfolder `conti`, include all `.xsls` from Intesa SanPaolo, one for each account. The name of the file should be `<account name>.xlsx` (e.g. `piemonte.xlsx`) or `carta <owner>.xlsx` (e.g. `carta lisena.xlsx`)
- `club-collect.xlsx`
- `paypal.csv`
- `stripe.csv`

### How to run

Run the following
    
    python process.py [-i input_path] [-o output_path]


E.g.

    python process.py -i ./input/ -o ./output/

Author: pasquale.lisena@volteuropa.org