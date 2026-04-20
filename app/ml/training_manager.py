import numpy as np
import joblib # Import joblib
from sklearn.preprocessing import StandardScaler # Import StandardScaler
from typing import List, Dict, Any, Tuple
import json

from app.database.crud import get_all_legitimate_transactions, get_all_honeypot_logs
from app.ml.adaptive_model import AdaptiveMLModel
from config.settings import settings # Import settings to get SCALER_PATH

class TrainingManager:
    def __init__(self, adaptive_model: AdaptiveMLModel):
        self.adaptive_model = adaptive_model

    def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Fetches data from databases and prepares it for model training using the AdaptiveMLModel's preprocessing."""
        print("Preparing training data using centralized preprocessing...")
        
        # 1. Fetch data
        legit_transactions = get_all_legitimate_transactions()
        honeypot_logs = get_all_honeypot_logs()

        features = []
        labels = []

        # 2. Process legitimate transactions (label = 0)
        for trans in legit_transactions:
            # The transaction data is in the 'details' column as a JSON string
            try:
                details = json.loads(trans['details'])
                feature_vector = self.adaptive_model._preprocess_transaction_data(details)
                features.append(feature_vector[0])
                labels.append(0) # 0 for legitimate
            except (json.JSONDecodeError, KeyError):
                continue

        # 3. Process fraudulent transactions from honeypot (label = 1)
        for log in honeypot_logs:
            trans_data = log.get('transaction_data', {})
            if not trans_data:
                continue
            # Use the AdaptiveMLModel's own preprocessing method
            feature_vector = self.adaptive_model._preprocess_transaction_data(trans_data)
            features.append(feature_vector[0])
            labels.append(1) # 1 for fraudulent

        if not features:
            print("No training data found. Skipping retraining.")
            return None, None

        print(f"Prepared {len(features)} total samples for training ({len(legit_transactions)} legitimate, {len(honeypot_logs)} fraudulent).")
        return np.array(features), np.array(labels)

    def retrain_model(self) -> Dict[str, Any]:
        """Orchestrates the model retraining process."""
        print("Starting model retraining process...")
        X_train, y_train = self._prepare_training_data()

        if X_train is None or y_train is None or len(X_train) == 0:
            return {"status": "skipped", "message": "No new training data was available."}

        # 1. Retrain the StandardScaler
        print("Retraining StandardScaler...")
        new_scaler = StandardScaler()
        X_train_scaled = new_scaler.fit_transform(X_train)
        joblib.dump(new_scaler, settings.SCALER_PATH)
        print(f"StandardScaler retrained and saved to {settings.SCALER_PATH}")

        # 2. Retrain the ML model using the newly scaled data
        self.adaptive_model.train_model(X_train_scaled, y_train)
        
        # 3. Update the AdaptiveMLModel's internal scaler with the new one
        self.adaptive_model.scaler = new_scaler

        return {
            "status": "success",
            "message": f"Model and Scaler retrained successfully with {len(X_train)} samples.",
            "samples_used": len(X_train)
        }
