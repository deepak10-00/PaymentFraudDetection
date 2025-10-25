import pymysql
from pymongo import MongoClient
from config.settings import settings

def get_mysql_db():
    """Establishes a connection to the main MySQL database."""
    return pymysql.connect(
        host=settings.MYSQL_HOST,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_mongo_db():
    """Establishes a connection to the MongoDB honeypot database (auth disabled)."""
    # Connect without username/password for local development
    client = MongoClient(
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT
    )
    return client[settings.MONGO_DB]
