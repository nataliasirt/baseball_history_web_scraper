import sqlite3
import pandas as pd
import os
import logging
import time

logging.basicConfig(
    filename=f"importer_{time.strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def import_to_db(input_folder, db_name):
    csv_files = [f for f in os.listdir(input_folder) if f.endswith("_cleaned.csv")]
    
    if not csv_files:
        logging.error(f"No _cleaned.csv files found in {input_folder}")
        return
    
    with sqlite3.connect(db_name) as conn:
        for file in csv_files:
            try:
                logging.info(f"Processing: {file}")
                file_path = os.path.join(input_folder, file)
                df = pd.read_csv(file_path)
                
                if df.empty:
                    logging.warning(f"Empty CSV: {file}. Skipping import.")
                    continue
                
                # Get table and metric names
                table_name = os.path.splitext(file)[0].replace("_cleaned", "").lower().replace(" ", "_")
                metric_col = df.columns[-1]
                metric_sql = metric_col.lower().replace(" ", "_")
                
                # Rename columns to match SQL table
                df = df.rename(columns={
                    "Year": "Year",
                    "League": "League",
                    "Player": "Player",
                    "Team": "Team",
                    metric_col: metric_sql
                })
                
                # Validate columns
                expected_columns = ["Year", "League", "Player", "Team", metric_sql]
                if not all(col in df.columns for col in expected_columns):
                    logging.error(f"Invalid columns in {file}: {df.columns}. Expected: {expected_columns}")
                    continue
                
                # Drop existing table
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                conn.execute(f"""
                    CREATE TABLE {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Year INTEGER,
                        League TEXT,
                        Player TEXT,
                        Team TEXT,
                        {metric_sql} REAL
                    )
                """)
                
                # Import data
                df.to_sql(table_name, conn, if_exists="append", index=False)
                logging.info(f"Imported: {file} -> {table_name} with {len(df)} rows")
                
                # Verify import
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                logging.info(f"Verified: {table_name} has {row_count} rows in database")
                
            except Exception as e:
                logging.error(f"Error importing {file}: {e}")
                continue

if __name__ == "__main__":
    import_to_db("cleaned_csv", "baseball.db")