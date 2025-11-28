import streamlit as st
import os
from base64 import b64encode
from pages_custom.quotation_page import quotation_app
from pages_custom.invoice_page import invoice_app
from pages_custom.receipt_page import receipt_app
from pages_custom.dashboard_new import dashboard_new_app
from pages_custom.customers_page import customers_app
from pages_custom.products_page import products_app
from pages_custom.reports_page import reports_app
from pages_custom.settings_page import settings_app
from utils.auth import validate_pin, can_access_page, is_admin
from utils.logger import log_event

# ===========================
# THEME ENGINE (Light/Dark Toggle)
# ===========================
# Persist UI theme in session state
if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "light"

light_css = """
<style>
:root {
    --bg-primary: #F5F5F7;
    --bg-card: #FFFFFF;
    --bg-input: #FFFFFF;
    --bg-sidebar: #FFFFFF;

    --text: #1D1D1F;
    --text-soft: #6E6E73;

    --border: rgba(0,0,0,0.10);
    --border-soft: rgba(0,0,0,0.06);

    --button: #0A84FF;
    --button-hover: #5AC8FA;

    --accent: #0A84FF;

/* Selectbox (light) – colors only */
[data-baseweb="select"] > div {
    background: var(--bg-input) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
[data-baseweb="select"] span { color: var(--text) !important; }
[data-baseweb="popover"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    z-index: 9999 !important;
}
[data-baseweb="menu-item"]:hover {
    background: var(--button-hover) !important;
    color: var(--text) !important;
}
[data-baseweb="menu"] li,
[data-baseweb="menu"] div {
    color: var(--text) !important;
    background: var(--bg-card) !important;
}
[data-baseweb="menu-item"][aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}
</style>
"""

dark_css = """
<style>
:root {
    --bg-primary: #0D0F12;
    --bg-card: #1A1C20;
    --bg-input: #1D1F24;
    --bg-sidebar: #0F1115;

    --text: #F5F5F7;
    --text-soft: #9A9AA2;

    --border: #2B2D31;
    --border-soft: rgba(255,255,255,0.08);

    --button: #0A84FF;
    --button-hover: #5AC8FA;

    --accent: #0A84FF;
}

/* Selectbox (dark) – colors only */
[data-baseweb="select"] > div {
    background: var(--bg-input) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="select"] span { color: var(--text) !important; }
[data-baseweb="popover"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    z-index: 9999 !important;
}
[data-baseweb="menu-item"]:hover {
    background: var(--button-hover) !important;
    color: var(--text) !important;
}
[data-baseweb="menu"] li,
[data-baseweb="menu"] div {
    color: var(--text) !important;
    background: var(--bg-card) !important;
}
[data-baseweb="menu-item"][aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}
</style>
"""

def inject_theme():
    """Inject the currently selected theme CSS."""
    if st.session_state.ui_theme == "light":
        st.markdown(light_css, unsafe_allow_html=True)
    else:
        st.markdown(dark_css, unsafe_allow_html=True)


st.set_page_config(page_title="Newton Smart Home OS", layout="wide")

# ===========================
# PIN LOGIN SYSTEM
# ===========================
# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "show_pin" not in st.session_state:
    st.session_state.show_pin = False

# Show login screen if not authenticated
if not st.session_state.authenticated:
    st.markdown("""
        <div style='text-align:center; padding:60px 20px;'>
            <h1 style='color:var(--accent); font-size:48px; margin-bottom:10px;'>Secure Access</h1>
            <h2 style='color:var(--text);'>Newton Smart Home</h2>
            <p style='color:var(--text-soft);'>Enter your PIN to continue</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pin_input = st.text_input(
            "PIN",
            type="password" if not st.session_state.show_pin else "default",
            max_chars=6,
            placeholder="Enter 4-6 digit PIN",
            label_visibility="collapsed"
        )
        
        show_hide = st.checkbox("Show PIN", value=st.session_state.show_pin, key="show_pin_checkbox")
        if show_hide != st.session_state.show_pin:
            st.session_state.show_pin = show_hide
            st.rerun()
        
        if st.button("Login", use_container_width=True):
            user_data = validate_pin(pin_input)
            if user_data:
                st.session_state.authenticated = True
                st.session_state.user = user_data
                log_event(user_data["name"], "Login", "login_success", f"Role: {user_data['role']}")
                st.success(f"✅ Welcome, {user_data['name']}!")
                st.rerun()
            else:
                log_event("Unknown", "Login", "login_failed", f"Invalid PIN: {pin_input[:2]}***")
                st.error("❌ Invalid PIN. Please try again.")
        
        st.markdown("<div style='text-align:center; margin-top:40px; color:var(--text-soft); font-size:12px;'>Default PINs: Admin=1234, Staff=5678, Viewer=9999</div>", unsafe_allow_html=True)
    
    st.stop()

# User is authenticated - continue with app

# Load logo as data URI
def _load_logo_datauri():
    candidates = ["data/newton_logo.png", "data/newton_logo.svg", "data/logo.png", "data/logo.svg"]
    base = os.path.dirname(__file__)
    for rel in candidates:
        path = os.path.join(base, rel)
        if os.path.exists(path):
            ext = os.path.splitext(path)[1].lower()
            mime = "image/png" if ext == ".png" else "image/svg+xml" if ext == ".svg" else None
            if not mime:
                continue
            with open(path, "rb") as f:
                data = b64encode(f.read()).decode("utf-8")
            return f"data:{mime};base64,{data}"
    return None

st.markdown(
    """
    <style>
    :root { 
        --brand-blue:#0a84ff; /* kept for nav highlights */
        --accent:#0a84ff; --accent-light:#5ac8fa; 
        --ink:#1d1d1f; --sub:#6e6e73; 
        --glass:rgba(255,255,255,.95); --glass-border:rgba(0,0,0,.06);
        --text-primary:#1d1d1f;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg,#fafafa 0%,#f0f0f5 100%);
        font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--text-primary);
    }
    [data-testid="stHeader"] { background-color: transparent; }

    .hero-card{
        background: linear-gradient(135deg, rgba(255,255,255,.95) 0%, rgba(248,248,252,.92) 100%);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 28px 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,.04), 0 12px 32px rgba(0,0,0,.08);
        backdrop-filter: blur(20px);
        margin-bottom: 18px;
        overflow: visible;
        position: relative;
    }

    /* New header layout: left (page title) | center (nav buttons) | right (logo) */
    .header-container{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        margin-bottom: 12px;
        min-height: 80px;
    }
    
    .page-title-section{
        flex: 0 0 auto;
        min-width: 200px;
    }
    
    .page-title{
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.2;
    }
    
    .page-subtitle{
        font-size: 14px;
        color: #6e6e73;
        margin: 4px 0 0 0;
    }
    
    .nav-buttons-section{
        flex: 1;
        display: flex;
        justify-content: center;
        gap: 12px;
    }
    
    .logo-section{
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        min-width: 200px;
        position: absolute;
        right: -30px;
        top: 50%;
        transform: translateY(-50%);
    }
    
    .logo-badge{
        width: 350px;
        height: auto;
        max-height: none;
    }

    /* Compact vertical rhythm */
    [data-testid="block-container"]{ padding-top: 4px !important; }
    div[data-testid="element-container"]{ margin-bottom: 6px !important; }
    [data-testid="stButton"]{ margin-bottom: 0 !important; }

    /* Global compact buttons (match Invoice page sizing) */
    [data-testid="stButton"] > button{
        background: linear-gradient(145deg,#ffffff 0%,#f9f9fb 100%) !important;
        border: 1px solid rgba(0,0,0,.08) !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: var(--ink) !important;
        box-shadow: 0 2px 6px rgba(0,0,0,.05) !important;
        transition: all .18s ease !important;
        white-space: nowrap !important;
    }
    [data-testid="stButton"] > button:hover{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 14px rgba(0,0,0,.12) !important;
    }

    /* Uniform compact sizing for top nav buttons (4 cards) */
    button[key^="nav_"]{
        min-height: 44px !important;
        height: 44px !important;
        padding: 6px 14px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 12px !important;
        white-space: nowrap !important;
        font-size: 13px !important;
        line-height: 1 !important;
    }
    /* Sidebar items consistent height as well */
    button[key^="sidenav_"]{
        min-height: 44px !important;
        height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 12px !important;
        font-size: 0.93rem !important;
    }

    /* Global form controls to match Invoice  pages */
    /* جميع الحقول تعتمد فقط على متغيرات الثيم */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] select{
        background: var(--bg-input) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,.04) !important;
        height: 40px !important;
        outline: none !important;
        transition: border-color .12s ease, box-shadow .12s ease !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stSelectbox"] select:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(10,132,255,.12) !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stNumberInput"] input::placeholder{
        color: #9ca3af !important;
        opacity: 1 !important;
    }
    .stSelectbox div[data-baseweb="select"],
    .stSelectbox div[role="combobox"],
    .stSelectbox div[role="listbox"],
    .stSelectbox [role="option"]{
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[role="combobox"] > div{
        background: var(--bg-input) !important;
    }
    .stSelectbox div[data-baseweb="select"]:focus-within,
    .stSelectbox div[role="combobox"]:focus-within{
        background: var(--bg-input) !important;
    }
    .stSelectbox svg{ color: var(--text-soft) !important; }
    /* أزرار + و - تعتمد فقط على متغيرات الثيم */
    [data-testid="stNumberInput"] button {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
        transition: background .15s;
    }
    [data-testid="stNumberInput"] button:hover {
        background: var(--bg-input) !important;
    }
    .stSelectbox [role="option"][aria-selected="true"]{
        background:#f3f4f6 !important;
        color: var(--text-primary) !important;
    }

    /* Common utility classes from Invoice theme */
    .section-title{ font-size:20px; font-weight:700; margin:18px `0 10px; color:var(--ink); }
    .added-product-row{
        background:#ffffff; padding:10px 14px; border:1px solid rgba(0,0,0,.08);
        border-radius:12px; margin-bottom:6px; box-shadow:0 2px 6px rgba(0,0,0,.05);
    }
    .product-header{
        display:flex; gap:1rem; padding:8px 0 12px;
        border-bottom:1px solid rgba(0,0,0,.08); background:transparent;
        font-size:11px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:#86868b;
        margin-bottom:10px; align-items:center;
    }
    .product-header span{text-align:center;}
    .product-header span:nth-child(1){flex:4.5; text-align:left;}
    .product-header span:nth-child(2){flex:0.7;}
    .product-header span:nth-child(3){flex:1;}
    .product-header span:nth-child(4){flex:1;}
    .product-header span:nth-child(5){flex:0.7;}
    .product-header span:nth-child(6){flex:0.7;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Inject the selected theme AFTER app base CSS so theme wins in cascade
inject_theme()

# Base color mapping using variables (colors only; no sizes changed)
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background: var(--bg-primary) !important; color: var(--text) !important; }
    [data-testid="stHeader"] { color: var(--text) !important; }
    [data-testid="stSidebar"] { background: var(--bg-sidebar) !important; color: var(--text) !important; }

    .page-subtitle { color: var(--text-soft) !important; }
    .hero-card { background: var(--bg-card) !important; border: 1px solid var(--border-soft) !important; color: var(--text) !important; }

    /* Generic buttons (neutral). Keep geometry elsewhere; colors from variables */
    [data-testid=stButton] > button { background: var(--bg-card) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    [data-testid=stButton] > button:hover { background: var(--button-hover) !important; color: #ffffff !important; }

    /* Nav buttons (default neutral, active accent) */
    button[key^="nav_"] { background: var(--bg-card) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    button[key^="nav_"]:hover { background: var(--button-hover) !important; color: #ffffff !important; }

    /* Sidebar buttons (default neutral, active accent set below) */
    button[key^="sidenav_"] { background: var(--bg-card) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    button[key^="sidenav_"]:hover { background: var(--button-hover) !important; color: #ffffff !important; }

    /* Inputs */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] select,
    textarea, input, select {
        background: var(--bg-input) !important; color: var(--text) !important; border: 1px solid var(--border) !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stNumberInput"] input::placeholder { color: var(--text-soft) !important; }

    /* Streamlit Selectbox (BaseWeb) — ensure dropdown and control use variables */
    .stSelectbox div[data-baseweb="select"],
    .stSelectbox div[role="combobox"] {
        background: var(--bg-input) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }
    .stSelectbox div[data-baseweb="select"]:focus-within,
    .stSelectbox div[role="combobox"]:focus-within {
        border-color: var(--accent) !important;
    }
    .stSelectbox svg { color: var(--text) !important; }
    .stSelectbox [role="listbox"],
    .stSelectbox [role="option"],
    [data-baseweb="menu"],
    [data-baseweb="popover"] [role="listbox"] {
        background: var(--bg-card) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }
    .stSelectbox [role="option"][aria-selected="true"],
    .stSelectbox [role="option"]:hover {
        background: var(--button-hover) !important;
        color: #ffffff !important;
    }
    .stSelectbox [aria-placeholder="true"],
    .stSelectbox [data-baseweb="select"] [class*="placeholder"],
    .stSelectbox [role="combobox"] [class*="placeholder"] {
        color: var(--text-soft) !important;
    }

    /* Horizontal rule under subheaders or sections */
    [data-testid="stMarkdownContainer"] hr, hr { border: none !important; border-top: 1px solid var(--border-soft) !important; }

    /* Tables */
    [data-testid="stTable"] table { background: var(--bg-card) !important; color: var(--text) !important; }
    [data-testid="stTable"] th { color: var(--text-soft) !important; border-bottom: 1px solid var(--border) !important; }
    [data-testid="stTable"] td { color: var(--text) !important; border-bottom: 1px solid var(--border-soft) !important; }

    /* Utility */
    .section-title { color: var(--text) !important; }
    .added-product-row { background: var(--bg-card) !important; border: 1px solid var(--border-soft) !important; color: var(--text) !important; }
    .product-header { border-bottom: 1px solid var(--border-soft) !important; color: var(--text-soft) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "active_page" not in st.session_state:
    st.session_state.active_page = "dashboard"

# Page titles mapping
PAGE_TITLES = {
    "dashboard": ("Newton Dashboard", "Monitor live analytics"),
    "quotation": ("Newton Quotation", "Draft elegant proposals"),
    "invoice": ("Newton Invoice", "Bill with confidence"),
    "receipt": ("Newton Receipt", "Acknowledge payments"),
    "customers": ("Customers", "Manage client accounts"),
    "products": ("Products", "Manage catalog"),
    "reports": ("Reports", "Business insights"),
    "settings": ("Settings", "Configure application"),
}

# Single source of truth for emojis used across nav buttons
ICON_MAP = {
    "dashboard": "📊",
    "quotation": "📝",
    "invoice": "💳",
    "receipt": "🧾",
    "customers": "👥",
    "products": "📦",
    "reports": "📈",
    "settings": "⚙️",
    "logout": "🚪",
    "dark": "🌙",
    "light": "☀️",
}

# Load logo as data URI
def _load_logo_datauri():
    candidates = ["data/newton_logo.png", "data/newton_logo.svg", "data/logo.png", "data/logo.svg"]
    base = os.path.dirname(__file__)
    for rel in candidates:
        path = os.path.join(base, rel)
        if os.path.exists(path):
            ext = os.path.splitext(path)[1].lower()
            mime = "image/png" if ext == ".png" else "image/svg+xml" if ext == ".svg" else None
            if not mime:
                continue
            with open(path, "rb") as f:
                data = b64encode(f.read()).decode("utf-8")
            return f"data:{mime};base64,{data}"
    return None

st.markdown(
    """
    <style>
    :root { 
        --brand-blue:#0a84ff; /* kept for nav highlights */
        --accent:#0a84ff; --accent-light:#5ac8fa; 
        --ink:#1d1d1f; --sub:#6e6e73; 
        --glass:rgba(255,255,255,.95); --glass-border:rgba(0,0,0,.06);
        --text-primary:#1d1d1f;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg,#fafafa 0%,#f0f0f5 100%);
        font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--text-primary);
    }
    [data-testid="stHeader"] { background-color: transparent; }

    .hero-card{
        background: linear-gradient(135deg, rgba(255,255,255,.95) 0%, rgba(248,248,252,.92) 100%);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 28px 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,.04), 0 12px 32px rgba(0,0,0,.08);
        backdrop-filter: blur(20px);
        margin-bottom: 18px;
        overflow: visible;
        position: relative;
    }

    /* New header layout: left (page title) | center (nav buttons) | right (logo) */
    .header-container{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        margin-bottom: 12px;
        min-height: 80px;
    }
    
    .page-title-section{
        flex: 0 0 auto;
        min-width: 200px;
    }
    
    .page-title{
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.2;
    }
    
    .page-subtitle{
        font-size: 14px;
        color: #6e6e73;
        margin: 4px 0 0 0;
    }
    
    .nav-buttons-section{
        flex: 1;
        display: flex;
        justify-content: center;
        gap: 12px;
    }
    
    .logo-section{
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        min-width: 200px;
        position: absolute;
        right: -30px;
        top: 50%;
        transform: translateY(-50%);
    }
    
    .logo-badge{
        width: 350px;
        height: auto;
        max-height: none;
    }

    /* Compact vertical rhythm */
    [data-testid="block-container"]{ padding-top: 4px !important; }
    div[data-testid="element-container"]{ margin-bottom: 6px !important; }
    [data-testid="stButton"]{ margin-bottom: 0 !important; }

    /* Global compact buttons (match Invoice page sizing) */
    [data-testid="stButton"] > button{
        background: linear-gradient(145deg,#ffffff 0%,#f9f9fb 100%) !important;
        border: 1px solid rgba(0,0,0,.08) !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: var(--ink) !important;
        box-shadow: 0 2px 6px rgba(0,0,0,.05) !important;
        transition: all .18s ease !important;
        white-space: nowrap !important;
    }
    [data-testid="stButton"] > button:hover{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 14px rgba(0,0,0,.12) !important;
    }

    /* Uniform compact sizing for top nav buttons (4 cards) */
    button[key^="nav_"]{
        min-height: 44px !important;
        height: 44px !important;
        padding: 6px 14px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 12px !important;
        white-space: nowrap !important;
        font-size: 13px !important;
        line-height: 1 !important;
    }
    /* Sidebar items consistent height as well */
    button[key^="sidenav_"]{
        min-height: 44px !important;
        height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 12px !important;
        font-size: 0.93rem !important;
    }

    /* Global form controls to match Invoice  pages */
    /* جميع الحقول تعتمد فقط على متغيرات الثيم */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] select{
        background: var(--bg-input) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,.04) !important;
        height: 40px !important;
        outline: none !important;
        transition: border-color .12s ease, box-shadow .12s ease !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stSelectbox"] select:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(10,132,255,.12) !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stNumberInput"] input::placeholder{
        color: #9ca3af !important;
        opacity: 1 !important;
    }
    .stSelectbox div[data-baseweb="select"],
    .stSelectbox div[role="combobox"],
    .stSelectbox div[role="listbox"],
    .stSelectbox [role="option"]{
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[role="combobox"] > div{
        background: var(--bg-input) !important;
    }
    .stSelectbox div[data-baseweb="select"]:focus-within,
    .stSelectbox div[role="combobox"]:focus-within{
        background: var(--bg-input) !important;
    }
    .stSelectbox svg{ color: var(--text-soft) !important; }
    /* أزرار + و - تعتمد فقط على متغيرات الثيم */
    [data-testid="stNumberInput"] button {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
        transition: background .15s;
    }
    [data-testid="stNumberInput"] button:hover {
        background: var(--bg-input) !important;
    }
    .stSelectbox [role="option"][aria-selected="true"]{
        background:#f3f4f6 !important;
        color: var(--text-primary) !important;
    }

    /* Common utility classes from Invoice theme */
    .section-title{ font-size:20px; font-weight:700; margin:18px `0 10px; color:var(--ink); }
    .added-product-row{
        background:#ffffff; padding:10px 14px; border:1px solid rgba(0,0,0,.08);
        border-radius:12px; margin-bottom:6px; box-shadow:0 2px 6px rgba(0,0,0,.05);
    }
    .product-header{
        display:flex; gap:1rem; padding:8px 0 12px;
        border-bottom:1px solid rgba(0,0,0,.08); background:transparent;
        font-size:11px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:#86868b;
        margin-bottom:10px; align-items:center;
    }
    .product-header span{text-align:center;}
    .product-header span:nth-child(1){flex:4.5; text-align:left;}
    .product-header span:nth-child(2){flex:0.7;}
    .product-header span:nth-child(3){flex:1;}
    .product-header span:nth-child(4){flex:1;}
    .product-header span:nth-child(5){flex:0.7;}
    .product-header span:nth-child(6){flex:0.7;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Inject the selected theme AFTER app base CSS so theme wins in cascade
inject_theme()

# Base color mapping using variables (colors only; no sizes changed)
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background: var(--bg-primary) !important; color: var(--text) !important; }
    [data-testid="stHeader"] { color: var(--text) !important; }
    [data-testid="stSidebar"] { background: var(--bg-sidebar) !important; color: var(--text) !important; }

    .page-subtitle { color: var(--text-soft) !important; }
    .hero-card { background: var(--bg-card) !important; border: 1px solid var(--border-soft) !important; color: var(--text) !important; }

    /* Generic buttons (neutral). Keep geometry elsewhere; colors from variables */
    [data-testid=stButton] > button { background: var(--bg-card) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    [data-testid=stButton] > button:hover { background: var(--button-hover) !important; color: #ffffff !important; }

    /* Nav buttons (default neutral, active accent) */
    button[key^="nav_"] { background: var(--bg-card) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    button[key^="nav_"]:hover { background: var(--button-hover) !important; color: #ffffff !important; }

    /* Sidebar buttons (default neutral, active accent set below) */
    button[key^="sidenav_"] { background: var(--bg-card) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    button[key^="sidenav_"]:hover { background: var(--button-hover) !important; color: #ffffff !important; }

    /* Inputs */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] select,
    textarea, input, select {
        background: var(--bg-input) !important; color: var(--text) !important; border: 1px solid var(--border) !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stNumberInput"] input::placeholder { color: var(--text-soft) !important; }

    /* Streamlit Selectbox (BaseWeb) — ensure dropdown and control use variables */
    .stSelectbox div[data-baseweb="select"],
    .stSelectbox div[role="combobox"] {
        background: var(--bg-input) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }
    .stSelectbox div[data-baseweb="select"]:focus-within,
    .stSelectbox div[role="combobox"]:focus-within {
        border-color: var(--accent) !important;
    }
    .stSelectbox svg { color: var(--text) !important; }
    .stSelectbox [role="listbox"],
    .stSelectbox [role="option"],
    [data-baseweb="menu"],
    [data-baseweb="popover"] [role="listbox"] {
        background: var(--bg-card) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }
    .stSelectbox [role="option"][aria-selected="true"],
    .stSelectbox [role="option"]:hover {
        background: var(--button-hover) !important;
        color: #ffffff !important;
    }
    .stSelectbox [aria-placeholder="true"],
    .stSelectbox [data-baseweb="select"] [class*="placeholder"],
    .stSelectbox [role="combobox"] [class*="placeholder"] {
        color: var(--text-soft) !important;
    }

    /* Horizontal rule under subheaders or sections */
    [data-testid="stMarkdownContainer"] hr, hr { border: none !important; border-top: 1px solid var(--border-soft) !important; }

    /* Tables */
    [data-testid="stTable"] table { background: var(--bg-card) !important; color: var(--text) !important; }
    [data-testid="stTable"] th { color: var(--text-soft) !important; border-bottom: 1px solid var(--border) !important; }
    [data-testid="stTable"] td { color: var(--text) !important; border-bottom: 1px solid var(--border-soft) !important; }

    /* Utility */
    .section-title { color: var(--text) !important; }
    .added-product-row { background: var(--bg-card) !important; border: 1px solid var(--border-soft) !important; color: var(--text) !important; }
    .product-header { border-bottom: 1px solid var(--border-soft) !important; color: var(--text-soft) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "active_page" not in st.session_state:
    st.session_state.active_page = "dashboard"

# Page titles mapping
PAGE_TITLES = {
    "dashboard": ("Newton Dashboard", "Monitor live analytics"),
    "quotation": ("Newton Quotation", "Draft elegant proposals"),
    "invoice": ("Newton Invoice", "Bill with confidence"),
    "receipt": ("Newton Receipt", "Acknowledge payments"),
    "customers": ("Customers", "Manage client accounts"),
    "products": ("Products", "Manage catalog"),
    "reports": ("Reports", "Business insights"),
    "settings": ("Settings", "Configure application"),
}

# Single source of truth for emojis used across nav buttons
ICON_MAP = {
    "dashboard": "📊",
    "quotation": "📝",
    "invoice": "💳",
    "receipt": "🧾",
    "customers": "👥",
    "products": "📦",
    "reports": "📈",
    "settings": "⚙️",
    "logout": "🚪",
    "dark": "🌙",
    "light": "☀️",
}

# Load logo
_logo_uri = _load_logo_datauri()
_logo_html = f'<img src="{_logo_uri}" alt="Newton Smart Home" class="logo-badge" />' if _logo_uri else '<div style="width:120px;height:80px;background:linear-gradient(135deg,#0a84ff,#5bc0ff);border-radius:16px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:18px;">NEWTON</div>'

# Get current page info
current_title, current_subtitle = PAGE_TITLES.get(st.session_state.active_page, ("Dashboard", "Monitor live analytics"))

# Header structure
st.markdown(
    f"""
    <div class="hero-card">
        <div class="header-container">
            <div class="page-title-section">
                <h1 class="page-title">{current_title}</h1>
                <p class="page-subtitle">{current_subtitle}</p>
            </div>
            <div class="nav-buttons-section" id="nav-buttons-placeholder"></div>
            <div class="logo-section">
                {_logo_html}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar navigation (mirrors top nav)
with st.sidebar:
    # User info and logout
    user = st.session_state.get("user", {})
    user_name = user.get("name", "User")
    user_role = user.get("role", "viewer")
    
    st.markdown(f"""
        <div style='padding:12px; background:var(--bg-card); border-radius:12px; margin-bottom:16px; border:1px solid var(--border-soft);'>
            <div style='font-weight:600; color:var(--text);'>User: {user_name}</div>
            <div style='font-size:12px; color:var(--text-soft); margin-top:4px;'>Role: {user_role.title()}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"{ICON_MAP['logout']} Logout", use_container_width=True, key="logout_btn"):
        log_event(user_name, "System", "logout", f"User logged out")
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()
    
    st.markdown("---")
    
    # Theme toggle
    if st.session_state.ui_theme == "light":
        if st.button(f"{ICON_MAP['dark']} Dark Mode", key="toggle_dark"):
            st.session_state.ui_theme = "dark"
            st.rerun()
    else:
        if st.button(f"{ICON_MAP['light']} Light Mode", key="toggle_light"):
            st.session_state.ui_theme = "light"
            st.rerun()

    st.markdown("<div style='font-weight:700;margin:6px 0;color:#0f172a;'>Navigation</div>", unsafe_allow_html=True)
    _side_nav_items = [
        ("dashboard", f"{ICON_MAP['dashboard']} Dashboard"),
        ("quotation", f"{ICON_MAP['quotation']} Quotation"),
        ("invoice", f"{ICON_MAP['invoice']} Invoice"),
        ("receipt", f"{ICON_MAP['receipt']} Receipt"),
        ("customers", f"{ICON_MAP['customers']} Customers"),
        ("products", f"{ICON_MAP['products']} Products"),
        ("reports", f"{ICON_MAP['reports']} Reports"),
        ("settings", f"{ICON_MAP['settings']} Settings"),
    ]
    for page_id, title in _side_nav_items:
        # Check if user has access to this page
        if not can_access_page(user, page_id):
            # Show disabled button for pages without access
            st.markdown(f"<div style='padding:8px; color:var(--text-soft); opacity:0.5;'>{title} (Locked)</div>", unsafe_allow_html=True)
        else:
            if st.button(title, key=f"sidenav_{page_id}", use_container_width=True):
                st.session_state.active_page = page_id
                st.rerun()

    

# Navigation buttons (will appear in the center)
NAV_ITEMS = [
    ("dashboard", f"{ICON_MAP['dashboard']} Dashboard"),
    ("quotation", f"{ICON_MAP['quotation']} Quotation"),
    ("invoice", f"{ICON_MAP['invoice']} Invoice"),
    ("receipt", f"{ICON_MAP['receipt']} Receipt"),
]

nav_cols = st.columns(4)
for col, (page_id, title) in zip(nav_cols, NAV_ITEMS):
    with col:
        pressed = st.button(title, key=f"nav_{page_id}", use_container_width=True)
        if pressed:
            st.session_state.active_page = page_id
            st.rerun()

st.markdown(
    f"""
    <style>
    button[key="nav_{st.session_state.active_page}"] {{
        background: var(--accent) !important;
        color: #ffffff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ===========================
# PAGE ACCESS CONTROL
# ===========================
current_page = st.session_state.active_page
user = st.session_state.get("user", {})

# Check if user has access to current page
if not can_access_page(user, current_page):
    log_event(user.get("name", "Unknown"), current_page, "access_denied", f"Attempted to access {current_page}")
    st.error("Access Denied")
    st.warning(f"You don't have permission to access the **{current_page.title()}** page.")
    st.info(f"Your role: **{user.get('role', 'unknown').title()}**")
    st.markdown("Please contact an administrator if you need access to this page.")
    st.stop()

# Log successful page access
log_event(user.get("name", "Unknown"), current_page, "access_granted", f"Opened {current_page} page")

if st.session_state.active_page == "dashboard":
    dashboard_new_app()
elif st.session_state.active_page == "quotation":
    quotation_app()
elif st.session_state.active_page == "invoice":
    invoice_app()
elif st.session_state.active_page == "receipt":
    receipt_app()
elif st.session_state.active_page == "customers":
    customers_app()
elif st.session_state.active_page == "products":
    products_app()
elif st.session_state.active_page == "reports":
    reports_app()
elif st.session_state.active_page == "settings":
    settings_app()
elif st.session_state.active_page == "settings":
    settings_app()
