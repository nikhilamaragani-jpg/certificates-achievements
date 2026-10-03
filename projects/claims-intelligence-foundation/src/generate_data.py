from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "data" / "claims.csv"

MARKETS = (
    ("Germany", 18, 3),
    ("Switzerland", 14, 2),
    ("France", 24, 5),
    ("Netherlands", 12, 1),
)
PRODUCT_LINES = (
    ("Auto", 6, 700, 4500),
    ("Home", 4, 400, 3000),
    ("Travel", -2, 100, 1800),
)
FIELDNAMES = (
    "claim_id",
    "market",
    "product_line",
    "reported_date",
    "closed_date",
    "status",
    "incurred_amount_eur",
)
AS_OF_DATE = date(2025, 4, 30)


def build_rows() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    claim_number = 1

    for market_index, (market, base_resolution_days, open_per_group) in enumerate(MARKETS):
        for product_index, (product, product_adjustment, amount_base, amount_range) in enumerate(PRODUCT_LINES):
            for sequence in range(20):
                reported = date(2025, 1, 1) + timedelta(
                    days=sequence * 3 + market_index * 7 + product_index * 2
                )
                is_open = sequence < open_per_group
                resolution_days = (
                    base_resolution_days
                    + product_adjustment
                    + (sequence * 7 + product_index * 3 + market_index) % 15
                )
                amount = amount_base + (
                    sequence * 137 + market_index * 211 + product_index * 97
                ) % amount_range
                closed = "" if is_open else (reported + timedelta(days=resolution_days)).isoformat()

                if is_open and reported > AS_OF_DATE:
                    raise ValueError("Generated open claim falls after the scenario as-of date.")

                rows.append(
                    {
                        "claim_id": f"CLM-{claim_number:04d}",
                        "market": market,
                        "product_line": product,
                        "reported_date": reported.isoformat(),
                        "closed_date": closed,
                        "status": "Open" if is_open else "Closed",
                        "incurred_amount_eur": amount,
                    }
                )
                claim_number += 1

    return rows


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic claims to {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
