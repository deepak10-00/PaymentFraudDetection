import pytest
import numpy as np
from app.ml.adaptive_model import AdaptiveMLModel

# Sample payload for a legitimate transaction (based on creditcard.csv 'Class' 0)
legit_payload = {
  "Time": 406, "V1": -2.31, "V2": 1.95, "V3": -1.60, "V4": 3.99, "V5": -0.52,
  "V6": -1.42, "V7": -2.53, "V8": 1.39, "V9": -2.77, "V10": -2.77, "V11": 3.20,
  "V12": -2.89, "V13": -0.59, "V14": -4.28, "V15": 0.38, "V16": -1.14, "V17": -2.83,
  "V18": -0.01, "V19": 0.41, "V20": 0.12, "V21": 0.51, "V22": -0.03, "V23": -0.46,
  "V24": 0.32, "V25": 0.04, "V26": 0.17, "V27": 0.26, "V28": -0.14, "Amount": 0.00
}

# Sample payload for a fraudulent transaction (based on creditcard.csv 'Class' 1)
fraud_payload = {
  "Time": 472, "V1": -3.04, "V2": -3.15, "V3": 1.08, "V4": 2.28, "V5": 1.35,
  "V6": -1.06, "V7": 0.32, "V8": -0.06, "V9": -0.27, "V10": -0.83, "V11": -0.41,
  "V12": -0.50, "V13": -0.11, "V14": -0.28, "V15": -0.51, "V16": 0.72, "V17": -0.88,
  "V18": -0.25, "V19": -0.63, "V20": -0.29, "V21": 0.66, "V22": 0.43, "V23": 1.37,
  "V24": -0.29, "V25": -0.14, "V26": -0.21, "V27": -0.54, "V28": 0.13, "Amount": 529.00
}

@pytest.fixture(scope="module")
def analyzer() -> AdaptiveMLModel:
    """Provides a single AdaptiveMLModel instance for all tests in this module."""
    return AdaptiveMLModel()

def test_risk_analyzer_initialization(analyzer: AdaptiveMLModel):
    """Tests that the analyzer and its components (model, scaler) are loaded."""
    assert analyzer is not None
    assert analyzer.model is not None
    assert analyzer.scaler is not None

def test_preprocess_transaction_data(analyzer: AdaptiveMLModel):
    """Tests the feature preparation logic to ensure it matches the training format."""
    features = analyzer._preprocess_transaction_data(legit_payload)
    
    # The shape should be (1, 30) because the model is trained on 30 features from the CSV
    assert isinstance(features, np.ndarray)
    assert features.shape == (1, 30)
    
    # Check that the 'Amount' is the last feature, as per the training script
    assert features[0, -1] == legit_payload["Amount"]

def test_analyze_legitimate_transaction(analyzer: AdaptiveMLModel):
    """Tests that a known legitimate transaction yields a low risk score."""
    risk_score, explanations, _ = analyzer.analyze_transaction(legit_payload)
    
    assert isinstance(risk_score, float)
    assert risk_score < 0.5 # Expect a low score for a legitimate transaction
    assert isinstance(explanations, list)
    assert len(explanations) == 0 # No explanations for low-risk transactions

def test_analyze_fraudulent_transaction(analyzer: AdaptiveMLModel):
    """Tests that a known fraudulent transaction yields a high risk score."""
    risk_score, explanations, _ = analyzer.analyze_transaction(fraud_payload)
    
    assert isinstance(risk_score, float)
    assert risk_score > 0.5 # Expect a high score for a fraudulent transaction
    assert isinstance(explanations, list)
    assert len(explanations) > 0 # Expect at least one explanation
