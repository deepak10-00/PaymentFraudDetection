import datetime
import random
from typing import List # Import List
from app.database.db import get_mongo_db
from app.threat_intelligence.extractor import ThreatIntelligenceExtractor
from app.ml.adaptive_model import AdaptiveMLModel

class HoneypotGateway:
    def __init__(self):
        self.db = get_mongo_db()
        self.honeypot_collection = self.db.honeypot_logs
        self.intelligence_extractor = ThreatIntelligenceExtractor()
        self.adaptive_ml_model = AdaptiveMLModel()
        print("HoneypotGateway initialized and connected to MongoDB.")

    def process_transaction(self, transaction_data: dict, scaled_features: List[float] = None) -> dict:
        """
        Simulates processing a transaction within the honeypot environment.
        All actions here are monitored and logged.

        Args:
            transaction_data: Details of the suspicious transaction.
            scaled_features: The scaled features used by the ML model.

        Returns:
            A dictionary containing simulated transaction results and intelligence gathered.
        """
        print(f"Honeypot processing suspicious transaction: {transaction_data.get('transaction_id')}")

        # Simulate varied honeypot interaction responses
        failure_messages = [
            "Transaction declined due to unusual activity pattern.",
            "Payment authorization failed. Please contact support.",
            "Insufficient funds in decoy account. Transaction halted.",
            "Security alert: Your transaction could not be completed.",
            "Error processing payment. Invalid credentials detected."
        ]
        failure_reasons = [
            "Unusual transaction velocity detected",
            "Mismatch in billing information",
            "High-risk IP address detected",
            "Account flagged for suspicious behavior",
            "Attempted access to restricted resources"
        ]

        simulated_response = {
            "status": "failed",
            "message": random.choice(failure_messages),
            "reason": random.choice(failure_reasons)
        }

        intelligence = self.intelligence_extractor.extract_intelligence(transaction_data)
        
        # Feedback loop: send intelligence back to Adaptive ML model
        self.adaptive_ml_model.receive_threat_intelligence(intelligence, scaled_features)

        log_entry = {
            "timestamp": datetime.datetime.utcnow(),
            "transaction_data": transaction_data,
            "simulated_response": simulated_response,
            "intelligence_gathered": intelligence,
            "scaled_features": scaled_features # Include scaled features
        }
        self.log_activity(log_entry)

        return {"status": "diverted_to_honeypot", "transaction_id": transaction_data.get('transaction_id'), "honeypot_info": simulated_response, "intelligence": intelligence}



    def log_activity(self, activity_data: dict):
        """
        Logs all activities occurring within the honeypot to MongoDB for later analysis.
        """
        try:
            self.honeypot_collection.insert_one(activity_data)
            print(f"Honeypot activity logged for transaction: {activity_data['transaction_data'].get('transaction_id')}")
        except Exception as e:
            print(f"Error logging honeypot activity to MongoDB: {e}")
