import joblib
import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from config.settings import settings
from typing import List, Tuple

class RiskAnalyzer:
    # The feature names must match the columns from the training script
    FEATURE_NAMES = ['Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
                     'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
                     'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 'Amount']

    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_path = settings.ML_MODEL_PATH
        self.scaler_path = settings.SCALER_PATH
        self._load_model()

    def _load_model(self):
        """Loads the model and scaler from disk."""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            print(f"Loading ML model from {self.model_path}")
            self.model = joblib.load(self.model_path)
            print(f"Loading scaler from {self.scaler_path}")
            self.scaler = joblib.load(self.scaler_path)
        else:
            # This should not happen in a production environment.
            # The model should be trained and available before the app starts.
            raise FileNotFoundError("Model or scaler not found. Please run the training script first.")

    def _preprocess_transaction_data(self, transaction_data: dict) -> np.ndarray:
        """
        Prepares the transaction data to match the feature set used during training.
        """
        # Create a feature vector from the transaction data in the correct order.
        # Default to 0 for any missing features.
        feature_values = [transaction_data.get(name, 0.0) for name in self.FEATURE_NAMES]
        
        features = np.array(feature_values).reshape(1, -1)
        return features

    def _get_risk_explanations(self, transaction_data: dict, risk_score: float) -> List[str]:
        """Generates human-readable explanations for a high-risk score."""
        explanations = []
        if risk_score < settings.RISK_THRESHOLD:
            return explanations

        # Example explanations based on the V-features (which are anonymized)
        if transaction_data.get("V4", 0) > 1:
            explanations.append("Unusual pattern detected in V4 feature.")
        if transaction_data.get("V17", 0) < -1:
            explanations.append("Suspiciously low value in V17 feature.")
        if transaction_data.get("Amount", 0) > 2000:
            explanations.append("Unusually high transaction amount.")
        
        if not explanations:
            explanations.append("Transaction pattern matches known fraudulent behavior.")

        return explanations

    def analyze_transaction(self, transaction_data: dict) -> Tuple[float, List[str], List[float]]:
        """
        Analyzes a transaction and returns a risk score, a list of explanations, and the scaled features.
        """
        if self.model is None or self.scaler is None:
            print("Error: ML model or scaler not loaded.")
            return 0.99, ["System error: Model not loaded"], []

        features = self._preprocess_transaction_data(transaction_data)
        scaled_features = self.scaler.transform(features)
        risk_score = float(self.model.predict_proba(scaled_features)[0][1])
        
        explanations = self._get_risk_explanations(transaction_data, risk_score)
        
        return risk_score, explanations, scaled_features.flatten().tolist()

    def update_model(self, new_model_path: str, new_scaler_path: str):
        """Updates the model and scaler from new files."""
        if os.path.exists(new_model_path) and os.path.exists(new_scaler_path):
            print(f"Updating ML model from {new_model_path}")
            self.model = joblib.load(new_model_path)
            joblib.dump(self.model, self.model_path)
            
            print(f"Updating scaler from {new_scaler_path}")
            self.scaler = joblib.load(new_scaler_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            print("ML model and scaler updated successfully.")
        else:
            print(f"Error: New model or scaler file not found.")
