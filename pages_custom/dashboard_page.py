import streamlit as st
import pandas as pd
from datetime import datetime

# ---------- THEME (Premium Apple Design) ----------
def _apply_dashboard_theme():
    st.markdown(
        """
        <style>
        :root {
            --dash-blue:#0a84ff;
            --dash-blue-soft:#5ac8fa;
            --dash-ink:#1d1d1f;
            --dash-sub:#6e6e73;
        }
        /* ---------------- ICON GRID ---------------- */
        #dashboard-icons .row {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap:12px; /* reduced from 16px */
            margin: 8px 0 18px; /* tighter vertical rhythm */
        }
        #dashboard-icons [data-testid="stButton"] > button {
            width:100%;
            white-space: pre-line;
            text-align:center;
            padding:18px 10px 14px; /* slightly more compact */
            border-radius:24px; /* larger roundness */
            /* colors handled globally */
            font-weight:600; font-size:13px;
            box-shadow:0 4px 12px rgba(0,0,0,.08),0 12px 28px rgba(0,0,0,.10);
            position:relative; overflow:hidden;
            transition: transform .35s cubic-bezier(.4,0,.2,1), box-shadow .35s, background .35s;
            backdrop-filter:blur(12px);
        }
        #dashboard-icons [data-testid="stButton"] > button::before {
            content:""; position:absolute; inset:0;
            /* color glow handled globally */
            opacity:0; transition:opacity .35s;
        }
        #dashboard-icons [data-testid="stButton"] > button:hover {
            transform:translateY(-3px) scale(1.01);
            box-shadow:0 6px 18px rgba(0,0,0,.12),0 18px 40px rgba(0,0,0,.16);
            backdrop-filter:blur(24px);
        }
        #dashboard-icons [data-testid="stButton"] > button:hover::before {opacity:1;}
        #dashboard-icons [data-testid="stButton"] > button:active {transform:translateY(-1px) scale(.995);}        
        #dashboard-icons [data-testid="stButton"] > button::first-line {font-size:30px; line-height:1.15;}

        /* ---------------- SECTION TITLE ---------------- */
        .section-title {
            font-family:"SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size:22px; font-weight:700; letter-spacing:.015em;
            margin: 4px 0 14px;
        }
        .metric {
            background:linear-gradient(145deg,rgba(255,255,255,.95) 0%,rgba(245,247,250,.90) 100%);
            border:1px solid rgba(0,0,0,.06);
            border-radius:24px;
            padding:22px 22px 20px;
            box-shadow:0 4px 14px rgba(0,0,0,.06),0 18px 48px rgba(0,0,0,.08);
            backdrop-filter:blur(18px);
            position:relative; overflow:hidden;
            transition:transform .35s cubic-bezier(.4,0,.2,1), box-shadow .35s;
        .metric::after {
        }
            content:""; position:absolute; inset:0;
            background:linear-gradient(115deg,rgba(10,132,255,.10),rgba(90,200,250,.08));
        .metric::before {
        }
            border-radius:6px 0 0 6px;
            background:linear-gradient(180deg,var(--dash-blue),var(--dash-blue-soft));
            box-shadow:0 0 0 0 rgba(10,132,255,.5); border-radius:6px 0 0 6px;
            transform:translateX(-8px); opacity:0; transition:all .45s cubic-bezier(.4,0,.2,1);
        }
        .metric:hover {transform:translateY(-3px) scale(1.01); box-shadow:0 8px 24px rgba(0,0,0,.10),0 24px 54px rgba(0,0,0,.14);}
        .metric .label {font-size:11px; letter-spacing:.09em; text-transform:uppercase; font-weight:600;}
        .metric:hover::after {opacity:1;}
        .metric .value {font-size:34px; font-weight:700;}
        .metric .sub {font-size:13px; margin-top:4px;}
        .metric .value {font-size:34px; font-weight:700; background:linear-gradient(135deg,#1d1d1f 0%,#434347 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
        .metric .sub {color:#86868b; font-size:13px; margin-top:4px;}

        /* ---------------- TABLE WRAPPER ---------------- */
        .table-wrap {
            border-radius:24px;
            padding:18px 22px 14px;
            box-shadow:0 4px 14px rgba(0,0,0,.05),0 18px 48px rgba(0,0,0,.07);
            backdrop-filter:blur(18px);
            margin-bottom:16px; /* consistent section spacing */
        }

        /* ---------------- STREAMLIT TABLE ---------------- */
        [data-testid="stTable"] {background:transparent !important;}
        [data-testid="stTable"] table {border-collapse:separate; border-spacing:0;}
        [data-testid="stTable"] th {
            font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.06em;
            padding:10px 12px; border-bottom:1px solid transparent;
        }
        [data-testid="stTable"] td {
            padding:11px 12px; border-bottom:1px solid transparent; font-size:14px;
        }
        [data-testid="stTable"] tr:last-child td {border-bottom:none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------- DATA HELPERS ----------
def _load_or_empty(path, columns):
    try:
        df = pd.read_excel(path)
        df.columns = [c.strip().lower() for c in df.columns]
    except Exception:
        df = pd.DataFrame(columns=columns)
    return df

def _metric(label, value, sub=""):
    st.markdown(
        f"""
        <div class="metric">
          <div class="label">{label}</div>
          <div class="row">
            <div class="value">{value}</div>
          </div>
          <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _app_icon_grid():
    items = [
        ("Quotations", "quotation"),
        ("Invoices",   "invoice"),
        ("Receipts",   "receipt"),
        ("Customers",  "customers"),
        ("Products",   "products"),
        ("Reports",    "reports"),
        ("⚙️\nSettings",   "settings"),
    ]
    st.markdown('<div id="dashboard-icons"><div class="row">', unsafe_allow_html=True)
    cols = st.columns(len(items))
    for i, (c, (label, target)) in enumerate(zip(cols, items)):
        with c:
            if st.button(label, key=f"dash_nav_{target}_{i}", use_container_width=True):
                st.session_state["active_page"] = target
                st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- MAIN ----------
def dashboard_app():
    _apply_dashboard_theme()


    _app_icon_grid()


    try:
        records = _load_or_empty(
            "data/records.xlsx",
            ["base_id", "date", "type", "number", "amount", "client_name", "phone", "location", "note"],
        )
    except Exception:
        records = pd.DataFrame(columns=["base_id", "date", "type", "number", "amount", "client_name", "phone", "location", "note"])

    try:
        customers = _load_or_empty(
            "data/customers.xlsx",
            ["client_name", "phone", "location", "last_activity", "status"],
        )
    except Exception:
        customers = pd.DataFrame(columns=["client_name", "phone", "location", "last_activity", "status"])

    rec = records.copy()
    if not rec.empty and "date" in rec.columns:
        rec["date"] = pd.to_datetime(rec["date"], errors="coerce")

    total_q = int((rec["type"] == "q").sum()) if "type" in rec.columns else 0
    total_i = int((rec["type"] == "i").sum()) if "type" in rec.columns else 0
    total_r = int((rec["type"] == "r").sum()) if "type" in rec.columns else 0
    total_invoice_amount = float(rec.loc[rec.get("type","") == "i", "amount"].sum()) if "amount" in rec.columns else 0.0
    total_received = float(rec.loc[rec.get("type","") == "r", "amount"].sum()) if "amount" in rec.columns else 0.0
    remaining_balance = total_invoice_amount - total_received

    # عرض الكروت دائماً حتى لو لم توجد بيانات
    c1, c2, c3 = st.columns(3)
    with c1: _metric("Quotations", total_q if total_q else 0, "Active proposals")
    with c2: _metric("Invoices", total_i if total_i else 0, "Issued bills")
    with c3: _metric("Receipts", total_r if total_r else 0, "Recorded payments")

    c4, c5, c6 = st.columns(3)
    with c4: _metric("Invoice Volume", f"AED {total_invoice_amount:,.0f}" if total_invoice_amount else "AED 0",)
    with c5: _metric("Received", f"AED {total_received:,.0f}" if total_received else "AED 0",)
    with c6: _metric("Outstanding", f"AED {remaining_balance:,.0f}" if remaining_balance else "AED 0",)

    st.markdown('<div class="section-title">Top Clients</div>', unsafe_allow_html=True)
    st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
    if not rec.empty and {"type","amount","client_name"}.issubset(rec.columns):
        top_clients = (
            rec[rec["type"] == "i"]
            .groupby("client_name")["amount"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )
        if not top_clients.empty:
            st.table(top_clients.rename(columns={"client_name": "Client", "amount": "Amount (AED)"}))
        else:
            st.write("No invoice data available.")
    else:
        st.write("No invoice data available.")
    st.markdown('</div>', unsafe_allow_html=True)

    two1, two2 = st.columns(2)
    with two1:
        st.markdown('<div class="section-title">Latest Invoices</div>', unsafe_allow_html=True)
        st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
        if not rec.empty and "type" in rec.columns:
            last_10_invoices = (
                rec[rec["type"] == "i"]
                .sort_values("date", ascending=False, na_position="last")
                .head(10)[["date", "number", "client_name", "amount"]]
            )
            if not last_10_invoices.empty:
                d = last_10_invoices.copy()
                if "date" in d.columns:
                    d["date"] = pd.to_datetime(d["date"], errors="coerce").dt.strftime("%Y-%m-%d")
                st.table(d.rename(columns={"date": "Date", "number": "Invoice", "client_name": "Client", "amount": "Amount (AED)"}))
            else:
                st.write("No invoices yet.")
        else:
            st.write("No invoices yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with two2:
        st.markdown('<div class="section-title">Latest Receipts</div>', unsafe_allow_html=True)
        st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
        if not rec.empty and "type" in rec.columns:
            last_10_receipts = (
                rec[rec["type"] == "r"]
                .sort_values("date", ascending=False, na_position="last")
                .head(10)[["date", "number", "client_name", "amount"]]
            )
            if not last_10_receipts.empty:
                d = last_10_receipts.copy()
                if "date" in d.columns:
                    d["date"] = pd.to_datetime(d["date"], errors="coerce").dt.strftime("%Y-%m-%d")
                st.table(d.rename(columns={"date": "Date", "number": "Receipt", "client_name": "Client", "amount": "Amount (AED)"}))
            else:
                st.write("No receipts yet.")
        else:
            st.write("No receipts yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Customer Signals</div>', unsafe_allow_html=True)
    st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
    if not customers.empty:
        st.table(
            customers.rename(
                columns={
                    "client_name": "Client",
                    "phone": "Phone",
                    "location": "Location",
                    "last_activity": "Last Activity",
                    "status": "Stage",
                }
            )
        )
    else:
        st.write("No customer records yet.")
    st.markdown('</div>', unsafe_allow_html=True)
