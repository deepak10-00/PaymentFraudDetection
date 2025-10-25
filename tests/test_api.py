from fastapi.testclient import TestClient
from app.main import app

# The correct way to initialize the TestClient is with a positional argument.
client = TestClient(app)

# Define a sample legitimate transaction
legit_transaction_payload = {
    "transaction_id": "test-legit-001",
    "user_id": "test_user_good",
    "amount": 150.0,
    "currency": "USD",
    "timestamp": "2023-10-27T10:00:00Z",
    "payment_method": "upi",
    "country": "IN"
}

# Define a sample fraudulent transaction
fraud_transaction_payload = {
    "transaction_id": "test-fraud-001",
    "user_id": "test_user_bad",
    "amount": 5000.0,
    "currency": "USD",
    "timestamp": "2023-10-27T11:00:00Z",
    "payment_method": "credit_card",
    "country": "US"
}

def test_process_legitimate_transaction():
    """Tests if a legitimate transaction is processed successfully."""
    response = client.post("/api/process_transaction", json=legit_transaction_payload)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "processed_legitimately"
    assert json_response["transaction_id"] == legit_transaction_payload["transaction_id"]

def test_process_fraudulent_transaction():
    """Tests if a fraudulent transaction is correctly diverted to the honeypot."""
    response = client.post("/api/process_transaction", json=fraud_transaction_payload)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "diverted_to_honeypot"
    assert "explanations" in json_response
    assert len(json_response["explanations"]) > 0

def test_health_check():
    """Tests the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Fraud detection system is running"}
