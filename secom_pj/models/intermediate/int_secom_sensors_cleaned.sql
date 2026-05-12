{{ config(materialized='table') }}

WITH staged_data AS (
    SELECT * FROM {{ ref('stg_secom_sensors') }}
),

imputed_data AS (
    SELECT 
        classification,
        record_timestamp,
        {% for i in range(1, 591) %}
        COALESCE(sensor_{{ "%03d" | format(i) }}, 0) AS sensor_{{ "%03d" | format(i) }},
        {% endfor %}
        
        ingestion_batch_at
        
    FROM staged_data
)

SELECT * FROM imputed_data