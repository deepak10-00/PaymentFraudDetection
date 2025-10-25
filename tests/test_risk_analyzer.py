import pytest
import numpy as np
from app.ml.risk_analyzer import RiskAnalyzer

# Sample transaction data for testing
sample_transaction = {
    "transaction_id": "test-tx-123",
    "user_id": "test-user-abc",
    "amount": 1500.0,
    "currency": "USD",
    "timestamp": "2023-10-27T10:00:00Z",
    "payment_method": "credit_card",
    "country": "US"
}

@pytest.fixture
def analyzer():
    """Provides a RiskAnalyzer instance for tests."""
    return RiskAnalyzer()

def test_risk_analyzer_initialization(analyzer: RiskAnalyzer):
    """Tests that the analyzer and its model initialize correctly."""
    assert analyzer is not None
    assert analyzer.model is not None

def test_preprocess_transaction_data(analyzer: RiskAnalyzer):
    """Tests the one-hot encoding and feature preparation logic."""
    features = analyzer._preprocess_transaction_data(sample_transaction)
    
    # The shape should be (1, 10) because:
    # 1 (amount) + 4 (payment_methods) + 5 (countries) = 10 features
    assert isinstance(features, np.ndarray)
    assert features.shape == (1, 10)
    
    # Check that the amount is the first feature
    assert features[0, 0] == sample_transaction["amount"]

def test_analyze_transaction_returns_score_and_explanations(analyzer: RiskAnalyzer):
    """Tests that the main analysis function returns the correct data types."""
    risk_score, explanations = analyzer.analyze_transaction(sample_transaction)
    
    assert isinstance(risk_score, float)
    assert 0.0 <= risk_score <= 1.0
    
    assert isinstance(explanations, list)
    # For this high-risk sample, we expect at least one explanation
    if risk_score > 0.7:
        assert len(explanations) > 0
