"""Generate Google Ads OAuth refresh token via Desktop app flow."""

import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv(os.path.expanduser("~/.env"))

CLIENT_ID = os.getenv("ADS_CLIENT_ID")
CLIENT_SECRET = os.getenv("ADS_CLIENT_SECRET")

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

flow = InstalledAppFlow.from_client_config(
    client_config,
    scopes=["https://www.googleapis.com/auth/adwords"],
)

flow.run_local_server(port=8090)

print(f"\n Refresh Token:\n{flow.credentials.refresh_token}")
print("\nCopia o token acima e me passa.")
