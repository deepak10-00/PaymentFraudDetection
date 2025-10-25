from flask import Blueprint, jsonify
from app.database.db import get_mongo_db
from bson import json_util
import json

# Create a new blueprint for the dashboard
dashboard_blueprint = Blueprint('dashboard', __name__)

@dashboard_blueprint.route('/', methods=['GET'])
def get_dashboard_data():
    """
    This endpoint provides the data needed for a front-end dashboard.
    It queries the honeypot database and returns a summary of suspicious activity.
    """
    try:
        mongo_db = get_mongo_db()
        collection = mongo_db['suspicious_transactions']
        
        # Fetch all suspicious transactions, sorted by most recent first
        suspicious_activities = list(collection.find().sort("_id", -1))
        
        # Use bson.json_util to correctly handle MongoDB's ObjectId
        activities_json = json.loads(json_util.dumps(suspicious_activities))

        dashboard_data = {
            "summary": {
                "total_suspicious_transactions": len(activities_json)
            },
            "honeypot_logs": activities_json
        }
        
        return jsonify(dashboard_data), 200

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve dashboard data: {e}"}), 500
