# Forex Performance report

This package assembles the Forex analytics experience used by the root Streamlit application. It owns report-level page registration and the visible sidebar, while each individual page owns its presentation, widgets, and page-level calculations. The service layer supplies Snowflake-backed data; see [services/README.md](../../services/README.md).

## Entry and registration

The runtime chain begins in the repository's app.py:

1. app.py calls st.set_page_config() for the page title, icon, and wide layout.
2. It imports this package's report module and calls report.show().
3. show() creates three st.Page entries, in order: Home (default), Forex Performance, and Transaction Analysis. Each entry specifies a page script, user-facing title, and URL path.
4. show() passes the page objects to st.navigation(..., position="hidden"). The hidden position suppresses Streamlit's built-in navigation menu; it does not hide the application pages or provide access control.
5. The report builds a custom sidebar with a title, caption, and st.page_link() entries referring to the registered Page objects. The sidebar also labels Snowflake as the data source.
6. navigation.run() executes the selected page. Streamlit reruns the selected page script in response to navigation or widget state changes.

The sidebar is therefore custom presentation over Streamlit's page navigation. It is not a separate authorization mechanism. The report does not implement role-based visibility or user sign-in.

## Page responsibilities

| Page | Purpose | Data dependency |
|---|---|---|
| Home | Landing page with overall Forex summary metrics and links into the report. | Calls services.forex_analytics.get_forex_summary(). |
| Forex Performance | Date/branch/currency/channel-filtered trend, branch, currency, and channel views. | Calls get_forex_transactions() and filters/aggregates locally in Pandas. |
| Transaction Analysis | Filtered transaction characteristics, matrix, daily activity, and product hierarchy. | Calls get_forex_transactions() and filters/aggregates locally in Pandas. |

Individual page widgets and KPI/chart formulas are documented in [pages/README.md](pages/README.md). The page modules invoke their own show() function at module end; Streamlit runs that page script when selected. report.py does not pass query results or shared page state into the page functions.

## Navigation links

The sidebar's st.page_link() calls use the Page objects created in show(), so the selected destination remains associated with the registered route. Home also has links to the two analysis scripts, and each analysis page provides a Home link in its content. These are navigation controls only; data remains loaded by the page's service call.

## Data path

The report layer does not query Snowflake itself. Home delegates its aggregate to the service layer. The analysis pages request a cached full-table Pandas DataFrame and apply their own cleaning, widget selections, aggregations, and rendering. For connection details, see [database/README.md](../../database/README.md); for function behavior and cache semantics, see [services/README.md](../../services/README.md).
