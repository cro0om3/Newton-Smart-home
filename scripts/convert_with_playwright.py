import http.server
import socketserver
import threading
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def _serve_dir_once(directory, server_holder):
    os.chdir(directory)
    handler = QuietHandler
    httpd = socketserver.TCPServer(('127.0.0.1', 0), handler)
    server_holder.append(httpd)
    httpd.serve_forever()


def convert_html_file(input_path: Path):
    if not input_path.exists():
        raise SystemExit(f'Missing HTML: {input_path}')

    serve_dir = str(input_path.parent)
    server_holder = []
    t = threading.Thread(target=_serve_dir_once, args=(serve_dir, server_holder), daemon=True)
    t.start()

    # Wait briefly for server to start
    import time
    for _ in range(20):
        if server_holder:
            break
        time.sleep(0.05)
    if not server_holder:
        raise RuntimeError('Failed to start HTTP server')

    httpd = server_holder[0]
    port = httpd.server_address[1]
    url = f'http://127.0.0.1:{port}/{input_path.name}'
    print('Serving', url)

    out_base = input_path.stem
    pdf_out = input_path.parent / f"{out_base}.pdf"
    png_out = input_path.parent / f"{out_base}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # allow optional env hints for viewport size
        vw = int(os.environ.get('PLAYWRIGHT_PDF_WIDTH', '0'))
        vh = int(os.environ.get('PLAYWRIGHT_PDF_HEIGHT', '0'))
        if vw and vh:
            page = browser.new_page(viewport={ 'width': vw, 'height': vh })
        else:
            page = browser.new_page()
        page.goto(url, wait_until='networkidle')
        # If explicit pixel size provided via env, use px dimensions for PDF
        if vw and vh:
            page.pdf(path=str(pdf_out), width=f'{vw}px', height=f'{vh}px', print_background=True)
        else:
            page.pdf(path=str(pdf_out), format='A4', print_background=True)
        page.screenshot(path=str(png_out), full_page=True)
        browser.close()

    print('Wrote', pdf_out)
    print('Wrote', png_out)


if __name__ == '__main__':
    # Accept an optional input HTML path argument
    if len(sys.argv) > 1:
        input_arg = sys.argv[1]
        html_file = Path(input_arg)
        if not html_file.is_absolute():
            html_file = (BASE / html_file).resolve()
    else:
        html_file = (BASE / 'data' / 'exports' / 'test_quotation.html').resolve()

    # Optional CLI width/height overrides (pixels)
    if len(sys.argv) > 2:
        try:
            os.environ['PLAYWRIGHT_PDF_WIDTH'] = str(int(sys.argv[2]))
        except Exception:
            pass
    if len(sys.argv) > 3:
        try:
            os.environ['PLAYWRIGHT_PDF_HEIGHT'] = str(int(sys.argv[3]))
        except Exception:
            pass

    convert_html_file(html_file)
