# Enterprise Analytics Platform

End-to-end enterprise-style analytics platform built with Python, SQL, PostgreSQL, and Docker.

---

## Tech Stack

- Python (pandas)
- PostgreSQL
- SQL (dimensional modeling)
- Docker & Docker Compose

---

## Project Flow

Raw CSVs  
→ Python ingestion (staging tables)  
→ Data quality validation  
→ SQL transformations  
→ Analytics-ready tables  

---

## How to Run (From Scratch)

```bash
# 1. Start Postgres using Docker
docker compose up -d

# 2. Load raw CSVs into staging tables
python3 -m src.ingest.load_to_postgres data/raw/customers.csv data/raw/transactions.csv

# 3. Run data quality checks
python3 -m src.quality.check_quality \
  data/raw/customers.csv \
  data/raw/transactions.csv \
  data/reports

# 4. Build analytics tables
docker exec -i enterprise-analytics-platform-db-1 psql -U app -d analytics < sql/models/001_dim_customer.sql
docker exec -i enterprise-analytics-platform-db-1 psql -U app -d analytics < sql/models/002_dim_time.sql
docker exec -i enterprise-analytics-platform-db-1 psql -U app -d analytics < sql/models/003_fact_transactions.sql

# 5. Verify tables
docker exec -i enterprise-analytics-platform-db-1 psql -U app -d analytics -c "\dt"
