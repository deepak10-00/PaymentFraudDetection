# Proactive Fraud Detection System

This project is a full-stack web application that demonstrates a proactive approach to digital payment fraud detection. It combines a machine learning model for real-time risk analysis with a honeypot system to safely gather intelligence on fraudulent attempts.

## Core Features

- **Transaction Processing:** An API endpoint to receive and process new payment transactions.
- **Risk Analysis with ML:** A machine learning model (Logistic Regression) that analyzes transaction data in real-time to produce a fraud risk score.
- **Honeypot Diversion:** An intelligent system that automatically diverts high-risk transactions to a honeypot gateway, protecting the main system and deceiving attackers.
- **Database Logging (MySQL & MongoDB):**
    - Legitimate transactions are logged to a **MySQL** database for clean, structured record-keeping.
    - Fraudulent attempts diverted to the honeypot are logged in rich detail to a **MongoDB** database for analysis.
- **Model Retraining:** A continuous improvement feedback loop via an API endpoint that retrains the ML model using the latest data from both databases.
- **Risk Explanations:** The system provides clear, human-readable reasons why a transaction was flagged as high-risk.
- **Interactive Filtering:** A dynamic, professional web dashboard that allows for live monitoring and interactive filtering of both legitimate and fraudulent transaction data.

## Technical Architecture

- **Backend:** Built with **FastAPI**, providing a high-performance API.
- **Machine Learning:** Implemented using **Scikit-learn** for model training and prediction.
- **Databases:** 
    - **MySQL:** For storing structured data of legitimate transactions.
    - **MongoDB:** For storing unstructured honeypot logs and intelligence.
- **Frontend:** A dynamic, single-page application built with vanilla **HTML, CSS, and JavaScript**, enhanced with **Bootstrap** for layout, **Chart.js** for data visualization, and **Feather Icons** for a professional UI.
- **Testing:** The backend includes a suite of automated tests written with **Pytest**.

## How to Run Locally

### 1. Prerequisites

- **Python 3.9+** installed and added to your PATH.
- **MySQL Community Server** installed and running.
- **MongoDB Community Server** installed and running as a service.

### 2. Database Setup

Open the MySQL Command Line Client and run the following commands to set up the database and user:

```sql
-- Create the database
CREATE DATABASE fraud_detection_db;

-- Create a dedicated user and set its password
CREATE USER 'fraud_user'@'localhost' IDENTIFIED BY 'mysecretpassword123';

-- Grant the user permissions on the new database
GRANT ALL PRIVILEGES ON fraud_detection_db.* TO 'fraud_user'@'localhost';

-- Use the database
USE fraud_detection_db;

-- Create the transactions table
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    payment_method VARCHAR(50),
    country VARCHAR(10),
    transaction_timestamp DATETIME NOT NULL,
    risk_score FLOAT,
    status VARCHAR(50) DEFAULT 'processed_legitimately',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Environment Setup

Navigate to the project's root directory (`D:\proactive`) in your terminal and run the following commands:

```sh
# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate
```

### 4. Install Dependencies

With the virtual environment active, install all required Python packages:

```sh
pip install -r requirements.txt
```

### 5. Run the Application

Start the FastAPI server with auto-reload enabled:

```sh
uvicorn app.main:app --reload
```

### 6. Access the Application

- **Dashboard:** Open your web browser and navigate to `http://localhost:8000`
- **API Docs:** The API documentation is available at `http://localhost:8000/docs`
"# ProactivePaymentFraudDetection" 
"# PaymentFruadDetection" 
