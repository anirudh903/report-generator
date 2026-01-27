import streamlit as st
import json
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from main import generate_report_from_df, send_email

# Page Config
st.set_page_config(page_title="Kytchens Report Generator", page_icon="logo.jpg", layout="wide")

# --- Cloud Doctor: Safety Checks ---
SECRET_CHECK = True
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    else:
        SECRET_CHECK = False
    
    # Sync Email Secrets
    if "EMAIL_USER" in st.secrets: os.environ["EMAIL_USER"] = st.secrets["EMAIL_USER"]
    if "EMAIL_PASS" in st.secrets: os.environ["EMAIL_PASS"] = st.secrets["EMAIL_PASS"]
except Exception:
    SECRET_CHECK = False

if not SECRET_CHECK:
    st.error("🔑 **Required Setup: Secrets Missing**")
    st.info("Please add GEMINI_API_KEY, EMAIL_USER, and EMAIL_PASS to your Streamlit secrets.")
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
            if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                creds_dict = dict(st.secrets["connections"]["gsheets"])
            elif "GCP_JSON" in st.secrets:
                creds_dict = json.loads(st.secrets["GCP_JSON"])
            else:
                st.error("GCP credentials not found in secrets.")
                st.stop()
            
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            
            with st.spinner("Connecting..."):
                sheet = client.open_by_url(sheet_url).get_worksheet(0)
                df = pd.DataFrame(sheet.get_all_records())
            st.success("Connected to Google Sheets!")
        except Exception as e:
            st.error(f"Connection Failed: {e}")

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
                
        col_dl, col_em = st.columns(2)
        
        pdf_data = None
        email_addr = None
        
        with col_dl:
            if st.button("🚀 Generate & Download Single Report"):
                try:
                    with st.spinner("Generating..."):
                        pdf_data, email_addr = generate_report_from_df(df, brand, location)
                        st.success(f"Generated!")
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_data,
                            file_name=f"{brand}_{location}_report.pdf",
                            mime="application/pdf"
                        )
                except Exception as e: st.error(f"Error: {e}")
        
        with col_em:
            if st.button("📧 Generate & Send via Email"):
                try:
                    with st.spinner("Sending email..."):
                        # Always re-generate or fetch to ensure we have latest
                        pdf_data, email_addr = generate_report_from_df(df, brand, location)
                        
                        if email_addr and "@" in str(email_addr):
                            success, msg = send_email(pdf_data, email_addr, brand)
                            if success: st.success(msg)
                            else: st.error(f"Email failed: {msg}")
                        else:
                            st.error(f"Invalid email address found: {email_addr}")
                except Exception as e: st.error(f"Error: {e}")

        # --- BULK GENERATE SECTION ---
        st.divider()
        st.subheader("📦 Bulk Processing")
        
        col_b1, col_b2 = st.columns(2)
        
        if col_b1.button("🗂️ Bulk Generate All Reports (ZIP)"):
            import zipfile
            import io
            try:
                combinations = df[[brand_col, loc_col]].drop_duplicates().values.tolist()
                combinations = [c for c in combinations if str(c[0]).strip() and str(c[1]).strip()]
                zip_buffer = io.BytesIO()
                total = len(combinations)
                progress = st.progress(0)
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for i, (b, l) in enumerate(combinations):
                        pdf, _ = generate_report_from_df(df, str(b), str(l))
                        zip_file.writestr(f"{b}_{l}_report.pdf".replace("/", "-"), pdf)
                        progress.progress((i + 1) / total)
                st.success(f"✅ Generated {total} reports!")
                st.download_button("📥 Download ZIP", data=zip_buffer.getvalue(), 
                                 file_name=f"Kytchens_Reports_{pd.Timestamp.now().strftime('%Y%m%d')}.zip")
            except Exception as e: st.error(f"Failed: {e}")

        if col_b2.button("✉️ Bulk Email All Managers"):
            try:
                combinations = df[[brand_col, loc_col]].drop_duplicates().values.tolist()
                combinations = [c for c in combinations if str(c[0]).strip() and str(c[1]).strip()]
                total = len(combinations)
                progress = st.progress(0)
                success_count = 0
                for i, (b, l) in enumerate(combinations):
                    try:
                        pdf, email = generate_report_from_df(df, str(b), str(l))
                        if email and "@" in str(email):
                            success, _ = send_email(pdf, email, str(b))
                            if success: success_count += 1
                    except: pass
                    progress.progress((i + 1) / total)
                st.success(f"📨 Successfully emailed {success_count} / {total} managers!")
            except Exception as e: st.error(f"Bulk email failed: {e}")
            
    else: st.warning(f"Could not find Brand/Location columns.")
else: st.info("Please provide a data source to begin.")

st.caption("Kychens Intelligence System v1.4")
