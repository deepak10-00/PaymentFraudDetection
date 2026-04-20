import joblib
import numpy as np

# Load the trained model and scaler
model = joblib.load('c:\\proactive\\fraud_model.pkl')
scaler = joblib.load('c:\\proactive\\scaler.pkl')

print("Model:", type(model))
# Try to figure out a "safe" vector
# For Logistic Regression, the safest point is moving in the opposite direction of the coefficients.
# Or simply using the scaler's mean which represents an "average" transaction from the training data.

mean_vector = scaler.mean_
safe_vector = mean_vector.reshape(1, -1)

# Scale it (using the mean vector scaled will be all 0s)
scaled_safe = scaler.transform(safe_vector)

prob = model.predict_proba(scaled_safe)[0][1]
print(f"Risk of mean vector: {prob}")

print("Mean vector values to use in frontend:")
feature_names = ['Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
                'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
                'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 'Amount']

for i, name in enumerate(feature_names):
    print(f"                {name}: {mean_vector[i]},")
