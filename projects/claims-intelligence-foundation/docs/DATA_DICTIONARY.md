# Data dictionary

`data/claims.csv` contains 240 deterministic, synthetic scenario records. The scenario snapshot date is **April 30, 2025**. No external or customer data is included.

| Field | Type | Definition | Nullability / checks |
|---|---|---|---|
| `claim_id` | Text | Synthetic unique claim key, formatted `CLM-####`. | Required; unique. |
| `market` | Text | Illustrative scenario market: France, Germany, Netherlands or Switzerland. | Required; category labels are not real market samples. |
| `product_line` | Text | Illustrative product line: Auto, Home or Travel. | Required; category labels are scenario values. |
| `reported_date` | ISO date | Date the synthetic claim is reported. | Required; on or before the scenario snapshot. |
| `closed_date` | ISO date | Date the synthetic claim is closed. | Blank for open claims; required for closed claims; cannot precede `reported_date` or exceed the snapshot date. |
| `status` | Text | `Open` or `Closed` scenario state at the snapshot. | Required; must agree with whether `closed_date` is blank. |
| `incurred_amount_eur` | Integer | Invented scenario amount in euros for illustrative grouping. | Required; non-negative; not a paid amount or verified financial measure. |

## Grain and interpretation

One CSV row represents one scenario claim. `status` is current only within this fixed synthetic snapshot. Open claims do not have a resolution duration; resolution-time analysis includes closed claims only. The amount values have no empirical meaning.
