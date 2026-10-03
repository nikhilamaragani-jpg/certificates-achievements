# Power BI workshop dashboards: review and redesign plan

## Source and scope

This review is based on the supplied two-page **Power BI Dashboards** PDF: page 1 is labeled *Campfly Sales Analysis* and page 2 *Netflix Analysis Dashboard*. The PDF is a flattened export. It does not include an editable `.pbix` model, Power Query steps, relationships, DAX measures or source files, so calculation correctness cannot be audited or changed from this artifact alone.

The notes below distinguish visible presentation risks from questions that must be checked in the editable report. They are not claims that the source model is wrong.

## Campfly sales analysis

### Visible improvement opportunities

- Replace auto-generated labels such as “Sum of Total Revenue” and “Count of City” with audience-facing measure names, units and a brief definition.
- Establish one top-level question and a restrained hierarchy: a small KPI strip, an order/revenue trend, then product and channel breakdowns.
- Make the date range, currency and reporting grain visible. The PDF includes multiple years and currency-related fields; totals should not be compared until currency treatment is explicit.
- Clarify “Goal” cards and their comparison period. The export shows large goal-variance labels; verify target values, denominators and percentage formatting in the model before publishing them.
- Replace product-description index fields with readable product names; check long category labels, sort order, chart titles and axis units.
- Remove duplicated or low-value visuals when they do not help the stated business question.

### Model checks before changing the report

Confirm that revenue and unit cost use the intended aggregation, orders are counted at the right grain, quantity is not accidentally double-counted after joins, targets use the same period/currency as actuals, and slicers filter each visual consistently.

## Netflix analysis dashboard

### Visible improvement opportunities

- Define each headline KPI and distinguish films, series, seasons and titles; use clear count and rating labels.
- Review score aggregation: the export includes “Sum of imdb_score” labels. For a typical ratings story, validate whether average rating is the intended measure and show its denominator.
- Treat missing values explicitly. The export exposes blank ratings and empty-list (`[]`) genre/country categories; either label missing data or state and apply an exclusion rule.
- Normalize multi-value genres and production countries before using them as categories. Otherwise list-valued strings can behave like opaque categories instead of individual genres/countries.
- Separate release year from catalog-addition year if both concepts exist; label the date definition, add a sensible year range and avoid implying a time trend from incomplete early-year coverage.
- Make filter behavior and sample size visible so selected genres, ratings and release periods can be interpreted.

### Model checks before changing the report

Confirm whether each row represents a title, season or episode; verify treatment of duplicate titles, multi-genre/country values, null ratings and rating scale. Check all chart aggregations and denominators against the data model before drawing comparisons.

## Changes applied in this repository

- The supplied dashboard PDF is preserved as [workshop evidence](../workshop-evidence/Power-BI-Workshop-Dashboards.pdf) and described accurately in the portfolio.
- The new [claims-operations project](../projects/claims-intelligence-foundation/README.md) uses concise metric names, explicit units and denominators, a clear synthetic-data disclosure, and a restrained two-measure comparison chart.
- The [shareable project brief](../projects/claims-intelligence-foundation/reports/project_brief.pdf) applies the same labeling and disclosure standards.

The original Power BI report itself has **not** been edited. The editable `.pbix` file and source dataset/workbook are needed to change visuals, measures, relationships or transformations; the user has indicated they will provide these. Once available, the redesign can be implemented and checked against the actual model rather than inferred from a PDF.
