import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.db import get_mysql_db, get_mongo_db

def clear_all_data():
    try:
        mysql_db = get_mysql_db()
        with mysql_db.cursor() as cursor:
            cursor.execute("DELETE FROM transactions")
        mysql_db.commit()
        mysql_db.close()
        print("Successfully cleared all legitimate transactions from MySQL.")
    except Exception as e:
        print(f"Error clearing MySQL data: {e}")

    try:
        mongo_db = get_mongo_db()
        result = mongo_db.honeypot_logs.delete_many({})
        print(f"Successfully cleared {result.deleted_count} honeypot logs from MongoDB.")
    except Exception as e:
        print(f"Error clearing MongoDB data: {e}")

if __name__ == "__main__":
    clear_all_data()
