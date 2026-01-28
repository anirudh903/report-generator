import streamlit as st
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

try:
    # Updated to work with the flattened structure in secrets.toml
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        creds = dict(st.secrets["connections"]["gsheets"])
    elif "GCP_JSON" in st.secrets:
        creds = json.loads(st.secrets["GCP_JSON"])
    else:
        raise KeyError("Neither connections.gsheets nor GCP_JSON found in secrets")

    # Healing: Fix private key formatting if needed
    if "private_key" in creds:
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")

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