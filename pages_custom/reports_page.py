import os
from io import BytesIO
from datetime import datetime, date
from typing import Tuple

import pandas as pd
import streamlit as st
import altair as alt

# ==========================================
# File Ensurers
# ==========================================

def ensure_report_files():
    os.makedirs("data", exist_ok=True)

    cust_path = "data/customers.xlsx"
    rec_path = "data/records.xlsx"

    if not os.path.exists(cust_path):
        pd.DataFrame(columns=[
            "client_name","phone","location","email","status",
            "notes","tags","next_follow_up","assigned_to","last_activity"
        ]).to_excel(cust_path, index=False)

    if not os.path.exists(rec_path):
        pd.DataFrame(columns=[
            "base_id","date","type","number","amount","client_name","phone","location","note"
        ]).to_excel(rec_path, index=False)

# ==========================================
# Loaders with normalization
# ==========================================

def _load_records() -> pd.DataFrame:
    ensure_report_files()
    try:
        df = pd.read_excel("data/records.xlsx")
        df.columns = [c.strip().lower() for c in df.columns]
        # Normalize types and dates
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if "type" in df.columns:
            df["type"] = df["type"].astype(str).str.lower()
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "base_id","date","type","number","amount","client_name","phone","location","note"
        ])


def _load_customers() -> pd.DataFrame:
    try:
        df = pd.read_excel("data/customers.xlsx")
        df.columns = [c.strip().lower() for c in df.columns]
        if "next_follow_up" in df.columns:
            df["next_follow_up"] = pd.to_datetime(df["next_follow_up"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "client_name","phone","location","email","status",
            "notes","tags","next_follow_up","assigned_to","last_activity"
        ])


def _load_products() -> pd.DataFrame:
    try:
        df = pd.read_excel("data/products.xlsx")
        return df
    except Exception:
        return pd.DataFrame()

# ==========================================
# Filters
# ==========================================

UAE_LOCATIONS = [
    "Abu Dhabi - Al Shamkha","Abu Dhabi - Al Shawamekh","Abu Dhabi - Khalifa City",
    "Abu Dhabi - Al Bateen","Abu Dhabi - Al Reem Island","Abu Dhabi - Yas Island",
    "Abu Dhabi - Al Mushrif","Abu Dhabi - Al Rawdah","Abu Dhabi - Al Muroor",
    "Abu Dhabi - Baniyas","Abu Dhabi - Mussafah","Abu Dhabi - Al Mafraq",
    "Abu Dhabi - Al Falah","Abu Dhabi - MBZ City","Abu Dhabi - Al Raha",
    "Abu Dhabi - Al Maqtaa","Abu Dhabi - Zayed Port","Abu Dhabi - Saadiyat Island",
    "Al Ain - Al Jimi","Al Ain - Falaj Hazza","Al Ain - Al Maqam",
    "Al Ain - Zakher","Al Ain - Hili","Al Ain - Al Foah","Al Ain - Al Mutaredh",
    "Al Ain - Al Towayya","Al Ain - Al Sarooj","Al Ain - Al Nyadat",
    "Dubai - Marina","Dubai - Downtown","Dubai - Business Bay",
    "Dubai - Jumeirah","Dubai - JBR","Dubai - Al Barsha","Dubai - Mirdif",
    "Dubai - Deira","Dubai - Bur Dubai","Dubai - Silicon Oasis",
    "Dubai - Academic City","Dubai - Arabian Ranches","Dubai - International City",
    "Dubai - Dubai Hills","Dubai - The Springs","Dubai - The Meadows",
    "Dubai - The Greens","Dubai - Palm Jumeirah","Dubai - Al Qusais",
    "Dubai - Al Nahda","Dubai - JVC","Dubai - Damac Hills",
    "Dubai - Discovery Gardens","Dubai - IMPZ","Dubai - Al Warqa",
    "Dubai - Nad Al Sheba",
    "Sharjah - Al Majaz","Sharjah - Al Nahda","Sharjah - Al Taawun",
    "Sharjah - Muwaileh","Sharjah - Al Khan","Sharjah - Al Yarmook",
    "Sharjah - Al Qasimia","Sharjah - Al Fisht","Sharjah - Al Nasserya",
    "Sharjah - Al Goaz","Sharjah - Al Jubail","Sharjah - Maysaloon",
    "Ajman - Al Rashidiya","Ajman - Al Nuaimiya","Ajman - Al Mowaihat",
    "Ajman - Al Rawda","Ajman - Al Jurf","Ajman - Al Hamidiya",
    "Ajman - Al Rumailah","Ajman - Al Bustan","Ajman - City Center",
    "RAK - Al Nakheel","RAK - Al Dhait","RAK - Julph",
    "RAK - Khuzam","RAK - Al Qusaidat","RAK - Seih Al Uraibi",
    "RAK - Al Rams","RAK - Al Mairid","RAK - Mina Al Arab",
    "RAK - Al Hamra Village","RAK - Marjan Island",
    "Fujairah - Al Faseel","Fujairah - Madhab","Fujairah - Dibba",
    "Fujairah - Sakamkam","Fujairah - Mirbah","Fujairah - Al Taween",
    "Fujairah - Kalba","Fujairah - Qidfa","Fujairah - Al Aqah",
    "UAQ - Al Salama","UAQ - Al Haditha","UAQ - Al Raas",
    "UAQ - Al Dar Al Baida","UAQ - Al Khor","UAQ - Al Ramlah",
    "UAQ - Al Maidan","UAQ - Emirates City",
]


def _apply_filters(records: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    st.markdown("<div class='section-title'>Filters</div>", unsafe_allow_html=True)

    # Default date range: this year
    today = date.today()
    start_default = date(today.year, 1, 1)
    end_default = today

    f1, f2, f3 = st.columns([1.2, 1, 1])
    with f1:
        start_date = st.date_input("Start Date", start_default)
        end_date = st.date_input("End Date", end_default)
    with f2:
        doc_type = st.selectbox("Document Type", ["All", "Quotation", "Invoice", "Receipt"], index=0)
        name_kw = st.text_input("Customer Name contains")
    with f3:
        location = st.selectbox("Location", ["All"] + UAE_LOCATIONS, index=0)
        min_amt, max_amt = st.columns(2)
        with min_amt:
            amt_min = st.number_input("Min Amount", min_value=0.0, value=0.0, step=100.0)
        with max_amt:
            amt_max = st.number_input("Max Amount", min_value=0.0, value=0.0, step=100.0)

    # Build mask
    m = pd.Series([True] * len(records))
    if not records.empty:
        if "date" in records.columns:
            m &= (records["date"].dt.date >= start_date) & (records["date"].dt.date <= end_date)
        if doc_type != "All" and "type" in records.columns:
            map_type = {"Quotation": "q", "Invoice": "i", "Receipt": "r"}
            m &= records["type"].isin([map_type.get(doc_type, "")])
        if name_kw:
            m &= records.get("client_name", pd.Series([""]*len(records))).astype(str).str.contains(name_kw, case=False, na=False)
        if location != "All":
            m &= records.get("location", pd.Series([""]*len(records))).astype(str) == location
        if amt_min > 0:
            m &= records.get("amount", pd.Series([0]*len(records))).astype(float) >= amt_min
        if amt_max > 0:
            m &= records.get("amount", pd.Series([0]*len(records))).astype(float) <= amt_max

    filtered = records[m].copy() if not records.empty else records.copy()
    return filtered, {
        "start": start_date, "end": end_date, "doc_type": doc_type,
        "name_kw": name_kw, "location": location, "amt_min": amt_min, "amt_max": amt_max,
    }

# ==========================================
# Metrics
# ==========================================


def _metric_card(label: str, value: str):
    st.markdown(
        f"""
        <div class='hero-card' style='padding:16px'>
            <div style='font-size:12px;color:#6e6e73;font-weight:700;text-transform:uppercase;letter-spacing:.06em'>{label}</div>
            <div style='font-size:26px;font-weight:800;margin-top:6px'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# Main App
# ==========================================

def reports_app():
    ensure_report_files()
    records = _load_records()
    customers = _load_customers()
    products = _load_products()

    # 1) ملخصات المستندات
    st.markdown("<div class='section-title'>ملخص المستندات</div>", unsafe_allow_html=True)
    q_count = records[records["type"] == "q"].shape[0]
    i_count = records[records["type"] == "i"].shape[0]
    r_count = records[records["type"] == "r"].shape[0]
    inv_sum = records[records["type"] == "i"]["amount"].sum()
    rec_sum = records[records["type"] == "r"]["amount"].sum()
    outstanding = inv_sum - rec_sum
    projects = records["base_id"].nunique() if "base_id" in records.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: _metric_card("العروض (Quotation)", f"{q_count}")
    with c2: _metric_card("الفواتير (Invoice)", f"{i_count}")
    with c3: _metric_card("الإيصالات (Receipt)", f"{r_count}")
    with c4: _metric_card("الرصيد المتبقي", f"{outstanding:,.2f} AED")

    st.markdown("---")
    st.markdown("<div class='section-title'>متابعة دورة حياة المشاريع</div>", unsafe_allow_html=True)
    # 2) جدول متابعة المشاريع
    if not records.empty:
        # بناء جدول لكل base_id
        lifecycle = []
        for base_id, group in records.groupby("base_id"):
            client = group["client_name"].iloc[0] if "client_name" in group.columns else "—"
            phone = group["phone"].iloc[0] if "phone" in group.columns else "—"
            location = group["location"].iloc[0] if "location" in group.columns else "—"
            q_row = group[group["type"] == "q"]
            i_row = group[group["type"] == "i"]
            r_row = group[group["type"] == "r"]
            status_q = "✅" if not q_row.empty else "❌"
            status_i = "✅" if not i_row.empty else "❌"
            status_r = "✅" if not r_row.empty else "❌"
            amt = i_row["amount"].sum() if not i_row.empty else 0.0
            paid = r_row["amount"].sum() if not r_row.empty else 0.0
            remain = amt - paid
            last_update = group["date"].max() if "date" in group.columns else "—"
            lifecycle.append({
                "base_id": base_id,
                "client": client,
                "phone": phone,
                "location": location,
                "عرض سعر": status_q,
                "فاتورة": status_i,
                "إيصال": status_r,
                "المبلغ": amt,
                "المدفوع": paid,
                "الرصيد": remain,
                "آخر تحديث": last_update,
            })
        df_life = pd.DataFrame(lifecycle)
        st.dataframe(df_life, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد مشاريع بعد.")

    st.markdown("---")
    st.markdown("<div class='section-title'>توزيع المستندات</div>", unsafe_allow_html=True)
    # 3) رسم بياني لتوزيع المستندات
    doc_counts = pd.DataFrame({
        "type": ["Quotation", "Invoice", "Receipt"],
        "count": [q_count, i_count, r_count]
    })
    chart = alt.Chart(doc_counts).mark_bar().encode(
        x=alt.X('type:N', title='نوع المستند'),
        y=alt.Y('count:Q', title='عدد المستندات'),
        color=alt.Color('type:N', scale=alt.Scale(range=['#0a84ff','#ff9f0a','#34c759']))
    ).properties(height=220)
    st.altair_chart(chart, use_container_width=True)

    # 3) جدول المستندات الكامل
    st.markdown("---")
    st.markdown("<div class='section-title'>Documents</div>", unsafe_allow_html=True)
    if not records.empty:
        view = records.copy()
        cols = [
            "date","type","number","client_name","phone","location","amount","base_id","note"
        ]
        cols = [c for c in cols if c in view.columns]
        view = view[cols].sort_values(by=["date"], ascending=False)
        st.dataframe(view, use_container_width=True, hide_index=True)

        buf_xlsx = BytesIO()
        view.to_excel(buf_xlsx, index=False)
        buf_xlsx.seek(0)
        st.download_button("Export Excel", buf_xlsx, file_name="documents_report.xlsx")

        buf_csv = BytesIO(view.to_csv(index=False).encode("utf-8"))
        st.download_button("Export CSV", buf_csv, file_name="documents_report.csv")
    else:
        st.info("No documents found.")

    # 4) Financial analytics
    st.markdown("---")
    st.markdown("<div class='section-title'>Financial Analytics</div>", unsafe_allow_html=True)
    if not records.empty and "date" in records.columns:
        df_i = records[records["type"] == "i"][['date','amount']].copy()
        df_r = records[records["type"] == "r"][['date','amount']].copy()
        if not df_i.empty:
            df_i['month'] = df_i['date'].dt.to_period('M').dt.to_timestamp()
            inv_month = df_i.groupby('month')['amount'].sum().reset_index()
            chart_i = alt.Chart(inv_month).mark_bar(color="#0a84ff").encode(x='month:T', y='amount:Q').properties(height=220)
            st.altair_chart(chart_i, use_container_width=True)
        else:
            st.info("No invoices in range for Monthly Revenue chart.")

        if not df_r.empty:
            df_r['month'] = df_r['date'].dt.to_period('M').dt.to_timestamp()
            rec_month = df_r.groupby('month')['amount'].sum().reset_index()
            chart_r = alt.Chart(rec_month).mark_area(color="#34c759", opacity=0.5).encode(x='month:T', y='amount:Q').properties(height=220)
            st.altair_chart(chart_r, use_container_width=True)
        else:
            st.info("No receipts in range for Monthly Collection chart.")

        # Outstanding pie
        paid = float(rec_sum)
        invoiced = float(inv_sum)
        remain = max(invoiced - paid, 0.0)
        pie_df = pd.DataFrame({
            'status': ['Paid','Unpaid'],
            'value': [paid, remain]
        })
        pie = alt.Chart(pie_df).mark_arc(innerRadius=60).encode(
            theta='value:Q', color=alt.Color('status:N', scale=alt.Scale(range=['#34c759','#ff3b30']))
        ).properties(height=250)
        st.altair_chart(pie, use_container_width=True)
    else:
        st.info("Not enough data for charts.")

    # 5) Top customers
    st.markdown("---")
    st.markdown("<div class='section-title'>Top Customers</div>", unsafe_allow_html=True)
    if not records.empty:
        inv = records[records['type'] == 'i']
        rec = records[records['type'] == 'r']
        inv_by = inv.groupby('client_name', dropna=False)['amount'].sum().rename('Total Invoiced')
        rec_by = rec.groupby('client_name', dropna=False)['amount'].sum().rename('Total Paid')
        top = pd.concat([inv_by, rec_by], axis=1).fillna(0.0)
        top['Balance'] = top['Total Invoiced'] - top['Total Paid']
        top = top.sort_values('Total Invoiced', ascending=False).reset_index().rename(columns={'client_name':'Customer Name'})
        st.dataframe(top, use_container_width=True, hide_index=True)

        # Optional horizontal bar chart by invoiced
        if not top.empty:
            chart_top = alt.Chart(top).mark_bar(color="#0a84ff").encode(
                x='Total Invoiced:Q', y=alt.Y('Customer Name:N', sort='-x')
            ).properties(height=300)
            st.altair_chart(chart_top, use_container_width=True)
    else:
        st.info("No invoice/receipt data available yet.")

    # 6) Top products (placeholder)
    st.markdown("---")
    st.markdown("<div class='section-title'>Top Products (coming soon)</div>", unsafe_allow_html=True)
    if products.empty:
        st.caption("Products file is empty or not linked to records yet.")
    else:
        st.caption("Future: aggregate line-items from documents.")

    # 7) Customer follow-up report
    st.markdown("---")
    st.markdown("<div class='section-title'>Customer Follow-up</div>", unsafe_allow_html=True)
    if not customers.empty:
        today = pd.to_datetime(date.today())
        need_follow = customers[(customers.get('status','').astype(str).str.lower() == 'follow-up') |
                                (customers.get('next_follow_up').notna() & (customers['next_follow_up'] <= today))]
        cols = [
            'client_name','phone','location','assigned_to','status','next_follow_up','notes'
        ]
        cols = [c for c in cols if c in need_follow.columns]
        st.dataframe(need_follow[cols], use_container_width=True, hide_index=True)
    else:
        st.info("No customers found.")

    # 8) Exporting
    st.markdown("---")
    st.markdown("<div class='section-title'>Exporting</div>", unsafe_allow_html=True)

    # Full report = جميع المستندات
    full_buf = BytesIO()
    records.to_excel(full_buf, index=False)
    full_buf.seek(0)
    st.download_button("Download Full Report (Excel)", full_buf, file_name="full_report.xlsx")

    # Summary only
    summary_df = pd.DataFrame([
        {"Metric":"Total Quotations","Value": q_count},
        {"Metric":"Total Invoice Amount","Value": inv_sum},
        {"Metric":"Total Received Amount","Value": rec_sum},
        {"Metric":"Outstanding Balance","Value": outstanding},
        {"Metric":"Total Projects","Value": projects},
    ])
    sum_buf = BytesIO()
    summary_df.to_excel(sum_buf, index=False)
    sum_buf.seek(0)
    st.download_button("Download Summary Only (Excel)", sum_buf, file_name="summary_report.xlsx")