from flask import Blueprint, request, jsonify
import json
from app.decision_layer.router import DecisionRouter

# --- Configuration ---
HIGH_RISK_THRESHOLD = 0.75

# --- Initialization ---
api_blueprint = Blueprint('api', __name__)
decision_router = DecisionRouter()


@api_blueprint.route('/transaction', methods=['POST'])
def handle_transaction():
    """
    This is the core endpoint for processing transactions.
    It now passes the full transaction data to the risk analysis engine.
    """
    transaction_data = request.get_json()
    if not transaction_data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Use the centralized Decision Layer to route the transaction
    result = decision_router.route_transaction(transaction_data)

    if result.get("status") == "diverted_to_honeypot":
        # Transaction was routed to honeypot
        return jsonify({"status": "error", "message": "Transaction declined", "reason": result.get("explanations", ["Suspicious activity"])}), 400
    else:
        # Legitimate transaction
        try:
            conn = get_mysql_db()
            with conn.cursor() as cursor:
                # Storing more details about the legitimate transaction.
                sql = "INSERT INTO transactions (is_fraud, amount, details) VALUES (%s, %s, %s)"
                amount = transaction_data.get('Amount', 0.0)
                details = json.dumps(transaction_data)
                cursor.execute(sql, (False, amount, details))
            conn.commit()
        except Exception as e:
            print(f"Error saving legitimate transaction: {e}")
        finally:
            conn.close()

        return jsonify({"status": "success", "message": "Transaction successful"})

@api_blueprint.route('/dashboard_data', methods=['GET'])
def get_dashboard_data():
    """
    This endpoint provides the data needed for the main dashboard.
    It now uses a consistent filter for suspicious transactions to match the analytics page.
    """
    try:
        mongo_db = get_mongo_db()
        honeypot_collection = mongo_db['suspicious_transactions']
        
        # Use the same filter as the analytics page for consistency.
        valid_suspicious_filter = {
            "$or": [
                {"Timestamp": {"$type": "date"}},
                {"_id": {"$ne": None}}
            ]
        }
        
        # Count only the valid, analyzable suspicious transactions.
        total_suspicious = honeypot_collection.count_documents(valid_suspicious_filter)
        
        # The list of recent logs can still show all recent attempts.
        honeypot_logs = list(honeypot_collection.find().sort("_id", -1).limit(50))
        honeypot_logs_json = json.loads(json_util.dumps(honeypot_logs))

        # --- Legitimate Transactions (MySQL) ---
        mysql_conn = get_mysql_db()
        total_legitimate = 0
        legitimate_transactions = []
        try:
            with mysql_conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM transactions WHERE is_fraud = 0")
                result = cursor.fetchone()
                if result:
                    total_legitimate = result[0]
            
            with mysql_conn.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM transactions WHERE is_fraud = 0 ORDER BY timestamp DESC LIMIT 50"
                cursor.execute(sql)
                legitimate_transactions = cursor.fetchall()
        finally:
            mysql_conn.close()

        # --- Failed Payments (MongoDB) ---
        failed_payments_collection = mongo_db['failed_payments']
        failed_payments_logs = list(failed_payments_collection.find().sort("_id", -1).limit(50))
        failed_payments_json = json.loads(json_util.dumps(failed_payments_logs))

        # --- Summary Calculation ---
        total_transactions = total_suspicious + total_legitimate
        fraud_percentage = (total_suspicious / total_transactions * 100) if total_transactions > 0 else 0

        dashboard_data = {
            "summary": {
                "total_suspicious": total_suspicious,
                "total_legitimate": total_legitimate,
                "fraud_percentage": f"{fraud_percentage:.2f}%"
            },
            "honeypot_logs": honeypot_logs_json,
            "legitimate_transactions": legitimate_transactions,
            "failed_payments": failed_payments_json
        }
        
        return jsonify(dashboard_data), 200

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve dashboard data: {e}"}), 500

@api_blueprint.route('/analytics_data', methods=['GET'])
def get_analytics_data():
    """
    This endpoint provides aggregated data for the analytics dashboard.
    It now robustly handles historical data that may be missing the 'Timestamp' field
    by using the record's creation time as a fallback.
    """
    try:
        mongo_db = get_mongo_db()
        honeypot_collection = mongo_db['suspicious_transactions']

        # Time series analysis: Use the '_id' creation time as a fallback for missing Timestamps.
        hourly_counts_agg = list(honeypot_collection.aggregate([
            {
                "$project": {
                    "activity_time": {
                        "$ifNull": ["$Timestamp", {"$toDate": "$_id"}]
                    }
                }
            },
            {
                "$group": {
                    "_id": {"hour": {"$hour": "$activity_time"}},
                    "count": {"$sum": 1}
                }
            }
        ]))
        hourly_counts_map = {item['_id']['hour']: item['count'] for item in hourly_counts_agg}
        hour_labels = [f"{h}:00" for h in range(24)]
        time_series_data = [hourly_counts_map.get(h, 0) for h in range(24)]

        # Geographic analysis
        country_breakdown = list(honeypot_collection.aggregate([
            {"$match": {"Country": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$Country", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))

        # KPI: Top Attacker IP
        top_ip_agg = list(honeypot_collection.aggregate([
            {"$match": {"Attacker IP": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$Attacker IP", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]))
        top_attacker_ip = top_ip_agg[0]['_id'] if top_ip_agg else 'N/A'

        # KPI: Peak Fraud Time
        peak_fraud_time = 'N/A'
        if hourly_counts_map:
            peak_hour = max(hourly_counts_map, key=hourly_counts_map.get)
            peak_fraud_time = f"{peak_hour}:00"

        # KPI: Most Attacked Country
        most_attacked_country = country_breakdown[0]['_id'] if country_breakdown else 'N/A'

        analytics_data = {
            "kpis": {
                "top_attacker_ip": top_attacker_ip,
                "peak_fraud_time": peak_fraud_time,
                "most_attacked_country": most_attacked_country
            },
            "time_series": {
                "labels": hour_labels,
                "data": time_series_data
            },
            "geo_breakdown": {
                "labels": [c['_id'] for c in country_breakdown],
                "data": [c['count'] for c in country_breakdown]
            }
        }
        print(f"Analytics Data: {analytics_data}")
        return jsonify(analytics_data), 200

    except Exception as e:
        print(f"CRITICAL Error in get_analytics_data: {e}")
        return jsonify({"error": f"Failed to retrieve analytics data: {e}"}), 500

@api_blueprint.route('/log_failed_payment', methods=['POST'])
def log_failed_payment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    try:
        # Avoid timezone-aware issues by using UTC time directly
        data['LoggedAt'] = datetime.utcnow()
        mongo_db = get_mongo_db()
        collection = mongo_db['failed_payments']
        collection.insert_one(data)
        return jsonify({"status": "success", "message": "Failed payment logged successfully"}), 200
    except Exception as e:
        print(f"Error logging failed payment: {e}")
        return jsonify({"error": f"Failed to log payment: {e}"}), 500

