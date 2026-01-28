import streamlit as st
import json
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from main import generate_report_from_df, send_email

# Page Config
st.set_page_config(page_title="Kytchens Report Generator", page_icon="page_icon.png", layout="wide")

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
sheet_urls = []

if mode == "📁 Upload Excel/CSV":
    uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success("File uploaded!")
        except Exception as e:
            st.error(f"Error: {e}")

else:  # Google Sheets Mode
    st.info("💡 You can enter multiple Google Sheet URLs (one per line) to combine data from all of them.")
    sheet_urls_raw = st.text_area("Google Sheet URL(s)", height=100, placeholder="https://docs.google.com/spreadsheets/d/...\nhttps://docs.google.com/spreadsheets/d/...")
    
    sheet_urls = [url.strip() for url in sheet_urls_raw.split('\n') if url.strip()]
    
    if sheet_urls:
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
            
            all_dfs = []
            with st.spinner(f"Connecting to {len(sheet_urls)} sheets..."):
                for i, url in enumerate(sheet_urls):
                    try:
                        sheet = client.open_by_url(url).get_worksheet(0)
                        data = sheet.get_all_records()
                        if data:
                            sheet_df = pd.DataFrame(data)
                            sheet_df['Source_URL'] = url
                            all_dfs.append(sheet_df)
                        else:
                            st.warning(f"Sheet {i+1} is empty.")
                    except Exception as sheet_err:
                        st.error(f"Error loading sheet {i+1}: {sheet_err}")
                
                if all_dfs:
                    df = pd.concat(all_dfs, ignore_index=True)
                    st.success(f"Connected! Combined {len(all_dfs)} sheets with {len(df)} total records.")
                    with st.expander("📊 Data Preview (Source URLs)"):
                        st.write(df[['Brand', 'Location', 'Source_URL']].head())
                else:
                    st.error("No data found in any of the provided sheets.")

        except Exception as e:
            st.error(f"Connection Failed: {str(e)}")
            if "Invalid credentials" in str(e) or "invalid_grant" in str(e):
                st.info("📋 **Solution**: Share your Google Sheet with: `service-account@n8n-local-host-485009.iam.gserviceaccount.com`")

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
        fallback_url = sheet_urls[0] if (mode == "🌐 Google Sheets" and sheet_urls) else None

        with col_dl:
            if st.button("🚀 Generate & Download Single Report"):
                try:
                    with st.spinner("Generating..."):
                        pdf_data, email_addr = generate_report_from_df(df, brand, location, spreadsheet_url=fallback_url)
                        st.success(f"Generated!")
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_data,
                            file_name=f"{brand}_{location}_report.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col_em:
            if st.button("📧 Generate & Send via Email"):
                try:
                    with st.spinner("Sending email..."):
                        pdf_data, email_addr = generate_report_from_df(df, brand, location, spreadsheet_url=fallback_url)
                        if email_addr and "@" in str(email_addr):
                            success, msg = send_email(pdf_data, email_addr, brand)
                            if success: st.success(msg)
                            else: st.error(f"Email failed: {msg}")
                        else:
                            st.error(f"Invalid email address found: {email_addr}")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Bulk processing
        st.divider()
        st.subheader("📦 Bulk Processing")
        col_b1, col_b2 = st.columns(2)
        
        if col_b1.button("🗂️ Bulk Generate All Reports (ZIP)"):
            import zipfile, io
            try:
                combinations = df[[brand_col, loc_col]].drop_duplicates().values.tolist()
                combinations = [c for c in combinations if str(c[0]).strip() and str(c[1]).strip()]
                zip_buffer = io.BytesIO()
                progress = st.progress(0)
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for i, (b, l) in enumerate(combinations):
                        pdf, _ = generate_report_from_df(df, str(b), str(l), spreadsheet_url=fallback_url)
                        zip_file.writestr(f"{b}_{l}_report.pdf".replace("/", "-"), pdf)
                        progress.progress((i + 1) / len(combinations))
                st.download_button("📥 Download ZIP", data=zip_buffer.getvalue(), file_name="Reports.zip")
            except Exception as e: st.error(f"Failed: {e}")

        if col_b2.button("✉️ Bulk Email All Managers"):
            try:
                combinations = df[[brand_col, loc_col]].drop_duplicates().values.tolist()
                combinations = [c for c in combinations if str(c[0]).strip() and str(c[1]).strip()]
                progress = st.progress(0)
                success_count = 0
                for i, (b, l) in enumerate(combinations):
                    try:
                        pdf, email = generate_report_from_df(df, str(b), str(l), spreadsheet_url=fallback_url)
                        if email and "@" in str(email):
                            success, _ = send_email(pdf, email, str(b))
                            if success: success_count += 1
                    except: pass
                    progress.progress((i + 1) / len(combinations))
                st.success(f"📨 Sent {success_count} / {len(combinations)} emails!")
            except Exception as e: st.error(f"Failed: {e}")
            
    else: st.warning(f"Could not find Brand/Location columns.")
else: st.info("Please provide a data source to begin.")
st.caption("Kychens Intelligence System v1.5")