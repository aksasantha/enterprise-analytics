# Services

The services package separates data retrieval and reusable analytics queries from Streamlit page layout. The implemented Forex functions query UNIMONI_PRACTICE.FOREX.FOREX_TRANSACTIONS through the shared helper in [database/](../database/README.md). Snowpark performs the simpler aggregations in Snowflake; Python receives Pandas DataFrames for rendering or further work.

## Files

| File | Current state |
|---|---|
| forex_analytics.py | Implemented Forex table queries and cached transaction retrieval. |
| analytics.py | Empty; it currently provides no general analytics functions. |
| __init__.py | Empty package marker. |

The query convention is to keep aggregations in Snowflake when implemented naturally with Snowpark or SQL. The two detailed dashboard pages are an exception for interactive analysis: they retrieve all rows into Pandas and do their filtering and chart preparation in the application. See [the page guide](../reports/forex_performance/pages/README.md) for those calculations.

## Shared source and connection

forex_analytics.py defines TABLE as the fully qualified identifier UNIMONI_PRACTICE.FOREX.FOREX_TRANSACTIONS. Each non-cached query function calls get_snowflake_session() from database/snowflake.py, accesses that table or executes SQL, and converts the result to Pandas with to_pandas(). The transaction loader also uses the same session helper.

The source fields used by these functions are TRANSACTION_ID (row count), TRANSACTION_DATE (monthly grouping), BRANCH (branch grouping), VOLUME_LOCAL, VOLUME_USD, and RATE. Dashboard pages additionally use currency/product/type/channel fields. The complete schema and formal business definitions are not included in the repository.

## Implemented functions

All five functions take no explicit arguments. They return Pandas DataFrames, not Snowpark DataFrames. Filters are not passed in: the summary query functions aggregate the whole table, while page-specific filters are applied later to the full-table result in Pandas.

| Function | Query and returned columns | Use in application |
|---|---|---|
| get_forex_summary() | Snowpark aggregation across the table: count(*) as TOTAL_TRANSACTIONS; sum VOLUME_LOCAL as TOTAL_LOCAL_VOLUME; sum VOLUME_USD as TOTAL_USD_VOLUME; avg RATE as AVERAGE_RATE. Returns the aggregate as a Pandas DataFrame, normally one row. | Called by the Home page. |
| get_monthly_performance() | Adds MONTH as DATE_TRUNC('MONTH', TRANSACTION_DATE), groups by MONTH, calculates row count and sum of VOLUME_USD, sorts ascending by MONTH, and returns Pandas columns MONTH, TOTAL_TRANSACTIONS, TOTAL_USD_VOLUME. | Available to scripts/developers; not called by the current dashboard pages. |
| get_branch_performance() | Groups by BRANCH, calculates row count, sum of VOLUME_USD, and average RATE; sorts TOTAL_USD_VOLUME descending; returns Pandas columns BRANCH, TOTAL_TRANSACTIONS, TOTAL_USD_VOLUME, AVERAGE_RATE. | Available to scripts/developers; not called by the current dashboard pages. |
| get_monthly_running_volume() | Executes SQL with a monthly-volume CTE. The outer query calculates a cumulative SUM of monthly USD volume ordered by month, using an unbounded-preceding through current-row window. Returns MONTH, MONTHLY_USD_VOLUME, RUNNING_USD_VOLUME as Pandas data. | Called by the analytics validation script; not by the dashboard pages. |
| get_forex_transactions() | Reads the table and calls to_pandas() without projection, filtering, or aggregation; returns the full table as a Pandas DataFrame. Decorated with st.cache_data(ttl=300), so the cached result can be reused for five minutes. | Called by Forex Performance and Transaction Analysis. |

### Query details and limits

- get_forex_summary() counts rows with COUNT(*) rather than distinct transaction IDs. Home displays that value as total transactions.
- get_monthly_performance() also counts rows; it does not count distinct IDs.
- get_branch_performance() groups NULL branch values according to Snowflake behavior; the service does not fill missing categories.
- get_monthly_running_volume() interpolates the module-level TABLE constant into SQL. No user-provided SQL parameters are accepted by this function.
- These aggregate functions do not specify a date range or other filters. The pages' filters do not change their results; only the transaction DataFrame loader is used for page filtering.
- The cache TTL is five minutes. Newly inserted/updated data may not appear in cached transaction data until expiry. The functions do not expose a manual cache invalidation control.
- Downloading the complete table makes data transfer and app memory use grow with source-table size. Results are converted to Pandas rather than streamed or paged.
- Database/network errors are not caught in this module; they propagate to Streamlit or the calling script.

## Function behavior in steps

### get_forex_summary()

1. Obtain the configured Snowpark session through get_snowflake_session().
2. Create a Snowpark DataFrame for TABLE.
3. Aggregate row count, local-volume sum, USD-volume sum, and average rate in Snowflake.
4. Convert that aggregate result to Pandas and return it.

### get_monthly_performance()

1. Read TABLE through the Snowpark session.
2. Add a month-truncated transaction-date column.
3. Group rows by month and calculate row count and USD-volume sum.
4. Sort months chronologically, convert to Pandas, and return.

### get_branch_performance()

1. Read TABLE and group rows by BRANCH.
2. Calculate row count, USD-volume sum, and mean RATE per branch.
3. Sort by total USD volume descending.
4. Convert the result to Pandas and return it.

### get_monthly_running_volume()

1. Obtain the shared Snowpark session.
2. In SQL, group the table into one USD-volume total per truncated month.
3. In the outer query, compute the running sum over months in chronological order.
4. Return the ordered SQL result as a Pandas DataFrame.

### get_forex_transactions()

1. Streamlit checks its data cache for this zero-argument call.
2. On a cache miss/expiry, obtain the shared session and select TABLE.
3. Download all table columns and rows into Pandas.
4. Cache and return the DataFrame for the configured 300-second TTL.

The service deliberately does not apply dashboard-specific filters in Snowflake. See [the report page documentation](../reports/forex_performance/pages/README.md) for client-side transformations, formulas, and visual data preparation.

## Page and script mapping

| Caller | Service function(s) | Purpose |
|---|---|---|
| reports/forex_performance/pages/home.py | get_forex_summary() | Overall Snowflake aggregate used for four Home metrics. |
| reports/forex_performance/pages/performance.py | get_forex_transactions() | Cached transaction rows for local filters, KPIs, and charts. |
| reports/forex_performance/pages/transaction_analysis.py | get_forex_transactions() | Cached transaction rows for local filters, KPIs, matrix, charts, and export. |
| tests/test_forex_analytics.py | All four aggregate query functions except the cached full-table loader | Prints aggregate query results for manual inspection. |
| Other current callers | get_monthly_performance(), get_branch_performance(), get_monthly_running_volume() | No dashboard page currently calls these functions. |

To extend the service layer, first verify the source columns and desired grain of the metric. Put reusable Snowflake retrieval/aggregation here, use the shared database helper, and return a documented structure. Keep page widgets and rendering in the report page modules. If interactive filters are moved into a service/query, document that change because the current analysis pages filter locally.
