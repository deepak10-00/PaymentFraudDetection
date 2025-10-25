import pandas as pd

class RiskAnalysisEngine:
    def __init__(self):
        """
        This is a SIMULATED engine. It does not use a real ML model.
        It is designed to demonstrate the project's architecture even with a flawed dataset.
        """
        print("--- Using SIMULATED Risk Analysis Engine ---")
        pass

    def analyze(self, transaction_data):
        """
        Simulates a risk score based on the transaction amount.
        - Amount > 1000 is considered high-risk.
        - Amount <= 1000 is considered low-risk.
        """
        try:
            amount = float(transaction_data.get('Amount', 0.0))
            
            if amount > 1000.0:
                print(f"SIMULATED: High-risk amount detected (${amount}).")
                return 0.9  # High risk score
            else:
                print(f"SIMULATED: Low-risk amount detected (${amount}).")
                return 0.1  # Low risk score

        except Exception as e:
            print(f"Error during simulated analysis: {e}")
            return 1.0 # Default to high risk on error
