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

# --- Auto-export PDF/PNG using Playwright ---
try:
    from playwright.sync_api import sync_playwright
    import threading
    import http.server
    import socketserver

    # serve the exports directory briefly so Playwright can load the HTML
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    def _serve(dirpath, port=8008):
        import os
        os.chdir(dirpath)
        with socketserver.TCPServer(('127.0.0.1', port), QuietHandler) as httpd:
            httpd.serve_forever()

    export_html = out_dir / 'test_quotation.html'
    pdf_out = out_dir / 'test_quotation_auto.pdf'
    png_out = out_dir / 'test_quotation_auto.png'

    t = threading.Thread(target=_serve, args=(str(out_dir), 8008), daemon=True)
    t.start()
    url = f'http://127.0.0.1:8008/{export_html.name}'

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')
        page.pdf(path=str(pdf_out), format='A4', print_background=True)
        page.screenshot(path=str(png_out), full_page=True)
        browser.close()

    print(f'Wrote {pdf_out}')
    print(f'Wrote {png_out}')
except Exception as e:
    print('Auto-export skipped (Playwright error):', e)
