import streamlit as st
import json
import pandas as pd
import os
from main import generate_report_from_df
from streamlit_gsheets import GSheetsConnection

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
    st.info("""
    To run this app in the cloud, you must add your API keys to the Streamlit Secret Dashboard:
    1. Go to your **Streamlit App Dashboard**.
    2. Click **Settings** > **Secrets**.
    3. Paste your `GEMINI_API_KEY` and `GCP_JSON` (or the new [connections.gsheets] format) from your local `secrets.toml`.
    """)
    st.stop()

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #6366f1;
        color: white;
        font-weight: bold;
    }
    .upload-section {
        border: 2px dashed #6366f1;
        padding: 20px;
        border-radius: 15px;
        background-color: #f0f7ff;
    }
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
    st.info("Upload an Excel or CSV file with columns: Brand, Location, Orders, Errors, KPT, Manager_Email")
    uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "csv"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")

else:  # Google Sheets Mode
    st.info("🔗 Provide your Google Sheet URL. Note: The Service Account must have access to the sheet.")
    sheet_url = st.text_input("Google Sheet URL", 
                             placeholder="https://docs.google.com/spreadsheets/d/...",
                             value=st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet", ""))
    
    if sheet_url:
        try:
            # --- CONNECTION HEALING ---
            # Streamlit Community Cloud sometimes double-escapes common keys. Let's fix it manually.
            g_creds = dict(st.secrets["connections"]["gsheets"])
            if "private_key" in g_creds:
                # Ensure literal newlines are correctly formatted
                g_creds["private_key"] = g_creds["private_key"].replace("\\n", "\n")
            
            conn = st.connection("gsheets", type=GSheetsConnection, **g_creds)
            # --------------------------
            
            with st.spinner("Connecting to Google Sheets..."):
                df = conn.read(spreadsheet=sheet_url, ttl=0)
            st.success("Connected to Google Sheets!")
            if st.checkbox("Show Sheet Data Preview"):
                st.dataframe(df.head(), use_container_width=True)
        except Exception as e:
            st.error(f"Error connecting to Google Sheets: {e}")
            st.warning("⚠️ **Tip:** This '401 Unauthorized' usually means the Google Service Account doesn't have access to your sheet. Share your sheet with the client_email found in your JSON key.")
    else:
        st.warning("Please paste a Google Sheet URL to proceed.")

# Report Generation Section
st.divider()

current_brands = []
current_locations = []

if df is not None:
    # Clean the DataFrame columns for consistent matching
    df.columns = [str(c).strip() for c in df.columns]
    
    # Identify key columns using the same logic as main.py
    brand_col = next((c for c in df.columns if c.lower() in ['brand', 'brand name', 'company', 'restaurant']), None)
    loc_col = next((c for c in df.columns if c.lower() in ['location', 'store', 'outlet', 'city', 'area']), None)
    
    if brand_col and loc_col:
        current_brands = sorted([str(b).strip() for b in df[brand_col].unique() if b])
        
        col1, col2 = st.columns(2)
        with col1:
            brand = st.selectbox("Select Brand", options=current_brands)
        with col2:
            if brand:
                brand_mask = df[brand_col].astype(str).str.strip() == brand
                relevant_locs = sorted([str(l).strip() for l in df[brand_mask][loc_col].unique() if l])
                location = st.selectbox("Select Location", options=relevant_locs)
            else:
                location = st.selectbox("Select Location", options=[], disabled=True)
                
        if st.button("🚀 Generate & Download Report"):
            try:
                with st.spinner("Generating report..."):
                    pdf, email = generate_report_from_df(df, brand, location)
                    
                    st.success(f"Report generated! Send to: {email}")
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf,
                        file_name=f"{brand}_{location}_report.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning(f"Could not find Brand or Location columns in the data. Found: {list(df.columns)}")
else:
    st.info("Please provide a data source (Upload or Google Sheets) to begin.")

st.divider()
st.caption("Kychens Intelligence System v1.2 • Powered by Streamlit & Gemini")
