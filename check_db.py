import sqlite3

def check_db(db_name="baseball.db"):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", tables)
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"Rows in {table_name}: {row_count}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"Columns in {table_name}: {columns}")
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_data = cursor.fetchall()
                print(f"Sample data from {table_name}: {sample_data}")
        conn.close()
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    check_db()