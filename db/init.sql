CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    payment_method VARCHAR(50), -- Added new feature
    country VARCHAR(10), -- Added new feature
    transaction_timestamp DATETIME NOT NULL,
    risk_score FLOAT,
    scaled_features TEXT, -- Added new column for scaled features
    status VARCHAR(50) DEFAULT 'processed_legitimately',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;