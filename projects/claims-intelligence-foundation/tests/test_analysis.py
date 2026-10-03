from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src import analyze
from src.generate_data import build_rows


class ClaimsAnalysisTests(unittest.TestCase):
    def test_generator_is_deterministic_and_has_unique_ids(self) -> None:
        first = build_rows()
        second = build_rows()

        self.assertEqual(first, second)
        self.assertEqual(len(first), 240)
        self.assertEqual(len({row["claim_id"] for row in first}), 240)

    def test_kpis_match_documented_synthetic_scenario(self) -> None:
        claims = pd.DataFrame(build_rows())
        claims["reported_date"] = pd.to_datetime(claims["reported_date"])
        claims["closed_date"] = pd.to_datetime(claims["closed_date"], errors="coerce")
        claims["resolution_days"] = (claims["closed_date"] - claims["reported_date"]).dt.days

        kpis = analyze.calculate_market_kpis(claims).set_index("market")

        self.assertEqual(kpis.loc["France", "open_claim_rate_pct"], 25.0)
        self.assertEqual(kpis.loc["France", "median_closed_resolution_days"], 34.0)
        self.assertEqual(kpis.loc["Netherlands", "open_claim_rate_pct"], 5.0)
        self.assertEqual(kpis.loc["Netherlands", "median_closed_resolution_days"], 21.0)

    def test_validator_accepts_blank_close_date_for_open_claims(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "claims.csv"
            pd.DataFrame(build_rows()).to_csv(data_file, index=False)
            with patch.object(analyze, "DATA_FILE", data_file):
                claims = analyze.load_and_validate()

        self.assertEqual(len(claims), 240)
        self.assertTrue(claims.loc[claims["status"] == "Open", "closed_date"].isna().all())

    def test_validator_rejects_closed_claim_without_close_date(self) -> None:
        rows = build_rows()
        closed_row = next(row for row in rows if row["status"] == "Closed")
        closed_row["closed_date"] = ""

        with tempfile.TemporaryDirectory() as directory:
            data_file = Path(directory) / "claims.csv"
            pd.DataFrame(rows).to_csv(data_file, index=False)
            with patch.object(analyze, "DATA_FILE", data_file):
                with self.assertRaisesRegex(ValueError, "Closed claims must have a close date"):
                    analyze.load_and_validate()


if __name__ == "__main__":
    unittest.main()
