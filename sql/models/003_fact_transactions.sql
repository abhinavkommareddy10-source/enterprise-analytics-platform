DROP TABLE IF EXISTS fact_transactions;

CREATE TABLE fact_transactions AS
SELECT
  transaction_id,
  customer_id,
  transaction_ts::timestamp AS transaction_ts,
  transaction_ts::date AS transaction_date,
  amount::numeric(12,2) AS amount,
  currency,
  merchant,
  category,
  payment_method,
  status
FROM stg_transactions;
