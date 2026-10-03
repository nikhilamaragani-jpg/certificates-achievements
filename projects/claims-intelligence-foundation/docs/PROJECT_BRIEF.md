# Claims Operations: Analyst Foundations

**An introductory, reproducible data-analysis case study**

## Project summary

This case study applies the first stages of the analytics lifecycle to an illustrative claims-operations question: **Which market segments have the largest open-claim backlog, and how does resolution time vary across markets?**

The data is generated locally from documented rules for a scenario snapshot dated **April 30, 2025**. It is wholly synthetic; no real customers, insurer, policy, market performance or financial outcomes are represented.

## Analytical approach

1. Define the operational question and the reporting grain: one row per claim.
2. Document the measures before analysis: claim volume, open-claim rate, median close time for closed claims, and illustrative incurred amount.
3. Validate the data structure, unique identifiers, required values, status/date consistency and non-negative amounts.
4. Summarize the measures by scenario market and visualize the backlog rate beside closed-claim resolution time.
5. Communicate the results with limits and avoid converting descriptive patterns into causal claims.

## Illustrative findings

In this generated sample, France has the highest open-claim rate (25%) and median closed-claim resolution time (34 days), while the Netherlands has the lowest rates (5% and 21 days). These results are deliberately determined by the transparent data-generation rules. They are not evidence about real insurance operations.

The reproducible KPI output is [`market_kpis.csv`](../reports/market_kpis.csv); the chart is [`market_kpis.png`](../reports/market_kpis.png), and a one-page export is [`project_brief.pdf`](../reports/project_brief.pdf).

## Tools and scope

Python, pandas and Matplotlib. This introductory project does not claim SQL, a Power BI report, statistical inference, predictive modeling, production deployment or professional insurance experience.

## Reproducibility

From this project directory, install `requirements.txt`, run `python src/generate_data.py`, then `python src/analyze.py`. The same seed-free deterministic rules regenerate the same 240 rows and report outputs.

## Shareable description

> Built an introductory data-analysis case study using a reproducible synthetic claims dataset. Defined operational KPIs, implemented data-quality checks, summarized backlog and resolution-time measures by scenario market, and communicated the results with explicit assumptions and limitations. Python, pandas and Matplotlib.

This description intentionally says **synthetic** and **introductory** so the project is not mistaken for client work or real-market evidence.
