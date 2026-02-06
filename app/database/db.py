import pymysql
from pymongo import MongoClient
from config.settings import settings

# Global clients to avoid reconnecting on every request
_mysql_client = None
_mongo_client = None

def get_mysql_db():
    """
    Establishes and/or returns a connection to the main MySQL database.
    This is a simplified connection pool for demonstration.
    """
    global _mysql_client
    if _mysql_client is None or not _mysql_client.open:
        print("Connecting to MySQL...")
        _mysql_client = pymysql.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True # Ensure changes are committed without explicit calls
        )
    return _mysql_client

def get_mongo_db():
    """
    Establishes and/or returns a connection to the MongoDB honeypot database.
    """
    global _mongo_client
    if _mongo_client is None:
        print("Connecting to MongoDB...")
        # Connect without username/password for local development
        _mongo_client = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
            # Add a timeout to prevent the app from hanging if Mongo is down
            serverSelectionTimeoutMS=5000 
        )
    # The client object is thread-safe and handles connection pooling automatically.
    return _mongo_client[settings.MONGO_DB]
