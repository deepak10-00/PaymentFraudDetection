import pymysql
from pymongo import MongoClient

# Database Settings (Localhost for non-docker)
MYSQL_HOST = "localhost"
MYSQL_USER = "fraud_user"
MYSQL_PASSWORD = "mysecretpassword123"
MYSQL_DB = "fraud_detection_db"

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "honeypot_db"

def clear_mysql():
    print("Connecting to MySQL...")
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            # Delete transaction data
            print("Deleting transactions from MySQL...")
            sql = "DELETE FROM transactions"
            cursor.execute(sql)
            connection.commit()
            print("Successfully cleared MySQL transactions.")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

def clear_mongodb():
    print("Connecting to MongoDB...")
    try:
        client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        db = client[MONGO_DB]
        collection = db['honeypot_logs']
        
        # Delete honeypot data
        print("Deleting logs from MongoDB...")
        result = collection.delete_many({})
        failed_res = db['failed_payments'].delete_many({})
        print(f"Successfully deleted {result.deleted_count} logs from honeypot_logs and {failed_res.deleted_count} from failed_payments.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    clear_mysql()
    print("-" * 20)
    clear_mongodb()
    print("Database clearing process finished.")
