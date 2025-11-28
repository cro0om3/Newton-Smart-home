import streamlit as st
import pandas as pd
from datetime import datetime
import os
from docx import Document
from io import BytesIO
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


def proper_case(text):
    if not text:
        return ""
    try:
        return text.title().strip()
    except:
        return text
def invoice_app():
    # Phone formatter (same logic as quotation)
    def format_phone_input(raw_input):
        if not raw_input:
            return None
        digits = ''.join(filter(str.isdigit, str(raw_input)))
        if digits.startswith("0"):
            digits = digits[1:]
        if digits.startswith("5") and len(digits) == 9:
            return f"+971 {digits[:2]} {digits[2:5]} {digits[5:]}"
        return None
    # Phone as 10-digit local (0502992932) for labels
    def phone_flat10(raw_input):
        if raw_input is None:
            return ""
        digits = ''.join(filter(str.isdigit, str(raw_input)))
        if not digits:
            return ""
        if digits.startswith('971') and len(digits) >= 12 and digits[3] == '5':
            return '0' + digits[3:12]
        if len(digits) == 9 and digits.startswith('5'):
            return '0' + digits
        if len(digits) == 10 and digits.startswith('05'):
            return digits
        return digits[-10:]

    def phone_label_mask(raw_input):
        flat = phone_flat10(raw_input)
        return f"{flat} xxxxxxxxxx" if flat else "xxxxxxxxxx"

    # Page CSS (colors handled globally; keep geometry only)
    st.markdown("""
    <style>
    .hero{ border-radius:24px; padding:32px; backdrop-filter:blur(20px); margin-bottom:18px; }
    .hero h2{ margin:0 0 8px; font-size:32px; font-weight:700; }
    .hero p{ margin:0; font-size:15px; }
    .section-title{ font-size:20px; font-weight:700; margin:18px 0 10px; }

    .product-header{ display:flex; gap:1rem; padding:8px 0 12px; background:transparent; font-size:11px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; margin-bottom:10px; align-items:center; }
    .product-header span{text-align:center;}
    .product-header span:nth-child(1){flex:4.5; text-align:left;}
    .product-header span:nth-child(2){flex:0.7;}
    .product-header span:nth-child(3){flex:1;}
    .product-header span:nth-child(4){flex:1;}
    .product-header span:nth-child(5){flex:0.7;}
    .product-header span:nth-child(6){flex:0.7;}

    .added-product-row{ padding:10px 14px; border-radius:12px; margin-bottom:6px; box-shadow:0 2px 6px rgba(0,0,0,.05); }
    .product-value{ font-weight:600; }
    </style>
    """, unsafe_allow_html=True)

        # (Header hero removed by request)

    # ---------------- LOAD DATA ----------------
    try:
        catalog = pd.read_excel("data/products.xlsx")
    except:
        st.error("❌ Cannot load products.xlsx")
        return

    # simple records list for quotations to pick from
    def load_records():
        try:
            df = pd.read_excel("data/records.xlsx")
            df.columns = [c.strip().lower() for c in df.columns]
            return df
        except:
            return pd.DataFrame(columns=[
                "base_id","date","type","number","amount","client_name","phone","location","note"
            ])

    def save_record(rec: dict):
        df = load_records()
        if not df.empty and {"type", "number"}.issubset(df.columns):
            df = df[~((df["type"] == rec.get("type")) & (df["number"] == rec.get("number")))]
        df = pd.concat([df, pd.DataFrame([rec])], ignore_index=True)
        if {"type", "number"}.issubset(df.columns):
            df = df.drop_duplicates(subset=["type", "number"], keep="last")
        df.to_excel("data/records.xlsx", index=False)

    # ---- Customers helpers (auto add/update) ----
    def ensure_customers_file():
        os.makedirs("data", exist_ok=True)
        path = "data/customers.xlsx"
        if not os.path.exists(path):
            cols = [
                "client_name","phone","location","email","status",
                "notes","tags","next_follow_up","assigned_to","last_activity"
            ]
            pd.DataFrame(columns=cols).to_excel(path, index=False)

    def load_customers():
        ensure_customers_file()
        try:
            df = pd.read_excel("data/customers.xlsx")
            df.columns = [c.strip().lower() for c in df.columns]
            return df
        except Exception:
            return pd.DataFrame(columns=[
                "client_name","phone","location","email","status",
                "notes","tags","next_follow_up","assigned_to","last_activity"
            ])

    def save_customers(df: pd.DataFrame):
        os.makedirs("data", exist_ok=True)
        df.to_excel("data/customers.xlsx", index=False)

    def _norm_phone(x: str):
        digits = ''.join(filter(str.isdigit, str(x)))
        if digits.startswith('971') and len(digits) >= 12 and digits[3] == '5':
            return '0' + digits[3:12]
        if len(digits) == 9 and digits.startswith('5'):
            return '0' + digits
        if len(digits) == 10 and digits.startswith('05'):
            return digits
        return digits[-10:]

    def upsert_customer_from_invoice(name: str, phone: str, location: str):
        if not str(name).strip():
            return
        cdf = load_customers()
        key = str(name).strip().lower()
        idx = None
        if not cdf.empty and "client_name" in cdf.columns:
            m = cdf["client_name"].astype(str).str.strip().str.lower() == key
            if m.any():
                idx = m[m].index[0]
            elif phone:
                cdf_phone = cdf.get("phone", pd.Series([], dtype=str)).apply(_norm_phone)
                target = _norm_phone(phone)
                pm = cdf_phone == target
                if pm.any():
                    idx = pm[pm].index[0]
        if idx is None:
            new_row = {
                "client_name": proper_case(name),
                "phone": phone,
                "location": proper_case(location),
                "email": "",
                "status": "Active",
                "notes": "",
                "tags": "",
                "next_follow_up": "",
                "assigned_to": "",
                "last_activity": datetime.today().strftime('%Y-%m-%d'),
            }
            cdf = pd.concat([cdf, pd.DataFrame([new_row])], ignore_index=True)
        else:
            cdf.loc[idx, "client_name"] = proper_case(name)
            if phone:
                cdf.loc[idx, "phone"] = phone
            if location:
                cdf.loc[idx, "location"] = proper_case(location)
            if not str(cdf.loc[idx, "status"]).strip():
                cdf.loc[idx, "status"] = "Active"
            cdf.loc[idx, "last_activity"] = datetime.today().strftime('%Y-%m-%d')
        save_customers(cdf)
    records = load_records()
    quotes_df = records[records["type"] == "q"].copy()

    # ---------------- LAYOUT: SAME ROWS ----------------
    st.markdown("<div class='section-title'>Invoice Summary</div>", unsafe_allow_html=True)

    mode = st.radio("Invoice Creation Method", ["From Quotation", "New Invoice"], horizontal=True, key="inv_mode")

    today = datetime.today().strftime('%Y%m%d')
    auto_no = f"INV-{today}-{str(len(records[records['type']=='i']) + 1).zfill(3)}"

    # Prefill defaults from previously selected quotation (before rendering widgets)
    sel_default_name = ""
    sel_default_loc = ""
    sel_default_phone = ""
    if mode == "From Quotation":
        selected_q = st.session_state.get("q_select_inline", None)
        if selected_q:
            try:
                q_prefill = records[records["number"] == selected_q].iloc[0]
                sel_default_name = q_prefill.get("client_name", "")
                sel_default_loc = q_prefill.get("location", "")
                sel_default_phone = q_prefill.get("phone", "")
            except Exception:
                pass
    else:
        selected_q = None

    # If a quotation was just selected, prefill and rerun so inputs show values
    if mode == "From Quotation":
        current_q = st.session_state.get("q_select_inline")
        last_q = st.session_state.get("_last_q_selected")
        if current_q and current_q != last_q:
            try:
                q_prefill = records[records["number"] == current_q].iloc[0]
                st.session_state["inv_client"] = q_prefill.get("client_name", "")
                st.session_state["inv_loc"] = q_prefill.get("location", "")
                st.session_state["inv_phone"] = q_prefill.get("phone", "")
            except Exception:
                pass
            st.session_state["_last_q_selected"] = current_q
            st.rerun()

    # Row 1: Name | Invoice Number
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        client_name = st.text_input("Client Name", value=sel_default_name, key="inv_client")
    with r1c2:
        invoice_no = st.text_input("Invoice Number", auto_no, disabled=True, key="inv_no")

    # UAE Locations (same as quotation)
    uae_locations = [
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

    # Row 2: Location | Select Quotation
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        default_loc_index = uae_locations.index(sel_default_loc) if sel_default_loc in uae_locations else 0
        selected_loc = st.selectbox("Project Location (UAE)", uae_locations, index=default_loc_index, key="inv_loc")
        client_location = proper_case(selected_loc)
    with r2c2:
        if mode == "From Quotation":
            if not quotes_df.empty:
                df = quotes_df.fillna("")
                numbers = df["number"].astype(str).tolist()
                labels = {}
                for _, row in df.iterrows():
                    labels[str(row["number"])] = f"{row['number']}  |  {row.get('client_name','')}  |  {phone_label_mask(row.get('phone',''))}"

                selected_q = st.selectbox(
                    "Select Quotation",
                    options=numbers if numbers else ["No quotations"],
                    key="q_select_inline",
                    format_func=lambda n: labels.get(n, n),
                )
            else:
                st.info("No quotations found in records")

    # Row 3: Phone | spacer
    r3c1, r3c2 = st.columns(2)
    with r3c1:
        phone_raw = st.text_input("Mobile Number", placeholder="050xxxxxxx", key="quo_phone")
        client_phone = format_phone_input(phone_raw)
        if client_phone:
            st.success(f" {client_phone}")
    with r3c2:
        st.write("")  # keep grid aligned

    # ---------- ITEMS (same logic/visuals as Quotation) ----------
    if "invoice_table" not in st.session_state:
        st.session_state.invoice_table = pd.DataFrame(columns=[
            "Item No","Product / Device","Description","Qty","Unit Price (AED)","Line Total (AED)","Warranty (Years)"
        ])

    st.markdown("---")
    st.markdown("<div class='section-title'>Add Product</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="product-header">
      <span>Product / Device</span>
      <span>Qty</span>
      <span>Unit Price</span>
      <span>Line Total</span>
      <span>Warranty</span>
      <span>Action</span>
    </div>
    """, unsafe_allow_html=True)

    df = st.session_state.invoice_table.copy()
    if not df.empty:
        for i, row in df.iterrows():
            cols = st.columns([4.5, 0.7, 1, 1, 0.7, 0.7])
            with cols[0]:
                st.markdown(f"<div class='added-product-row'><b>✓ {row['Product / Device']}</b></div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"<div class='added-product-row'><span class='product-value'>{int(row['Qty'])}</span></div>", unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"<div class='added-product-row'><span class='product-value'>{row['Unit Price (AED)']:.2f}</span></div>", unsafe_allow_html=True)
            with cols[3]:
                st.markdown(
                    f"<div class='added-product-row'><span class='product-value'>AED {row['Line Total (AED)']:.2f}</span></div>",
                    unsafe_allow_html=True
                )
            with cols[4]:
                st.markdown(f"<div class='added-product-row'><span class='product-value'>{int(row['Warranty (Years)'])} yr</span></div>", unsafe_allow_html=True)
            with cols[5]:
                if st.button("❌", key=f"delete_{i}"):
                    st.session_state.invoice_table = st.session_state.invoice_table.drop(i).reset_index(drop=True)
                    st.session_state.invoice_table["Item No"] = range(1, len(st.session_state.invoice_table)+1)
                    st.rerun()

    e = st.columns([4.5, 0.7, 1, 1, 0.7, 0.7])
    with e[0]:
        product = st.selectbox("Product", catalog["Device"], key="add_prod", label_visibility="collapsed")
        row = catalog[catalog["Device"] == product].iloc[0]
        desc = row["Description"]
    # Sync defaults when product changes
    if st.session_state.get("last_prod_inv") != product:
        st.session_state["price_inv"] = float(row["UnitPrice"])
        st.session_state["war_inv"] = int(row["Warranty"])
        st.session_state["qty_inv"] = 1
        st.session_state["last_prod_inv"] = product

    with e[1]:
        qty = st.number_input("Qty", min_value=1, value=st.session_state.get("qty_inv", 1), step=1, label_visibility="collapsed", key="qty_inv")
    with e[2]:
        price = st.number_input("Unit Price (AED)", value=st.session_state.get("price_inv", float(row["UnitPrice"])), step=10.0, label_visibility="collapsed", key="price_inv")
    line_total = qty * price
    with e[3]:
        st.markdown(
            f"<div class='added-product-row'><span class='product-value'>AED {line_total:.2f}</span></div>",
            unsafe_allow_html=True
        )
    with e[4]:
        warranty = st.number_input("Warranty (Years)", min_value=0, value=st.session_state.get("war_inv", int(row["Warranty"])), step=1, label_visibility="collapsed", key="war_inv")
    with e[5]:
        if st.button("✅", key="add_inv_btn"):
            new_item = {
                "Item No": len(st.session_state.invoice_table) + 1,
                "Product / Device": product,
                "Description": desc,
                "Qty": qty,
                "Unit Price (AED)": price,
                "Line Total (AED)": line_total,
                "Warranty (Years)": warranty,
            }
            st.session_state.invoice_table = pd.concat([st.session_state.invoice_table, pd.DataFrame([new_item])], ignore_index=True)
            st.rerun()

    # ---------- SUMMARY ----------
    st.markdown("---")
    
    # Two columns: Summary Table (left) | Installation & Discount (right)
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("<div class='section-title'>Project Costs</div>", unsafe_allow_html=True)
        
        # Professional summary table (like receipt)
        product_total = st.session_state.invoice_table["Line Total (AED)"].sum()
        
        # Calculate installation/discount (needs to be defined before display)
        installation_cost = st.session_state.get("install_cost_inv_value", 0.0)
        discount_value = st.session_state.get("disc_value_inv_value", 0.0)
        discount_percent = st.session_state.get("disc_percent_inv_value", 0.0)
        
        percent_value = (product_total + installation_cost) * (discount_percent / 100)
        total_discount = percent_value + discount_value
        grand_total = (product_total + installation_cost) - total_discount
        
        st.markdown("""
        <div style='background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:16px;'>
            <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border-soft);'>
                <span style='font-weight:600;color:var(--text-soft);'>Price (AED)</span>
                <span style='font-weight:700;color:var(--text);'>{:,.2f} AED</span>
            </div>
            <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border-soft);'>
                <span style='font-weight:600;color:var(--text-soft);'>Installation & Operation Devices</span>
                <span style='font-weight:700;color:var(--text);'>{:,.2f} AED</span>
            </div>
            <div style='display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border-soft);'>
                <span style='font-weight:600;color:var(--text-soft);'>Discount</span>
                <span style='font-weight:700;color:var(--text);'>-{:,.2f} AED</span>
            </div>
            <div style='display:flex;justify-content:space-between;padding:15px 0;background:var(--bg-input);margin-top:8px;border-radius:8px;padding-left:12px;padding-right:12px;'>
                <span style='font-weight:700;font-size:16px;color:var(--text);'>TOTAL AMOUNT</span>
                <span style='font-weight:700;font-size:18px;color:var(--text);'>{:,.2f} AED</span>
            </div>
        </div>
        """.format(product_total, installation_cost, total_discount, grand_total), unsafe_allow_html=True)
    
    with col_right:
        st.markdown("<div class='section-title'>Installation & Discount</div>", unsafe_allow_html=True)
        
        # Installation Cost
        installation_cost = st.number_input("Installation & Operation Devices (AED)", min_value=0.0, step=50.0, key="install_cost_inv")
        st.session_state["install_cost_inv_value"] = installation_cost
        
        # Discount section
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        cD1, cD2 = st.columns(2)
        with cD1:
            discount_value = st.number_input("Discount Value (AED)", min_value=0.0, key="disc_value_inv")
            st.session_state["disc_value_inv_value"] = discount_value
        with cD2:
            discount_percent = st.number_input("Discount %", min_value=0.0, max_value=100.0, key="disc_percent_inv")
            st.session_state["disc_percent_inv_value"] = discount_percent

    # ======================================================
    #      SAVE + EXPORT WORD
    # ======================================================
    def generate_word_invoice(template, data):
        doc = Document(template)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for k, v in data.items():
                        if k in cell.text:
                            safe_v = "" if v is None else str(v)
                            cell.text = cell.text.replace(k, safe_v)
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf

    st.markdown("---")
    st.markdown('<div class="section-title">Export Invoice</div>', unsafe_allow_html=True)

    # Recalculate for download (same logic as UI summary)
    formatted_phone = format_phone_input(phone_raw) or phone_raw
    product_total = st.session_state.invoice_table["Line Total (AED)"].sum()
    installation_cost = st.session_state.get("install_cost_inv_value", 0.0)
    discount_value = st.session_state.get("disc_value_inv_value", 0.0)
    discount_percent = st.session_state.get("disc_percent_inv_value", 0.0)
    percent_value = (product_total + installation_cost) * (discount_percent / 100)
    total_discount = percent_value + discount_value
    grand_total = (product_total + installation_cost) - total_discount

    data = {
        "{{client_name}}": client_name,
        "{{invoice_no}}": invoice_no,
        "{{client_location}}": client_location,
        "{{client_phone}}": formatted_phone,
        "{{total_products}}": f"{product_total:,.2f}",
        "{{installation}}": f"{installation_cost:,.2f}",
        "{{discount_value}}": f"{discount_value:,.2f}",
        "{{discount_percent}}": f"{discount_percent:,.0f}",
        "{{grand_total}}": f"{grand_total:,.2f}",
    }

    try:
        word_file = generate_word_invoice("data/invoice_template.docx", data)

        clicked = st.download_button(
            label="Download Invoice (Word)",
            data=word_file,
            file_name=f"Invoice_{invoice_no}.docx"
        )

        if clicked:
            # Determine base_id linkage
            base_id = None
            if mode == "From Quotation":
                try:
                    q_row = records[records["number"] == st.session_state.get("q_select_inline")].iloc[0]
                    base_id = q_row.get("base_id", None)
                except Exception:
                    base_id = None
            if not base_id:
                # Generate a new base id for standalone invoices
                today_id = datetime.today().strftime('%Y%m%d')
                same_day = records[records.get("base_id", "").astype(str).str.contains(today_id, na=False)] if not records.empty else pd.DataFrame()
                seq = len(same_day) + 1
                base_id = f"{today_id}-{str(seq).zfill(3)}"

            try:
                save_record({
                    "base_id": base_id,
                    "date": datetime.today().strftime('%Y-%m-%d'),
                    "type": "i",
                    "number": invoice_no,
                    "amount": grand_total,
                    "client_name": client_name,
                    "phone": phone_raw,
                    "location": client_location,
                    "note": st.session_state.get("q_select_inline") or ""
                })
                # Auto-add/update the customer so future quotations/invoices link to same record
                upsert_customer_from_invoice(client_name, phone_raw, client_location)
                st.success(f"✅ Saved to records as base {base_id}")
            except Exception as e:
                st.warning(f"⚠️ Downloaded, but failed to save record: {e}")
    except Exception as e:
        st.error(f"❌ Unable to generate Word file: {e}")
