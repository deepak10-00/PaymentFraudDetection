from app.database.db import get_mongo_db

class HoneypotGateway:
    def __init__(self):
        # Establish a connection to the honeypot's database
        self.mongo_db = get_mongo_db()
    
    def log_activity(self, suspicious_transaction_data):
        """
        Logs the details of a suspicious transaction to the honeypot database.
        """
        try:
            # Log the suspicious transaction to a dedicated collection for analysis
            collection = self.mongo_db['suspicious_transactions']
            collection.insert_one(suspicious_transaction_data)
            print("Successfully logged suspicious activity to honeypot.")
        except Exception as e:
            print(f"Error logging to honeypot: {e}")
