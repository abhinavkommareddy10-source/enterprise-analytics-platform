import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


def db_url() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "analytics")
    user = os.getenv("DB_USER", "app")
    password = os.getenv("DB_PASSWORD", "app")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


def load_csv(table_name: str, csv_path: str, engine) -> None:
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"Loaded {table_name}: rows={len(df)} from {csv_path}")


def main(customers_csv: str, transactions_csv: str) -> int:
    if not Path(customers_csv).exists():
        print(f"Missing file: {customers_csv}")
        return 2
    if not Path(transactions_csv).exists():
        print(f"Missing file: {transactions_csv}")
        return 2

    engine = create_engine(db_url())

    # quick connection check
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        conn.commit()

    load_csv("stg_customers", customers_csv, engine)
    load_csv("stg_transactions", transactions_csv, engine)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m src.ingest.load_to_postgres <customers_csv> <transactions_csv>")
        sys.exit(2)

    raise SystemExit(main(sys.argv[1], sys.argv[2]))
