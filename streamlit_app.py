import streamlit as st
import json
import pandas as pd
import os
from main import generate_report, generate_report_from_df

# Page Config
st.set_page_config(page_title="Kychens Report Generator", page_icon="🍳", layout="wide")

# Sync secrets to environment variables
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

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

st.title("🍳 Kychens Report Generator")
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
col1, col2 = st.columns(2)
with col1:
    brand = st.text_input("Brand Name", placeholder="e.g., Burger King")
with col2:
    location = st.text_input("Location", placeholder="e.g., Mumbai")

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
