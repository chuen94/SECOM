import subprocess
from dagster import asset, Definitions, ScheduleDefinition, define_asset_job
import sys

@asset
def ingest_sensor_data():
    # Fetch raw SECOM sensor data and upload to Snowflake internal stage
    subprocess.run([sys.executable, "ingestion.py"], check=True)
    return "Ingestion Complete"

@asset(deps=[ingest_sensor_data])
def run_dbt_pipeline():
    # Run all dbt transformations and data quality tests.
    subprocess.run(["dbt", "build"], cwd="secom_pj", shell=True, check=True)
    return "dbt Pipeline Complete"

# Define a daily schedule 
daily_refresh_schedule = ScheduleDefinition(
    job=define_asset_job(name="secom_daily_refresh", selection="*"),
    cron_schedule="0 2 * * *", # Run at 2:00 AM every day
)

# Bundle everything up 
defs = Definitions(
    assets=[ingest_sensor_data, run_dbt_pipeline],
    schedules=[daily_refresh_schedule],
)