import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def test_connection():
    # Load from local secrets
    try:
        import streamlit as st
        # This will only work if run via streamlit, so let's parse manual
        path = ".streamlit/secrets.toml"
        if not os.path.exists(path):
            print("❌ .streamlit/secrets.toml not found")
            return
            
        import toml
        secrets = toml.load(path)
        creds_dict = secrets["connections"]["gsheets"]
        # Healing
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        print("✅ Successfully authorized with Google!")
        
        url = "https://docs.google.com/spreadsheets/d/1X1gTBdyNtQeLgkrRol4UctH54gCObZzBH0NTRKCr8O4/"
        sheet = client.open_by_url(url).get_worksheet(0)
        print(f"✅ Successfully opened sheet: {sheet.title}")
        
        data = sheet.get_all_records()
        print(f"✅ Successfully read {len(data)} rows of data")
        
    except Exception as e:
        print(f"❌ Connection Failed: {str(e)}")
        if "401" in str(e):
            print("\n💡 TIP: Your credentials are being rejected. This is usually because:")
            print("1. Your private_key in secrets.toml is incorrectly formatted (check backslashes).")
            print("2. The project's Google Sheets API is not enabled in Google Cloud Console.")
        elif "Permission denied" in str(e) or "403" in str(e):
            print("\n💡 TIP: You MUST share your Google Sheet with the email:")
            print(f"👉 {creds_dict.get('client_email', 'Your Service Account Email')}")

if __name__ == "__main__":
    test_connection()
