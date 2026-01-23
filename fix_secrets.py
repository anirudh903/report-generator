import toml
import json

json_data = {
  "type": "service_account",
  "project_id": "n8n-local-host-485009",
  "private_key_id": "23b258c2b7bffd553d7e066232865ed1c20ad76b",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC1iYGxrpyCAPLa\nRGD2pZowurvmChdUGLnKG53HW1AkOGRQQY8FTJzuvFa9On2KwKEdVO1yb8kmKF4T\n0EaRzX2jVOmDqo3/54mF7x4eoKfPPMUCQLt0JzHJBGx2TZbKsTqJBdRsqDR5IdmT\nHvtzP6F+6ZzPv83yOe2G32+qesIOGOzeyH2JDe437Knsn9NV1qDRQZQ50t4DjN1K\nN/gfBRvRdylDn4aBva0VNCFl8MzkDQv8ye7EQNbw4eEePIkl+4tmR7awvi/yMIGW\n+SweqBiRT1YlQXoZhf3HA70tftsCC52y4C80rPM3iOLCRZxbE0CnK3Que+PeUGgF\n/YFu6NH3AgMBAAECggEAGAQtM8gBbZOEOAsEIZfuqlQHSAYoEu3tz7FP8iVVmLfF\n0aDys6/wh7GZRLx9tQMJ7ZBO6iz5bq0Ne8/kiM/SN275hlE51alDK4RjDDM92sVT\n3O9FErdIDKt4ppKviHjiNmlz3RIdqwl8OCHzqx9iaqCrqF0Gzm0Kdvrip3+eYkXX\nIBfsfL84qRcI61EVZtMYxSDreRaZmtVNNu+NOxo0VIZVk6bKtlpfqfDwtMxg8smz\nHKDzZmsFbJJnUQEvaCtHD8QxC7vqlZY+znnD9Z1RuYcpJ9DkhFBWDMUfP250IX6V\nfhVLK1g5QqdnBjvXBlVIp9PM7glAgtAUJr0DqGy0pQKBgQDhttO7t+x27yQGfy1w\nveCEuts6zunR2ibiYexuXlKBsCTAONyGWnvc67Hd7nqaSsBVITA15g8ahZwn4VNs\nJxqc70BBIS/Jjht05bNf0H0FyjKWq8DqkcrKvEIbKCtwgxxzItvBSHpE25cNOlhK\nYYeWwzRXzheFUHVeNaDrkE6mQwKBgQDN5ThAm9G/Pbrpx2T3/aGRSVPVST94jPl1\ndcsLJK+vlFAmBu1ZwJS33gVrxe5PKm7YUkVMzL3TDGJSxhI3gUHo1r8nfqsOUC0w\nz8lEUw01A221jy7e3ysof3b7/xW6cgUXELC/pydAT/yNSQyipB8AWw1RKjroZFVv\zdFHAYa8PQKBgAT+cIzUsuymudtS8QRvjwogwDz62v2DoByeIgcHGzg3V3jRST/H\nvLnUlSjd3+SOBtdbVp+6qVbi4eOX/qqD6vjR6lAGlfIVrNHXSzKxgDKimJ/wyOHn\nu97kb2n+Z4ejvvtlKAuMuPfRC/SE9/MdWUyioQPYUXjnoNEmypqrpLHVAoGAE7Hy\ngJOnK7D++S/eo646T0iBYWyhSqnJjwfWhVlcCOKaDBkriSNX1oLBZ/7F/gKkGcM8\n58zJ968+lIZn5bFSmbA5FtESEctvlzS5HvUG1WRfkTeCF0Wnvjb7Lb3H2U7g18T7\n80lNAuTj1qv/Lmuen40WKAZvHh3C4nAArdciiU0CgYEA19UXlY5q12tGss4Zn14l\nsaTaK6Zmw2c+AiRXe3QtYcmV7/rK3SxizuZK/avOviwnU6CXIkMOyqNO4x/ITaR4\n7RosuaVktl8F7bvIb5iVqGcGevbsfVtNO+LyTHFYwDf/nth+jVwEF3dkm3GQbNgh\nkOYsbS6VmJh8XX4ExiAV6Zw=\n-----END PRIVATE KEY-----\n",
  "client_email": "report-generation@n8n-local-host-485009.iam.gserviceaccount.com",
  "client_id": "103845932497618041680",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/report-generation%40n8n-local-host-485009.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

secrets = {
    "GEMINI_API_KEY": "AIzaSyB-KEZVlHBu5f6QqgBandDtZTDiMhQy1mE",
    "GCP_JSON": json.dumps(json_data)
}

with open(".streamlit/secrets.toml", "w") as f:
    toml.dump(secrets, f)
