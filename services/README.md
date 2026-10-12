# Services

## Purpose
Contains data retrieval and business analytics logic.

## Files
- `analytics.py`: General analytics functions.
- `forex_analytics.py`: Queries and aggregations for the Forex report.

## Query Conventions
- Prefer Snowpark for straightforward filtering, grouping,
  and aggregations.
- Use SQL when it expresses complex analytical logic more clearly.
- Both approaches use the shared Snowflake connection.
- Perform aggregations in Snowflake whenever practical.

## Change Log
- 2026-10-12: Documented the services layer.
- 2026-10-12: Added Forex summary, monthly, and branch analytics.
- 2026-10-12: Added monthly cumulative volume using SQL.