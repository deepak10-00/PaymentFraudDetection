from app.database.db import get_mongo_db
from datetime import datetime

class HoneypotGateway:
    def __init__(self):
        # Establish a connection to the honeypot's database
        self.mongo_db = get_mongo_db()
    
    def log_activity(self, suspicious_transaction_data):
        """
        Logs the details of a suspicious transaction to the honeypot database,
        ensuring a timestamp is included and correctly formatted.
        """
        try:
            # Ensure the document to be inserted is a mutable copy
            log_data = suspicious_transaction_data.copy()
            
            # Add a server-side UTC timestamp to the record.
            # This ensures the 'Timestamp' field is a proper BSON date.
            log_data['Timestamp'] = datetime.utcnow()
            
            # Log the suspicious transaction to a dedicated collection for analysis
            collection = self.mongo_db['suspicious_transactions']
            collection.insert_one(log_data)
            print("Successfully logged suspicious activity to honeypot.")
        except Exception as e:
            print(f"Error logging to honeypot: {e}")
