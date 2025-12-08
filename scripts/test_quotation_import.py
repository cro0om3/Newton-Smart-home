# Quick smoke test to import quotation_page and check for import errors
import importlib
import sys
import os

# Ensure repository root is on sys.path for direct script runs
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root not in sys.path:
    sys.path.insert(0, root)

try:
    mod = importlib.import_module('pages_custom.quotation_page')
    print('Imported pages_custom.quotation_page OK')
except Exception as e:
    print('Import failed:', e)
    raise
