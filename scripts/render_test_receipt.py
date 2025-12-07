import sys
import pathlib
repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from utils.quotation_utils import render_quotation_html
from utils.settings import load_settings

html = render_quotation_html({
    'company_name': load_settings().get('company_name', 'Newton Smart Home'),
    'receipt_number': 'R-PREVIEW-1',
    'receipt_date': '2025-12-08',
    'client_name': 'Preview Client',
    'client_phone': '+971 50 123 4567',
    'client_location': 'Dubai - Marina',
    'amount': 250.0,
    'previous_paid': 0.0,
    'balance': 250.0,
}, template_name='newton_receipt_A4.html')

open('data/exports/test_receipt.html','w',encoding='utf-8').write(html)
print('Wrote data/exports/test_receipt.html')
