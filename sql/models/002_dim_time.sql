DROP TABLE IF EXISTS dim_time;

CREATE TABLE dim_time AS
SELECT DISTINCT
  transaction_ts::date AS date,
  EXTRACT(YEAR FROM transaction_ts::date)::int  AS year,
  EXTRACT(MONTH FROM transaction_ts::date)::int AS month,
  EXTRACT(DAY FROM transaction_ts::date)::int   AS day
FROM stg_transactions;
