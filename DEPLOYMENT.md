Streamlit Cloud deployment (quick guide)

Overview

- This repo contains a Streamlit app. The quotation pages now render an HTML template and convert to PDF locally using WeasyPrint or via ConvertAPI as fallback.

Requirements

- Python 3.10+ recommended
- If you want PDF conversion on Streamlit Cloud, use ConvertAPI fallback (set secret). Installing WeasyPrint system deps on Streamlit Cloud is not supported.

Steps

1. Push your repo to GitHub (main branch)
2. In Streamlit Cloud, create a new app and link the GitHub repo.
3. Set secrets in Streamlit Cloud (Deployment > Advanced > Secrets) or via the dashboard:
   - `CONVERTAPI_SECRET` = your ConvertAPI secret key
4. Ensure `requirements.txt` includes `weasyprint` and `Jinja2` (already added). Streamlit Cloud will install these packages.

Behavior on Streamlit Cloud

- At runtime `html_to_pdf` will first try to use WeasyPrint. If system deps are not present (very likely on Streamlit Cloud), it will fall back to ConvertAPI using `CONVERTAPI_SECRET`.
- If neither available, the app will raise an informative runtime error instructing how to set the secret or install WeasyPrint locally.

Security

- Keep `CONVERTAPI_SECRET` private — add it only as a Streamlit secret (not committed to the repo).

Local testing

- Create a venv and install requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- If you prefer local PDF conversion, install WeasyPrint system dependencies following:
  <https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation>

- Or set `CONVERTAPI_SECRET` locally to use ConvertAPI:

```powershell
$env:CONVERTAPI_SECRET = 'your-key-here'
```

- Run the app:

```powershell
streamlit run main.py
```

Support

- If you want, I can prepare the Streamlit Cloud deploy steps with screenshots and help set the secret value interactively.
