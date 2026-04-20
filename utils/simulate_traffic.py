import json
import requests
import random
import time

API_BASE = "http://localhost:8000/api"

def generate_transaction(is_fraud):
    print(f"Fetching sample {'fraudulent' if is_fraud else 'legitimate'} transaction from dataset...")
    # 1. Fetch sample from dataset
    resp = requests.get(f"{API_BASE}/sample_transaction?is_fraud={str(is_fraud).lower()}")
    if resp.status_code != 200:
        print("Failed to get sample.")
        return
    data = resp.json()
    if 'error' in data:
        print(f"Error: {data['error']}")
        return

    # Add required meta
    data["transaction_id"] = f"txn_sim_{int(time.time()*1000)}_{random.randint(100,999)}"
    data["user_id"] = f"user_sim_{random.randint(1000,9999)}"
    
    if is_fraud:
        data["country"] = random.choice(["RU", "CN", "BR", "NG", "VN"])
        data["payment_method"] = "stolen_credit_card"
    else:
        data["country"] = random.choice(["US", "GB", "IN", "CA", "DE"])
        data["payment_method"] = "credit_card"

    # 2. Process Transaction
    print(f"Processing transaction {data['transaction_id']} (Expected: {'Fraud' if is_fraud else 'Legit'})")
    process_resp = requests.post(f"{API_BASE}/process_transaction", json=data)
    process_data = process_resp.json()

    print(f"Status: {process_data.get('status')}")

    # 3. If legit, confirm it so it saves to MySQL
    if process_data.get('status') == 'processed_legitimately':
        confirm_data = {
            "transaction": data,
            "risk_score": process_data.get('risk_score', 0),
            "scaled_features": process_data.get('scaled_features', [])
        }
        conf_resp = requests.post(f"{API_BASE}/confirm_transaction", json=confirm_data)
        print(f"Confirmation: {conf_resp.json().get('status')}")
    print("-" * 30)

if __name__ == "__main__":
    print("Beginning Traffic Simulation...")
    print("Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    # Generate 1 Legitimate
    for _ in range(1):
        generate_transaction(is_fraud=False)
        time.sleep(0.5)

    # Generate 1 Fraud
    for _ in range(1):
        generate_transaction(is_fraud=True)
        time.sleep(0.5)

    print("Traffic generation complete. Check your dashboard!")
