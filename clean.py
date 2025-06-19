import pandas as pd
import os
import logging

logging.basicConfig(filename="cleaner.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def clean_data(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    csv_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]
    
    for file in csv_files:
        try:
            logging.info(f"Processing file: {file}")
            file_path = os.path.join(input_folder, file)
            df = pd.read_csv(file_path)
            metric_col = df.columns[-1]
            
            logging.info(f"Before cleaning {file}: {len(df)} rows")
            
            # Relaxed validation
            df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
            valid_year = df["Year"].notna()
            valid_league = df["League"].notna()
            df[metric_col] = pd.to_numeric(df[metric_col], errors="coerce")
            valid_metric = df[metric_col].notna()
            is_valid = valid_year & valid_league & valid_metric
            
            cleaned_df = df[is_valid].copy()
            cleaned_df["Year"] = cleaned_df["Year"].astype(int)
            cleaned_df["League"] = cleaned_df["League"].str.strip().str.upper()
            cleaned_df["Player"] = cleaned_df["Player"].str.strip()
            cleaned_df["Team"] = cleaned_df["Team"].str.strip().str.upper()
            cleaned_df[metric_col] = cleaned_df[metric_col].astype(float)
            
            cleaned_df = cleaned_df.drop_duplicates(subset=["Year", "League", "Player", metric_col])
            
            logging.info(f"After cleaning {file}: {len(cleaned_df)} rows, removed {len(df) - len(cleaned_df)} rows")
            
            cleaned_filename = f"{os.path.splitext(file)[0]}_cleaned.csv"
            output_path = os.path.join(output_folder, cleaned_filename)
            cleaned_df.to_csv(output_path, index=False)
            logging.info(f"Saved: {output_path}")
        except Exception as e:
            logging.error(f"Error in {file}: {e}")

if __name__ == "__main__":
    clean_data("started_csv", "cleaned_csv")