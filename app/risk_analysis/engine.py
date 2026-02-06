import joblib
import numpy as np
import os
from app.ml.risk_analyzer import RiskAnalyzer

class RiskAnalysisEngine:
    def __init__(self, model_path='fraud_model.pkl', scaler_path='scaler.pkl'):
        """
        Initializes the risk analysis engine by creating an instance of the RiskAnalyzer.
        """
        print("--- Initializing Real Risk Analysis Engine ---")
        # The RiskAnalyzer class now encapsulates all the ML logic.
        self.analyzer = RiskAnalyzer()

    def analyze(self, transaction_data):
        """
        Analyzes a transaction by delegating to the RiskAnalyzer instance.
        """
        try:
            # The analyze_transaction method returns the score, explanations, and features.
            risk_score, _, _ = self.analyzer.analyze_transaction(transaction_data)
            
            print(f"Analyzed transaction. Risk score: {risk_score:.4f}")
            return risk_score

        except Exception as e:
            print(f"Error during real analysis: {e}")
            # Default to a high-risk score to be safe in case of errors.
            return 1.0
