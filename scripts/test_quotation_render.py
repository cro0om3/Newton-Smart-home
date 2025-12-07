import sys
from pathlib import Path

# Add project root to sys.path to allow importing `utils` when running this script
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.quotation_utils import render_quotation_html
from utils.settings import load_settings
from datetime import datetime
from pathlib import Path

ctx = {
    'company_name': load_settings().get('company_name', 'Newton Smart Home'),
    'quotation_number': 'QT-TEST-001',
    'date': datetime.today().strftime('%Y-%m-%d'),
    'customer': {'name': 'Test Customer', 'address': '123 Test Street'},
    'items': [
        {'Description': 'Test product A', 'Qty': 2, 'Unit Price (AED)': 100, 'Line Total (AED)': 200},
        {'Description': 'Test product B', 'Qty': 1, 'Unit Price (AED)': 300, 'Line Total (AED)': 300},
    ],
    'subtotal': 500,
    'tax': 0,
    'total': 500,
    'rtl': False,
}

html = render_quotation_html(ctx, template_name="newton_quotation_A4.html")
out_dir = Path('data') / 'exports'
out_dir.mkdir(parents=True, exist_ok=True)
with open(out_dir / 'test_quotation.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Wrote data/exports/test_quotation.html')
