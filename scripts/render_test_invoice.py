import sys
import pathlib
repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from utils.quotation_utils import render_quotation_html
from utils.settings import load_settings
import pandas as pd
catalog = pd.read_excel('data/products.xlsx')
# build a sample invoice using first two products
items = []
for i,r in catalog.head(2).iterrows():
    items.append({
        'description': r.get('Description') or r.get('Device'),
        'qty': 1,
        'unit_price': float(r.get('UnitPrice') or 0),
        'total': float(r.get('UnitPrice') or 0),
        'warranty': r.get('Warranty') or '',
        'image': r.get('ImagePath') if not pd.isna(r.get('ImagePath')) else (r.get('ImageBase64') if not pd.isna(r.get('ImageBase64')) else None)
    })
html = render_quotation_html({
    'company_name': load_settings().get('company_name','Newton Smart Home'),
    'quotation_number': 'INV-PREVIEW-1',
    'quotation_date': '2025-12-08',
    'client_name': 'Preview Client',
    'items': items,
    'subtotal': sum(i['total'] for i in items),
    'Installation': 150.0,
    'total_amount': sum(i['total'] for i in items) + 150.0,
}, template_name='newton_invoice_A4.html')
open('data/exports/test_invoice.html','w',encoding='utf-8').write(html)
print('Wrote data/exports/test_invoice.html')
