import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS  # Import the CORS library
from app.api.routes import api_blueprint
from app.dashboard.routes import dashboard_blueprint

app = Flask(__name__)

# This is the key change: Enable CORS for the entire application.
# This tells the browser to allow requests from the dashboard.html file.
CORS(app)

# Register the existing API blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')

# Register the new Dashboard blueprint
app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
