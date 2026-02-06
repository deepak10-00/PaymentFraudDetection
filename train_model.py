import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

# Paths for saving model and scaler
MODEL_PATH = "fraud_model.pkl"
SCALER_PATH = "scaler.pkl"

def load_and_preprocess_data(filepath='creditcard.csv'):
    """
    Loads the real dataset from creditcard.csv, preprocesses it, 
    and prepares it for training using all available features.
    """
    print(f"Loading and preprocessing data from {filepath}...")
    
    # Load the dataset
    df = pd.read_csv(filepath)
    
    # --- Feature Selection ---
    # Use all available features from the CSV.
    # The 'Class' column is the label, so we drop it from the features.
    if 'Class' in df.columns:
        X = df.drop('Class', axis=1)
        y = df['Class']
    else:
        # Handle case where 'Class' column might be missing
        raise ValueError("Target column 'Class' not found in the dataset.")

    print("Data preprocessing complete. Using all available features.")
    return X, y

if __name__ == "__main__":
    # 1. Load and preprocess the real data from creditcard.csv
    X, y = load_and_preprocess_data()
    
    # 2. Split data for training and testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 3. Scale features
    # It's important to scale the features for models like Logistic Regression.
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Train the Logistic Regression model
    print("Training the Logistic Regression model...")
    model = LogisticRegression(random_state=42, max_iter=1000, solver='lbfgs') # Using a robust solver
    model.fit(X_train_scaled, y_train)
    
    # 5. Evaluate the model
    print("\nModel Evaluation Report:")
    y_pred = model.predict(X_test_scaled)
    print(classification_report(y_test, y_pred))
    
    # 6. Save the trained model and scaler
    joblib.dump(model, MODEL_PATH)
    print(f"Model successfully trained and saved to {MODEL_PATH}")
    
    joblib.dump(scaler, SCALER_PATH)
    print(f"Scaler successfully trained and saved to {SCALER_PATH}")
