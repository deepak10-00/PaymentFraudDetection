# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for pymysql (if any, though often not needed for pure Python)
# For example, if you were using psycopg2 for PostgreSQL, you might need build-essential and libpq-dev
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Define environment variables for database connections (these should ideally be managed by your deployment environment)
ENV MYSQL_HOST=localhost
ENV MYSQL_USER=fraud_user
ENV MYSQL_PASSWORD=your_mysql_password
ENV MYSQL_DB=fraud_detection_db
ENV MONGO_HOST=localhost
ENV MONGO_PORT=27017
ENV MONGO_DB=honeypot_db
ENV RISK_THRESHOLD=0.7
ENV ML_MODEL_PATH=/app/app/ml/models/fraud_model.pkl

# Command to run the application using Uvicorn
# We use gunicorn to manage uvicorn workers for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
