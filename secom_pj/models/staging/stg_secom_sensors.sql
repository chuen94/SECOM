{{ config(
    materialized='table',
    pre_hook="CREATE FILE FORMAT IF NOT EXISTS {{ target.schema }}.secom_csv_format TYPE = 'CSV' FIELD_DELIMITER = ',' SKIP_HEADER = 0;"
) }}

WITH staged_data AS (
    SELECT 
        $1::NUMBER AS classification,
        $2::TIMESTAMP AS record_timestamp,
        
        {% for i in range(3, 593) %}
        ${{ i }}::FLOAT AS sensor_{{ "%03d" | format(i - 2) }},
        {% endfor %}
        
        $593::TIMESTAMP AS ingestion_batch_at
        
    FROM @SECOM_MFG.RAW.SECOM_INTERNAL_STAGE
    (FILE_FORMAT => '{{ target.schema }}.secom_csv_format')
)

SELECT * FROM staged_data