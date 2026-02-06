import pytest
from fastapi.testclient import TestClient
from app.main import app # Import the FastAPI app instance

@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client

# Sample payload for a legitimate transaction (based on creditcard.csv 'Class' 0)
legit_payload = {
  "Time": 406, "V1": -2.31, "V2": 1.95, "V3": -1.60, "V4": 3.99, "V5": -0.52,
  "V6": -1.42, "V7": -2.53, "V8": 1.39, "V9": -2.77, "V10": -2.77, "V11": 3.20,
  "V12": -2.89, "V13": -0.59, "V14": -4.28, "V15": 0.38, "V16": -1.14, "V17": -2.83,
  "V18": -0.01, "V19": 0.41, "V20": 0.12, "V21": 0.51, "V22": -0.03, "V23": -0.46,
  "V24": 0.32, "V25": 0.04, "V26": 0.17, "V27": 0.26, "V28": -0.14, "Amount": 0.00
}

# Sample payload for a fraudulent transaction (based on creditcard.csv 'Class' 1)
fraud_payload = {
  "Time": 472, "V1": -3.04, "V2": -3.15, "V3": 1.08, "V4": 2.28, "V5": 1.35,
  "V6": -1.06, "V7": 0.32, "V8": -0.06, "V9": -0.27, "V10": -0.83, "V11": -0.41,
  "V12": -0.50, "V13": -0.11, "V14": -0.28, "V15": -0.51, "V16": 0.72, "V17": -0.88,
  "V18": -0.25, "V19": -0.63, "V20": -0.29, "V21": 0.66, "V22": 0.43, "V23": 1.37,
  "V24": -0.29, "V25": -0.14, "V26": -0.21, "V27": -0.54, "V28": 0.13, "Amount": 529.00
}

def test_handle_legitimate_transaction(client: TestClient):
    """Test that a legitimate transaction is processed successfully."""
    response = client.post("/api/process_transaction", json=legit_payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "processed_legitimately"

def test_handle_fraudulent_transaction(client: TestClient):
    """Test that a fraudulent transaction is diverted to the honeypot."""
    response = client.post("/api/process_transaction", json=fraud_payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "diverted_to_honeypot"

def test_get_dashboard_data(client: TestClient):
    """Test the dashboard data endpoint."""
    response = client.get("/api/dashboard_data")
    assert response.status_code == 200
    json_data = response.json()
    assert "summary" in json_data
    assert "honeypot_logs" in json_data
    assert "legitimate_transactions" in json_data

def test_get_analytics_data(client: TestClient):
    """Test the analytics data endpoint."""
    response = client.get("/api/analytics_data")
    assert response.status_code == 200
    json_data = response.json()
    assert "country_chart" in json_data
    assert "payment_method_chart" in json_data
