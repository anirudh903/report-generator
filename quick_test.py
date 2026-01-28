import gspread
import toml
import os
from oauth2client.service_account import ServiceAccountCredentials

def test():
    try:
        secrets = toml.load(".streamlit/secrets.toml")
        creds_dict = secrets["connections"]["gsheets"]
        
        # Healing private key
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        print("✅ Authorization Success!")
        
        print(f"Service Account: {creds_dict.get('client_email')}")
        
        # Try to open the specific sheet
        url = creds_dict.get("spreadsheet", "https://docs.google.com/spreadsheets/d/1X1gTBdyNtQeLgkrRol4UctH54gCObZzBH0NTRKCr8O4/")
        print(f"Attempting to open: {url}")
        
        try:
            sheet = client.open_by_url(url)
            print(f"✅ Found Spreadsheet: {sheet.title}")
            ws = sheet.get_worksheet(0)
            print(f"✅ Found Worksheet: {ws.title}")
            data = ws.row_values(1)
            print(f"✅ Read first row: {data}")
        except Exception as e:
            print(f"❌ Failed to open sheet: {e}")
            print("\n💡 TIP: Please double-check that you have SHARED the Google Sheet with:")
            print(f"👉 {creds_dict.get('client_email')}")
            
    except Exception as e:
        print(f"❌ General Error: {e}")

if __name__ == "__main__":
    test()
