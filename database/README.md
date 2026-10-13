# Database layer

The database package centralizes how application code obtains a Snowflake session. Keeping this small adapter separate means report pages and analytics functions can request a session without each implementing Streamlit connection setup. Query definitions and dashboard calculations belong in the services and report layers, respectively.

## Files

| File | Responsibility |
|---|---|
| snowflake.py | Implements get_snowflake_session(), the shared connection helper. |
| __init__.py | Package marker; contains no additional behavior. |

## Snowflake session

get_snowflake_session() calls st.connection("snowflake").session() and returns the Snowpark Session exposed by Streamlit's named Snowflake connection. It accepts no arguments and has no custom return wrapper. Callers use the returned session to access a table with session.table(), issue SQL with session.sql(), and convert results to Pandas where needed.

Streamlit's connection integration reads the named connection configuration from Streamlit configuration/secrets. The repository includes .streamlit/secrets.example.toml as a placeholder template; create a local .streamlit/secrets.toml with valid connection configuration and keep it private. The exact authentication mode depends on the local/deployment connection settings. Do not put credentials in Python or commit real secrets.

The helper contains no explicit retry logic, exception handling, or additional cache decorator. Streamlit manages its connection integration; the application code simply requests its Snowpark session. Do not confuse connection/session handling with viewer authentication or data authorization.

## Data-access flow

1. A page calls a function in services/forex_analytics.py, or a validation script calls the shared helper.
2. The service calls get_snowflake_session() to obtain the session.
3. Snowpark table operations or session.sql() execute against Snowflake using the configured principal and its permissions.
4. The service returns query results as a Pandas DataFrame. For detailed dashboards, the service downloads the full source table; page filtering and visual calculations then happen locally in Pandas.

The current source table is fully qualified in the service as UNIMONI_PRACTICE.FOREX.FOREX_TRANSACTIONS. Access therefore depends on the configured principal having permission to use the referenced database, schema, table, and an appropriate warehouse. Service query logic and return details are documented in [services/README.md](../services/README.md); page behavior is in [the Forex page guide](../reports/forex_performance/pages/README.md).

## Configuration and security

- Use the named Snowflake connection expected by st.connection("snowflake").
- Treat secrets.example.toml as a template, not as credentials.
- Keep the real local secrets file out of version control; the repository .gitignore excludes .streamlit/secrets.toml.
- Use an approved secrets store when deploying, and grant the Snowflake principal only the required access.
- Do not print credentials or connection secrets while diagnosing failures.

This layer does not implement application login, per-viewer authorization, RBAC, row-level policies, or deployment access restrictions. Snowflake permissions apply to the connection principal; they do not independently protect an application endpoint from its viewers.

## Troubleshooting

| Symptom | Checks |
|---|---|
| Streamlit reports that the snowflake connection is missing or invalid | Confirm that local Streamlit secrets are present, valid TOML, and define the expected named connection. Do not paste the secret contents into logs or chat. |
| Authentication/connection failure | Verify account and authentication settings with the Snowflake administrator; confirm network access and that the credentials or identity are active. |
| Database, schema, or table not found/accessible | Confirm the fixed source identifier and that the connected role can use the database/schema and select from the table. |
| Warehouse error | Confirm a warehouse is configured and the connected role has permission to use it. |
| Connection works but an analytics query fails | Inspect the failing query and returned column names in services/forex_analytics.py; check the source schema and Snowflake role grants. |

Exact account settings and deployment-specific authentication requirements are environment-dependent and cannot be established from this helper alone.
