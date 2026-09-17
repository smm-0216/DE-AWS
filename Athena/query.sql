CREATE DATABASE IF NOT EXISTS db;

CREATE EXTERNAL TABLE IF NOT EXISTS db.customers (
    name STRING,
    city STRING,
    age INT,
    status STRING,
    amount DOUBLE
)
STORED AS PARQUET
LOCATION 's3://smm-0216-de/data/customers/';

SELECT
    status,
    COUNT(*) AS total_registros,
    AVG(amount) AS promedio_amount,
    SUM(amount) AS total_amount
FROM db.customers
GROUP BY status
ORDER BY total_registros DESC;