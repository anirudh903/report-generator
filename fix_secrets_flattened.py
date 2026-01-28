import toml
import json

# Flattened structure preferred by st-gsheets-connection
json_data = {
  "type": "service_account",
  "project_id": "n8n-local-host-485009",
  "private_key_id": "23b258c2b7bffd553d7e066232865ed1c20ad76b",
  "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC1iYGxrpyCAPLa
RGD2pZowurvmChdUGLnKG53HW1AkOGRQQY8FTJzuvFa9On2KwKEdVO1yb8kmKF4T
0EaRzX2jVOmDqo3/54mF7x4eoKfPPMUCQLt0JzHJBGx2TZbKsTqJBdRsqDR5IdmT
HvtzP6F+6ZzPv83yOe2G32+qesIOGOzeyH2JDe437Knsn9NV1qDRQZQ50t4DjN1K
N/gfBRvRdylDn4aBva0VNCFl8MzkDQv8ye7EQNbw4eEePIkl+4tmR7awvi/yMIGW
+SweqBiRT1YlQXoZhf3HA70tftsCC52y4C80rPM3iOLCRZxbE0CnK3Que+PeUGgF
/YFu6NH3AgMBAAECggEAGAQtM8gBbZOEOAsEIZfuqlQHSAYoEu3tz7FP8iVVmLfF
0aDys6/wh7GZRLx9tQMJ7ZBO6iz5bq0Ne8/kiM/SN275hlE51alDK4RjDDM92sVT
3O9FErdIDKt4ppKviHjiNmlz3RIdqwl8OCHzqx9iaqCrqF0Gzm0Kdvrip3+eYkXX
IBfsfL84qRcI61EVZtMYxSDreRaZmtVNNu+NOxo0VIZVk6bKtlpfqfDwtMxg8smz
HKDzZmsFbJJnUQEvaCtHD8QxC7vqlZY+znnD9Z1RuYcpJ9DkhFBWDMUfP250IX6V
fhVLK1g5QqdnBjvXBlVIp9PM7glAgtAUJr0DqGy0pQKBgQDhttO7t+x27yQGfy1w
veCEuts6zunR2ibiYexuXlKBsCTAONyGWnvc67Hd7nqaSsBVITA15g8ahZwn4VNs
Jxqc70BBIS/Jjht05bNf0H0FyjKWq8DqkcrKvEIbKCtwgxxzItvBSHpE25cNOlhK
YYeWwzRXzheFUHVeNaDrkE6mQwKBgQDN5ThAm9G/Pbrpx2T3/aGRSVPVST94jPl1
dcsLJK+vlFAmBu1ZwJS33gVrxe5PKm7YUkVMzL3TDGJSxhI3gUHo1r8nfqsOUC0w
z8lEUw01A221jy7e3ysof3b7/xW6cgUXELC/pydAT/yNSQyipB8AWw1RKjroZFVv
zdFHAYa8PQKBgAT+cIzUsuymudtS8QRvjwogwDz62v2DoByeIgcHGzg3V3jRST/H
vLnUlSjd3+SOBtdbVp+6qVbi4eOX/qqD6vjR6lAGlfIVrNHXSzKxgDKimJ/wyOHn
u97kb2n+Z4ejvvtlKAuMuPfRC/SE9/MdWUyioQPYUXjnoNEmypqrpLHVAoGAE7Hy
gJOnK7D++S/eo646T0iBYWyhSqnJjwfWhVlcCOKaDBkriSNX1oLBZ/7F/gKkGcM8
58zJ968+lIZn5bFSmbA5FtESEctvlzS5HvUG1WRfkTeCF0Wnvjb7Lb3H2U7g18T7
80lNAuTj1qv/Lmuen40WKAZvHh3C4nAArdciiU0CgYEA19UXlY5q12tGss4Zn14l
saTaK6Zmw2c+AiRXe3QtYcmV7/rK3SxizuZK/avOviwnU6CXIkMOyqNO4x/ITaR4
7RosuaVktl8F7bvIb5iVqGcGevbsfVtNO+LyTHFYwDf/nth+jVwEF3dkm3GQbNgh
kOYsbS6VmJh8XX4ExiAV6Zw=
-----END PRIVATE KEY-----""",
  "client_email": "report-generation@n8n-local-host-485009.iam.gserviceaccount.com",
  "client_id": "103845932497618041680",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/report-generation%40n8n-local-host-485009.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# The library st-gsheets-connection looks for keys directly inside [connections.gsheets]
secrets = {
    "GEMINI_API_KEY": "AIzaSyB-KEZVlHBu5f6QqgBandDtZTDiMhQy1mE",
    "connections": {
        "gsheets": {
            "spreadsheet": "https://docs.google.com/spreadsheets/d/1X1gTBdyNtQeLgkrRol4UctH54gCObZzBH0NTRKCr8O4/"
        }
    }
}

# Add the json_data fields to the gsheets section
secrets["connections"]["gsheets"].update(json_data)

with open(".streamlit/secrets.toml", "w") as f:
    toml.dump(secrets, f)
print("Successfully updated secrets.toml with flattened GCP keys.")