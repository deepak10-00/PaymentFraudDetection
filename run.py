import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.api.routes import api_blueprint

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize the Flask app with the static folder pointing to the 'static' directory
app = Flask(__name__, static_folder='static', static_url_path='')

# Enable CORS for the entire application
CORS(app)

# Register the consolidated API blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')

# --- Frontend Routes ---

@app.route('/')
def serve_index():
    """Serves the main dashboard page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/analytics.html')
def serve_analytics():
    """Serves the analytics page."""
    return send_from_directory(app.static_folder, 'analytics.html')

@app.route('/settings.html')
def serve_settings():
    """Serves the settings page."""
    return send_from_directory(app.static_folder, 'settings.html')

if __name__ == '__main__':
    # The debug=True flag enables live reloading and detailed error pages.
    app.run(debug=True)
