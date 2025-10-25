from flask import Blueprint, request, jsonify
import json
from app.risk_analysis.engine import RiskAnalysisEngine
from app.honeypot.gateway import HoneypotGateway
from app.database.db import get_mysql_db

# --- Configuration ---
# This threshold determines which transactions are diverted to the honeypot.
# We've raised it from 0.5 to 0.75 to reduce false positives on legitimate transactions.
HIGH_RISK_THRESHOLD = 0.75

# --- Initialization ---
api_blueprint = Blueprint('api', __name__)
risk_engine = RiskAnalysisEngine()
honeypot_gateway = HoneypotGateway()


@api_blueprint.route('/transaction', methods=['POST'])
def handle_transaction():
    """
    This is the core endpoint for processing transactions.
    It implements the proactive honeypot-based fraud detection logic.
    """
    transaction_data = request.get_json()
    if not transaction_data:
        return jsonify({"error": "Invalid JSON"}), 400

    # 1. Risk Analysis: Every transaction is first analyzed by the ML engine.
    risk_score = risk_engine.analyze(transaction_data)

    # 2. Intelligent Diversion:
    if risk_score > HIGH_RISK_THRESHOLD:
        # HIGH-RISK: The transaction is suspicious.
        # - Log the attacker's activity in the honeypot for intelligence gathering.
        # - Return a generic "declined" message to deceive the attacker.
        print(f"High-risk transaction detected (Score: {risk_score:.2f}). Diverting to honeypot.")
        honeypot_gateway.log_activity(transaction_data)
        return jsonify({"status": "error", "message": "Transaction declined"}), 400
    else:
        # LOW-RISK: The transaction is considered legitimate.
        # - Process the payment normally.
        # - Log the successful transaction in the main database.
        print(f"Legitimate transaction processed (Score: {risk_score:.2f}).")
        try:
            conn = get_mysql_db()
            with conn.cursor() as cursor:
                sql = "INSERT INTO transactions (is_fraud, amount, details) VALUES (%s, %s, %s)"
                # We log 'is_fraud' as False since it passed the check
                cursor.execute(sql, (False, transaction_data.get('Amount'), json.dumps(transaction_data)))
            conn.commit()
            conn.close()
        except Exception as e:
            # If logging fails, the user's transaction should still succeed.
            print(f"Error logging legitimate transaction to MySQL: {e}")

        return jsonify({"status": "success", "message": "Transaction successful"})
