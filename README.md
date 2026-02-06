# Proactive Fraud Detection System

This project is a full-stack web application that demonstrates a proactive approach to digital payment fraud detection. It combines a machine learning model for real-time risk analysis with a honeypot system to safely gather intelligence on fraudulent attempts.

## Core Features

- **Real-Time Transaction Analysis:** A FastAPI-based API endpoint that processes payment transactions in real-time.
- **ML-Powered Risk Scoring:** A Logistic Regression model trained on real-world data to assign a fraud risk score to each transaction.
- **Honeypot Diversion:** High-risk transactions are automatically diverted to a honeypot, protecting the core system while gathering data on attack patterns.
- **Dual-Database Architecture:**
    - **MySQL:** Stores all legitimate transaction records.
    - **MongoDB:** Logs all suspicious activity diverted to the honeypot for detailed analysis.
- **Dashboard & Analytics:** A clean, professional web interface for monitoring system activity, viewing transaction lists, and exploring analytics on fraudulent trends.
- **Containerized Deployment:** The entire application stack is containerized with Docker and managed with Docker Compose for easy, consistent deployment.

## Technical Architecture

- **Backend:** **FastAPI** (a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints).
- **Machine Learning:** **Scikit-learn** for model training and real-time predictions.
- **Databases:** 
    - **MySQL 8.0** for structured transaction data.
    - **MongoDB 5.0** for flexible, unstructured honeypot logs.
- **Frontend:** A responsive single-page application built with vanilla **HTML, CSS, and JavaScript**, using **Chart.js** for data visualization.
- **Containerization:** **Docker** and **Docker Compose**.

## How to Run with Docker (Recommended)

This is the simplest and most reliable way to run the entire application stack.

### 1. Prerequisites

- **Docker** and **Docker Compose** installed and running on your machine.

### 2. Build and Run the Application

From the project's root directory, run the following command:

```sh
docker-compose up --build
```

This command will:
1. Build the Docker image for the FastAPI application.
2. Start containers for the FastAPI app, MySQL database, and MongoDB database.
3. Initialize the MySQL database using the `db/init.sql` script.

### 3. Access the Application

- **Web Dashboard:** Open your browser and go to `http://localhost:8000`
- **API Docs:** The API documentation is available at `http://localhost:8000/docs`
- **API Testing:** Use the provided `test_api.http` file in an IDE like VS Code (with the REST Client extension) to send test transactions to `http://localhost:8000/api/process_transaction`.

## Local Development (Without Docker)

### 1. Prerequisites

- Python 3.9+
- MySQL Server
- MongoDB Server

### 2. Database Setup

1. **MySQL:**
   - Ensure your MySQL server is running.
   - Create a database named `fraud_detection_db`.
   - Create a user `fraud_user` with the password `mysecretpassword123` and grant it all privileges on the database.
   - Run the script in `db/init.sql` to create the `transactions` table.

2. **MongoDB:**
   - Ensure your MongoDB server is running on its default port (27017). No authentication is required for local setup.

### 3. Environment Setup

From the project root:

```sh
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

### 4. Train the Model

Before running the app, you must train the ML model using the provided dataset:

```sh
python train_model.py
```

This will generate `fraud_model.pkl` and `scaler.pkl` in the project root.

### 5. Run the Application

```sh
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.
