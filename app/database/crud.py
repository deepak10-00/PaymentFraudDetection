from app.database.db import get_mysql_db, get_mongo_db
from app.schemas import Transaction
from typing import List, Dict, Any
import json # Import the json module

def save_legitimate_transaction(transaction: Transaction, risk_score: float, scaled_features: List[float]):
    """Saves a legitimate transaction to the MySQL database."""
    db_conn = None
    try:
        db_conn = get_mysql_db()
        with db_conn.cursor() as cursor:
            mysql_timestamp = transaction.timestamp.replace('T', ' ').replace('Z', '')
            scaled_features_json = json.dumps(scaled_features) # Convert list to JSON string

            sql = """INSERT INTO transactions 
                     (transaction_id, user_id, amount, currency, payment_method, country, transaction_timestamp, risk_score, scaled_features)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                transaction.transaction_id,
                transaction.user_id,
                transaction.amount,
                transaction.currency,
                transaction.payment_method,
                transaction.country,
                mysql_timestamp,
                risk_score,
                scaled_features_json # Store the JSON string
            ))
        db_conn.commit()
        print(f"Successfully saved legitimate transaction {transaction.transaction_id} to MySQL.")
    except Exception as e:
        print(f"Error saving transaction {transaction.transaction_id} to MySQL: {e}")
    finally:
        if db_conn:
            db_conn.close()

def get_all_legitimate_transactions() -> List[Dict[str, Any]]:
    """Fetches all legitimate transaction records from the MySQL database."""
    db_conn = None
    try:
        db_conn = get_mysql_db()
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT * FROM transactions")
            results = cursor.fetchall()
            print(f"Fetched {len(results)} legitimate transactions from MySQL.")
            return results
    except Exception as e:
        print(f"Error fetching legitimate transactions from MySQL: {e}")
        return []
    finally:
        if db_conn:
            db_conn.close()

def get_all_honeypot_logs() -> List[Dict[str, Any]]:
    """Fetches all fraudulent activity logs from the MongoDB honeypot database."""
    try:
        db = get_mongo_db()
        logs = list(db.honeypot_logs.find({}, {'_id': 0}))
        print(f"Fetched {len(logs)} honeypot logs from MongoDB.")
        return logs
    except Exception as e:
        print(f"Error fetching honeypot logs from MongoDB: {e}")
        return []
