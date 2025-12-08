from weasyprint import HTML
from pdf2image import convert_from_path
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT = os.path.join(BASE, 'data', 'exports', 'test_quotation.html')
PDF_OUT = os.path.join(BASE, 'data', 'exports', 'test_quotation.pdf')
PNG_OUT = os.path.join(BASE, 'data', 'exports', 'test_quotation.png')

print('Input HTML:', INPUT)
HTML(INPUT).write_pdf(PDF_OUT)
print('Wrote', PDF_OUT)

# Convert first page of PDF to PNG
pages = convert_from_path(PDF_OUT, dpi=150)
if pages:
    pages[0].save(PNG_OUT, 'PNG')
    print('Wrote', PNG_OUT)
else:
    print('No pages rendered from PDF')
