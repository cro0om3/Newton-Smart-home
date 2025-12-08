from playwright.sync_api import sync_playwright
p = None
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://localhost:8501')
    page.wait_for_timeout(1500)
    page.screenshot(path='data/exports/accent_toast_check.png', full_page=True)
    browser.close()
