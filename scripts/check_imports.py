import importlib
mods = [
    'pages_custom.receipt_page',
    'pages_custom.invoice_page',
    'pages_custom.quotation_page'
]
for m in mods:
    try:
        importlib.import_module(m)
        print(m + ' OK')
    except Exception as e:
        print(m + ' ERR ->', e)
        raise
