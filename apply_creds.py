import json
import toml
import os

def apply_new_creds(json_path, secrets_path):
    print(f"Reading new credentials from: {json_path}")
    
    if not os.path.exists(json_path):
        print(f"❌ Error: JSON file not found at {json_path}")
        return

    with open(json_path, 'r') as f:
        new_creds = json.load(f)

    # Load existing secrets to preserve other keys (like GEMINI_API_KEY)
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as f:
            secrets = toml.load(f)
    else:
        secrets = {}

    # Update the gsheets connection section
    if "connections" not in secrets:
        secrets["connections"] = {}
    
    if "gsheets" not in secrets["connections"]:
        secrets["connections"]["gsheets"] = {}

    # The library st-gsheets-connection and gspread both need these fields
    # We update while keeping existing spreadsheet URL if it exists
    spreadsheet_url = secrets["connections"]["gsheets"].get("spreadsheet", "https://docs.google.com/spreadsheets/d/1X1gTBdyNtQeLgkrRol4UctH54gCObZzBH0NTRKCr8O4/")
    
    secrets["connections"]["gsheets"].update(new_creds)
    secrets["connections"]["gsheets"]["spreadsheet"] = spreadsheet_url

    with open(secrets_path, 'w') as f:
        toml.dump(secrets, f)
    
    print(f"✅ Successfully updated {secrets_path} with new credentials.")
    print(f"New Client Email: {new_creds.get('client_email')}")

if __name__ == "__main__":
    # Updated to the LATEST JSON file path provided
    JSON_FILE = r"c:\Users\sunny\Desktop\n8n-local-host-485009-edbaef62f75d.json"
    SECRETS_FILE = r".streamlit\secrets.toml"
    apply_new_creds(JSON_FILE, SECRETS_FILE)
