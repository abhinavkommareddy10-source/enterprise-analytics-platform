DROP TABLE IF EXISTS dim_customer;

CREATE TABLE dim_customer AS
SELECT
  customer_id,
  first_name,
  last_name,
  email,
  signup_date::date AS signup_date,
  age::int AS age,
  country
FROM stg_customers;
