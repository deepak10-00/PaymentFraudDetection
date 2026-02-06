"""
This module contains the application settings and configurations.
"""

import os

class Settings:
    APP_NAME: str = "Proactive Fraud Detection System"
    APP_VERSION: str = "0.0.1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    # --- Local Development Database Settings ---
    # These are the hostnames for local development
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "fraud_user")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "mysecretpassword123")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "fraud_detection_db")

    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", 27017))
    MONGO_DB: str = os.getenv("MONGO_DB", "honeypot_db")

    # Risk Analysis Engine settings
    RISK_THRESHOLD: float = float(os.getenv("RISK_THRESHOLD", 0.7))
    # Correct paths for the model and scaler files at the project root
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "fraud_model.pkl")
    SCALER_PATH: str = os.getenv("SCALER_PATH", "scaler.pkl")

settings = Settings()
