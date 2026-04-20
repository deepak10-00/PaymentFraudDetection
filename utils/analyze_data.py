import pandas as pd

try:
    df = pd.read_csv('creditcard.csv')
    print(f"Total rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print("Class distribution:")
    print(df['Class'].value_counts())
    
    # Save a sample if we have both classes
    if 1 in df['Class'].values:
        fraud = df[df['Class'] == 1].sample(n=min(5, len(df[df['Class'] == 1])))
        normal = df[df['Class'] == 0].sample(n=5)
        sample = pd.concat([fraud, normal])
        sample.to_csv('sample_fraud_dataset.csv', index=False)
        print("Created sample_fraud_dataset.csv with mixed classes.")
    else:
        print("No fraud cases found in creditcard.csv")

except Exception as e:
    print(f"Error: {e}")
