-- This script initializes the database for the Proactive Fraud Detection System.

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    is_fraud BOOLEAN NOT NULL DEFAULT FALSE,
    amount DECIMAL(10, 2) NOT NULL,
    details TEXT, -- A JSON blob to store all transaction details
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Note: The 'suspicious_transactions' collection is created automatically by MongoDB
-- when the first document is inserted into it by the HoneypotGateway.
