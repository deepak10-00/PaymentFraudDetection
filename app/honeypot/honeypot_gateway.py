import datetime
import random
from typing import List # Import List
from app.database.db import get_mongo_db

class HoneypotGateway:
    def __init__(self):
        self.db = get_mongo_db()
        self.honeypot_collection = self.db.honeypot_logs
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

        intelligence = self._gather_intelligence(transaction_data)

        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "transaction_data": transaction_data,
            "simulated_response": simulated_response,
            "intelligence_gathered": intelligence,
            "scaled_features": scaled_features # Include scaled features
        }
        self.log_activity(log_entry)

        return {"status": "diverted_to_honeypot", "transaction_id": transaction_data.get('transaction_id'), "honeypot_info": simulated_response, "intelligence": intelligence}

    def _gather_intelligence(self, transaction_data: dict) -> dict:
        """
        Collects information about the attacker's actions within the honeypot.
        This is a simulated intelligence gathering.
        """
        print("Gathering intelligence from honeypot...")
        
        # Dynamically generate attacker IP
        attacker_ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

        attempted_actions = []
        # Make actions dynamic based on transaction characteristics
        if transaction_data.get("amount", 0) > 1000:
            attempted_actions.append("attempted_high_value_transaction")
        if transaction_data.get("payment_method") == 'credit_card':
            attempted_actions.append("attempted_payment_with_credit_card")
        if random.random() < 0.3: # 30% chance of trying to enumerate accounts
            attempted_actions.append("tried_to_enumerate_account_details")
        if random.random() < 0.2: # 20% chance of accessing fake profile
            attempted_actions.append("accessed_fake_user_profile")
        if not attempted_actions:
            attempted_actions.append("generic_suspicious_activity")

        tool_signatures = [
            random.choice(["fake_card_bruteforcer_v1.0", "generic_phishing_kit_variant_A", "automated_script_v2.1"])
        ]

        # Simulate device fingerprint
        device_fingerprint = f"browser_id_{random.randint(10000, 99999)}_os_{random.choice(['Windows', 'Linux', 'MacOS'])}"

        return {
            "attacker_ip": attacker_ip,
            "attempted_actions": attempted_actions,
            "tool_signatures": tool_signatures,
            "device_fingerprint": device_fingerprint,
            "transaction_id": transaction_data.get("transaction_id"),
            "user_id": transaction_data.get("user_id")
        }

    def log_activity(self, activity_data: dict):
        """
        Logs all activities occurring within the honeypot to MongoDB for later analysis.
        """
        try:
            self.honeypot_collection.insert_one(activity_data)
            print(f"Honeypot activity logged for transaction: {activity_data['transaction_data'].get('transaction_id')}")
        except Exception as e:
            print(f"Error logging honeypot activity to MongoDB: {e}")
