from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "claims.csv"
REPORT_DIR = PROJECT_ROOT / "reports"
SCENARIO_AS_OF = pd.Timestamp("2025-04-30")
REQUIRED_COLUMNS = {
    "claim_id",
    "market",
    "product_line",
    "reported_date",
    "closed_date",
    "status",
    "incurred_amount_eur",
}


def load_and_validate() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Input data not found at {DATA_FILE}. Run `python src/generate_data.py` first."
        )

    claims = pd.read_csv(DATA_FILE, dtype={"claim_id": "string"})
    missing_columns = REQUIRED_COLUMNS.difference(claims.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
    if claims.empty:
        raise ValueError("Input data has no rows.")
    if claims["claim_id"].isna().any() or claims["claim_id"].duplicated().any():
        raise ValueError("Claim IDs must be present and unique.")
    non_nullable_columns = REQUIRED_COLUMNS.difference({"closed_date"})
    if claims[list(non_nullable_columns)].isna().any().any():
        raise ValueError("Required fields contain missing values.")
    if not claims["status"].isin({"Open", "Closed"}).all():
        raise ValueError("Status must be either 'Open' or 'Closed'.")

    claims["reported_date"] = pd.to_datetime(claims["reported_date"], errors="raise")
    claims["closed_date"] = pd.to_datetime(claims["closed_date"], errors="coerce")
    if claims["reported_date"].gt(SCENARIO_AS_OF).any():
        raise ValueError("Reported dates cannot be after the scenario as-of date.")
    claims["incurred_amount_eur"] = pd.to_numeric(
        claims["incurred_amount_eur"], errors="raise"
    )
    if (claims["incurred_amount_eur"] < 0).any():
        raise ValueError("Incurred amounts cannot be negative.")
    if claims.loc[claims["status"] == "Open", "closed_date"].notna().any():
        raise ValueError("Open claims must not have a close date.")
    if claims.loc[claims["status"] == "Closed", "closed_date"].isna().any():
        raise ValueError("Closed claims must have a close date.")
    if claims["closed_date"].dropna().gt(SCENARIO_AS_OF).any():
        raise ValueError("Closed dates cannot be after the scenario as-of date.")
    if (claims["closed_date"].dropna() < claims.loc[claims["status"] == "Closed", "reported_date"]).any():
        raise ValueError("A closed claim cannot close before it was reported.")

    claims["resolution_days"] = (
        claims["closed_date"] - claims["reported_date"]
    ).dt.days
    return claims


def calculate_market_kpis(claims: pd.DataFrame) -> pd.DataFrame:
    grouped = claims.groupby("market", sort=True)
    totals = grouped.size().rename("total_claims")
    open_counts = (
        claims.loc[claims["status"] == "Open"]
        .groupby("market")
        .size()
        .rename("open_claims")
    )
    median_resolution = (
        claims.loc[claims["status"] == "Closed"]
        .groupby("market")["resolution_days"]
        .median()
        .rename("median_closed_resolution_days")
    )
    incurred = grouped["incurred_amount_eur"].sum().rename("incurred_amount_eur")

    kpis = pd.concat([totals, open_counts, median_resolution, incurred], axis=1)
    kpis["open_claims"] = kpis["open_claims"].fillna(0).astype(int)
    kpis["open_claim_rate_pct"] = (
        kpis["open_claims"] / kpis["total_claims"] * 100
    ).round(1)
    kpis["median_closed_resolution_days"] = kpis[
        "median_closed_resolution_days"
    ].round(1)
    kpis["incurred_amount_eur"] = kpis["incurred_amount_eur"].astype(int)
    return kpis.reset_index()


def save_chart(kpis: pd.DataFrame) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    color = "#197c78"

    axes[0].bar(kpis["market"], kpis["open_claim_rate_pct"], color=color)
    axes[0].set_title("Open-claim rate")
    axes[0].set_ylabel("Open claims / all claims (%)")
    axes[0].set_ylim(0, max(10, float(kpis["open_claim_rate_pct"].max()) * 1.25))
    axes[1].bar(kpis["market"], kpis["median_closed_resolution_days"], color="#d18b47")
    axes[1].set_title("Median resolution time")
    axes[1].set_ylabel("Days (closed claims only)")

    for axis, values in (
        (axes[0], kpis["open_claim_rate_pct"]),
        (axes[1], kpis["median_closed_resolution_days"]),
    ):
        axis.tick_params(axis="x", rotation=20)
        axis.spines[["top", "right"]].set_visible(False)
        for index, value in enumerate(values):
            axis.text(index, value, f" {value:g}", ha="center", va="bottom", fontsize=9)

    fig.suptitle("Claims operations | illustrative synthetic scenario", fontsize=15, weight="bold")
    fig.text(
        0.5,
        -0.02,
        "Synthetic data only. Not actual insurer or market performance.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.savefig(REPORT_DIR / "market_kpis.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_project_brief(kpis: pd.DataFrame, claims: pd.DataFrame) -> None:
    figure = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    figure.text(
        0.08,
        0.96,
        "DATA ANALYSIS | INTRODUCTORY CASE STUDY",
        fontsize=9,
        color="#197c78",
        weight="bold",
    )
    figure.text(
        0.08,
        0.92,
        "Claims Operations: Analyst Foundations",
        fontsize=21,
        color="#17332f",
        weight="bold",
    )
    figure.text(
        0.08,
        0.885,
        "Business question, KPI definitions, quality checks and descriptive analysis",
        fontsize=10,
        color="#475753",
    )
    figure.text(
        0.08,
        0.835,
        "SYNTHETIC DATA ONLY  |  This scenario is not real insurer or market performance.",
        fontsize=9,
        color="#8a4c21",
        weight="bold",
        bbox={"boxstyle": "round,pad=0.6", "facecolor": "#fff2df", "edgecolor": "#ead2b0"},
    )
    figure.text(0.08, 0.78, "Business question", fontsize=11, weight="bold", color="#17332f")
    figure.text(
        0.08,
        0.75,
        "Which scenario markets have the largest open-claim backlog, and how does the",
        fontsize=10,
        color="#34423e",
    )
    figure.text(
        0.08,
        0.725,
        "resolution time of closed claims vary?",
        fontsize=10,
        color="#34423e",
    )

    figure.text(0.08, 0.675, "Market KPIs (illustrative sample)", fontsize=11, weight="bold", color="#17332f")
    figure.text(
        0.08,
        0.645,
        "Market-level KPIs",
        fontsize=9,
        color="#53635e",
        weight="bold",
    )
    for row_index, row in enumerate(kpis.itertuples(index=False)):
        figure.text(
            0.08,
            0.615 - row_index * 0.026,
            f"{row.market}: {int(row.total_claims)} claims, {int(row.open_claims)} open "
            f"({row.open_claim_rate_pct:.1f}%); median close time "
            f"{row.median_closed_resolution_days:.1f} days",
            fontsize=9,
            color="#34423e",
        )

    chart_axis = figure.add_axes([0.09, 0.255, 0.82, 0.23])
    chart_axis.imshow(plt.imread(REPORT_DIR / "market_kpis.png"))
    chart_axis.axis("off")
    figure.text(0.08, 0.215, "Method and interpretation", fontsize=11, weight="bold", color="#17332f")
    figure.text(
        0.08,
        0.187,
        f"{len(claims)} generated rows; April 30, 2025 snapshot; required-field, status/date and amount checks.",
        fontsize=9,
        color="#34423e",
    )
    figure.text(
        0.08,
        0.16,
        "Open-claim rate = open claims / all claims. Median resolution uses closed claims only.",
        fontsize=9,
        color="#34423e",
    )
    figure.text(
        0.08,
        0.112,
        "All observed differences come from the transparent sample-generation rules. They are",
        fontsize=9,
        color="#8a4c21",
    )
    figure.text(
        0.08,
        0.088,
        "not evidence for operational decisions, causal effects or real-world market comparisons.",
        fontsize=9,
        color="#8a4c21",
    )
    figure.text(0.08, 0.04, "Python | pandas | Matplotlib", fontsize=8, color="#61706b")

    with PdfPages(REPORT_DIR / "project_brief.pdf") as pdf:
        pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    claims = load_and_validate()
    kpis = calculate_market_kpis(claims)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    kpis.to_csv(REPORT_DIR / "market_kpis.csv", index=False)
    save_chart(kpis)
    save_project_brief(kpis, claims)

    print(f"Validated {len(claims)} synthetic claims across {claims['market'].nunique()} markets.")
    print(kpis.to_string(index=False))
    print(f"CSV, chart and PDF brief written to {REPORT_DIR.relative_to(PROJECT_ROOT)}.")


if __name__ == "__main__":
    main()
