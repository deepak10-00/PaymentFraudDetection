import random
from app.services.location_service import geolocation_service

class ThreatIntelligenceExtractor:
    def extract_intelligence(self, transaction_data: dict) -> dict:
        """
        Collects information about the attacker's actions and extracts
        intelligence directly from the transaction context.
        """
        print("Gathering threat intelligence from transaction data...")
        
        # Dynamically generate attacker IP and location or use the provided IP
        attacker_ip = transaction_data.get("ip_address", f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}")
        
        # Resolve real location from IP (Prioritize over client-reported placeholders)
        geo_data = geolocation_service.get_location(attacker_ip)
        
        # Helper to prefer geo_data if valid
        def pick_best(geo_key, tx_key):
            g_val = geo_data.get(geo_key)
            if g_val and g_val not in ["N/A", "Local"]:
                return g_val
            t_val = transaction_data.get(tx_key)
            return t_val if t_val and t_val != "N/A" else g_val

        attacker_city = pick_best("city", "city")
        attacker_state = pick_best("state", "state")
        attacker_location = pick_best("country", "country")

        attempted_actions = []
        # Make actions dynamic based on transaction characteristics
        if transaction_data.get("amount", 0) > 1000:
            attempted_actions.append("attempted_high_value_transaction")
        method = transaction_data.get("payment_method", "unknown")
        attempted_actions.append(f"attempted_payment_with_{method}")
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
            "attacker_location": attacker_location,
            "attacker_state": attacker_state,
            "attacker_city": attacker_city,
            "attempted_actions": attempted_actions,
            "tool_signatures": tool_signatures,
            "device_fingerprint": device_fingerprint,
            "transaction_id": transaction_data.get("transaction_id"),
            "user_id": transaction_data.get("user_id")
        }
