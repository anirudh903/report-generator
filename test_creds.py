import streamlit as st
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

try:
    creds_json = st.secrets["GCP_JSON"]
    creds = json.loads(creds_json)
    print("Keys in JSON:", list(creds.keys()))
    
    # Check specifically for standard keys
    required = ['private_key', 'client_email']
    for k in required:
        if k in creds:
            print(f"✅ Found {k}")
        else:
            print(f"❌ Missing {k}")
            
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_obj = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    print("✅ Successfully created ServiceAccountCredentials object")
    
except Exception as e:
    print(f"❌ Error: {e}")
