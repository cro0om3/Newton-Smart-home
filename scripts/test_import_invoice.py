import sys
sys.path.insert(0, '.')
try:
    import pages_custom.invoice_page as ip
    print('Imported pages_custom.invoice_page OK')
except Exception as e:
    print('Import failed:', e)
