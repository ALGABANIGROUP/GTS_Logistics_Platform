import csv
import requests
from datetime import datetime

# 🔗 API Endpoint
API_URL = "http://localhost:8000/expenses/"

# 📂 CSV File Path
CSV_FILE = "GTS_Financial_Ledger.csv"

# 🧠 Helper: Try to safely parse float
def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0

# 🚀 Start uploading
with open(CSV_FILE, newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        payload = {
            "category": row.get("category", "Other"),
            "amount": safe_float(row.get("amount_usd", 0)),
            "description": f"{row.get('description', '')} | Vendor: {row.get('vendor', '')} | Status: {row.get('status', '')}",
            "created_at": datetime.strptime(row.get("date", ""), "%Y-%m-%d").isoformat() if row.get("date") else None
        }

        # ⚠️ Skip expenses with invalid or zero amount
        if payload["amount"] <= 0:
            print("❌ Skipped row due to invalid amount:", payload)
            continue

        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                print(f"✅ Uploaded: {payload['category']} - ${payload['amount']}")
            else:
                print(f"❌ Failed to upload: {response.status_code} - {response.text}")
        except Exception as e:
            print("⚠️ Error uploading:", e)
