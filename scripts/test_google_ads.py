"""Test Google Ads API connection."""

import os
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv(os.path.expanduser("~/.env"))

CUSTOMER_ID = os.getenv("ADS_CUSTOMER_ID", "").replace("-", "")
MCC_ID = os.getenv("ADS_MCC_ID", "").replace("-", "")

config = {
    "developer_token": os.getenv("ADS_DEVELOPER_TOKEN"),
    "client_id": os.getenv("ADS_CLIENT_ID"),
    "client_secret": os.getenv("ADS_CLIENT_SECRET"),
    "refresh_token": os.getenv("ADS_REFRESH_TOKEN"),
    "login_customer_id": MCC_ID,
    "use_proto_plus": True,
}

client = GoogleAdsClient.load_from_dict(config)
ga_service = client.get_service("GoogleAdsService")

# Query account info
query = """
    SELECT
        customer.id,
        customer.descriptive_name,
        customer.currency_code,
        customer.time_zone
    FROM customer
    LIMIT 1
"""

# Try MCC first, then customer
for label, cid in [("MCC", MCC_ID), ("Customer", CUSTOMER_ID)]:
    print(f"\nTestando {label} ({cid})...")
    try:
        response = ga_service.search(customer_id=cid, query=query)
        for row in response:
            c = row.customer
            print(f"  ID:       {c.id}")
            print(f"  Nome:     {c.descriptive_name}")
            print(f"  Moeda:    {c.currency_code}")
            print(f"  Timezone: {c.time_zone}")
            print(f"\n   {label} OK!")
    except Exception as e:
        err = str(e).split("\n")[0][:120]
        print(f"   {err}")
