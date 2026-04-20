"""
This module defines the API endpoints for the fraud detection system.
It will handle incoming transactions, route them for risk analysis, and divert suspicious ones to the honeypot.
"""

import json # Import the json module
from fastapi import APIRouter, BackgroundTasks, Body, Request
from typing import Dict, Any, List, Optional
from collections import Counter
import pandas as pd
import random
import os
from app.honeypot.honeypot_gateway import HoneypotGateway
from app.services.location_service import geolocation_service
from datetime import datetime
from app.database.db import get_mongo_db
from bson import json_util

from app.database.crud import save_legitimate_transaction, get_all_legitimate_transactions, get_all_honeypot_logs
from app.schemas import Transaction, ConfirmTransactionRequest
from app.decision_layer.router import DecisionRouter
from app.ml.training_manager import TrainingManager

router = APIRouter()

# Initialize our component
decision_router = DecisionRouter()

@router.post("/process_transaction")
async def process_transaction(request: Request, transaction: Transaction):
    """
    Receives a transaction, analyzes its risk, and processes it accordingly.
    """
    print(f"Received transaction for processing: {transaction.transaction_id}")

    # Inject client IP into transaction data
    transaction_data = transaction.model_dump()
    transaction_data["ip_address"] = request.client.host

    # 1. Route transaction through Decision Layer
    return decision_router.route_transaction(transaction_data)

@router.post("/confirm_transaction")
async def confirm_transaction(request: Request, req: ConfirmTransactionRequest):
    """
    Saves a legitimate transaction to the database after successful payment confirmation.
    """
    client_ip = request.client.host
    print(f"Payment successful for {req.transaction.transaction_id} from IP {client_ip}. Resolving location...")
    
    # Resolve real location (Source of Truth)
    geo = geolocation_service.get_location(client_ip)
    
    # Overwrite client fields with real data if available
    if geo.get('city') not in [None, "N/A", "Local"]:
        req.transaction.city = geo.get('city')
    if geo.get('state') not in [None, "N/A", "Local"]:
        req.transaction.state = geo.get('state')
    if geo.get('country') not in [None, "N/A", "Local"]:
        req.transaction.country = geo.get('country')
    
    save_legitimate_transaction(req.transaction, req.risk_score, req.scaled_features, client_ip)
    return {"status": "saved_legitimately"}

@router.post("/retrain_model", status_code=202)
def retrain_model(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Triggers the model retraining process using data from MySQL and MongoDB.
    This runs as a background task to avoid blocking the API.
    """
    print("Received request to retrain model.")

    def run_retraining():
        training_manager = TrainingManager(adaptive_model=decision_router.risk_engine.ml_model)
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
    for log in honeypot_logs[-20:]:  # Increase to last 20 for better visibility
        transaction_data = log.get("transaction_data", {})
        intelligence = log.get("intelligence_gathered", {})
        
        # Handle datetime object from MongoDB with multiple fallbacks
        ts = log.get("timestamp") or log.get("Timestamp")
        
        # If timestamp is missing, try to extract from MongoDB _id or use current time
        if not ts:
            if '_id' in log and hasattr(log['_id'], 'generation_time'):
                 ts = log['_id'].generation_time
            else:
                 ts = datetime.utcnow()

        if isinstance(ts, datetime):
            # Ensure the string ends with Z to indicate UTC for the browser
            ts_str = ts.isoformat() + "Z"
        else:
            ts_str = str(ts) if ts else datetime.utcnow().isoformat() + "Z"

        formatted_honeypot_logs.append({
            "Timestamp": ts_str,
            "Transaction ID": transaction_data.get("transaction_id", transaction_data.get("Transaction ID", "N/A")),
            "User ID": transaction_data.get("user_id", "N/A"),
            "Amount": float(transaction_data.get("Amount", transaction_data.get("amount", 0))),
            "Country": transaction_data.get("country", intelligence.get("attacker_location", "N/A")),
            "State": transaction_data.get("state", intelligence.get("attacker_state", "N/A")),
            "City": transaction_data.get("city", intelligence.get("attacker_city", "N/A")),
            "Payment Method": intelligence.get("payment_method", transaction_data.get("payment_method", "N/A")),
            "Attacker IP": intelligence.get("attacker_ip", transaction_data.get("ip_address", "N/A")),
            "Attempted Actions": ", ".join(intelligence.get("attempted_actions", [])),
            "Scaled Features": log.get("scaled_features", [])
        })

    # Format legitimate transactions for the dashboard table
    formatted_legit_transactions = []
    for trans in legit_transactions[-10:]:
        # 'trans' contains id, is_fraud, amount, details, timestamp based on init.sql
        details_str = trans.get("details", "{}")
        try:
            details = json.loads(details_str)
        except json.JSONDecodeError:
            details = {}
            
        scaled_features_list = details.get("scaled_features", [])

        ts = trans.get("timestamp") or datetime.utcnow()
        ts_str = ts.isoformat() + "Z" if isinstance(ts, datetime) else str(ts)

        formatted_legit_transactions.append({
            "Timestamp": ts_str,
            "Transaction ID": details.get("transaction_id", "N/A"),
            "User ID": details.get("user_id", "N/A"),
            "Amount": float(trans.get("amount", details.get("Amount", 0))),
            "Country": details.get("country", "N/A"),
            "State": details.get("state", "N/A"),
            "City": details.get("city", "N/A"),
            "Payment Method": details.get("payment_method", "N/A"),
            "Risk Score": f"{details.get('risk_score', 0):.4f}",
            "IP Address": details.get("ip_address", "N/A"),
            "Scaled Features": scaled_features_list # Display as a list
        })

    try:
        mongo_db = get_mongo_db()
        failed_col = mongo_db['failed_payments']
        failed_logs = list(failed_col.find().sort("_id", -1).limit(50))
        
        # Convert MongoDB dates to ISO strings for frontend
        failed_json = []
        for log in failed_logs:
            log_copy = log.copy()
            if '_id' in log_copy:
                log_copy['_id'] = str(log_copy['_id'])
                
            # Extract location from transaction sub-object
            tx_data = log_copy.get('transaction', {})
            log_copy['Country'] = tx_data.get('country', 'N/A')
            log_copy['State'] = tx_data.get('state', 'N/A')
            log_copy['City'] = tx_data.get('city', 'N/A')
            
            # Use LoggedAt or fallback to DB id generation time or current time
            la = log_copy.get('LoggedAt')
            if not la:
                if '_id' in log_copy and hasattr(log_copy['_id'], 'generation_time'):
                    la = log_copy['_id'].generation_time
                else:
                    la = datetime.utcnow()
            
            if isinstance(la, datetime):
                log_copy['LoggedAt'] = la.isoformat() + "Z"
            
            failed_json.append(log_copy)
            
    except Exception as e:
        print(f"Failed to fetch failed payments: {e}")
        failed_json = []

    return {
        "summary": summary,
        "honeypot_logs": formatted_honeypot_logs,
        "legitimate_transactions": formatted_legit_transactions,
        "failed_payments": failed_json
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
    from datetime import datetime
    
    honeypot_logs = get_all_honeypot_logs()

    # Extract data for KPIs with robust fallbacks
    ips = []
    countries = []
    for log in honeypot_logs:
        intel = log.get("intelligence_gathered", {})
        tx = log.get("transaction_data", {})
        
        ip = intel.get("attacker_ip") or tx.get("ip_address") or log.get("Attacker IP")
        country = intel.get("attacker_location") or tx.get("country") or log.get("Country")
        
        if ip: ips.append(ip)
        if country: countries.append(country)
    
    # Extract hours for time series
    hours = []
    for log in honeypot_logs:
        # Check multiple possible timestamp fields
        ts_val = log.get("timestamp") or log.get("Timestamp")
        if ts_val:
            try:
                if isinstance(ts_val, str):
                    dt = datetime.fromisoformat(ts_val.replace('Z', '+00:00'))
                else:
                    dt = ts_val
                hours.append(f"{dt.hour:02d}:00")
            except Exception as e:
                print(f"Error parsing timestamp {ts_val}: {e}")

    top_ip = Counter(ips).most_common(1)[0][0] if ips else "--"
    top_country = Counter(countries).most_common(1)[0][0] if countries else "--"
    peak_time_val = Counter(hours).most_common(1)[0][0] if hours else "--"

    kpis = {
        "top_attacker_ip": top_ip,
        "peak_fraud_time": peak_time_val,
        "most_attacked_country": top_country
    }

    # Time series data (Suspicious Activity by Hour)
    hour_counts = Counter(hours)
    sorted_hours = sorted(hour_counts.keys())
    time_series = {
        "labels": sorted_hours,
        "data": [hour_counts[h] for h in sorted_hours]
    }

    # Geo breakdown data (Attacks by Country)
    country_counts = Counter(countries)
    geo_breakdown = {
        "labels": list(country_counts.keys()),
        "data": list(country_counts.values())
    }

    return {
        "kpis": kpis,
        "time_series": time_series,
        "geo_breakdown": geo_breakdown
    }

@router.get("/sample_transaction")
def get_sample_transaction(is_fraud: bool = False):
    """
    Fetches a real row from the original creditcard.csv dataset
    to use in the checkout frontend for authentic demonstrations.
    """
    try:
        csv_path = os.path.join(os.getcwd(), "creditcard.csv")
        if not os.path.exists(csv_path):
            return {"error": "Dataset creditcard.csv not found"}
            
        df = pd.read_csv(csv_path)
        
        # Filter for requested class (1 for fraud, 0 for legitimate)
        target_class = 1 if is_fraud else 0
        subset = df[df['Class'] == target_class]
        
        if subset.empty:
             return {"error": "No matching data found"}
             
        sample = subset.sample(1).iloc[0].to_dict()
        
        # Format it
        transaction = {
            "Time": sample.get("Time", 0),
            "Amount": sample.get("Amount", 0),
        }
        for i in range(1, 29):
            transaction[f"V{i}"] = sample.get(f"V{i}", 0)
            
        return transaction
    except Exception as e:
        return {"error": str(e)}

@router.post("/log_failed_payment")
async def log_failed_payment(request: Request, data: Dict[str, Any] = Body(...)):
    if not data:
        return {"error": "Invalid Data"}
    try:
        data['LoggedAt'] = datetime.utcnow()
        client_ip = request.client.host
        data['ip_address'] = client_ip
        
        # Resolve real location before logging (Source of Truth)
        geo = geolocation_service.get_location(client_ip)
        if 'transaction' in data:
            if geo.get('city') not in [None, "N/A", "Local"]:
                 data['transaction']['city'] = geo.get('city')
            if geo.get('state') not in [None, "N/A", "Local"]:
                 data['transaction']['state'] = geo.get('state')
            if geo.get('country') not in [None, "N/A", "Local"]:
                 data['transaction']['country'] = geo.get('country')
            
        mongo_db = get_mongo_db()
        collection = mongo_db['failed_payments']
        collection.insert_one(data)
        return {"status": "success", "message": "Failed payment logged successfully"}
    except Exception as e:
        print(f"Error logging failed payment: {e}")
        return {"error": f"Failed to log payment: {e}"}
