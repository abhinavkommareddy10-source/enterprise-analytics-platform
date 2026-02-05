import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

import pandas as pd


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: dict


def _now_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def run_quality_checks(customers_path: str, transactions_path: str, reports_dir: str) -> int:
    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)

    customers = pd.read_csv(customers_path)
    tx = pd.read_csv(transactions_path)

    results: list[CheckResult] = []

    # --- schema checks ---
    expected_customers_cols = {
        "customer_id", "first_name", "last_name", "email", "signup_date", "age", "country"
    }
    expected_tx_cols = {
        "transaction_id", "customer_id", "transaction_ts", "amount", "currency",
        "merchant", "category", "payment_method", "status"
    }

    results.append(CheckResult(
        name="customers_schema",
        passed=set(customers.columns) == expected_customers_cols,
        details={"columns": list(customers.columns), "expected": sorted(expected_customers_cols)},
    ))
    results.append(CheckResult(
        name="transactions_schema",
        passed=set(tx.columns) == expected_tx_cols,
        details={"columns": list(tx.columns), "expected": sorted(expected_tx_cols)},
    ))

    # If schema is wrong, stop early (other checks may crash)
    if not all(r.passed for r in results):
        return _write_report_and_exit(results, customers_path, transactions_path, reports_path)

    # --- null / empty checks ---
    results.append(CheckResult(
        name="transactions_customer_id_not_null",
        passed=tx["customer_id"].notna().all() and (tx["customer_id"].astype(str).str.strip() != "").all(),
        details={"null_count": int(tx["customer_id"].isna().sum()),
                 "empty_count": int((tx["customer_id"].astype(str).str.strip() == "").sum())},
    ))

    results.append(CheckResult(
        name="transactions_id_not_null",
        passed=tx["transaction_id"].notna().all() and (tx["transaction_id"].astype(str).str.strip() != "").all(),
        details={"null_count": int(tx["transaction_id"].isna().sum()),
                 "empty_count": int((tx["transaction_id"].astype(str).str.strip() == "").sum())},
    ))

    # --- duplicate transaction_id ---
    dup_count = int(tx["transaction_id"].duplicated().sum())
    results.append(CheckResult(
        name="transactions_id_unique",
        passed=dup_count == 0,
        details={"duplicate_count": dup_count},
    ))

    # --- range checks ---
    # ensure amount numeric
    amount_numeric = pd.to_numeric(tx["amount"], errors="coerce")
    non_numeric = int(amount_numeric.isna().sum())
    neg_count = int((amount_numeric < 0).sum())
    results.append(CheckResult(
        name="transactions_amount_numeric",
        passed=non_numeric == 0,
        details={"non_numeric_count": non_numeric},
    ))
    results.append(CheckResult(
        name="transactions_amount_non_negative",
        passed=neg_count == 0,
        details={"negative_count": neg_count},
    ))

    # --- allowed values ---
    allowed_status = {"APPROVED", "DECLINED", "PENDING"}
    invalid_status = tx.loc[~tx["status"].isin(allowed_status), "status"].value_counts().to_dict()
    results.append(CheckResult(
        name="transactions_status_allowed",
        passed=len(invalid_status) == 0,
        details={"invalid_status_counts": invalid_status, "allowed": sorted(allowed_status)},
    ))

    # --- referential integrity: customer_id exists in customers ---
    customer_set = set(customers["customer_id"].astype(str))
    missing_customers = int((~tx["customer_id"].astype(str).isin(customer_set)).sum())
    results.append(CheckResult(
        name="transactions_customer_id_exists",
        passed=missing_customers == 0,
        details={"missing_customer_id_count": missing_customers},
    ))

    return _write_report_and_exit(results, customers_path, transactions_path, reports_path)


def _write_report_and_exit(results, customers_path, transactions_path, reports_path: Path) -> int:
    passed_all = all(r.passed for r in results)

    report = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "inputs": {
            "customers": customers_path,
            "transactions": transactions_path,
        },
        "summary": {
            "passed_all": bool(passed_all),
            "passed": int(sum(1 for r in results if r.passed)),
            "failed": int(sum(1 for r in results if not r.passed)),
        },
        "checks": [
            {
                "name": r.name,
                "passed": bool(r.passed),
                "details": {
                    k: (bool(v) if isinstance(v, (bool,)) else v)
                    for k, v in r.details.items()
                },
            }
            for r in results
        ],
    }

    tx_name = Path(transactions_path).stem
    out_file = reports_path / f"quality_report_{tx_name}_{_now_stamp()}.json"
    out_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== DATA QUALITY RESULT ===")
    print("Customers:", customers_path)
    print("Transactions:", transactions_path)
    print("Passed all:", passed_all)
    print("Report:", str(out_file))

    # print failed checks
    for r in results:
        if not r.passed:
            print(f"❌ FAIL: {r.name} -> {r.details}")
    if passed_all:
        print("✅ All checks passed.")

    return 0 if passed_all else 1


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python -m src.quality.check_quality <customers_csv> <transactions_csv> <reports_dir>")
        sys.exit(2)

    sys.exit(run_quality_checks(sys.argv[1], sys.argv[2], sys.argv[3]))
