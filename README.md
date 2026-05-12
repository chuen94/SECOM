# SECOM Manufacturing Data Pipeline

**Business Problem:** Manufacturing facilities generate thousands of sensor readings per wafer daily. Without a clean, validated data infrastructure, downstream predictive maintenance models (like anomaly detection) fail silently on corrupt or missing inputs, leading to undetected equipment degradation and costly yield losses. 

**Solution:** This pipeline ensures Machine Learning-ready data by automatically extracting raw sensor outputs, enforcing strict data quality contracts, and dynamically standardizing sparse features before they ever reach the data science team.

---

## Pipeline Scale & Metrics

* **Throughput:** Processed **1,567** high-frequency manufacturing records per batch.
* **Dynamic Transformation:** Leveraged programmatic SQL (Jinja) to dynamically normalize and type-cast **590** independent sensor columns simultaneously.
* **Data Imputation:** Automatically caught and handled highly sparse data, imputing thousands of `NaN`/`NULL` sensor readings to prevent downstream ML clustering failures.
* **Performance:** End-to-end dbt transformation and test execution completes in **< 10 seconds**, fully optimized for cloud warehouse compute.

---

## Architecture & Tech Stack

* **Data Ingestion:** `Python` & `Pandas` (Extracting data via API and loading into cloud stages).
* **Data Warehouse:** `Snowflake` (Cloud storage and compute).
* **Data Transformation:** `dbt` (Medallion architecture, Jinja macros, and YAML data contracts).
* **Orchestration:** `Dagster` (Managing dependencies between Python and dbt via a visual DAG).
* **CI/CD:** `GitHub Actions` (Automated testing in temporary Snowflake schemas on Pull Requests).

## Key Engineering Highlights

1. **Dynamic SQL Generation:** Utilized **Jinja `for` loops** in dbt to dynamically generate over 600 lines of SQL, handling the transformation of 590 poorly-named sensor columns without manual, error-prone typing.
2. **Data Quality Contracts:** Implemented strict dbt tests to catch `NULL` classifications, enforce accepted mathematical bounds, and prevent broken sensor data from reaching downstream environments.
3. **Automated CI/CD:** Configured a GitHub Actions workflow that automatically builds a temporary Snowflake schema, installs dbt, and runs all data quality tests whenever new code is pushed, blocking bad code from production.

## Project Structure

* `ingestion.py`: Python script simulating a daily batch job. Downloads raw data, merges features/labels, and pushes the CSV to a secure Snowflake Internal Stage.
* `orchestration.py`: Dagster definitions linking the Python ingestion script to the dbt transformations.
* `secom_pj/`: The dbt project folder containing the staging and intermediate models, plus `schema.yml` data tests.
* `.github/workflows/`: Contains the CI/CD YAML configuration for automated PR testing.

## Instruction to Run Locally

1. Clone this repository.
2. Create a virtual environment and install dependencies: `pip install dagster dbt-snowflake pandas python-dotenv`
3. Create a `.env` file in the root directory with your Snowflake credentials (`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`).
4. Start the Dagster UI:
   ```bash
   dagster dev -f orchestration.py
5. Open http://127.0.0.1:3000, select all files, and click Materialize to run the pipeline.