# Database Layer

## Purpose

Centralizes database connectivity for the application.

## Files

- `snowflake.py`: Provides the Snowflake session used by reports
  and analytics services.
- `__init__.py`: Marks this directory as a Python package.

## Snowflake Connection

The application uses Streamlit's Snowflake connection integration.

Connection settings and local credentials are maintained in
`.streamlit/secrets.toml`.

Use `get_snowflake_session()` to obtain a session.

## Guidelines

- Reuse the central connection function.
- Keep report-specific SQL in the services layer.
- Never commit credentials to Git.

## Change Log

- 2026-10-12: Documented the database layer.
- 2026-10-12: Added a reusable Snowflake session function.