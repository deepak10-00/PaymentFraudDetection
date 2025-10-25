"""
This module defines the API endpoints for the fraud detection system.
It will handle incoming transactions, route them for risk analysis, and divert suspicious ones to the honeypot.
"""

import json # Import the json module
from fastapi import APIRouter, BackgroundTasks, Body
from typing import Dict, Any, List
from collections import Counter

from app.ml.risk_analyzer import RiskAnalyzer
from app.honeypot.honeypot_gateway import HoneypotGateway
from app.services.payment_gateway import PaymentGateway # Import the new service
from config.settings import settings
from app.database.crud import save_legitimate_transaction, get_all_legitimate_transactions, get_all_honeypot_logs
from app.schemas import Transaction
from app.ml.training_manager import TrainingManager

router = APIRouter()

# Initialize our components (in a real app, this might be done via dependency injection)
r_analyzer = RiskAnalyzer()
h_gateway = HoneypotGateway()
p_gateway = PaymentGateway() # Initialize the PaymentGateway

@router.post("/process_transaction")
async def process_transaction(transaction: Transaction):
    """
    Receives a transaction, analyzes its risk, and processes it accordingly.
    """
    print(f"Received transaction for processing: {transaction.transaction_id}")

    # 1. Risk Analysis now returns score, explanations, AND scaled_features
    risk_score, explanations, scaled_features = r_analyzer.analyze_transaction(transaction.dict())
    print(f"Transaction {transaction.transaction_id} risk score: {risk_score}")

    if risk_score > settings.RISK_THRESHOLD:
        print(f"Transaction {transaction.transaction_id} deemed suspicious. Diverting to honeypot.")
        # Pass scaled_features to honeypot for logging
        honeypot_result = h_gateway.process_transaction(transaction.dict(), scaled_features)
        # Include the new explanations in the response
        return {
            "status": "diverted_to_honeypot",
            "transaction_id": transaction.transaction_id,
            "honeypot_info": honeypot_result,
            "explanations": explanations
        }
    else:
        print(f"Transaction {transaction.transaction_id} deemed legitimate. Proceeding to payment gateway.")
        # Save legitimate transaction with scaled_features
        save_legitimate_transaction(transaction, risk_score, scaled_features)

        # Process with the simulated payment gateway
        payment_confirmation = p_gateway.process_payment(transaction.dict())

        return {
            "status": "processed_legitimately",
            "transaction_id": transaction.transaction_id,
            "payment_confirmation": payment_confirmation # Include payment confirmation
        }

@router.post("/retrain_model", status_code=202)
def retrain_model(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Triggers the model retraining process using data from MySQL and MongoDB.
    This runs as a background task to avoid blocking the API.
    """
    print("Received request to retrain model.")

    def run_retraining():
        training_manager = TrainingManager(risk_analyzer=r_analyzer)
        result = training_manager.retrain_model()
        print(f"Retraining process finished with status: {result.get('status')}")

    background_tasks.add_task(run_retraining)

    return {"message": "Model retraining process has been initiated in the background."}

@router.get("/transactions", response_model=List[Dict[str, Any]])
def get_transactions():
    """Endpoint to fetch all legitimate transactions from the MySQL database."""
    return get_all_legitimate_transactions()

@router.get("/honeypot_logs", response_model=List[Dict[str, Any]])
def get_honeypot_logs():
    """Endpoint to fetch all fraudulent activity logs from the MongoDB honeypot database."""
    return get_all_honeypot_logs()

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "message": "Fraud detection system is running"}


@router.get("/dashboard_data")
def get_dashboard_data():
    """
    Provides comprehensive data for the frontend dashboard.
    """
    legit_transactions = get_all_legitimate_transactions()
    honeypot_logs = get_all_honeypot_logs()

    total_legit = len(legit_transactions)
    total_suspicious = len(honeypot_logs)
    total_transactions = total_legit + total_suspicious
    fraud_percentage = (total_suspicious / total_transactions * 100) if total_transactions > 0 else 0

    summary = {
        "total_legitimate": total_legit,
        "total_suspicious": total_suspicious,
        "fraud_percentage": f"{fraud_percentage:.2f}%"
    }

    # Format honeypot logs for the dashboard table
    formatted_honeypot_logs = []
    for log in honeypot_logs[-10:]:
        transaction_data = log.get("transaction_data", {})
        intelligence = log.get("intelligence_gathered", {})
        formatted_honeypot_logs.append({
            "Timestamp": log.get("timestamp", "N/A"),
            "Transaction ID": transaction_data.get("transaction_id", "N/A"),
            "User ID": transaction_data.get("user_id", "N/A"),
            "Amount": transaction_data.get("amount", 0),
            "Country": transaction_data.get("country", "N/A"),
            "Payment Method": intelligence.get("payment_method", transaction_data.get("payment_method", "N/A")),
            "Attacker IP": intelligence.get("attacker_ip", "N/A"),
            "Attempted Actions": ", ".join(intelligence.get("attempted_actions", [])),
            "Scaled Features": log.get("scaled_features", []) # Include scaled features
        })

    # Format legitimate transactions for the dashboard table
    formatted_legit_transactions = []
    for trans in legit_transactions[-10:]:
        # Scaled features are stored as a JSON string in MySQL, so we need to parse it
        scaled_features_str = trans.get("scaled_features", "[]")
        try:
            scaled_features_list = json.loads(scaled_features_str)
        except json.JSONDecodeError:
            scaled_features_list = [] # Default to empty list if parsing fails

        formatted_legit_transactions.append({
            "Timestamp": trans.get("transaction_timestamp", "N/A"),
            "Transaction ID": trans.get("transaction_id", "N/A"),
            "User ID": trans.get("user_id", "N/A"),
            "Amount": trans.get("amount", 0),
            "Country": trans.get("country", "N/A"),
            "Payment Method": trans.get("payment_method", "N/A"),
            "Risk Score": f"{trans.get('risk_score', 0):.4f}",
            "Scaled Features": scaled_features_list # Display as a list
        })

    return {
        "summary": summary,
        "honeypot_logs": formatted_honeypot_logs,
        "legitimate_transactions": formatted_legit_transactions
    }

@router.get("/settings")
def get_settings():
    """Returns the current application settings."""
    return {"risk_threshold": settings.RISK_THRESHOLD}

@router.post("/settings")
def update_settings(new_settings: Dict[str, Any] = Body(...)):
    """Updates a specific application setting."""
    if "risk_threshold" in new_settings:
        new_value = float(new_settings["risk_threshold"])
        settings.RISK_THRESHOLD = new_value
        print(f"Updated RISK_THRESHOLD to: {new_value}")
        return {"status": "success", "message": f"Risk threshold updated to {new_value}."}
    return {"status": "error", "message": "Invalid setting provided."}


@router.get("/analytics_data")
def get_analytics_data():
    """
    Provides aggregated data for the analytics dashboard.
    """
    honeypot_logs = get_all_honeypot_logs()

    # Aggregate by country
    country_counts = Counter(log.get("transaction_data", {}).get("country") for log in honeypot_logs if log.get("transaction_data", {}).get("country"))
    country_chart_data = {
        "labels": list(country_counts.keys()),
        "datasets": [{
            "label": "Suspicious Transactions by Country",
            "data": list(country_counts.values()),
            "backgroundColor": ['#e74c3c', '#f39c12', '#3498db', '#2ecc71', '#9b59b6', '#f1c40f'], # Example colors
            "borderColor": ['#c0392b', '#e67e22', '#2980b9', '#27ae60', '#8e44ad', '#d4ac0d'],
            "borderWidth": 1
        }]
    }

    # Aggregate by payment method
    payment_method_counts = Counter(log.get("transaction_data", {}).get("payment_method") for log in honeypot_logs if log.get("transaction_data", {}).get("payment_method"))
    payment_method_chart_data = {
        "labels": list(payment_method_counts.keys()),
        "datasets": [{
            "label": "Suspicious Transactions by Payment Method",
            "data": list(payment_method_counts.values()),
            "backgroundColor": ['#e74c3c', '#f39c12', '#3498db', '#2ecc71', '#9b59b6', '#f1c40f'], # Example colors
            "hoverOffset": 4
        }]
    }

    return {
        "country_chart": country_chart_data,
        "payment_method_chart": payment_method_chart_data
    }
