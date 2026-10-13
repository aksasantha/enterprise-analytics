# Forex dashboard pages

This directory contains the three page scripts registered by the [Forex report](../README.md). Home reads a Snowflake aggregate. The two analysis pages use a cached full-table Pandas DataFrame and perform interactive filters and most calculations locally. Service function details are in [services/README.md](../../../services/README.md); session configuration is covered by [database/README.md](../../../database/README.md).

## Home page

home.py is the report landing page. It calls get_forex_summary(), selects the first row of the resulting aggregate DataFrame, and displays four metrics. That service query aggregates the whole source table in Snowflake; Home has no date or category filters and the call is not decorated with a page-level cache.

| Metric | Source and formula | Display |
|---|---|---|
| Total Transactions | Snowflake COUNT(*) across table rows. This is a row count, not a distinct TRANSACTION_ID count. | Integer with thousands separators. |
| Total USD Volume | SUM(VOLUME_USD). | Divided by 1,000,000 and shown with an M suffix and two decimals. |
| Total Local Volume | SUM(VOLUME_LOCAL). | Divided by 1,000,000 and shown with an M suffix and two decimals. |
| Average Exchange Rate | AVG(RATE). | Two decimal places. |

The page also provides links to Forex Performance and Transaction Analysis. The labels describe the volume as monetary amounts; formal currency/business definitions and rate conventions are not supplied by the code.

## Shared preparation and formatting on analysis pages

Both analysis pages call get_forex_transactions() and then prepare a copy of its DataFrame:

1. Parse TRANSACTION_DATE with Pandas datetime conversion; invalid values become missing.
2. Convert VOLUME_USD to numeric; invalid values become missing.
3. Drop rows with missing TRANSACTION_DATE or TRANSACTION_ID.
4. Replace missing VOLUME_USD with zero.
5. Replace missing category values with Unknown and cast categories to strings. Performance prepares BRANCH, CURRENCY, CHANNEL; Transaction Analysis also prepares PRODUCT and TRANSACTION_TYPE.

format_compact() is defined separately in each page. It returns an em dash for a missing number, otherwise formats absolute values in billions, millions, or thousands with two decimals and a supplied prefix; smaller values also receive two decimals and a thousands separator. It does not change the stored value.

If cleaned data is empty, a warning is displayed and the page stops. If data remains but selected filters yield no rows, the page displays an informational message and stops before KPIs and visuals.

## Forex Performance dashboard

### Filters and reset behavior

The page derives minimum and maximum selectable dates from the cleaned transaction dates. The default end is the earlier of the maximum data date and today; if every row is future-dated, it uses the maximum data date instead. The default start is at most 364 days before the end, clipped to the earliest available date, giving up to a 365-day inclusive window.

| Filter | Source | Selection and effect |
|---|---|---|
| Date range | TRANSACTION_DATE | One date or a date pair. Defaults to the range above and is inclusive at both ends. |
| Branch | BRANCH | Multiselect. Empty means all branches. |
| Currency | CURRENCY | Multiselect. Empty means all currencies. |
| Channel | CHANNEL | Multiselect. Empty means all channels. |

The page applies these conditions successively to the prepared Pandas DataFrame. All four filters affect every KPI and chart. They do not add predicates to the Snowflake query. Reset removes the page's four widget keys from session state and reruns the page.

### KPIs

| KPI | Exact calculation on filtered rows | Interpretation |
|---|---|---|
| Total Transactions | Number of distinct TRANSACTION_ID values. | Distinct transaction identifiers remaining after filters. |
| Total USD Volume | Sum of VOLUME_USD, with invalid/missing volumes already converted to zero. | Total USD volume represented by the filtered rows. |
| Average Transaction Value | Sum of VOLUME_USD divided by distinct transaction count; zero if that count is zero. | Total row-level volume divided by unique IDs. If IDs occur on multiple rows, the numerator can include multiple rows while the denominator remains distinct IDs. |
| Active Branches | Number of distinct prepared BRANCH values. | Branch categories represented after filters; a missing branch is represented as Unknown. |

USD metrics use format_compact() with a dollar prefix. This is the page's display convention; the source's formal currency definition is not available here.

### Visualizations

| Visual | Construction and fields | Question and interpretation |
|---|---|---|
| Monthly Business Trend | Native Streamlit line chart. The filtered rows receive a month-start MONTH value from TRANSACTION_DATE; Pandas groups by month, summing VOLUME_USD and counting distinct TRANSACTION_ID. The chart plots MONTH against USD_VOLUME. The computed TRANSACTIONS field is not plotted. | How does filtered USD volume change by month? A first or last month can be partial when the selected date range cuts through that month. |
| Branch Contribution | Native Streamlit horizontal bar chart. Pandas groups by BRANCH, sums VOLUME_USD, counts distinct transaction IDs, and sorts volume descending. It plots branch against USD_VOLUME; the count is not plotted. | Which filtered branches contribute the most USD volume? |
| Currency Analysis | Native Streamlit scatter chart. Currency groups contain distinct transaction count and summed USD volume. AVERAGE_TRANSACTION_VALUE is summed USD volume divided by distinct count. X is TRANSACTIONS, Y is average value, color is CURRENCY, and bubble size is USD_VOLUME. | How do transaction count and average value compare by currency, with total volume shown by bubble size? |
| Transaction Channel Distribution | Plotly pie chart with a 0.55 hole (donut). Grouping by CHANNEL produces distinct transaction count and summed USD volume. Wedge size is TRANSACTIONS; labels show percent and channel; USD volume is available on hover. | What share of the filtered distinct transaction count belongs to each channel? Hover also exposes the grouped USD volume. |

The data are already restricted by the selected dates and categories before these groupings are created. Monthly totals are selected-period totals, not necessarily complete calendar months.

## Transaction Analysis dashboard

### Filters and reset behavior

Date bounds and defaults follow the same approach described for Forex Performance. The page provides:

| Filter | Source | Selection and effect |
|---|---|---|
| Date range | TRANSACTION_DATE | Inclusive single date or date pair; defaults to up to the most recent 365 available days, with the future-only fallback. |
| Branch | BRANCH | Multiselect; empty includes all. |
| Currency | CURRENCY | Multiselect; empty includes all. |
| Product | PRODUCT | Multiselect; empty includes all. |
| Transaction Type | TRANSACTION_TYPE | Multiselect; empty includes all. |
| Channel | CHANNEL | Multiselect; empty includes all. |

All filters are applied in Pandas before metrics, matrix, heatmap, or sunburst construction. They do not filter the Snowflake query. Reset clears all six associated session-state keys and reruns.

### KPIs

| KPI | Exact calculation on filtered rows | Interpretation |
|---|---|---|
| Total Transactions | Distinct count of TRANSACTION_ID. | Unique IDs in the filtered rows. |
| Average Transaction Value | Pandas mean of row-level VOLUME_USD. | Average row value; unlike Forex Performance, this is not total volume divided by distinct IDs. |
| Largest Transaction | Maximum row-level VOLUME_USD. | Largest single row's USD volume, not a sum grouped by transaction ID. |
| Active Days | Distinct values of TRANSACTION_DATE converted to calendar dates. | Number of calendar dates represented, regardless of intraday timestamps. |

The three USD values use format_compact() with a dollar prefix. Active Days and Total Transactions use integer formatting.

### Transaction matrix and CSV

The matrix groups the already-filtered rows by BRANCH, CURRENCY, PRODUCT, TRANSACTION_TYPE, and CHANNEL. It calculates:

- TRANSACTIONS: distinct TRANSACTION_ID count per five-field group.
- USD_VOLUME: sum of VOLUME_USD per group.
- AVG_TRANSACTION_VALUE: arithmetic mean of row-level VOLUME_USD per group.

Rows are sorted by USD_VOLUME descending. A Pandas Styler applies a blue background gradient to USD_VOLUME and formats the three measures for display. Streamlit renders the styled dataframe with hidden index and a fixed height of 400 pixels; users can sort by column headings.

The CSV button exports the underlying unstyled matrix DataFrame as UTF-8 CSV, without the Pandas display formatting or row index. It includes only the currently filtered matrix groups and measures, with filename transaction_analysis.csv.

This matrix helps compare the combination of five categories by count, total volume, and average row value. It is not a raw transaction-level export.

### Daily Transaction Activity heatmap

The page uses Plotly Graph Objects to draw a Heatmap. Starting with filtered rows, it normalizes transaction timestamps to calendar days and calculates distinct TRANSACTION_ID counts per day. It then reindexes that series to every calendar day from selected start through selected end, filling dates with no matching rows as zero.

Each date is assigned the Monday of its week as WEEK_START and a weekday name. The data are pivoted to weekday rows (Monday through Sunday) and week columns. The z-values controlling color intensity are daily transaction counts; the blue color scale and colorbar are labeled Transactions. Week labels use the Monday date, with approximately every fourth week shown as an axis tick.

Darker cells mean more distinct transactions on that weekday in that week; zero-count dates inside the selected range are included. The date calendar spans the whole selected range, but category filters still determine which transactions contribute to counts. Days before/after the selected range in its first/last week have no generated daily row and therefore appear blank.

### Product Composition sunburst

Plotly Express builds a sunburst from filtered rows grouped by PRODUCT, TRANSACTION_TYPE, and CHANNEL. Its hierarchy follows that order from inner level to outer breakdown. USD_VOLUME is the sum of VOLUME_USD for each grouped path and controls both segment size and continuous blue color. Larger segments therefore represent more summed USD volume, not more transaction IDs.

The chart answers how filtered USD volume decomposes across product, transaction type, and channel. All six filters have already been applied to the source rows. Missing categories use the Unknown label from page preparation.

## Page-to-service mapping and calculation location

| Feature | Page | Service function | Fields and calculation location |
|---|---|---|---|
| Home summary | home.py | get_forex_summary() | Snowpark in Snowflake: row count, local/USD volume sums, average rate; returned as Pandas for display. |
| Performance KPIs and visuals | performance.py | get_forex_transactions() | Full table returned to Pandas; local date/category filters, distinct-ID and volume calculations, then Pandas chart grouping. |
| Transaction KPIs, matrix, heatmap, sunburst, CSV | transaction_analysis.py | get_forex_transactions() | Full table returned to Pandas; local filters and all listed calculations/groupings occur in Python/Pandas. Plotly renders three visuals; Streamlit renders the dataframe and download. |

The analysis page service call itself is cached for up to five minutes. The Home summary function has no explicit application cache. The analysis pages retrieve every source-table column and row before applying filters, so network transfer and memory use scale with the complete table rather than the selected view.

## Validation status

This guide documents formulas and transformations by inspection of the current page and service source. The repository includes manual scripts that print service results and an interactive Snowflake explorer; it does not include automated assertions for the dashboard calculations or visualizations. No live Snowflake query or data-backed validation was performed while preparing this README, so historical KPI values are not repeated here. Data-dependent results will vary with the selected filters and source-table contents.
