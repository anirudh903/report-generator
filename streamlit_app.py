import streamlit as st
import json
import pandas as pd
import os
from main import generate_report, generate_report_from_df

# Page Config
st.set_page_config(page_title="Kychens Report Generator", page_icon="🍳", layout="wide")

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
    3. Paste your `GEMINI_API_KEY` and `GCP_JSON` from your local `secrets.toml`.
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
            st.dataframe(df.head(), use_container_width=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")

else:  # Google Sheets Mode
    st.info("🔗 Provide your Google Sheet URL or Name. Note: The Service Account must have access to the sheet.")
    sheet_link = st.text_input("Google Sheet URL or Name", placeholder="https://docs.google.com/spreadsheets/d/...")
    
    try:
        creds_json = st.secrets.get("GCP_JSON")
        if not creds_json:
            st.warning("GCP_JSON secret not found. Please configure your Google Service Account keys.")
            st.stop()
        creds = json.loads(creds_json)
    except Exception as e:
        st.error(f"Error loading secrets: {e}")
        st.stop()

# Report Generation Section
st.divider()

current_brands = []
current_locations = []

if mode == "🌐 Google Sheets" and sheet_link:
    try:
        with st.spinner("Fetching available brands and locations..."):
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            from oauth2client.service_account import ServiceAccountCredentials
            import gspread
            creds_obj = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
            client = gspread.authorize(creds_obj)
            
            # Use same logic as main.py for sheet finding
            try:
                if "docs.google.com/spreadsheets" in sheet_link:
                    sheet = client.open_by_url(sheet_link).get_worksheet(0)
                else:
                    sheet = client.open(sheet_link).get_worksheet(0)
            except:
                st.error("Could not access the Google Sheet. Please check the URL and sharing permissions.")
                st.stop()
                
            df = pd.DataFrame(sheet.get_all_records())
            # Clean columns
            df.columns = [str(c).strip() for c in df.columns]
            brand_col = next((c for c in df.columns if c.lower() in ['brand', 'brand name', 'company', 'restaurant']), None)
            loc_col = next((c for c in df.columns if c.lower() in ['location', 'store', 'outlet', 'city', 'area']), None)
            
            if brand_col and loc_col:
                current_brands = sorted([str(b).strip() for b in df[brand_col].unique() if b])
                current_locations = sorted([str(l).strip() for l in df[loc_col].unique() if l])
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")

elif mode == "📁 Upload Excel/CSV" and df is not None:
    # Clean columns
    df.columns = [str(c).strip() for c in df.columns]
    brand_col = next((c for c in df.columns if c.lower() in ['brand', 'brand name', 'company', 'restaurant']), None)
    loc_col = next((c for c in df.columns if c.lower() in ['location', 'store', 'outlet', 'city', 'area']), None)
    
    if brand_col and loc_col:
        current_brands = sorted([str(b).strip() for b in df[brand_col].unique() if b])
        current_locations = sorted([str(l).strip() for l in df[loc_col].unique() if l])

col1, col2 = st.columns(2)
with col1:
    if current_brands:
        brand = st.selectbox("Select Brand", options=current_brands)
    else:
        brand = st.text_input("Brand Name", placeholder="Upload data to see list", disabled=True)
with col2:
    if current_locations and brand:
        # Show only locations available for the selected brand
        if brand_col and loc_col:
            brand_mask = df[brand_col].astype(str).str.strip() == brand
            relevant_locs = sorted([str(l).strip() for l in df[brand_mask][loc_col].unique() if l])
            location = st.selectbox("Select Location", options=relevant_locs)
        else:
            location = st.selectbox("Select Location", options=current_locations)
    else:
        location = st.text_input("Location", placeholder="Select brand first", disabled=True)

if st.button("🚀 Generate & Download Report"):
    if not brand or not location:
        st.warning("Please provide both Brand and Location.")
    else:
        try:
            with st.spinner("Generating report..."):
                if mode == "📁 Upload Excel/CSV":
                    if df is not None:
                        pdf, email = generate_report_from_df(df, brand, location)
                    else:
                        st.error("Please upload a file first.")
                        st.stop()
                else:
                    if not sheet_link:
                        st.error("Please provide a Google Sheet URL or Name.")
                        st.stop()
                    pdf, email = generate_report(brand, location, creds, sheet_link)
                
                st.success(f"Report generated! Send to: {email}")
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf,
                    file_name=f"{brand}_{location}_report.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")

st.divider()
st.caption("Kychens Intelligence System v1.1 • Simple & Powerful")
