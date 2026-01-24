import streamlit as st
import json
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from main import generate_report_from_df

# Page Config
st.set_page_config(page_title="Kytchens Report Generator", page_icon="🍳", layout="wide")

# --- Cloud Doctor: Safety Checks ---
SECRET_CHECK = True
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    else:
        SECRET_CHECK = False
except Exception:
    SECRET_CHECK = False

if not SECRET_CHECK:
    st.error("🔑 **Required Setup: Secrets Missing**")
    st.info("Please add your API keys to the Streamlit Secrets Dashboard.")
    st.stop()

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #6366f1; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# App Header
col_logo, col_text = st.columns([1, 6])
with col_logo:
    if os.path.exists("streamlit_logo.png"):
        st.image("streamlit_logo.png", width=100)
with col_text:
    st.title("Kytchens report generator")
st.subheader("Professional AI-Powered Report Portal")

# Sidebar for Settings
st.sidebar.title("Settings")
mode = st.sidebar.radio("Data Source", ["📁 Upload Excel/CSV", "🌐 Google Sheets"])

df = None

if mode == "📁 Upload Excel/CSV":
    uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success("File uploaded!")
        except Exception as e:
            st.error(f"Error: {e}")

else:  # Google Sheets Mode
    sheet_url = st.text_input("Google Sheet URL", placeholder="https://docs.google.com/spreadsheets/d/...")
    
    if sheet_url:
        try:
            # 1. Get raw creds from secrets
            # We try both the new flattened format and the old GCP_JSON format
            if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                creds_dict = dict(st.secrets["connections"]["gsheets"])
            elif "GCP_JSON" in st.secrets:
                creds_dict = json.loads(st.secrets["GCP_JSON"])
            else:
                st.error("GCP credentials not found in secrets.")
                st.stop()
            
            # 2. Fix private key formatting
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
            # 3. Connect via gspread (More reliable than the st-gsheets-connection for some keys)
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            
            with st.spinner("Connecting..."):
                sheet = client.open_by_url(sheet_url).get_worksheet(0)
                df = pd.DataFrame(sheet.get_all_records())
            st.success("Connected to Google Sheets!")
        except Exception as e:
            st.error(f"Connection Failed: {e}")
            st.info("💡 **Common Fix:** Share your sheet with: " + creds_dict.get('client_email', 'the email in your JSON'))

# Report Generation
st.divider()
if df is not None:
    df.columns = [str(c).strip() for c in df.columns]
    brand_col = next((c for c in df.columns if c.lower() in ['brand', 'brand name', 'company', 'restaurant']), None)
    loc_col = next((c for c in df.columns if c.lower() in ['location', 'store', 'outlet', 'city', 'area']), None)
    
    if brand_col and loc_col:
        current_brands = sorted([str(b).strip() for b in df[brand_col].unique() if b])
        col1, col2 = st.columns(2)
        with col1: brand = st.selectbox("Select Brand", options=current_brands)
        with col2:
            brand_mask = df[brand_col].astype(str).str.strip() == brand
            relevant_locs = sorted([str(l).strip() for l in df[brand_mask][loc_col].unique() if l])
            location = st.selectbox("Select Location", options=relevant_locs)
                
        if st.button("🚀 Generate & Download Report"):
            try:
                pdf, email = generate_report_from_df(df, brand, location)
                st.success(f"Generated! Sent to: {email}")
                st.download_button("📥 Download PDF", data=pdf, file_name=f"{brand}_{location}.pdf", mime="application/pdf")
            except Exception as e: st.error(f"Error: {e}")
    else: st.warning(f"Could not find Brand/Location columns.")
else: st.info("Please provide a data source to begin.")

st.caption("Kychens Intelligence System v1.3")
