# Run SQL Models (Build Analytics Tables)

This document explains how to build analytics tables from staging data in Postgres.

---

## Prerequisites

- Docker Desktop is running
- Postgres container is running

```bash
docker compose up -d
```

- Staging tables are loaded from CSVs

```bash
python3 -m src.ingest.load_to_postgres data/raw/customers.csv data/raw/transactions.csv
```

---

## Build Analytics Tables

Run the following commands in order:

```bash
docker exec -i enterprise-analytics-platform-db-1 psql -U app -d analytics < sql/models/001_dim_customer.sql
docker exec -i enterprise-analytics-platform-db-1 psql -U app -d analytics < sql/models/002_dim_time.sql
docker exec -i enterprise-analytics-platform-db-1 psql -U app -d analytics < sql/models/003_fact_transactions.sql
```

---

## Verify Tables

```bash
docker exec -i enterprise-analytics-platform-db-1 psql -U app -d analytics -c "\dt"
```

Expected tables:
- stg_customers
- stg_transactions
- dim_customer
- dim_time
- fact_transactions

