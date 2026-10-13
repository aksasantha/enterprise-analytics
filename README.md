# Enterprise Analytics

Enterprise Analytics is a Streamlit application for exploring business data in Snowflake. Its current implementation focuses on Forex transactions: it summarizes overall activity and provides interactive pages for performance trends and transaction composition.

Streamlit provides page layout, navigation, filters, metrics, tables, and native charts. Snowflake is the analytical source. Snowpark and SQL perform summary queries; the detailed dashboards retrieve transaction rows into Pandas and perform their filtering and chart preparation in the application process.

This repository is an implemented report application, not a complete enterprise BI platform. The code runs as a Streamlit application and connects to Snowflake; the actual hosting location is Unable to verify from this repository. It has no deployment configuration, application sign-in, authorization layer, automated unit-test suite, or transformation/semantic modeling project. See [Current scope and limitations](#current-scope-and-limitations) before treating it as production-ready.

## Project goals

- Build business reports that are easy to use and extend.
- Separate Snowflake session access, analytics/data retrieval, and page presentation.
- Give users interactive views of Forex volumes and transaction patterns.
- Keep setup and validation understandable to developers.

The first three goals have a working Forex implementation. Reusable components, automated testing, deployment controls, and broader enterprise analytics remain future work; their presence should not be inferred from folder names.

## Current features

- app.py starts a wide-layout Streamlit application and invokes the Forex report.
- The report registers Home, Forex Performance, and Transaction Analysis pages and creates a custom sidebar.
- Home displays overall transaction count, local and USD volume, and average rate.
- Forex Performance provides date, branch, currency, and channel filters; KPI cards; monthly and branch volume charts; a currency scatter chart; and channel distribution.
- Transaction Analysis provides date, branch, currency, product, transaction-type, and channel filters; KPI cards; a grouped transaction matrix with conditional formatting; a CSV download; a daily activity heatmap; and a product hierarchy sunburst.
- The Forex service uses Snowpark for aggregate queries and SQL for cumulative monthly volume. It also caches a full transaction-table download for five minutes.
- Three scripts in tests/ provide manual connection/analytics checks and an interactive Snowflake explorer. They are not an automated unit-test suite.

Detailed behavior is documented in [the report overview](reports/forex_performance/README.md), [the page guide](reports/forex_performance/pages/README.md), and [the services guide](services/README.md).

## Technology stack

| Dependency | Role in this application |
|---|---|
| Python | Runtime for the application and its scripts. The repository does not specify a required Python version. |
| streamlit[snowflake] | Streamlit renders the application and provides st.connection("snowflake"); the Snowflake extra supplies Snowflake integration dependencies. The app uses navigation, widgets, KPI display, native charts, Plotly rendering, dataframes, CSV download, and st.cache_data. |
| pandas | Receives service query results and transaction rows; the analysis pages coerce fields, filter rows, aggregate chart/matrix inputs, format the matrix, and generate CSV data. |
| plotly | Builds the channel pie/donut chart, transaction activity heatmap, and product hierarchy sunburst. Other report charts use Streamlit's native chart methods. |
| matplotlib | Declared directly in requirements.txt. The transaction matrix calls Pandas Styler background_gradient, which uses Matplotlib color mapping for the gradient. No direct Matplotlib plotting calls appear in application code. |

requirements.txt lists these four direct requirements without version pins. Snowpark is imported by the service through snowflake.snowpark.functions; it is supplied through the Snowflake integration dependency set rather than listed as a separate line in this requirements file. Other transitive packages are managed by those dependencies and are not enumerated here.

## Project structure

~~~text
.
├── README.md
├── app.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│   ├── secrets.example.toml
│   └── secrets.toml                 # local secret file; do not commit or disclose
├── components/
│   ├── README.md
│   ├── charts.py                    # currently empty
│   ├── filters.py                   # currently empty
│   ├── metrics.py                   # currently empty
│   └── navigation.py                # currently empty
├── config/
│   └── settings.py                  # currently empty
├── database/
│   ├── README.md
│   └── snowflake.py                 # shared Snowpark session helper
├── services/
│   ├── README.md
│   ├── analytics.py                 # currently empty
│   └── forex_analytics.py           # Forex queries and transaction retrieval
├── reports/
│   └── forex_performance/
│       ├── README.md
│       ├── report.py                # page registration and sidebar navigation
│       └── pages/
│           ├── README.md
│           ├── home.py
│           ├── performance.py
│           └── transaction_analysis.py
└── tests/
    ├── test_database_connection.py
    ├── test_forex_analytics.py
    └── test_snowflake_connection.py
~~~

| Location | Current responsibility |
|---|---|
| app.py | Streamlit entry point and global page configuration. |
| database/ | Shared Snowflake connection/session access. See [database documentation](database/README.md). |
| services/ | Snowflake-backed Forex aggregations and cached transaction retrieval. See [services documentation](services/README.md). |
| components/ | Reserved for reusable interface pieces; its current Python modules are empty. See [components documentation](components/README.md). |
| config/ | Reserved for application settings; settings.py is empty. |
| reports/ | Report packages. The Forex report owns its page registry and dashboard pages. |
| reports/forex_performance/ | Page registration, custom sidebar, and report documentation. |
| reports/forex_performance/pages/ | The three implemented dashboard pages and detailed page documentation. |
| tests/ | Manual diagnostics and analytics output scripts, not a conventional automated test suite. |
| .streamlit/ | Streamlit connection example and local secrets configuration. Actual secret values are intentionally excluded from this documentation. |
| requirements.txt | Direct Python dependencies. |

The tree omits the local virtual environment, Python caches, and package files. Empty package initializer files are omitted for readability.

## Application architecture and data flow

The current architecture is a small Streamlit application with one Snowflake-backed report. It does not include dbt, separate staging/intermediate/mart layers, a semantic layer, or other enterprise warehouse components.

1. A developer starts Streamlit with app.py. The script sets the page title, icon, and wide layout, then calls report.show().
2. reports/forex_performance/report.py registers three st.Page objects, creates st.navigation(..., position="hidden"), builds the visible sidebar from st.page_link() controls, and calls navigation.run() for the selected page.
3. Home calls get_forex_summary(). The two analysis pages call get_forex_transactions() and prepare the returned Pandas DataFrame.
4. Service functions obtain a Snowpark session through database/snowflake.py. Snowpark aggregations or SQL execute against the fully qualified Forex table in Snowflake.
5. The analysis pages filter downloaded Pandas rows locally. They calculate page KPIs and group rows into chart and matrix inputs in Python/Pandas.
6. Streamlit renders KPI cards, native charts, Plotly charts, a styled matrix, and the matrix CSV download.

Streamlit reruns a page script when a widget interaction changes its state. Transaction retrieval uses st.cache_data(ttl=300), so reruns can reuse its serialized result for up to five minutes. Filters and page-level calculations still run against that result on each rerun.

## Data source and fields

The service constant names UNIMONI_PRACTICE.FOREX.FOREX_TRANSACTIONS as the source. The pages and query functions reference these columns:

| Column | How the implementation uses it |
|---|---|
| TRANSACTION_ID | Counted distinctly for page KPIs and transaction groupings; required by page cleaning. |
| TRANSACTION_DATE | Date-range filter and monthly/daily grouping. |
| BRANCH | Filter and branch grouping. |
| CURRENCY | Filter and currency grouping. |
| PRODUCT | Transaction Analysis filter and sunburst grouping. |
| TRANSACTION_TYPE | Transaction Analysis filter and sunburst grouping. |
| CHANNEL | Filter, channel grouping, and sunburst grouping. |
| VOLUME_LOCAL | Summed for the Home page local volume metric. |
| VOLUME_USD | Summed or averaged for USD-volume KPIs, groupings, and charts. |
| RATE | Averaged for the Home page summary and branch analytics query. |

These uses follow from code references and field names. Formal business definitions, constraints, and the full Snowflake schema are Unable to verify from the repository alone. CUSTOMER_SEGMENT is not used by the inspected application code.

## Local setup and run

Prerequisites: Python installed, access to this repository, and a Snowflake account/role/warehouse with permission to query the configured source table. The repository does not declare a required Python version.

From the project root, create and activate a virtual environment, install the declared dependencies, and start the app:

~~~bash
python3 -m venv .venv
source .venv/bin/activate                 # macOS/Linux
# Windows PowerShell: py -3 -m venv .venv, then .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
~~~

Streamlit normally prints a local URL (commonly http://localhost:8501) in the terminal. Open that URL in a browser. Stop the server with Ctrl+C in the terminal. If activation fails, use the activation command for the current shell or invoke the environment's Python directly; do not install dependencies into a different environment by mistake.

The app requires a working Snowflake connection. Configure a local .streamlit/secrets.toml using the shape documented in .streamlit/secrets.example.toml; provide valid account/user authentication details and a warehouse/role with required access. The application calls st.connection("snowflake"), which reads Streamlit's named connection configuration. The fully qualified table name is fixed in the service, so the configured Snowflake principal must be able to access that database, schema, and table. Keep real credentials in the ignored local secrets file or an approved deployment secret store; never copy them into source or documentation.

## Configuration and security boundaries

.streamlit/secrets.example.toml is a template with placeholder values. .gitignore excludes .streamlit/secrets.toml; the example is not a substitute for a valid local connection. The app delegates Snowflake connection construction to Streamlit's connection integration and then requests its Snowpark session.

The repository demonstrates credential configuration, but it does not implement application sign-in, viewer authorization, role-based access control, or row-level restrictions. Snowflake permissions govern the connected principal's data access; they do not, by themselves, authenticate or authorize each application viewer. Deployment access controls and production authentication are not configured in the inspected project. See [database connection guidance](database/README.md).

## Validation scripts

The files under tests/ are developer scripts, not automatically discovered unit tests with assertions:

- test_database_connection.py prints the current database, schema, and role using the shared session helper.
- test_forex_analytics.py calls each service aggregation and prints its returned DataFrame.
- test_snowflake_connection.py is an interactive Streamlit explorer for connection metadata, visible databases/schemas/tables, column metadata, and a ten-row table preview.

With the project environment activated, run the first two from the repository root, for example python tests/test_database_connection.py and python tests/test_forex_analytics.py. Run the explorer with streamlit run tests/test_snowflake_connection.py. These scripts require Snowflake connectivity and suitable permissions; they do not establish automated test coverage or validate every dashboard visualization. No live database validation was performed while preparing this documentation.

## Current scope and limitations

- The two analytical pages download the full table into Pandas before applying interactive filters. This transfers data and uses application memory; the five-minute cache reduces repeat downloads but means new rows can take up to five minutes to appear in that cached result.
- Detailed filters and most dashboard aggregations execute locally in Pandas rather than being pushed down to Snowflake. Summary/service aggregation functions execute in Snowflake.
- The monthly performance chart groups all selected rows by month. A selected range that begins or ends mid-month produces partial-month totals; those should not be compared as full-month values without accounting for the date boundaries.
- Empty components/ and config/ modules do not provide the reusable or settings behavior their names may suggest. The general services/analytics.py module is also empty.
- The scripts in tests/ provide manual checks, not regression coverage. Production deployment, application authentication, authorization, and row-level policies are not configured here.
- Future-dated records are handled when setting the default date range: if all records are later than today, the pages use the dataset's maximum date. The underlying data's business status (for example, synthetic versus live) is Unable to verify.

## Detailed documentation

- [Database layer](database/README.md): Snowflake session access, connection configuration, and troubleshooting.
- [Services](services/README.md): query functions, returned data, aggregations, and caching.
- [Components](components/README.md): current status and intended scope of reusable UI modules.
- [Forex report](reports/forex_performance/README.md): report setup, page registration, and sidebar navigation.
- [Dashboard pages](reports/forex_performance/pages/README.md): filters, KPI formulas, tables, charts, and page-to-service mapping.

## Project notes

The original project goals and architecture have been retained here and expanded to reflect the implementation currently present in the repository. This documentation describes the application as inspected; it does not claim that proposed enterprise data-platform capabilities have been delivered.
