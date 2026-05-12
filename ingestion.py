import pandas as pd
import snowflake.connector
import os
from dotenv import load_dotenv
import tempfile

load_dotenv(override=True)

def fetch_and_prep_secom_data():
    print("Fetching raw SECOM data from UCI Repository")
    
    # URLs for the raw data
    data_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom.data"
    labels_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom_labels.data"

    df_data = pd.read_csv(data_url, sep=' ', header=None)
    
    df_labels = pd.read_csv(labels_url, sep=' ', header=None, parse_dates=[1], dayfirst=True)
    df_labels.columns = ['CLASSIFICATION', 'RECORD_TIMESTAMP']

    df_merged = pd.concat([df_labels, df_data], axis=1).copy()
    
    df_merged['INGESTION_BATCH_AT'] = pd.Timestamp.now()
    
    print(f"Data fetched successfully. Shape: {df_merged.shape}")
    return df_merged

def upload_to_snowflake(df):
    
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        role=os.getenv('SNOWFLAKE_ROLE'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
    )
    cursor = conn.cursor()

    try:
        # Create a working environment
        print("Building Snowflake Database and Stage")
        cursor.execute("CREATE DATABASE IF NOT EXISTS SECOM_MFG;")
        cursor.execute("USE DATABASE SECOM_MFG;")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS RAW;")
        cursor.execute("USE SCHEMA RAW;")
        
       
        cursor.execute("CREATE STAGE IF NOT EXISTS SECOM_INTERNAL_STAGE;")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            df.to_csv(temp_file.name, index=False, header=False)
            temp_path = temp_file.name

        print("Uploading batch file to Internal Stage")
        safe_path = temp_path.replace('\\', '\\\\')
        cursor.execute(f"PUT file://{safe_path} @SECOM_INTERNAL_STAGE auto_compress=true;")
        
        os.remove(temp_path)
        print("Batch ingestion complete! File is in @SECOM_INTERNAL_STAGE")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    df_secom = fetch_and_prep_secom_data()
    upload_to_snowflake(df_secom)