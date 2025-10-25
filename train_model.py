import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import os

# Define the same feature lists as in RiskAnalyzer for consistency
PAYMENT_METHODS = ['credit_card', 'upi', 'wallet', 'net_banking']
COUNTRIES = ['IN', 'US', 'GB', 'DE', 'AU']

# Paths for saving model and scaler
MODEL_PATH = "fraud_model.pkl"
SCALER_PATH = "scaler.pkl"

def generate_synthetic_data(n_samples=10000):
    """Generates a synthetic dataset that mirrors the real-world data structure."""
    print(f"Generating {n_samples} synthetic data samples...")
    
    # Generate features
    amounts = np.random.lognormal(mean=4, sigma=1.5, size=n_samples) # Realistic amount distribution
    payment_methods = np.random.choice(PAYMENT_METHODS, n_samples, p=[0.5, 0.2, 0.2, 0.1])
    countries = np.random.choice(COUNTRIES, n_samples, p=[0.6, 0.2, 0.1, 0.05, 0.05])

    df = pd.DataFrame({
        'amount': amounts,
        'payment_method': payment_methods,
        'country': countries,
    })

    # Create a 'Class' column for fraud classification (0: legitimate, 1: fraudulent)
    df['Class'] = 0

    # Rule-based fraud for demonstration purposes (can be made more complex)
    # High amount transactions are more likely to be fraud
    df.loc[df['amount'] > 3000, 'Class'] = np.random.choice([0, 1], size=len(df[df['amount'] > 3000]), p=[0.7, 0.3])
    # Transactions from certain countries with high amounts are suspicious
    df.loc[(df['country'] != 'IN') & (df['amount'] > 1000), 'Class'] = np.random.choice([0, 1], size=len(df[(df['country'] != 'IN') & (df['amount'] > 1000)]), p=[0.5, 0.5])
    # Specific payment methods might be riskier
    df.loc[(df['payment_method'] == 'credit_card') & (df['amount'] > 2000), 'Class'] = np.random.choice([0, 1], size=len(df[(df['payment_method'] == 'credit_card') & (df['amount'] > 2000)]), p=[0.6, 0.4])

    print(f"Generated dataset with {df['Class'].sum()} fraudulent samples.")
    return df

def preprocess_data_for_training(df):
    """Applies one-hot encoding and selects feature columns consistent with RiskAnalyzer."""
    print("Preprocessing data with one-hot encoding...")
    
    # One-hot encode payment_method
    pm_dummies = pd.get_dummies(df['payment_method'], prefix='pm')
    # Ensure all PAYMENT_METHODS columns exist, fill missing with 0
    for method in PAYMENT_METHODS:
        if f'pm_{method}' not in pm_dummies.columns:
            pm_dummies[f'pm_{method}'] = 0
    pm_dummies = pm_dummies[[f'pm_{m}' for m in PAYMENT_METHODS]] # Ensure order

    # One-hot encode country
    country_dummies = pd.get_dummies(df['country'], prefix='country')
    # Ensure all COUNTRIES columns exist, fill missing with 0
    for country in COUNTRIES:
        if f'country_{country}' not in country_dummies.columns:
            country_dummies[f'country_{country}'] = 0
    country_dummies = country_dummies[[f'country_{c}' for c in COUNTRIES]] # Ensure order

    # Combine all features
    X_processed = pd.concat([df['amount'], pm_dummies, country_dummies], axis=1)
    y_labels = df['Class']
    
    return X_processed, y_labels

if __name__ == "__main__":
    # 1. Generate synthetic data
    synthetic_df = generate_synthetic_data(n_samples=20000) # Increased samples for better training
    
    # 2. Preprocess the data to create features and labels
    X, y = preprocess_data_for_training(synthetic_df)
    
    # 3. Split data for training and testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Scale features
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 5. Train the Logistic Regression model
    print("Training the Logistic Regression model...")
    model = LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000)
    model.fit(X_train_scaled, y_train)
    
    # 6. Evaluate the model
    print("\nModel Evaluation Report:")
    y_pred = model.predict(X_test_scaled)
    print(classification_report(y_test, y_pred))
    
    # 7. Save the trained model and scaler
    joblib.dump(model, MODEL_PATH)
    print(f"Model successfully trained and saved to {MODEL_PATH}")
    
    joblib.dump(scaler, SCALER_PATH)
    print(f"Scaler successfully trained and saved to {SCALER_PATH}")
